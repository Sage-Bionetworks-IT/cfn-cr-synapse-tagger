import json
import logging
import traceback

import boto3
import requests


MISSING_BUCKET_NAME_ERROR_MESSAGE = 'BucketName parameter is required'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_s3_client():
  return boto3.client('s3')


def get_bucket_name(event):
  '''Get the bucket name from event params sent to lambda'''
  parameters = event['params']
  bucket_name = parameters.get('BucketName')
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


def get_principal_arn(tags):
  '''Find the value of the principal arn among the bucket tags'''
  principal_arn_tag = 'aws:servicecatalog:provisioningPrincipalArn'
  for tag in tags:
    if tag.get('Key') == principal_arn_tag:
      principal_arn_value = tag.get('Value')
      return principal_arn_value
  else:
    raise ValueError('Could not derive a provisioningPrincipalArn from tags')


def get_synapse_user_name(principal_arn):
  '''Use the synapse id embedded in the principal arn to look up the synapse user name'''
  synapse_id = principal_arn.split('/')[-1]
  if not synapse_id.isdigit():
    error_msg = (f'The synapse_id {synapse_id} derived from the principal_arn'
      f'{principal_arn} is in an unexpected format')
    raise ValueError(error_msg)
  synapse_url = f'https://repo-prod.prod.sagebase.org/repo/v1/userProfile/{synapse_id}'
  response = requests.get(synapse_url)
  response.raise_for_status()
  user_profile = response.json()
  log.debug(f'Synpase user profile response: {user_profile}')
  user_name = user_profile.get('userName')
  return user_name


def add_owner_email_tag(tags, synapse_username):
  '''Add an OwnerEmail tag for the synapse email based on synapse usename'''
  synapse_email = f'{synapse_username}@synapse.org'
  owner_email_tag = { 'Key': 'OwnerEmail', 'Value': synapse_email}
  tags.append(owner_email_tag)
  return tags


def handler(event, context):
  '''
  Handles a service catalog transform event.

  This uses a value in the current bucket tags to call synapse for the
  username which is used to create an OwnerEmail tag.
  '''
  log.info('Start SetBucketTags Lambda processing')
  log.debug('Received event: ' + json.dumps(event, sort_keys=False))
  response = {
    'requestId': event['requestId'],
    'status': 'success'
  }

  try:
    bucket_name = get_bucket_name(event)
    tags = get_bucket_tags(bucket_name)
    principal_arn = get_principal_arn(tags)
    synapse_username = get_synapse_user_name(principal_arn)
    tags = add_owner_email_tag(tags, synapse_username)
    client = get_s3_client()
    client.put_bucket_tagging(
      Bucket=bucket_name,
      Tagging={ 'TagSet': tags }
      )

  except Exception as e:
    traceback.print_exc()
    response['status'] = 'failure'
    response['errorMessage'] = str(e)

  return response
