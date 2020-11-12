import unittest
import boto3

from unittest.mock import patch
from set_tags import utils
from botocore.stub import Stubber

class TestGetMarketplaceTags(unittest.TestCase):

  MOCK_MARKETPLACE_PRODUCT_CODE_SC = {
    "Parameter": {
      "Name": "/service-catalog/MarketplaceProductCodeSC",
      "Type": "String",
      "Value": "mkt-prod-1234",
      "Version": 1,
      "LastModifiedDate": "today",
      "ARN": "arn:aws:ssm:us-east-1:1111111111:parameter/service-catalog/MarketplaceProductCodeSC",
      "DataType": "text"
    }
  }

  def test_has_tags(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_marketplace_customer_id') as customer_id_mock, \
      patch('set_tags.utils.get_env_var_value') as env_var_mock, \
      patch('set_tags.utils.get_ssm_parameter') as ssm_param_mock:
        customer_id_mock.return_value = "mkt-cust-1234"
        env_var_mock.return_value = "some-value"
        ssm_param_mock.return_value = self.MOCK_MARKETPLACE_PRODUCT_CODE_SC
        result = utils.get_marketplace_tags(1234567)
        expected = [
          {'Key': 'marketplace:productCode', 'Value': 'mkt-prod-1234'},
          {'Key': 'marketplace:customerId', 'Value': 'mkt-cust-1234'}
        ]
        self.assertListEqual(result, expected)

  def test_no_customer_id_tag(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_marketplace_customer_id') as customer_id_mock, \
      patch('set_tags.utils.get_env_var_value') as env_var_mock, \
      patch('set_tags.utils.get_ssm_parameter') as ssm_param_mock:
        customer_id_mock.return_value = ""
        env_var_mock.return_value = "some-value"
        ssm_param_mock.return_value = self.MOCK_MARKETPLACE_PRODUCT_CODE_SC
        result = utils.get_marketplace_tags(1234567)
        expected = [
          {'Key': 'marketplace:productCode', 'Value': 'mkt-prod-1234'}
        ]
        self.assertListEqual(result, expected)

  def test_no_product_code_tag(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_marketplace_customer_id') as customer_id_mock, \
      patch('set_tags.utils.get_env_var_value') as env_var_mock, \
      patch('set_tags.utils.get_ssm_parameter') as ssm_param_mock:
        customer_id_mock.return_value = "mkt-cust-1234"
        env_var_mock.return_value = "some-value"
        ssm_param_mock.return_value = {
          "Parameter": {
            "Name": "/service-catalog/MarketplaceProductCodeSC",
            "Type": "String",
            "Value": "",
            "Version": 1,
            "LastModifiedDate": "today",
            "ARN": "arn:aws:ssm:us-east-1:1111111111:parameter/service-catalog/MarketplaceProductCodeSC",
            "DataType": "text"
          }
        }
        result = utils.get_marketplace_tags(1234567)
        expected = [
          {'Key': 'marketplace:customerId', 'Value': 'mkt-cust-1234'}
        ]
        self.assertListEqual(result, expected)

  def test_no_tags(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_marketplace_customer_id') as customer_id_mock, \
      patch('set_tags.utils.get_env_var_value') as env_var_mock, \
      patch('set_tags.utils.get_ssm_parameter') as ssm_param_mock:
        customer_id_mock.return_value = ""
        env_var_mock.return_value = "some-value"
        ssm_param_mock.return_value = {
          "Parameter": {
            "Name": "/service-catalog/MarketplaceProductCodeSC",
            "Type": "String",
            "Value": "",
            "Version": 1,
            "LastModifiedDate": "today",
            "ARN": "arn:aws:ssm:us-east-1:1111111111:parameter/service-catalog/MarketplaceProductCodeSC",
            "DataType": "text"
          }
        }
        result = utils.get_marketplace_tags(1234567)
        expected = []
        self.assertListEqual(result, expected)

  def test_no_env_var_marketplace_product_code_sc_param_name(self):
    ddb = utils.get_dynamo_client()
    with Stubber(ddb) as stubber, \
      patch('set_tags.utils.get_env_var_value') as env_var_mock:
        env_var_mock.return_value = None
        result = utils.get_marketplace_tags(1234567)
        expected = []
        self.assertListEqual(result, expected)

  def test_no_ssm_param_marketplace_product_code_sc(self):
    ddb = utils.get_dynamo_client()
    with Stubber(ddb) as stubber, \
      patch('set_tags.utils.get_ssm_parameter') as get_ssm_param_mock:
        get_ssm_param_mock.return_value = None
        result = utils.get_marketplace_tags(1234567)
        expected = []
        self.assertListEqual(result, expected)
