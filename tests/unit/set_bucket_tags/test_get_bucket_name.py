import unittest

from set_bucket_tags import app


class TestGetBucketName(unittest.TestCase):

  def test_bucketname_present(self):
    event = {
      'ResourceProperties': {
        'BucketName': 'a_bucket_name'
      }
    }
    result = app.get_bucket_name(event)
    self.assertEqual(result, 'a_bucket_name')


  def test_bucketname_missing(self):
    with self.assertRaises(ValueError):
      event = { 'ResourceProperties': {} }
      app.get_bucket_name(event)
