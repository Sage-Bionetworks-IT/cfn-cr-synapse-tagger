import unittest

from set_tags import utils

TEST_USER_PROFILE = {
  "createdOn": "2020-06-18T16:34:18.000Z",
  "firstName": "Joe",
  "lastName": "Smith",
  "ownerId": "1111111",
  "userName": "jsmith",
  "company": "Sage Bionetworks",
  "summary": "I'm a sager",
  "position": "dev guy",
  "location": "Seattle, WA",
  "industry": "Life Sciences Research",
  "profilePicureFileHandleId": "222222",
  "url": "https://www.linkedin.com/company/sage-bionetworks/",
  "teamName": "Sage Team"
}

class TestGetSynapseUserProfileTags(unittest.TestCase):

  def test_happy_default_include(self):
    result = utils.get_synapse_user_profile_tags(TEST_USER_PROFILE)
    expected = [
        {'Key': 'synapse:firstName', 'Value': 'Joe'},
        {'Key': 'synapse:lastName', 'Value': 'Smith'},
        {'Key': 'synapse:ownerId', 'Value': '1111111'},
        {'Key': 'synapse:email', 'Value': 'jsmith@synapse.org'},
        {'Key': 'OwnerEmail', 'Value': 'jsmith@synapse.org'},
        {'Key': 'synapse:userName', 'Value': 'jsmith'},
        {'Key': 'synapse:company', 'Value': 'Sage Bionetworks'},
        {'Key': 'synapse:teamName', 'Value': 'Sage Team'}
    ]
    self.assertListEqual(result, expected)

  def test_happy_mulitple_includes(self):
    result = utils.get_synapse_user_profile_tags(TEST_USER_PROFILE,
                                               ["ownerId","userName"])
    expected = [
        {'Key': 'synapse:ownerId', 'Value': '1111111'},
        {'Key': 'synapse:email', 'Value': 'jsmith@synapse.org'},
        {'Key': 'OwnerEmail', 'Value': 'jsmith@synapse.org'},
        {'Key': 'synapse:userName', 'Value': 'jsmith'},
    ]
    self.assertListEqual(result, expected)

  def test_happy_not_include_user_name(self):
    result = utils.get_synapse_user_profile_tags(TEST_USER_PROFILE, ["ownerId"])
    expected = [
        {'Key': 'synapse:ownerId', 'Value': '1111111'}
    ]
    self.assertListEqual(result, expected)
