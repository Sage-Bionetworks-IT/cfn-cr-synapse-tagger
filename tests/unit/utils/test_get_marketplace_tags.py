import unittest

from unittest.mock import patch
from set_tags import utils
from set_tags.utils import MARKETPLACE_TAG_PREFIX

class TestGetMarketplaceTags(unittest.TestCase):

  @patch('set_tags.utils.get_marketplace_customer_info')
  def test_no_tags(self,
                   mock_get_marketplace_customer_info):
    mock_get_marketplace_customer_info.return_value = {}
    tags = utils.get_marketplace_tags("111111")
    expected = []
    self.assertListEqual(tags, expected)

  @patch('set_tags.utils.get_marketplace_customer_info')
  def test_has_tags(self,
                    mock_get_marketplace_customer_info):
    mock_get_marketplace_customer_info.return_value = {
      'SynapseUserId': '111111',
      'MarketplaceCustomerId': 'cust-1234',
      'ProductCode': 'prod-9876'
    }

    tags = utils.get_marketplace_tags("111111")
    expected = [
      {'Key': f'{MARKETPLACE_TAG_PREFIX}:customerId', 'Value': 'cust-1234'},
      {'Key': f'{MARKETPLACE_TAG_PREFIX}:productCode', 'Value': 'prod-9876'}
    ]
    self.assertListEqual(tags, expected)
