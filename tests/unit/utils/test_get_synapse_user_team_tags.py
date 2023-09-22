import unittest
import boto3

from unittest.mock import patch
from set_tags import utils
from botocore.stub import Stubber

class TestGetSynapseUserTeamTags(unittest.TestCase):

  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_user_in_a_team(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_synapse_user_team_id') as user_team_id_mock:
        user_team_id_mock.return_value = "1111111"
        result = utils.get_synapse_user_team_tags(1234567,["1111111","222222"])
        expected = [{'Key': 'synapse:teamId', 'Value': '1111111'}]
        self.assertListEqual(result, expected)

  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_user_not_in_a_team(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_synapse_user_team_id') as user_team_id_mock:
        user_team_id_mock.return_value = None
        result = utils.get_synapse_user_team_tags(1234567,["1111111","222222"])
        expected = []
        self.assertListEqual(result, expected)
