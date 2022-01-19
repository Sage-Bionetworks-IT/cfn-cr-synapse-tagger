import json
import logging
import set_tags.utils as utils

from crhelper import CfnResource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='CRITICAL')


def get_resource_arn(event, parameter):
  '''Get the resource ARN from event params sent to lambda'''
  resource_properties = event.get('ResourceProperties')
  resource_arn = resource_properties.get(parameter)
  if not resource_arn:
    raise ValueError(f'Missing template parameter: {parameter}')
  return resource_arn

def get_resource_tags(resource_arn):
  '''Look up the resource tags'''
  client = utils.get_batch_client()
  response = client.list_tags_for_resource(
    resourceArn=resource_arn
  )
  log.debug(f'batch list_tags_for_resouce response: {response}')
  tags = response.get('tags')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')

  return tags

def apply_tags(name, resource_arn, tags):
  '''Apply tags to a batch resource'''
  client = utils.get_batch_client()
  batch_formatted_tags = {}  # batch accepts tags formatted as tags={'string': 'string'}
  for tag in tags:
    batch_formatted_tags[tag['Key']] = tag['Value']
  response = client.tag_resource(
    resourceArn=resource_arn,
    tags=batch_formatted_tags
  )
  log.debug(f'Apply tags response: {response}')

@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start Lambda processing')
  # Batch resources that support tags are compute environments, jobs, job definitions,
  # job queues, and scheduling policies
  template_input_parameters = [
    "JobDefinitionArn",
    "JobQueueArn",
    "ComputeEnvironmentArn",
    "SchedulingPolicyArn"
  ]
  for template_input_parameter in template_input_parameters:
    resource_arn = get_resource_arn(event, template_input_parameter)
    resource_tags = get_resource_tags(resource_arn)
    synapse_owner_id = utils.get_synapse_owner_id(resource_tags)
    synapse_tags = utils.get_synapse_tags(synapse_owner_id)
    log.debug(f'Apply tags: {synapse_tags} to resource {resource_arn}')
    apply_tags(resource_arn, synapse_tags)

@helper.delete
def delete(event, context):
  '''Handles custom resource delete events'''
  pass


def handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
