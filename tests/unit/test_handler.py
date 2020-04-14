import json
import unittest
from unittest.mock import MagicMock, patch

import boto3
import botocore
from botocore.stub import Stubber

from set_bucket_tags import app


class TestHandler(unittest.TestCase):

  def test_happy_path(self):
    s3 = boto3.client('s3')
    with Stubber(s3) as stubber, \
      patch('set_bucket_tags.app.get_bucket_name') as name_mock, \
      patch('set_bucket_tags.app.get_bucket_tags') as get_mock, \
      patch('set_bucket_tags.app.get_principal_id') as arn_mock, \
      patch('set_bucket_tags.app.get_synapse_email') as syn_mock, \
      patch('set_bucket_tags.app.add_owner_email_tag') as tags_mock:
        name_mock.return_value = 'some-improbable-bucket-name'
        tags_mock.return_value = [{ 'Key': 'OwnerEmail', 'Value': 'janedoe@synapse.org' }]
        stubber.add_response(
          method='put_bucket_tagging',
          service_response={
            'ResponseMetadata': {
              'RequestId': '12345',
              'HostId': 'etc',
              'HTTPStatusCode': 204,
              'HTTPHeaders': {}
            }})
        app.get_s3_client = MagicMock(return_value=s3)
        result = app.create_or_update({},{})
        self.assertEqual(True, result)
