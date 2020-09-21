import unittest

from set_tags import set_instance_tags


class TestGetInstanceId(unittest.TestCase):

  def test_instance_id_present(self):
    event = {
      'ResourceProperties': {
        'InstanceId': 'a_instance_id'
      }
    }
    result = set_instance_tags.get_instance_id(event)
    self.assertEqual(result, 'a_instance_id')


  def test_instance_id_missing(self):
    with self.assertRaises(ValueError):
      event = { 'ResourceProperties': {} }
      set_instance_tags.get_instance_id(event)
