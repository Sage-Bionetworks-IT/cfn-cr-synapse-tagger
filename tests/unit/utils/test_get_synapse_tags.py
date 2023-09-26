import unittest
import boto3

from unittest.mock import patch
from set_tags import utils
from botocore.stub import Stubber

MOCK_USER_PROFILE_TAGS = [
    {'Key': 'synapse:ownerId', 'Value': '1111111'},
    {'Key': 'synapse:email', 'Value': 'jsmith@synapse.org'},
    {'Key': 'OwnerEmail', 'Value': 'jsmith@synapse.org'},
    {'Key': 'synapse:userName', 'Value': 'jsmith'},
]

MOCK_TEAM_TAGS = [
  {'Key': 'synapse:teamId', 'Value': '9999999'}
]

class TestGetSynapseTags(unittest.TestCase):

  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_happy_path(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_synapse_user_profile') as user_profile_mock, \
      patch('set_tags.utils.get_synapse_user_profile_tags') as user_profile_tags_mock, \
      patch('set_tags.utils.get_synapse_team_ids') as team_ids_mock, \
      patch('set_tags.utils.get_synapse_user_team_tags') as user_team_tags_mock:
        user_profile_tags_mock.return_value = MOCK_USER_PROFILE_TAGS
        user_team_tags_mock.return_value = MOCK_TEAM_TAGS
        result = utils.get_synapse_tags("1111111")
        expected = [
          {'Key': 'synapse:ownerId', 'Value': '1111111'},
          {'Key': 'synapse:email', 'Value': 'jsmith@synapse.org'},
          {'Key': 'OwnerEmail', 'Value': 'jsmith@synapse.org'},
          {'Key': 'synapse:userName', 'Value': 'jsmith'},
          {'Key': 'synapse:teamId', 'Value': '9999999'}
        ]
        self.assertListEqual(result, expected)
