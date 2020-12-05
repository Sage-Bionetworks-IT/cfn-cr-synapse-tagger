import unittest

from unittest.mock import MagicMock, patch
from botocore.stub import Stubber
from set_tags import utils


class TestGetMarketplaceCustomerInfo(unittest.TestCase):

  def test_registered_customer(self):
    ddb = utils.get_dynamo_client()
    with Stubber(ddb) as stubber, \
      patch('set_tags.utils.get_env_var_value') as env_var_val:
      env_var_val.return_value = "SomeTable"
      response = {
        "Item": {
          "ProductCode": {
            "S": "prod-1234"
          },
          "MarketplaceCustomerId": {
            "S": "cust-1234"
          },
          "SynapseUserId": {
            "S": "11111"
          }
        },
        "ResponseMetadata": {
          "RequestId": "7O3ULIVRKDGRG2I27D5NOO8SSRVV4KQNSO5AEMVJF66Q9ASUAAJG",
          "HTTPStatusCode": 200,
        }
      }
      stubber.add_response('get_item', response)
      utils.get_dynamo_client = MagicMock(return_value=ddb)
      synapse_id = "11111"
      result = utils.get_marketplace_customer_info(synapse_id)
      expected = {
        'SynapseUserId': '11111',
        'MarketplaceCustomerId': 'cust-1234',
        'ProductCode': 'prod-1234'
      }
      self.assertEqual(result, expected)

  def test_no_registered_customer(self):
    ddb = utils.get_dynamo_client()
    with Stubber(ddb) as stubber, \
      patch('set_tags.utils.get_env_var_value') as env_var_val:
      env_var_val.return_value = "SomeTable"
      response = {}
      stubber.add_response('get_item', response)
      utils.get_dynamo_client = MagicMock(return_value=ddb)
      synapse_id = "11111"
      result = utils.get_marketplace_customer_info(synapse_id)
      self.assertEqual({}, result)

  def test_no_env_var_marketplace_id_dynamo_table_name(self):
    ddb = utils.get_dynamo_client()
    with Stubber(ddb) as stubber, \
      patch('set_tags.utils.get_env_var_value') as env_var_mock:
        env_var_mock.return_value = None
        synapse_id = "11111"
        result = utils.get_marketplace_customer_info(synapse_id)
        self.assertEqual({}, result)
