import unittest
import boto3

from unittest.mock import MagicMock, patch
from set_tags import utils
from botocore.stub import Stubber

from set_tags import set_instance_tags


class TestGetVolumeIds(unittest.TestCase):

  @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'test-region'})
  def test_happy(self):
    ec2 = boto3.client('ec2')
    with Stubber(ec2) as stubber:
      stubber.add_response(
        method='describe_volumes',
        expected_params={
          'Filters': [
            {
               'Name': 'attachment.instance-id',
               'Values': ['i-123456789']
             }
          ]
        },
        service_response={
          'Volumes': [
            {
              'Attachments': [
                {
                  'AttachTime': '2020-09-17 00:00:00',
                  'DeleteOnTermination': True,
                  'Device': '/dev/sda1',
                  'InstanceId': 'i-1234567890abcdef0',
                  'State': 'attached',
                  'VolumeId': 'vol-049df61146c4d7901',
                },
              ],
              'AvailabilityZone': 'us-east-1a',
              'CreateTime': '2020-09-17 00:00:00',
              'Size': 8,
              'SnapshotId': 'snap-1234567890abcdef0',
              'State': 'in-use',
              'VolumeId': 'vol-049df61146c4d7901',
              'VolumeType': 'standard'
            },
          ],
        }
      )
      utils.get_ec2_client = MagicMock(return_value=ec2)
      result = set_instance_tags.get_volume_ids("i-123456789")
      expected = ['vol-049df61146c4d7901']
      self.assertEqual(result, expected)
