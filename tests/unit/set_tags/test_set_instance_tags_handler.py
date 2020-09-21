import unittest
from unittest.mock import MagicMock, patch

from botocore.stub import Stubber

from set_tags import set_instance_tags
from set_tags import utils


class TestSetInstanceTagsHandler(unittest.TestCase):

  def test_happy_path(self):
    ec2 = utils.get_ec2_client()
    with Stubber(ec2) as stubber, \
      patch('set_tags.set_instance_tags.get_instance_id') as name_mock, \
      patch('set_tags.set_instance_tags.get_instance_tags') as get_mock, \
      patch('set_tags.utils.get_principal_id') as arn_mock, \
      patch('set_tags.utils.get_synapse_user_profile') as profile_mock, \
      patch('set_tags.utils.get_synapse_tags') as tags_mock:
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
        utils.get_ec2_client = MagicMock(return_value=ec2)
        result = set_instance_tags.create_or_update({},{})


  def test_client_error(self):
    ec2 = utils.get_ec2_client()
    with Stubber(ec2) as stubber, self.assertRaises(Exception), \
      patch('set_tags.set_instance_tags.get_instance_id') as name_mock, \
      patch('set_tags.set_instance_tags.get_instance_tags') as get_mock, \
      patch('set_tags.utils.get_principal_id') as arn_mock, \
      patch('set_tags.utils.get_synapse_user_profile') as profile_mock, \
      patch('set_tags.utils.get_synapse_tags') as tags_mock:
        name_mock.return_value = 'some-improbable-instance-id'
        tags_mock.return_value = [{ 'Key': 'OwnerEmail', 'Value': 'janedoe@synapse.org' }]
        stubber.add_client_error(
        method='get_instance_tagging',
        service_error_code='NoSuchInstance',
        service_message='The specified instance does not exist',
        http_status_code=404)
        utils.get_ec2_client = MagicMock(return_value=ec2)
        result = set_instance_tags.create_or_update({},{})
