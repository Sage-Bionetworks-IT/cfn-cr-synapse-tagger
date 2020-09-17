import unittest
import boto3

from unittest.mock import patch
from set_bucket_tags import app
from botocore.stub import Stubber

class TestGetSynapseUserTeamTags(unittest.TestCase):

  def test_user_in_a_team(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_bucket_tags.app.get_synapse_user_team_id') as user_team_id_mock:
        user_team_id_mock.return_value = "1111111"
        result = app.get_synapse_user_team_tags(1234567,["1111111","222222"])
        expected = [{'Key': 'synapse:teamId', 'Value': '1111111'}]
        self.assertListEqual(result, expected)

  def test_user_not_in_a_team(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_bucket_tags.app.get_synapse_user_team_id') as user_team_id_mock:
        user_team_id_mock.return_value = None
        result = app.get_synapse_user_team_tags(1234567,["1111111","222222"])
        expected = []
        self.assertListEqual(result, expected)
