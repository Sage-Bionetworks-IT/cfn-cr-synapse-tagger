import unittest

from set_tags import utils

class TestFormatTags(unittest.TestCase):

  def test_format_tags_none(self):
    tags = []
    result = utils.format_tags_kv_kp(tags)
    self.assertEqual(result, {})

  def test_format_tags_multiple(self):
    tags = [
      {'Key': 'heresatag', 'Value': 'heresatagvalue'},
      {'Key': 'theresatag', 'Value': 'theresatagvalue'},
      {'Key': 'aws:servicecatalog:provisioningPrincipalArn', 'Value': 'foo/bar'}
    ]
    result = utils.format_tags_kv_kp(tags)
    expected = {
      "heresatag": "heresatagvalue",
      "theresatag": "theresatagvalue",
      "aws:servicecatalog:provisioningPrincipalArn": "foo/bar"
    }
    self.assertEqual(result, expected)
 