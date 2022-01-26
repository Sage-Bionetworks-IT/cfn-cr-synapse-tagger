import json
import logging
import set_tags.utils as utils

from crhelper import CfnResource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='CRITICAL')


def get_batch_tags(resource_arn):
  '''Look up the batch tags

  resource_arn: the ARN of the AWS resource
  '''
  client = utils.get_batch_client()
  response = client.list_tags_for_resource(
    resourceArn=resource_arn
  )
  log.debug(f'batch list_tags_for_resouce response: {response}')
  tags = response.get('tags')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')

  return tags

def apply_tags(resource_arn, tags):
  '''Apply tags to a batch resource

  resource_arn: the ARN of the AWS resource
  tags: A dictionary of key pairs
      i.e. tags:{'string':'string'}
  '''
  client = utils.get_batch_client()
  response = client.tag_resource(
    resourceArn=resource_arn,
    tags=tags
  )
  log.debug(f'Apply tags response: {response}')

@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start Lambda processing')

  # workaround for AWS bug in issue SC-379 (AWS case 9477374541)
  # get synapse owner id from cloudformation stack
  stack_id = utils.get_stack_id(event)
  stack_tags = utils.get_cfn_stack_tags(stack_id)
  synapse_owner_id = utils.get_synapse_owner_id(stack_tags)

  # get synapse tags and format it into dict key/pair
  synapse_tags_kv = utils.get_synapse_tags(synapse_owner_id)
  synapse_tags_kp = utils.format_tags_kv_kp(synapse_tags_kv)

  # get passed in batch resource ARNs
  batch_resources = utils.get_property_value(event, "BatchResources")
  if not batch_resources:
    raise Exception(f'No batch resources passed in, received: {batch_resources}')

  # apply tags to each batch resource
  for key, value in batch_resources.items():
    resource_arn = value
    log.debug(f'Apply tags: {synapse_tags} to resource {resource_arn}')
    apply_tags(resource_arn, synapse_tags_kp)

@helper.delete
def delete(event, context):
  '''Handles custom resource delete events'''
  pass


def handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
