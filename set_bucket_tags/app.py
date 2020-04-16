import json
import logging
import re
import traceback

import boto3
import requests

from crhelper import CfnResource


MISSING_BUCKET_NAME_ERROR_MESSAGE = 'BucketName parameter is required'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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
  email_check = re.compile(r"[^@]+@[^@]+\.[^@]+")
  if principal_id.isdigit():
    email = get_synapse_email(principal_id)
  elif email_check.fullmatch(principal_id):
    email = principal_id
  else:
    raise ValueError(f'Principal id value "{principal_id}" uses invalid format')
  return email


def add_owner_email_tag(tags, email):
  '''Add an OwnerEmail tag to set of bucket tags'''
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
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  log.info('Start SetBucketTags Lambda processing')
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  bucket_name = get_bucket_name(event)
  tags = get_bucket_tags(bucket_name)
  principal_id = get_principal_id(tags)
  email = get_owner_email(principal_id)
  tags = add_owner_email_tag(tags, email)
  client = get_s3_client()
  tagging_response = client.put_bucket_tagging(
    Bucket=bucket_name,
    Tagging={ 'TagSet': tags }
    )
  log.debug(f'Tagging response: {tagging_response}')


@helper.delete
def delete(event, context):
  pass


def handler(event, context):
  helper(event, context)
