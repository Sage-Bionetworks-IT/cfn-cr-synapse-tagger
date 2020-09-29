import unittest
from unittest.mock import MagicMock

from botocore.stub import Stubber

from set_tags import set_instance_tags
from set_tags import utils


class TestSetInstanceTagsHandler(unittest.TestCase):

  TEST_INSTANCE_ID = 'i-123456789'
  TEST_TAGS = [{
    'Key': 'foo',
    'Value': 'bar'
  }]

  def test_happy_path(self):
    ec2 = utils.get_ec2_client()
    with Stubber(ec2) as stubber:
      stubber.add_response(
        method='create_tags',
        expected_params={
          'Resources': ['i-123456789'],
          'Tags': self.TEST_TAGS
        },
        service_response={
          'ResponseMetadata': {
            'RequestId': '12345',
            'HostId': 'etc',
            'HTTPStatusCode': 204,
            'HTTPHeaders': {}
          }})
      utils.get_ec2_client = MagicMock(return_value=ec2)
      result = set_instance_tags.apply_tags(self.TEST_INSTANCE_ID, self.TEST_TAGS)


  def test_client_error(self):
    ec2 = utils.get_ec2_client()
    with Stubber(ec2) as stubber, self.assertRaises(Exception):
      stubber.add_client_error(
      method='create_tags',
      service_error_code='NoSuchInstance',
      service_message='The specified instance does not exist',
      http_status_code=404)
      utils.get_ec2_client = MagicMock(return_value=ec2)
      result = set_instance_tags.apply_tags(self.TEST_INSTANCE_ID, self.TEST_TAGS)
