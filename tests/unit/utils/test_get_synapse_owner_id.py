import unittest

from set_tags import utils


class TestGetSynapseOwnerId(unittest.TestCase):

  def test_list_tag_present(self):
    tags = [
      {'Key': 'heresatag', 'Value': 'heresatagvalue'},
      {'Key': 'theresatag', 'Value': 'theresatagvalue'},
      {'Key': 'aws:servicecatalog:provisioningPrincipalArn', 'Value': 'foo/bar'}
    ]
    result = utils.get_synapse_owner_id(tags)
    self.assertEqual(result, 'bar')

  def test_list_tag_missing(self):
    with self.assertRaises(ValueError):
      tags = [
        {'Key': 'heresatag', 'Value': 'heresatagvalue'},
        {'Key': 'theresatag', 'Value': 'theresatagvalue'}
      ]
      utils.get_synapse_owner_id(tags)

  def test_dict_tag_present(self):
    tags = {
      'heresatag': 'heresatagvalue',
      'theresatag':'theresatagvalue',
      'aws:servicecatalog:provisioningPrincipalArn':'foo/bar'
    }
    result = utils.get_synapse_owner_id(tags)
    self.assertEqual(result, 'bar')

  def test_dict_tag_missing(self):
    with self.assertRaises(ValueError):
      tags = {
        'heresatag': 'heresatagvalue',
        'theresatag': 'theresatagvalue',
      }
      utils.get_synapse_owner_id(tags)
