import unittest

from set_tags import utils

TEST_USER_PROFILE = {
  "createdOn": "2020-06-18T16:34:18.000Z",
  "firstName": "Joe",
  "lastName": "Smith",
  "ownerId": "1111111",
  "userName": "jsmith",
  "company": "Sage Bionetworks",
}

class TestGetSynapseUserProfileTags(unittest.TestCase):

  def test_happy_default_ignore(self):
    result = utils.get_synapse_user_profile_tags(TEST_USER_PROFILE)
    expected = [
        {'Key': 'synapse:firstName', 'Value': 'Joe'},
        {'Key': 'synapse:lastName', 'Value': 'Smith'},
        {'Key': 'synapse:ownerId', 'Value': '1111111'},
        {'Key': 'synapse:email', 'Value': 'jsmith@synapse.org'},
        {'Key': 'OwnerEmail', 'Value': 'jsmith@synapse.org'},
        {'Key': 'synapse:userName', 'Value': 'jsmith'},
        {'Key': 'synapse:company', 'Value': 'Sage Bionetworks'},
    ]
    self.assertListEqual(result, expected)

  def test_happy_mulitple_ignores(self):
    result = utils.get_synapse_user_profile_tags(TEST_USER_PROFILE,
                                               ["createdOn","company","firstName","lastName"])
    expected = [
        {'Key': 'synapse:ownerId', 'Value': '1111111'},
        {'Key': 'synapse:email', 'Value': 'jsmith@synapse.org'},
        {'Key': 'OwnerEmail', 'Value': 'jsmith@synapse.org'},
        {'Key': 'synapse:userName', 'Value': 'jsmith'},
    ]
    self.assertListEqual(result, expected)

  def test_happy_ignores_user_name(self):
    result = utils.get_synapse_user_profile_tags(TEST_USER_PROFILE, ["userName"])
    expected = [
        {'Key': 'synapse:createdOn', 'Value': '2020-06-18T16:34:18.000Z'},
        {'Key': 'synapse:firstName', 'Value': 'Joe'},
        {'Key': 'synapse:lastName', 'Value': 'Smith'},
        {'Key': 'synapse:ownerId', 'Value': '1111111'},
        {'Key': 'synapse:company', 'Value': 'Sage Bionetworks'},
    ]
    self.assertListEqual(result, expected)
