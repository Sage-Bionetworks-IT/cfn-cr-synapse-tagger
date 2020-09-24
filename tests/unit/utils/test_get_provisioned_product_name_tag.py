import unittest
from unittest.mock import MagicMock

from botocore.stub import Stubber

from set_tags import utils


class TestGetAccessApprovedRoleTag(unittest.TestCase):

  def test_principle_arn_tag_present(self):
    tags = [{
      'Key': 'aws:servicecatalog:provisioningPrincipalArn',
      'Value': 'arn:aws:sts::123456789012:assumed-role/ServiceCatalogEndusers/1234567'
    }]

    iam = utils.get_iam_client()
    with Stubber(iam) as stubber:
        stubber.add_response(
          method='get_role',
          expected_params={
            'RoleName': 'ServiceCatalogEndusers'
          },
          service_response={
            'Role': {
              'Arn': 'arn:aws:iam::123456789012:role/ServiceCatalogEndusers',
              'CreateDate': '2020-09-17 00:00:00',
              'Path': '/',
              'RoleId': 'AIDIODR4TAW7CSEXAMPLE',
              'RoleName': 'ServiceCatalogEndusers',
            }
          }
        )
        utils.get_iam_client = MagicMock(return_value=iam)
        result = utils.get_access_approved_role_tag(tags)
        expected = {'Key': 'Protected/AccessApprovedCaller', 'Value': 'AIDIODR4TAW7CSEXAMPLE:1234567'}
        self.assertEqual(result, expected)


  def test_principal_arn_tag_missing(self):
    with self.assertRaises(ValueError):
      tags = [{
        'Key': 'foo',
        'Value': 'bar'
      }]
      utils.get_access_approved_role_tag(tags)
