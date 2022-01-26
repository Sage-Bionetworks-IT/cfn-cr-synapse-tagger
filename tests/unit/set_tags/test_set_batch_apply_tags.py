import unittest
from unittest.mock import MagicMock

from botocore.stub import Stubber

from set_tags import set_batch_tags
from set_tags import utils


class TestSetBatchTagsHandler(unittest.TestCase):

  STACK_ID = 'arn:aws:cloudformation:us-east-1:1111111111:stack/SC-465877038949-pp-yd5tcochoi32c/932c7240-74bc-11ec-9ed8-0ab60a8ca761'
  TEST_TAGS = {
    'foo': 'bar'
  }

  def test_happy_path(self):
    batch = utils.get_batch_client()
    with Stubber(batch) as stubber:
      stubber.add_response(
        method='tag_resource',
        expected_params={
          'resourceArn': self.STACK_ID,
          'tags': self.TEST_TAGS
        },
        service_response={
          'ResponseMetadata': {
            'RequestId': '12345',
            'HostId': 'etc',
            'HTTPStatusCode': 204,
            'HTTPHeaders': {}
          }})
      utils.get_batch_client = MagicMock(return_value=batch)
      result = set_batch_tags.apply_tags(self.STACK_ID, self.TEST_TAGS)
