import unittest
from unittest.mock import MagicMock, patch

import boto3
from botocore.stub import Stubber

from set_instance_tags import app


class TestHandler(unittest.TestCase):

  def test_happy_path(self):
    ec2 = boto3.client('ec2')
    with Stubber(ec2) as stubber, \
      patch('set_instance_tags.app.get_instance_id') as name_mock, \
      patch('set_instance_tags.app.get_instance_tags') as get_mock, \
      patch('set_instance_tags.app.get_principal_id') as arn_mock, \
      patch('set_instance_tags.app.get_synapse_userProfile') as profile_mock, \
      patch('set_instance_tags.app.get_synapse_tags') as tags_mock:
        name_mock.return_value = 'some-improbable-instance-id'
        tags_mock.return_value = [{ 'Key': 'OwnerEmail', 'Value': 'janedoe@synapse.org' }]
        stubber.add_response(
          method='create_tags',
          service_response={
            'ResponseMetadata': {
              'RequestId': '12345',
              'HostId': 'etc',
              'HTTPStatusCode': 204,
              'HTTPHeaders': {}
            }})
        app.get_ec2_client = MagicMock(return_value=ec2)
        result = app.create_or_update({},{})


  def test_client_error(self):
    ec2 = boto3.client('ec2')
    with Stubber(ec2) as stubber, self.assertRaises(Exception), \
      patch('set_instance_tags.app.get_instance_id') as name_mock, \
      patch('set_instance_tags.app.get_instance_tags') as get_mock, \
      patch('set_instance_tags.app.get_principal_id') as arn_mock, \
      patch('set_instance_tags.app.get_synapse_email') as syn_mock, \
      patch('set_instance_tags.app.add_owner_email_tag') as tags_mock, \
      patch('set_instance_tags.app.filter_tags') as filter_mock:
        name_mock.return_value = 'some-improbable-instance-id'
        filter_mock.return_value = [{ 'Key': 'OwnerEmail', 'Value': 'janedoe@synapse.org' }]
        stubber.add_client_error(
        method='get_instance_tagging',
        service_error_code='NoSuchInstance',
        service_message='The specified instance does not exist',
        http_status_code=404)
        app.get_ec2_client = MagicMock(return_value=ec2)
        result = app.create_or_update({},{})
