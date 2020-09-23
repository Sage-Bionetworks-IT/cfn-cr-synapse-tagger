import unittest

from set_tags import set_bucket_tags


class TestGetBucketName(unittest.TestCase):

  def test_bucketname_present(self):
    event = {
      'ResourceProperties': {
        'BucketName': 'a_bucket_name'
      }
    }
    result = set_bucket_tags.get_bucket_name(event)
    self.assertEqual(result, 'a_bucket_name')


  def test_bucketname_missing(self):
    with self.assertRaises(ValueError):
      event = { 'ResourceProperties': {} }
      set_bucket_tags.get_bucket_name(event)
