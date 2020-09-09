import unittest
from set_instance_tags import app


class TestFilterTags(unittest.TestCase):

  def test_filter_tags(self):
    full_tags = [
      {
        "Key": "Department",
        "ResourceId": "i-0f08b4ff6872c9786",
        "ResourceType": "instance",
        "Value": "Platform"
      },
      {
        "Key": "aws:cloudformation:stack-id",
        "ResourceId": "i-0f08b4ff6872c9786",
        "ResourceType": "instance",
        "Value": "arn:aws:cloudformation:us-east-1:465877038949:stack/SC-465877038949-pp-5ydwosuynbtpq/26318a30-f214-11ea-bce0-0e706f74ed45"
      }
    ]
    filtered_tags = [
      {
        "Key": "Department",
        "Value": "Platform"
      }
    ]
    tags = app.filter_tags(full_tags)
    self.assertEqual(tags, filtered_tags)
