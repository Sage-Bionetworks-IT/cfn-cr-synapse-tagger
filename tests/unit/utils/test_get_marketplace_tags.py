import unittest

from unittest.mock import patch
from set_tags import utils
from set_tags.utils import MARKETPLACE_TAG_PREFIX

class TestGetMarketplaceTags(unittest.TestCase):

  @patch('set_tags.utils.get_marketplace_product_code')
  @patch('set_tags.utils.get_marketplace_customer_id')
  def test_no_tags(self,
                   mock_get_marketplace_customer_id,
                   mock_get_marketplace_product_code):
    mock_get_marketplace_customer_id.return_value = None
    mock_get_marketplace_product_code.return_value = None
    tags = utils.get_marketplace_tags("111111")
    expected = []
    self.assertListEqual(tags, expected)

  @patch('set_tags.utils.get_marketplace_product_code')
  @patch('set_tags.utils.get_marketplace_customer_id')
  def test_has_tags(self,
                    mock_get_marketplace_customer_id,
                    mock_get_marketplace_product_code):
    mock_get_marketplace_customer_id.return_value = "cust-1234"
    mock_get_marketplace_product_code.return_value = "prod-9876"
    tags = utils.get_marketplace_tags("111111")
    expected = [
      {'Key': f'{MARKETPLACE_TAG_PREFIX}:customerId', 'Value': 'cust-1234'},
      {'Key': f'{MARKETPLACE_TAG_PREFIX}:productCode', 'Value': 'prod-9876'}
    ]
    self.assertListEqual(tags, expected)
