import unittest
from unittest.mock import MagicMock

from botocore.stub import Stubber

from set_tags import set_bucket_tags
from set_tags import utils


class TestSetInstanceTagsHandler(unittest.TestCase):

  TEST_BUCKET_NAME = 'my-bucket'
  TEST_TAGS = [{
    'Key': 'foo',
    'Value': 'bar'
  }]

  def test_happy_path(self):
    s3 = utils.get_s3_client()
    with Stubber(s3) as stubber:
      stubber.add_response(
        method='put_bucket_tagging',
        expected_params={
          'Bucket': self.TEST_BUCKET_NAME,
          'Tagging': {
            'TagSet': self.TEST_TAGS
          }
        },
        service_response={
          'ResponseMetadata': {
            'RequestId': '12345',
            'HostId': 'etc',
            'HTTPStatusCode': 204,
            'HTTPHeaders': {}
          }})
      utils.get_s3_client = MagicMock(return_value=s3)
      result = set_bucket_tags.apply_tags(self.TEST_BUCKET_NAME, self.TEST_TAGS)


  def test_client_error(self):
    s3 = utils.get_s3_client()
    with Stubber(s3) as stubber, self.assertRaises(Exception):
      stubber.add_client_error(
        method='put_bucket_tagging',
        service_error_code='NoSuchBucket',
        service_message='The specified bucket does not exist',
        http_status_code=404)
      utils.get_s3_client = MagicMock(return_value=s3)
      result = set_bucket_tags.apply_tags(self.TEST_BUCKET_NAME, self.TEST_TAGS)
