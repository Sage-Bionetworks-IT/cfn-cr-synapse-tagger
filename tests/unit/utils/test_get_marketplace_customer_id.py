import unittest

from unittest.mock import MagicMock, patch
from botocore.stub import Stubber
from set_tags import utils


class TestGetMarketplaceCustomerId(unittest.TestCase):

  def test_registered_customer(self):
    ddb = utils.get_dynamo_client()
    with Stubber(ddb) as stubber, \
      patch('set_tags.utils.get_env_var_value') as env_var_val:
      env_var_val.return_value = "SomeTable"
      response = {
          "Item": {
              "MarketplaceCustomerId": {
                  "S": "mkt-cust-1234"
              }
          }
      }
      stubber.add_response('get_item', response)
      utils.get_dynamo_client = MagicMock(return_value=ddb)
      synapse_id = "1234567"
      result = utils.get_marketplace_customer_id(synapse_id)
      self.assertEqual("mkt-cust-1234", result)

  def test_no_registered_customer(self):
    ddb = utils.get_dynamo_client()
    with Stubber(ddb) as stubber, \
      patch('set_tags.utils.get_env_var_value') as env_var_val:
      env_var_val.return_value = "SomeTable"
      response = {}
      stubber.add_response('get_item', response)
      utils.get_dynamo_client = MagicMock(return_value=ddb)
      synapse_id = "1234567"
      result = utils.get_marketplace_customer_id(synapse_id)
      self.assertEqual(None, result)
