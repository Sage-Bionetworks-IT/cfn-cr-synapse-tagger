import unittest
import synapseclient

from synapseclient.core.exceptions import SynapseHTTPError
from unittest.mock import patch, MagicMock
from set_bucket_tags import app

tags_a = [
  {"Key": "Department", "Value": "Platform"},
  {"Key": "aws:cloudformation:stack-name", "Value": "SC-465877038949-pp-5ydwosuynbtpq"}
]

tags_b = [
  {"Key": "synapse:ownerId", "Value": "1111111"},
  {"Key": "synapse:userName", "Value": "jsmith"}
]

class TestMerge(unittest.TestCase):

  def test_happy(self):
    result = app.merge(tags_a, tags_b)
    expected = [
      {'Key': 'Department', 'Value': 'Platform'},
      {'Key': 'aws:cloudformation:stack-name', 'Value': 'SC-465877038949-pp-5ydwosuynbtpq'},
      {'Key': 'synapse:ownerId', 'Value': '1111111'},
      {'Key': 'synapse:userName', 'Value': 'jsmith'}
    ]
    self.assertEqual(result, expected)
