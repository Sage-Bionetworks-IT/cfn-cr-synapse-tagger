import unittest
from unittest.mock import MagicMock, patch

from botocore.stub import Stubber

from set_tags import set_instance_tags
from set_tags import utils
from set_tags.utils import SYNAPSE_TAG_PREFIX

class TestSetInstanceTagsHandler(unittest.TestCase):

  SYNAPSE_EMAIL_TAG = { 'Key': f'{SYNAPSE_TAG_PREFIX}:email', 'Value': 'janedoe@synapse.org' }

  def test_happy_path(self):
    ec2 = utils.get_ec2_client()
    with Stubber(ec2) as stubber, \
      patch('set_tags.set_instance_tags.get_instance_id') as name_mock, \
      patch('set_tags.set_instance_tags.get_instance_tags') as instance_tags_mock, \
      patch('set_tags.utils.get_principal_id') as arn_mock, \
      patch('set_tags.utils.get_synapse_user_profile') as profile_mock, \
      patch('set_tags.utils.get_provisioned_product_name_tag') as product_name_tag_mock, \
      patch('set_tags.utils.get_access_approved_role_tag') as approved_role_tag_mock, \
      patch('set_tags.utils.get_synapse_tags') as synapse_tags_mock:
        name_mock.return_value = 'some-improbable-instance-id'
        product_name_tag_mock.return_value = {
          'Key': 'Name',
          'Value': 'my-product'
        }
        approved_role_tag_mock.return_value = {
          'Key': 'Protected/AccessApprovedCaller',
          'Value': 'AROATOOICTTHKNSFVWL5U:1234567'
        }
        synapse_tags_mock.return_value = [self.SYNAPSE_EMAIL_TAG]
        stubber.add_response(
          method='create_tags',
          expected_params={
            'Resources': ['some-improbable-instance-id'],
            'Tags': [
              self.SYNAPSE_EMAIL_TAG,
              {'Key': 'Name', 'Value': 'my-product'},
              {'Key': 'Protected/AccessApprovedCaller', 'Value': 'AROATOOICTTHKNSFVWL5U:1234567'},
            ]
          },
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
      patch('set_tags.set_instance_tags.get_instance_tags') as instance_tags_mock, \
      patch('set_tags.utils.get_principal_id') as arn_mock, \
      patch('set_tags.utils.get_synapse_user_profile') as profile_mock, \
      patch('set_tags.utils.get_synapse_tags') as synapse_tags_mock:
        name_mock.return_value = 'some-improbable-instance-id'
        synapse_tags_mock.return_value = [self.SYNAPSE_EMAIL_TAG]
        stubber.add_client_error(
        method='get_instance_tagging',
        service_error_code='NoSuchInstance',
        service_message='The specified instance does not exist',
        http_status_code=404)
        utils.get_ec2_client = MagicMock(return_value=ec2)
        result = set_instance_tags.create_or_update({},{})
