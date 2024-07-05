import json
import logging
import synapseclient
import boto3
import botocore
import os
import re

from botocore.exceptions import ClientError

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

def get_batch_client():
  return boto3.client('batch')

def get_iam_client():
  return boto3.client('iam')

def get_synapse_client():
  return synapseclient.Synapse()

def get_cfn_client():
  return boto3.client('cloudformation')

def get_stack_id(event):
  '''Get the stack id from the event

  evemt: the service catalog event
  returns: the stack id
  '''
  stack_id = event.get('StackId')
  if not stack_id:
    raise AssertionError(f'StackId property not in service catalog event')

  return stack_id

def get_property_value(event, property):
  '''Get the resource properties from event params sent to lambda

  evemt: the service catalog event
  property: the passed in property from the service catalog template
  returns: the value for the property
  '''
  resource_properties = event.get('ResourceProperties')
  property_value = resource_properties.get(property)
  if not property_value:
    raise ValueError(f'Template property {property} not found')

  return property_value

def format_tags_kv_kp(tags):
  '''Format tags from a list of Key/Value pairs to a dict of key pairs

  tags: A list of dictionary of key/value pairs
      i.e. tags:[{'Key':'string', 'Value':'string'}]
  returns:  A dictionary of key pairs
      i.e. tags:{'string':'string'}
  '''
  kp = {}
  for tag in tags:
    kp[tag['Key']] = tag['Value']

  return kp

def get_cfn_stack_tags(stack_id):
  '''Look up tags from a cloudformation stack

  returns: A list of dictionary of key/value pairs
      i.e. tags:[{'Key':'string', 'Value':'string'}]
  '''
  client = get_cfn_client()
  response = client.describe_stacks(
    StackName=stack_id
  )
  log.debug(f'cloudformation describe_stacks response: {response}')
  stack = response.get('Stacks')[0]
  tags = stack.get('Tags')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')

  return tags

def get_env_var_value(env_var):
  '''Get the value of an environment variable
  :param env_var: the environment variable
  :returns: the environment variable's value, None if env var is not found
  '''
  value = os.getenv(env_var)
  if not value:
    log.warning(f'cannot get environment variable: {env_var}')

  return value

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

def get_synapse_owner_id(tags):
  '''Find the value of the principal ARN among the resource tags. The principal
  ARN tag is applied by AWS and it's value should be in the following format
  'arn:aws:sts::111111111:assumed-role/ServiceCatalogEndusers/378505'
  :param tags: resource tags can take two forms
    * A list of dictionary of key/value pairs
      i.e. tags:[{'Key':'string', 'Value':'string'}]
    * A dictionary of key pairs
      i.e. tags:{'string':'string'}
  returns: the synapse user id (i.e. 378505)
  '''
  principal_arn_tag = 'aws:servicecatalog:provisioningPrincipalArn'
  synapse_owner_id = None

  if isinstance(tags, list):  # tags:[{'Key':'string', 'Value':'string'}]
    for tag in tags:
      if tag.get('Key') == principal_arn_tag:
        principal_arn_value = tag.get('Value')
        synapse_owner_id = principal_arn_value.split('/')[-1]
  if isinstance(tags, dict):  # tags:{'string':'string'}
    if principal_arn_tag in tags:
        principal_arn_value = tags.get(principal_arn_tag)
        synapse_owner_id = principal_arn_value.split('/')[-1]

  if synapse_owner_id is None:
      raise ValueError(f'{principal_arn_tag} not found in tags: {tags}')

  return synapse_owner_id

def get_synapse_user_profile(synapse_id):
  '''Get synapse user profile data'''
  syn = get_synapse_client()
  user_profile = syn.getUserProfile(synapse_id)
  log.debug(f'Synapse user profile: {user_profile}')
  return user_profile

def get_ssm_parameter(name):
  '''
  Get a parameter from the SSM parameter store
  :param name: the parameter name
  :return: a parameter dict, None if the parameter name is not found
  '''
  client = boto3.client('ssm')
  parameter = None
  try:
    parameter = client.get_parameter(Name=name)
    log.debug(f'SSM parameter value: {parameter}')
  except ClientError as e:
    if e.response['Error']['Code'] == "ParameterNotFound":
      log.warning(f'Could not find SSM parameter {name}')
    else:
      raise(e)

  return parameter

def get_synapse_team_ids():
  '''Return the list of IDs of teams through which a user can access service catalog'''
  team_ids = []
  TeamToRoleArnMap = get_env_var_value('TEAM_TO_ROLE_ARN_MAP_PARAM_NAME')
  if TeamToRoleArnMap:
    ssm_param = get_ssm_parameter(TeamToRoleArnMap)
    if ssm_param:
      team_to_role_arn_map = json.loads(ssm_param["Parameter"]["Value"])
      log.debug(f'ssm param: {TeamToRoleArnMap} = {team_to_role_arn_map}')
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
  '''
  Derive synapse tags to apply to SC resources
  Returns a list of key/value pairs of tags
  :param synapse_id: the synapse user id
  :return A list containing a dictionary of key/value pairs representing tags
  '''

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

def merge_tags(list1, list2):
  '''Merge two lists of tags, the second overriding the first on key collisions
  '''
  unique_tags = format_tags_kv_kp(list1)
  unique_tags.update(format_tags_kv_kp(list2))
  result=[]
  for entry in unique_tags:
      result.append({'Key':entry,'Value':unique_tags[entry]})
  return result
