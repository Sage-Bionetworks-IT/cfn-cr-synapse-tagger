import json
import logging
import synapseclient
import boto3
import os
import re

SYNAPSE_TAG_PREFIX = 'synapse'
SYNAPSE_USER_PROFILE_INCLUDES = [
  "ownerId", "firstName", "lastName", "userName", "company", "teamName",
]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

synapseclient.core.cache.CACHE_ROOT_DIR = '/tmp/.synapseCache'


def get_s3_client():
  return boto3.client('s3')

def get_ec2_client():
  return boto3.client('ec2')

def get_iam_client():
  return boto3.client('iam')

def get_dynamo_client():
  return boto3.client('dynamodb')

def get_synapse_client():
  return synapseclient.Synapse()

def get_env_var_value(env_var):
  '''Get the value of an environment variable'''
  return os.getenv(env_var)

def get_synapse_owner_id(tags):
  '''Find the value of the principal ARN among the resource tags. The principal
  ARN tag is applied by AWS and it's value should be in the following format
  'arn:aws:sts::111111111:assumed-role/ServiceCatalogEndusers/1234567'
  '''
  principal_arn_tag = 'aws:servicecatalog:provisioningPrincipalArn'
  for tag in tags:
    if tag.get('Key') == principal_arn_tag:
      principal_arn_value = tag.get('Value')
      synapse_owner_id = principal_arn_value.split('/')[-1]
      return synapse_owner_id
  else:
    raise ValueError(f'Expected to find {principal_arn_tag} in {tags}')

def get_synapse_user_profile(synapse_id):
  '''Get synapse user profile data'''
  syn = get_synapse_client()
  user_profile = syn.getUserProfile(synapse_id)
  log.debug(f'Synapse user profile: {user_profile}')
  return user_profile

def get_ssm_parameter(name):
  '''Get an parameter from the SSM parameter store'''
  client = boto3.client('ssm')
  parameter = client.get_parameter(Name=name)
  log.debug(f'Synapse ssm parameter: {parameter}')
  return parameter

def get_synapse_team_ids():
  '''Return the list of IDs of teams through which a user can access service catalog'''
  TeamToRoleArnMap = get_env_var_value('TEAM_TO_ROLE_ARN_MAP_PARAM_NAME')
  ssm_param = get_ssm_parameter(TeamToRoleArnMap)
  team_to_role_arn_map = json.loads(ssm_param["Parameter"]["Value"])
  log.debug(f'/service-catalog/TeamToRoleArnMap value: {team_to_role_arn_map}')
  team_ids = []
  for item in team_to_role_arn_map:
    team_ids.append(item["teamId"])

  log.debug(f'Synapse team IDs: {team_ids}')
  return team_ids

def get_synapse_user_team_id(synapse_id, team_ids):
  '''Get the first Synapse team in the given list that the user is in
  :param synapse_id: synapse user id
  :param team_ids: the synapse team ids
  :returns: the id of the first synapse team in the given list that the user is in,
            None if user is not in any teams
  '''
  syn = get_synapse_client()
  for team_id in team_ids:
    membership_status = syn.get_membership_status(synapse_id, team_id)
    if membership_status["isMember"]:
      log.debug(f'Synapse user team ID: {team_id}')
      return team_id

  return None

def get_synapse_user_profile_tags(user_profile, includes=SYNAPSE_USER_PROFILE_INCLUDES):
  '''Derive synapse tags from synapse user profile data
  :param user_profile: the synapse user profile info
  :param includes: list of Synapse userProfile data to create tags
         Note - no email tags are returned if userName is not in the list
  :return a list containing a dictionary of tags
         Note - AWS tag restrictions only allow a subset of characters for tag values.
         The returned list will contain sanitized tag values.
         https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html#tag-restrictions
  '''
  VALID_TAG_CHARS = r'[^a-zA-Z0-9.+=_:@/\-]'

  tags = []
  for key, value in user_profile.items():
    if key not in includes:
      continue

    # replace invalid characters with a space
    value = re.sub(VALID_TAG_CHARS, ' ', value)

    # derive synapse email tag based on userName
    if key == "userName":
      synapse_email = f'{value}@synapse.org'
      tags.append({'Key': f'{SYNAPSE_TAG_PREFIX}:email', 'Value': synapse_email})
      tags.append({'Key': 'OwnerEmail', 'Value': synapse_email})  # legacy

    tag = {'Key': f'{SYNAPSE_TAG_PREFIX}:{key}', 'Value': value}
    tags.append(tag)

  log.debug(f'Synapse user profile tags: {tags}')
  return tags

def get_synapse_user_team_tags(synapse_id, synapse_team_ids):
  '''Derive team tags from synapse team data'''
  tags = []
  user_team_id = get_synapse_user_team_id(synapse_id, synapse_team_ids)
  if user_team_id:
    tags.append({'Key': f'{SYNAPSE_TAG_PREFIX}:teamId', 'Value': user_team_id})

  log.debug(f'Synapse user team tags: {tags}')
  return tags

