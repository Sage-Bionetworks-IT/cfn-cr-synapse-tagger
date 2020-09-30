import unittest

from set_tags import utils


class TestGetSynapseOwnerId(unittest.TestCase):

  def test_tag_present(self):
    tags = [
      {'Key': 'heresatag', 'Value': 'heresatagvalue'},
      {'Key': 'theresatag', 'Value': 'theresatagvalue'},
      {'Key': 'aws:servicecatalog:provisioningPrincipalArn', 'Value': 'foo/bar'}
    ]
    result = utils.get_synapse_owner_id(tags)
    self.assertEqual(result, 'bar')


  def test_tag_missing(self):
    with self.assertRaises(ValueError):
      tags = [
        {'Key': 'heresatag', 'Value': 'heresatagvalue'},
        {'Key': 'theresatag', 'Value': 'theresatagvalue'}
      ]
      utils.get_synapse_owner_id(tags)
