import unittest
from unittest.mock import MagicMock, patch

import boto3
import botocore
from botocore.stub import Stubber

from set_tags import set_instance_tags
from set_tags import utils


class TestGetInstanceTags(unittest.TestCase):

  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_valid_instance(self):
    ec2 = utils.get_ec2_client()
    with Stubber(ec2) as stubber:
      tags = [
        {'Key': 'heresatag', 'ResourceId': 'i-1234', 'ResourceType': 'dedicated', 'Value': 'heresatagvalue'},
        {'Key': 'theresatag', 'ResourceId': 'i-1234', 'ResourceType': 'dedicated', 'Value': 'theresatagvalue'}
      ]
      response = {
        'ResponseMetadata': {'RequestId': 'gobbledygoop','HTTPStatusCode': 200,},
        'Tags': tags
      }
      stubber.add_response('describe_tags', response)
      utils.get_ec2_client = MagicMock(return_value=ec2)
      valid_instance_id ='some_reasonable_instance_id'
      result = set_instance_tags.get_instance_tags(valid_instance_id)
      self.assertEqual(tags, result)


  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_invalid_instance(self):
    ec2 = utils.get_ec2_client()
    with Stubber(ec2) as stubber, self.assertRaises(botocore.exceptions.ClientError):
      stubber.add_client_error(
        method='describe_tags',
        service_error_code='NoSuchInstance',
        service_message='The specified instance does not exist',
        http_status_code=404)
      utils.get_ec2_client = MagicMock(return_value=ec2)
      invalid_instance_id ='some_unreasonable_instance_id'
      result = set_instance_tags.get_instance_tags(invalid_instance_id)


  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_no_tags(self):
    ec2 = boto3.client('ec2')
    with Stubber(ec2) as stubber, self.assertRaises(Exception):
      response = {
        'ResponseMetadata': {'RequestId': 'gobbledygoop','HTTPStatusCode': 200,},
        'TagSet': []
      }
      stubber.add_response('get_instance_tagging', response)
      utils.get_ec2_client = MagicMock(return_value=ec2)
      valid_instance_id ='some_reasonable_instance_id'
      result = set_instance_tags.get_instance_tags(valid_instance_id)
