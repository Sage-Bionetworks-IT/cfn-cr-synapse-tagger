import unittest
import synapseclient

from synapseclient.core.exceptions import SynapseHTTPError
from unittest.mock import patch, MagicMock
from set_instance_tags import app

def mock_get_user_profile(synapse_id):
  jsmith_profile = {
    "createdOn": "2020-06-18T16:34:18.000Z",
    "firstName": "Joe",
    "lastName": "Smith",
    "ownerId": "1111111",
    "userName": "jsmith"
  }
  VALID_USER_IDS = [jsmith_profile["ownerId"]]

  if synapse_id not in VALID_USER_IDS:
    raise SynapseHTTPError("404 Client Error: UserProfile cannot be found for: " + synapse_id)

  return jsmith_profile


class TestGetSynapseEmail(unittest.TestCase):

  @patch('synapseclient.Synapse')
  def test_valid_id(self, MockSynapse):
    MockSynapse.return_value.getUserProfile=mock_get_user_profile
    result = app.get_synapse_email("1111111")
    expected = "jsmith@synapse.org"
    self.assertEqual(result, expected)

  @patch('synapseclient.Synapse')
  def test_invalid_id(self, MockSynapse):
    MockSynapse.return_value.getUserProfile=mock_get_user_profile
    with self.assertRaises(SynapseHTTPError):
        app.get_synapse_email("3333333")
