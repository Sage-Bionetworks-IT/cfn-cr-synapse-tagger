import unittest
from unittest.mock import MagicMock, patch

import boto3
import botocore
from botocore.stub import Stubber

from set_tags import set_batch_tags
from set_tags import utils


class TestGetBatchTags(unittest.TestCase):

  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_valid_instance(self):
    batch = utils.get_batch_client()
    with Stubber(batch) as stubber:
      tags = {
        'heresatag': 'heresatagvalue',
        'theresatag': 'theresatagvalue',
        'anothertag': 'anothertagvalue'
      }
      response = {
        'tags': tags
      }
      stubber.add_response('list_tags_for_resource', response)
      utils.get_batch_client = MagicMock(return_value=batch)
      valid_resource_id ='some_reasonable_instance_id'
      result = set_batch_tags.get_batch_tags(valid_resource_id)
      self.assertEqual(tags, result)


  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_invalid_instance(self):
    batch = utils.get_batch_client()
    with Stubber(batch) as stubber, self.assertRaises(botocore.exceptions.ClientError):
      stubber.add_client_error(
        method='list_tags_for_resource',
        service_error_code='NoSuchResource',
        service_message='Resource was not found',
        http_status_code=404)
      utils.get_batch_client = MagicMock(return_value=batch)
      invalid_resource_id ='some_unreasonable_instance_id'
      result = set_batch_tags.get_batch_tags(invalid_resource_id)


  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_no_tags(self):
    batch = utils.get_batch_client()
    with Stubber(batch) as stubber, self.assertRaises(Exception):
      response = {
        'tags': []
      }
      stubber.add_response('list_tags_for_resource', response)
      utils.get_batch_client = MagicMock(return_value=batch)
      valid_resource_id ='some_reasonable_instance_id'
      result = set_instance_tags.get_instance_tags(valid_resource_id)
