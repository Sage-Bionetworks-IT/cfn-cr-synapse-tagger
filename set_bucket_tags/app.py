import json
import logging
import synapseclient
import boto3
import os

from crhelper import CfnResource


MISSING_BUCKET_NAME_ERROR_MESSAGE = 'BucketName parameter is required'
SYNAPSE_TAG_PREFIX = 'synapse'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

synapseclient.core.cache.CACHE_ROOT_DIR = '/tmp/.synapseCache'

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='DEBUG')


def get_s3_client():
  return boto3.client('s3')

def get_synapse_client():
  return synapseclient.Synapse()

def get_bucket_name(event):
  '''Get the bucket name from event params sent to lambda'''
  resource_properties = event.get('ResourceProperties')
  bucket_name = resource_properties.get('BucketName')
  if not bucket_name:
    raise ValueError(MISSING_BUCKET_NAME_ERROR_MESSAGE)
  return bucket_name


def get_bucket_tags(bucket_name):
  '''Look up the bucket tags'''
  client = get_s3_client()
  response = client.get_bucket_tagging(Bucket=bucket_name)
  log.debug(f'S3 bucket tags response: {response}')
  tags = response.get('TagSet')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')
  return tags


def get_principal_id(tags):
  '''Find the value of the principal arn among the bucket tags'''
  principal_arn_tag = 'aws:servicecatalog:provisioningPrincipalArn'
  for tag in tags:
    if tag.get('Key') == principal_arn_tag:
      principal_arn_value = tag.get('Value')
      principal_id = principal_arn_value.split('/')[-1]
      return principal_id
  else:
    raise ValueError('Could not derive a provisioningPrincipalArn from tags')


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
  '''Get synapse team IDs'''
  TeamToRoleArnMap = os.getenv('TEAM_TO_ROLE_ARN_MAP_PARAM_NAME')
  ssm_param = get_ssm_parameter(TeamToRoleArnMap)
  team_to_role_arn_map = json.loads(ssm_param["Parameter"]["Value"])
  log.debug(f'/service-catalog/TeamToRoleArnMap value: {team_to_role_arn_map}')
  team_ids = []
  for item in team_to_role_arn_map:
    team_ids.append(item["teamId"])

  log.debug(f'Synapse team IDs: {team_ids}')
  return team_ids


def get_synapse_user_team_id(synapse_id, team_ids):
  '''Get the Synapse team that the user is in
  :param synapse_id: synapse user id
  :param team_ids: the synapse team ids
  :returns: the synapse team id that the user is in, None if user is not
            in any teams
  '''
  syn = get_synapse_client()
  for team_id in team_ids:
    membership_status = syn.get_membership_status(synapse_id, team_id)
    if membership_status["isMember"]:
      log.debug(f'Synapse user team ID: {team_id}')
      return team_id

  return None

def get_synapse_user_profile_tags(user_profile, ignore_keys=["createdOn"]):
  '''Derive synapse tags from synapse user profile data
  :param user_profile: the synapse user profile info
  :param ignore_keys: the keys from the user profile to ignore
         Note - no email tags are returned if userName is ignored
  :return a list containing a dictionary of tags
  '''
  tags = []
  for key, value in user_profile.items():
    if key in ignore_keys:
      continue

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


@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start Lambda processing')
  bucket_name = get_bucket_name(event)
  bucket_tags = get_bucket_tags(bucket_name)
  principal_id = get_principal_id(bucket_tags)
  synapse_tags = get_synapse_tags(principal_id)
  # put_bucket_tagging is a replace operation.  need to give it all
  # tags otherwise it will remove existing tags not in the list
  all_tags = list(bucket_tags + synapse_tags)
  log.debug(f'Tags to apply: {all_tags}')
  client = get_s3_client()
  tagging_response = client.put_bucket_tagging(
    Bucket=bucket_name,
    Tagging={ 'TagSet': all_tags }
    )
  log.debug(f'Tagging response: {tagging_response}')


@helper.delete
def delete(event, context):
  '''Handles custom resource delete events'''
  pass


def handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
