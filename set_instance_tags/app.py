import json
import logging
import synapseclient
import boto3

from crhelper import CfnResource


MISSING_INSTANCE_ID_ERROR_MESSAGE = 'InstanceId parameter is required'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

synapseclient.core.cache.CACHE_ROOT_DIR = '/tmp/.synapseCache'

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='INFO')


def get_ec2_client():
  return boto3.client('ec2')


def get_instance_id(event):
  '''Get the instance id from event params sent to lambda'''
  resource_properties = event.get('ResourceProperties')
  instance_id = resource_properties.get('InstanceId')
  if not instance_id:
    raise ValueError(MISSING_INSTANCE_ID_ERROR_MESSAGE)
  return instance_id


def get_instance_tags(instance_id):
  '''Look up the instance tags'''
  client = get_ec2_client()
  response = client.describe_tags(
    Filters = [{'Name': 'resource-id', 'Values': [instance_id]}]
  )
  log.debug(f'EC2 describe tags response: {response}')
  tags = response.get('Tags')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')

  return tags


def get_principal_id(tags):
  '''Find the value of the principal arn among the EC2 tags'''
  principal_arn_tag = 'aws:servicecatalog:provisioningPrincipalArn'
  for tag in tags:
    if tag.get('Key') == principal_arn_tag:
      principal_arn_value = tag.get('Value')
      principal_id = principal_arn_value.split('/')[-1]
      return principal_id
  else:
    raise ValueError('Could not derive a provisioningPrincipalArn from tags')


def get_synapse_userProfile(synapse_id):
  '''Get synapse user profile data'''
  syn = synapseclient.Synapse()
  user_profile = syn.getUserProfile(synapse_id)
  log.debug(f'Synapse user profile: {user_profile}')

  return user_profile


def get_synapse_tags(user_profile):
  '''Derive synapse tags from synapse user profile data'''

  tags = []
  IGNORE_KEYS = ["createdOn"]
  for key, value in user_profile.items():
    if key in IGNORE_KEYS:
      continue

    # derive synapse email tag based on userName
    if key == "userName":
      synapse_email = f'{value}@synapse.org'
      tags.append({'Key': 'synapse:email', 'Value': synapse_email})
      tags.append({'Key': 'OwnerEmail', 'Value': synapse_email})  # legacy

    tag = {'Key': f'synapse:{key}', 'Value': value}
    tags.append(tag)

  log.debug(f'Synapse tags: {tags}')
  return tags


@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start Lambda processing')
  instance_id = get_instance_id(event)
  instance_tags = get_instance_tags(instance_id)
  principal_id = get_principal_id(instance_tags)
  user_profile = get_synapse_userProfile(principal_id)
  synapse_tags = get_synapse_tags(user_profile)
  log.debug(f'Tags to apply: {synapse_tags}')
  client = get_ec2_client()
  tagging_response = client.create_tags(
    Resources=[instance_id],
    Tags=synapse_tags
  )
  log.debug(f'Tagging response: {tagging_response}')


@helper.delete
def delete(event, context):
  '''Handles custom resource delete events'''
  pass


def handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
