import json
import logging
import set_tags.utils as utils

from crhelper import CfnResource

MISSING_BUCKET_NAME_ERROR_MESSAGE = 'BucketName parameter is required'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='DEBUG')


def get_bucket_name(event):
  '''Get the bucket name from event params sent to lambda'''
  resource_properties = event.get('ResourceProperties')
  bucket_name = resource_properties.get('BucketName')
  if not bucket_name:
    raise ValueError(MISSING_BUCKET_NAME_ERROR_MESSAGE)
  return bucket_name


def get_bucket_tags(bucket_name):
  '''Look up the bucket tags'''
  client = utils.get_s3_client()
  response = client.get_bucket_tagging(Bucket=bucket_name)
  log.debug(f'S3 bucket tags response: {response}')
  tags = response.get('TagSet')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')

  return tags


def apply_tags(name, tags):
  '''Apply tags to an S3 resource'''
  client = utils.get_s3_client()
  response = client.put_bucket_tagging(
    Bucket=name,
    Tagging={
      'TagSet': tags
    }
  )
  log.debug(f'Apply tags response: {response}')


@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start Lambda processing')
  bucket_name = get_bucket_name(event)
  bucket_tags = get_bucket_tags(bucket_name)
  synapse_ower_id = utils.get_synapse_ower_id(bucket_tags)
  synapse_tags = utils.get_synapse_tags(synapse_ower_id)
  # put_bucket_tagging is a replace operation.  need to give it all
  # tags otherwise it will remove existing tags not in the list
  all_tags = list(bucket_tags + synapse_tags)
  log.debug(f'Apply tags: {all_tags} to bucket {bucket_name}')
  apply_tags(bucket_name, all_tags)


@helper.delete
def delete(event, context):
  '''Handles custom resource delete events'''
  pass


def handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