def get_synapse_tags(synapse_id):
  '''Derive synapse tags to apply to SC resources'''

  user_profile = get_synapse_user_profile(synapse_id)
  synapse_user_tags = get_synapse_user_profile_tags(user_profile)
  synapse_team_ids = get_synapse_team_ids()
  synapse_team_tags = get_synapse_user_team_tags(synapse_id, synapse_team_ids)
  tags = list(synapse_user_tags + synapse_team_tags)
  log.debug(f'Synapse tags: {tags}')
  return tags

def get_provisioned_product_name_tag(tags):
  '''Get provisioned product name among the resource tags.
  :param tags: the list of tags on the instance, assume to contain a provisioned product
         ARN tag that is applied by AWS and its value should be in the following format
         'arn:aws:servicecatalog:us-east-1:123456712:stack/my-product/pp-mycpuogt2i45s'
  :return a dict containing the the product name tag
  '''
  PRODUCT_ARN_TAG_KEY = 'aws:servicecatalog:provisionedProductArn'
  for tag in tags:
    if tag.get('Key') == PRODUCT_ARN_TAG_KEY:
      provisioned_product_arn_value = tag.get('Value')
      provisioned_product_arn_name = provisioned_product_arn_value.split('/')[-2]
      provisioned_product_arn_tag = {
        'Key': 'Name',
        'Value': provisioned_product_arn_name
      }
      log.debug(f'provisioned product arn tag: {provisioned_product_arn_tag}')
      return provisioned_product_arn_tag
  else:
    raise ValueError(f'Expected to find {PRODUCT_ARN_TAG_KEY} in {tags}')

def get_access_approved_role_tag(tags):
  '''Get the access approve role tag from among the resource tags.
  :param tags: the list of tags on the instance, assume to contain a principal
         ARN tag that is applied by AWS and its value should be in the following format
         'arn:aws:sts::111111111:assumed-role/ServiceCatalogEndusers/1234567'
  :return a dict containing the access approved role tag
  '''
  PRINCIPAL_ARN_TAG_KEY = 'aws:servicecatalog:provisioningPrincipalArn'
  for tag in tags:
    if tag.get('Key') == PRINCIPAL_ARN_TAG_KEY:
      principal_arn_value = tag.get('Value')
      synapse_owner_id = principal_arn_value.split('/')[-1]
      assumed_role_name = principal_arn_value.split('/')[-2]
      client = get_iam_client()
      response = client.get_role(
        RoleName=assumed_role_name
      )
      access_approved_role = response['Role']['RoleId']
      access_approved_role_tag = {
        'Key': 'Protected/AccessApprovedCaller',
        'Value': f'{access_approved_role}:{synapse_owner_id}'
      }
      log.debug(f'access approved role tag: {access_approved_role_tag}')
      return access_approved_role_tag
  else:
    raise ValueError(f'Expected to find {PRINCIPAL_ARN_TAG_KEY} in {tags}')

def get_marketplace_customer_id(synapse_id):
  '''Get the Service Catalog customer ID.
  :param synapse_id: synapse user id
  :return the customer ID of the service catalog subscriber, None if cannot find customer ID
  '''
  marketplace_table_name = get_env_var_value('MARKETPLACE_ID_DYNAMO_TABLE_NAME')
  customer_id = None
  client = get_dynamo_client()
  try:
    response = client.get_item(
      Key={
        'userId': {
          'S': synapse_id,
        }
      },
      TableName=marketplace_table_name,
      ConsistentRead=True,
      AttributesToGet=[
        'marketplaceCustomerId'
      ]
    )
    customer_id = response["Item"]["marketplaceCustomerId"]["S"]
    log.debug(f'marketplace customer id: {customer_id}')
  except Exception as e:
    log.debug(e.response['Error']['Message'])

  return customer_id

def get_marketplace_tags(synapse_id):
  '''Get the AWS Marketplace tags
  :param synapse_id: synapse user id
  :return a dict containing the marketplace SC product tags
  '''
  tags = []

  marketplace_product_code_sc = get_ssm_parameter("MarketplaceProductCodeSC")
  if marketplace_product_code_sc:
    tags.append({'Key': f'{SYNAPSE_TAG_PREFIX}:marketplaceProductCode', 'Value': marketplace_product_code_sc})

  marketplace_customer_id = get_marketplace_customer_id(synapse_id)
  if marketplace_customer_id:
    tags.append({'Key': f'{SYNAPSE_TAG_PREFIX}:marketplaceCustomerId', 'Value': marketplace_customer_id})

  log.debug(f'Marketplace SC product code tags: {tags}')
  return tags
