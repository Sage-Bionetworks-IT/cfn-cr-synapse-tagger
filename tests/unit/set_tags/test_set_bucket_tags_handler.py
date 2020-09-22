import unittest
from unittest.mock import MagicMock, patch

from botocore.stub import Stubber

from set_tags import set_bucket_tags
from set_tags import utils


class TestSetBucketTagsHandler(unittest.TestCase):

  def test_happy_path(self):
    s3 = utils.get_s3_client()
    with Stubber(s3) as stubber, \
      patch('set_tags.set_bucket_tags.get_bucket_name') as name_mock, \
      patch('set_tags.set_bucket_tags.get_bucket_tags') as bucket_tags_mock, \
      patch('set_tags.utils.get_principal_id') as arn_mock, \
      patch('set_tags.utils.get_synapse_user_profile') as profile_mock, \
      patch('set_tags.utils.get_synapse_tags') as synapse_tags_mock:
        name_mock.return_value = 'some-improbable-bucket-name'
        bucket_tags_mock.return_value = [{'Key': 'aws:servicecatalog:provisioningPrincipalArn',
                                          'Value': 'arn:aws:sts::9999999999:assumed-role/ServiceCatalogEndusers/3377358' }]
        synapse_tags_mock.return_value = [{'Key': 'synapse:email',
                                           'Value': 'janedoe@synapse.org'}]
        stubber.add_response(
          method='put_bucket_tagging',
          expected_params = {
            'Bucket': 'some-improbable-bucket-name',
            'Tagging': {'TagSet': [{'Key': 'aws:servicecatalog:provisioningPrincipalArn',
                                    'Value': 'arn:aws:sts::9999999999:assumed-role/ServiceCatalogEndusers/3377358'},
                                   {'Key': 'synapse:email',
                                    'Value': 'janedoe@synapse.org'}]}
          },
          service_response={
            'ResponseMetadata': {
              'RequestId': '12345',
              'HostId': 'etc',
              'HTTPStatusCode': 204,
              'HTTPHeaders': {}
            }})
        utils.get_s3_client = MagicMock(return_value=s3)
        result = set_bucket_tags.create_or_update({},{})


  def test_client_error(self):
    s3 = utils.get_s3_client()
    with Stubber(s3) as stubber, self.assertRaises(Exception), \
      patch('set_tags.set_bucket_tags.get_bucket_name') as name_mock, \
      patch('set_tags.set_bucket_tags.get_bucket_tags') as bucket_tags_mock, \
      patch('set_tags.utils.get_principal_id') as arn_mock, \
      patch('set_tags.utils.get_synapse_email') as syn_mock, \
      patch('set_tags.utils.get_synapse_tags') as synapse_tags_mock:
        name_mock.return_value = 'some-improbable-bucket-name'
        bucket_tags_mock.return_value = [{'Key': 'aws:servicecatalog:provisioningPrincipalArn',
                                          'Value': 'arn:aws:sts::9999999999:assumed-role/ServiceCatalogEndusers/3377358' }]
        synapse_tags_mock.return_value = [{'Key': 'synapse:email',
                                           'Value': 'janedoe@synapse.org'}]
        stubber.add_client_error(
        method='get_bucket_tagging',
        service_error_code='NoSuchBucket',
        service_message='The specified bucket does not exist',
        http_status_code=404)
        utils.get_s3_client = MagicMock(return_value=s3)
        result = set_bucket_tags.create_or_update({},{})
