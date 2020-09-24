import unittest

from set_tags import utils


class TestGetProvisionedProductNameTag(unittest.TestCase):

  def test_product_arn_tag_present(self):
    tags = [{
      'Key': 'aws:servicecatalog:provisionedProductArn',
      'Value': 'arn:aws:servicecatalog:us-east-1:123456712:stack/my-product/pp-mycpuogt2i45s'
    }]
    result = utils.get_provisioned_product_name_tag(tags)
    expected = {
      'Key': 'Name',
      'Value': 'my-product'
    }
    self.assertEqual(result, expected)


  def test_product_arn_tag_missing(self):
    with self.assertRaises(ValueError):
      tags = [{
        'Key': 'foo',
        'Value': 'bar'
      }]
      utils.get_provisioned_product_name_tag(tags)
