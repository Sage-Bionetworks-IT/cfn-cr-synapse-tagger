import unittest
import boto3

from unittest.mock import patch
from set_tags import utils
from botocore.stub import Stubber

class TestGetMarketplaceTags(unittest.TestCase):

  def test_has_tags(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_marketplace_customer_id') as customer_id_mock, \
      patch('set_tags.utils.get_ssm_parameter') as ssm_param_mock:
        customer_id_mock.return_value = "mkt-cust-1234"
        ssm_param_mock.return_value = "mkt-prod-1234"
        result = utils.get_marketplace_tags(1234567)
        expected = [
          {'Key': 'synapse:marketplaceProductCode', 'Value': 'mkt-prod-1234'},
          {'Key': 'synapse:marketplaceCustomerId', 'Value': 'mkt-cust-1234'}
        ]
        self.assertListEqual(result, expected)

  def test_no_product_code_tag(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_marketplace_customer_id') as customer_id_mock, \
      patch('set_tags.utils.get_ssm_parameter') as ssm_param_mock:
        customer_id_mock.return_value = ""
        ssm_param_mock.return_value = "mkt-prod-1234"
        result = utils.get_marketplace_tags(1234567)
        expected = [
          {'Key': 'synapse:marketplaceProductCode', 'Value': 'mkt-prod-1234'}
        ]
        self.assertListEqual(result, expected)

  def test_no_customer_id_tag(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_marketplace_customer_id') as customer_id_mock, \
      patch('set_tags.utils.get_ssm_parameter') as ssm_param_mock:
        customer_id_mock.return_value = "mkt-cust-1234"
        ssm_param_mock.return_value = ""
        result = utils.get_marketplace_tags(1234567)
        expected = [
          {'Key': 'synapse:marketplaceCustomerId', 'Value': 'mkt-cust-1234'}
        ]
        self.assertListEqual(result, expected)

  def test_no_tags(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_marketplace_customer_id') as customer_id_mock, \
      patch('set_tags.utils.get_ssm_parameter') as ssm_param_mock:
        customer_id_mock.return_value = ""
        ssm_param_mock.return_value = ""
        result = utils.get_marketplace_tags(1234567)
        expected = []
        self.assertListEqual(result, expected)
