import unittest

from set_tags import utils


class TestGetSynapseOwnerId(unittest.TestCase):

  def test_dict_with_both_keys(self):
      data = {
          "synapse:ownerId": "1234567",
          "aws:servicecatalog:provisioningPrincipalArn": "arn:aws:sts::111111111:assumed-role/ServiceCatalogEndusers/378505"
      }
      self.assertEqual(utils.get_synapse_owner_id(data), "1234567")

  def test_dict_with_only_owner(self):
      data = {"synapse:ownerId": "1234567"}
      self.assertEqual(utils.get_synapse_owner_id(data), "1234567")

  def test_dict_with_only_principal(self):
      data = {"aws:servicecatalog:provisioningPrincipalArn": "arn:aws:sts::111111111:assumed-role/ServiceCatalogEndusers/378505"}
      self.assertEqual(
          utils.get_synapse_owner_id(data),
          "378505"
      )

  def test_dict_with_no_keys(self):
      data = {"foo": "bar"}
      self.assertIsNone(utils.get_synapse_owner_id(data))

  def test_list_with_both_keys(self):
      data = [
          {"Key": "aws:servicecatalog:provisioningPrincipalArn", "Value": "arn:aws:sts::111111111:assumed-role/ServiceCatalogEndusers/378505"},
          {"Key": "synapse:ownerId", "Value": "1234567"},
      ]
      self.assertEqual(utils.get_synapse_owner_id(data), "1234567")

  def test_list_with_only_owner(self):
      data = [{"Key": "synapse:ownerId", "Value": "1234567"}]
      self.assertEqual(utils.get_synapse_owner_id(data), "1234567")

  def test_list_with_only_principal(self):
      data = [{"Key": "aws:servicecatalog:provisioningPrincipalArn", "Value": "arn:aws:sts::111111111:assumed-role/ServiceCatalogEndusers/378505"}]
      self.assertEqual(
          utils.get_synapse_owner_id(data),
          "378505"
      )

  def test_list_with_no_keys(self):
      data = [{"Key": "foo", "Value": "bar"}]
      self.assertIsNone(utils.get_synapse_owner_id(data))

  def test_empty_dict(self):
      self.assertIsNone(utils.get_synapse_owner_id({}))

  def test_empty_list(self):
      self.assertIsNone(utils.get_synapse_owner_id([]))

  def test_invalid_type(self):
      with self.assertRaises(TypeError):
          utils.get_synapse_owner_id("not a dict or list")
