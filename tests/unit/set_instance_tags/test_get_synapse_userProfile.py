import unittest

from synapseclient.core.exceptions import SynapseHTTPError
from unittest.mock import patch, MagicMock
from set_instance_tags import app

TEST_USER_PROFILE = {
  "createdOn": "2020-06-18T16:34:18.000Z",
  "firstName": "Joe",
  "lastName": "Smith",
  "ownerId": "1111111",
  "userName": "jsmith"
}

def mock_get_user_profile(synapse_id):
  VALID_USER_IDS = [TEST_USER_PROFILE["ownerId"]]

  if synapse_id not in VALID_USER_IDS:
    raise SynapseHTTPError("404 Client Error: UserProfile cannot be found for: " + synapse_id)

  return TEST_USER_PROFILE


class TestGetSynapseUserProfile(unittest.TestCase):

  @patch('synapseclient.Synapse')
  def test_valid_id(self, MockSynapse):
    MockSynapse.return_value.getUserProfile=mock_get_user_profile
    result = app.get_synapse_user_profile("1111111")
    self.assertEqual(result, TEST_USER_PROFILE)

  @patch('synapseclient.Synapse')
  def test_invalid_id(self, MockSynapse):
    MockSynapse.return_value.getUserProfile=mock_get_user_profile
    with self.assertRaises(SynapseHTTPError):
        app.get_synapse_user_profile("3333333")
