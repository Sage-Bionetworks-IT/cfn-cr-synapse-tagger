import unittest
from unittest.mock import MagicMock, patch

import boto3
import botocore
from botocore.stub import Stubber

from set_tags import utils


class TestGetCfnStackTags(unittest.TestCase):

  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_valid_stack(self):
    cfn = utils.get_cfn_client()
    with Stubber(cfn) as stubber:
      tags = [
        {
          "Key": "aws:servicecatalog:productArn",
          "Value": "arn:aws:catalog:us-east-1:11111111111:product/prod-6xe6xagbqxb4q"
        },
        {
          "Key": "Project",
          "Value": "Infrastructure"
        },
        {
          "Key": "aws:servicecatalog:provisioningPrincipalArn",
          "Value": "arn:aws:sts::11111111111:assumed-role/ServiceCatalogEndusers/273960"
        },
        {
          "Key": "Department",
          "Value": "Platform"
        },
        {
          "Key": "CostCenter",
          "Value": "NO PROGRAM / 000000"
        },
        {
          "Key": "aws:servicecatalog:provisioningArtifactIdentifier",
          "Value": "pa-v5wkshtu5tykw"
        },
        {
          "Key": "aws:servicecatalog:portfolioArn",
          "Value": "arn:aws:catalog:us-east-1:11111111111:portfolio/port-uk3nkvvmvw64y"
        },
        {
          "Key": "aws:servicecatalog:provisionedProductArn",
          "Value": "arn:aws:servicecatalog:us-east-1:11111111111:stack/sc306.3/pp-yd5tcochoi32c"
        }
      ]
      response = {
        "Stacks": [
          {
            "StackId": "arn:aws:cloudformation:us-east-1:1111111111:stack/SC-11111111111-pp-yd5tcochoi32c/932c7240-74bc-11ec-9ed8-0ab60a8ca761",
            "StackName": "SC-11111111111-pp-yd5tcochoi32c",
            "CreationTime": "2022-01-13T22:03:01.468000+00:00",
            "LastUpdatedTime": "2022-01-13T22:42:31.079000+00:00",
            "RollbackConfiguration": {},
            "StackStatus": "UPDATE_COMPLETE",
            "DisableRollback": False,
            "NotificationARNs": [],
            "Tags": tags
          }
        ]
      }
      stubber.add_response('describe_stacks', response)
      utils.get_cfn_client = MagicMock(return_value=cfn)
      valid_stack_id ='some_reasonable_stack_id'
      result = utils.get_cfn_stack_tags(valid_stack_id)
      self.assertEqual(tags, result)

  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_no_tags(self):
    cfn = utils.get_cfn_client()
    with Stubber(cfn) as stubber, self.assertRaises(Exception):
      response = {
        "Stacks": [
          {
            "StackId": "arn:aws:cloudformation:us-east-1:1111111111:stack/SC-11111111111-pp-yd5tcochoi32c/932c7240-74bc-11ec-9ed8-0ab60a8ca761",
            "StackName": "SC-11111111111-pp-yd5tcochoi32c",
            "CreationTime": "2022-01-13T22:03:01.468000+00:00",
            "LastUpdatedTime": "2022-01-13T22:42:31.079000+00:00",
            "RollbackConfiguration": {},
            "StackStatus": "UPDATE_COMPLETE",
            "DisableRollback": False,
            "NotificationARNs": [],
            "Tags": []
          }
        ]
      }
      stubber.add_response('describe_stacks', response)
      utils.get_cfn_client = MagicMock(return_value=cfn)
      valid_stack_id ='some_reasonable_stack_id'
      result = utils.get_cfn_stack_tags(valid_stack_id)
