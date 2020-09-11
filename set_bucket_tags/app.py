import json
import logging
import synapseclient
import boto3

from crhelper import CfnResource


MISSING_BUCKET_NAME_ERROR_MESSAGE = 'BucketName parameter is required'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

synapseclient.core.cache.CACHE_ROOT_DIR = '/tmp/.synapseCache'

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='DEBUG')


def get_s3_client():
  return boto3.client('s3')


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


def merge(list_x, list_y):
  '''Merge two list of tags'''
  z = []
  for x in list_x:
    z.append(x)

  for y in list_y:
    z.append(y)

  return z


@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start SetBucketTags Lambda processing')
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  bucket_name = get_bucket_name(event)
  bucket_tags = get_bucket_tags(bucket_name)
  principal_id = get_principal_id(bucket_tags)
  user_profile = get_synapse_userProfile(principal_id)
  synapse_tags = get_synapse_tags(user_profile)
  # put_bucket_tagging is a replace operation.  need to give it all
  # tags otherwise it will remove existing tags not in the list
  all_tags = merge(bucket_tags, synapse_tags)
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
