import unittest

from set_instance_tags import app

jsmith_profile = {
  "createdOn": "2020-06-18T16:34:18.000Z",
  "firstName": "Joe",
  "lastName": "Smith",
  "ownerId": "1111111",
  "userName": "jsmith"
}


class TestGetSynapseTags(unittest.TestCase):

  def test_happy(self):
    result = app.get_synapse_tags(jsmith_profile)
    expected = [
      {'Key': 'synapse:firstName', 'Value': 'Joe'},
      {'Key': 'synapse:lastName', 'Value': 'Smith'},
      {'Key': 'synapse:ownerId', 'Value': '1111111'},
      {'Key': 'synapse:userName', 'Value': 'jsmith'},
      {'Key': 'synapse:email', 'Value': 'jsmith@synapse.org'},
      {'Key': 'OwnerEmail', 'Value': 'jsmith@synapse.org'}
    ]
    self.assertDictEqual(result[0], expected[0])

  def test_sad(self):
    with self.assertRaises(AttributeError):
      app.get_synapse_tags("invalid input")
