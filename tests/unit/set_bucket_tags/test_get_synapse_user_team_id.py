import unittest
import boto3
import synapseclient

from unittest.mock import patch
from set_bucket_tags import app
from botocore.stub import Stubber


def get_membership_status_is_member(synapse_id, team_id):
  return {"isMember": True}

def get_membership_status_is_not_member(synapse_id, team_id):
  return {"isMember": False}


class TestGetSynapseUserTeamId(unittest.TestCase):

  def test_is_team_member(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('synapseclient.Synapse') as syn_mock, \
      patch('set_bucket_tags.app.get_synapse_team_ids') as team_ids_mock:
        syn_mock.return_value.get_membership_status = get_membership_status_is_member
        team_ids_mock.return_value = ["1111111","2222222"]
        result = app.get_synapse_user_team_id(1111111, ["1111111","2222222"])
        expected = "1111111"
        self.assertEqual(result, expected)


  def test_is_not_team_member(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('synapseclient.Synapse') as syn_mock, \
      patch('set_bucket_tags.app.get_synapse_team_ids') as team_ids_mock:
        syn_mock.return_value.get_membership_status = get_membership_status_is_not_member
        team_ids_mock.return_value = ["1111111","2222222"]
        result = app.get_synapse_user_team_id(3333333, ["1111111","2222222"])
        expected = None
        self.assertEqual(result, expected)
