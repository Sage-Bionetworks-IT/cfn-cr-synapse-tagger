import json
import logging
import re
import traceback

import boto3
import requests

from crhelper import CfnResource


MISSING_INSTANCE_ID_ERROR_MESSAGE = 'InstanceId parameter is required'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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

  # format tags to easily pass to create_tags
  for tag in tags:
    tag.pop("ResourceId")
    tag.pop("ResourceType")

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


def get_synapse_email(synapse_id):
  '''Use the synapse id to look up the synapse user name'''
  synapse_url = f'https://repo-prod.prod.sagebase.org/repo/v1/userProfile/{synapse_id}'
  response = requests.get(synapse_url)
  response.raise_for_status()
  user_profile = response.json()
  log.debug(f'Synapse user profile response: {user_profile}')
  user_name = user_profile.get('userName')
  synapse_email = f'{user_name}@synapse.org'
  return synapse_email


def get_owner_email(principal_id):
  '''Derive an email from a id'''
  email_check = re.compile(r"[^@]+@[^@]+\.[^@]+")
  if principal_id.isdigit():
    email = get_synapse_email(principal_id)
  elif email_check.fullmatch(principal_id):
    email = principal_id
  else:
    raise ValueError(f'Principal id value "{principal_id}" uses invalid format')
  return email


def add_owner_email_tag(tags, email):
  '''Add an OwnerEmail tag to set of EC2 tags'''
  owner_email_tag = next((tag for tag in tags if tag['Key'] == 'OwnerEmail'), None)
  if owner_email_tag:
    owner_email_tag['Value'] = email
  else:
    new_owner_email_tag = { 'Key': 'OwnerEmail', 'Value': email}
    tags.append(new_owner_email_tag)
  return tags


@helper.create
@helper.update
def create_or_update(event, context):
  '''Handles customm resource create and update events'''
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start Lambda processing')
  instance_id = get_instance_id(event)
  tags = get_instance_tags(instance_id)
  principal_id = get_principal_id(tags)
  email = get_owner_email(principal_id)
  tags = add_owner_email_tag(tags, email)
  client = get_ec2_client()
  log.debug(f'Tags to apply: {tags}')
  tagging_response = client.create_tags(
    Resources=[instance_id],
    Tags=tags
  )
  log.debug(f'Tagging response: {tagging_response}')


@helper.delete
def delete(event, context):
  '''Handles custom resource delete events'''
  pass


def handler(event, context):
  '''Lambda handler, invokes custom resource helper'''
  helper(event, context)
