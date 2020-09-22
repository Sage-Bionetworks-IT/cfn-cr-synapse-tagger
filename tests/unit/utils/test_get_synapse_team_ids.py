import unittest
import boto3

from unittest.mock import patch
from set_tags import utils
from botocore.stub import Stubber

MOCK_GET_PARAMETER_RESPONSE = {
    "Parameter": {
        "Name": "/service-catalog/TeamToRoleArnMap",
        "Type": "String",
        "Value": "[ {\"teamId\":\"1111111\",\"roleArn\":\"arn:aws:iam::999999999999:role/ServiceCatalogEndusers\"},"
                 "{\"teamId\":\"2222222\",\"roleArn\":\"arn:aws:iam::999999999999:role/ServiceCatalogExternalEndusers\"} ]",
        "Version": 1,
        "LastModifiedDate": 1600127530.776,
        "ARN": "arn:aws:ssm:us-east-1:999999999999:parameter/service-catalog/TeamToRoleArnMap",
        "DataType": "text"
    }
}

class TestGetSynapseTeamIds(unittest.TestCase):

  def test_happy_path(self):
    ssm = boto3.client('ssm')
    with Stubber(ssm) as stubber, \
      patch('set_tags.utils.get_ssm_parameter') as param_mock:
        param_mock.return_value = MOCK_GET_PARAMETER_RESPONSE
        result = utils.get_synapse_team_ids()
        expected = ["1111111","2222222"]
        self.assertListEqual(result, expected)