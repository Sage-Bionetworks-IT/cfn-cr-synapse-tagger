import json
import logging
import set_tags.utils as utils

from crhelper import CfnResource

MISSING_INSTANCE_ID_ERROR_MESSAGE = 'InstanceId parameter is required'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

helper = CfnResource(
  json_logging=False, log_level='DEBUG', boto_level='INFO')


def get_instance_id(event):
  '''Get the instance id from event params sent to lambda'''
  resource_properties = event.get('ResourceProperties')
  instance_id = resource_properties.get('InstanceId')
  if not instance_id:
    raise ValueError(MISSING_INSTANCE_ID_ERROR_MESSAGE)
  return instance_id


def get_instance_tags(instance_id):
  '''Look up the instance tags'''
  client = utils.get_ec2_client()
  response = client.describe_tags(
    Filters = [{'Name': 'resource-id', 'Values': [instance_id]}]
  )
  log.debug(f'EC2 describe tags response: {response}')
  tags = response.get('Tags')
  if not tags or len(tags) == 0:
    raise Exception(f'No tags returned, received: {response}')

  return tags


@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start Lambda processing')
  instance_id = get_instance_id(event)
  instance_tags = get_instance_tags(instance_id)
  principal_id = utils.get_principal_id(instance_tags)
  synapse_tags = utils.get_synapse_tags(principal_id)
  extra_tags = []
  provisioned_product_name_tag = utils.get_provisioned_product_name_tag(instance_tags)
  extra_tags.append(provisioned_product_name_tag)
  access_approved_role_tag = utils.get_access_approved_role_tag(instance_tags)
  extra_tags.append(access_approved_role_tag)
  all_tags = list(synapse_tags + extra_tags)
  log.debug(f'Tags to apply: {all_tags}')
  client = utils.get_ec2_client()
  tagging_response = client.create_tags(
    Resources=[instance_id],
    Tags=all_tags
  )
  log.debug(f'Tagging response: {tagging_response}')


@helper.delete
def delete(event, context):
  '''Handles custom resource delete events'''
  pass


def handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
