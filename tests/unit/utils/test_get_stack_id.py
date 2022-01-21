import unittest

from set_tags import utils


class TestGetStackId(unittest.TestCase):

  def test_get_stack_id_not_found(self):

    with self.assertRaises(AssertionError):
      event = {
        "RequestType": "Create",
        "ServiceToken": "arn:aws:lambda:us-east-1:1111111111:function:cfn-cr-synapse-tagger-SetInstanceTagsFunction-3WJHJ7EN7GG4",
        "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A1111111111%3Astack/SC-1111111111-pp-sgs4ci2tpu562/5812d0a0-6de1-11ec-9206-1222684e5ea9%7CTagInstance%7C3929fbbf-739f-422e-8fce-60766c2cac91?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220105T044210Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWTXJ26R7U6%2F20220105%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=0da97030e5af5ca31d68af3d11d8fdbda814ce013541c4aeaa1866f811414207",
        "RequestId": "3929fbbf-739f-422e-8fce-60766c2cac91",
        "LogicalResourceId": "TagInstance",
        "ResourceType": "Custom::SynapseTagger",
        "ResourceProperties": {
          "ServiceToken": "arn:aws:lambda:us-east-1:1111111111:function:cfn-cr-synapse-tagger-SetInstanceTagsFunction-3WJHJ7EN7GG4",
        }
      }
      result = utils.get_stack_id(event)

  def test_get_stack_id_value(self):
    STACK_ID = "arn:aws:cloudformation:us-east-1:1111111111:stack/SC-1111111111-pp-sgs4ci2tpu562/5812d0a0-6de1-11ec-9206-1222684e5ea9"

    event = {
      "RequestType": "Create",
      "ServiceToken": "arn:aws:lambda:us-east-1:1111111111:function:cfn-cr-synapse-tagger-SetInstanceTagsFunction-3WJHJ7EN7GG4",
      "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A1111111111%3Astack/SC-1111111111-pp-sgs4ci2tpu562/5812d0a0-6de1-11ec-9206-1222684e5ea9%7CTagInstance%7C3929fbbf-739f-422e-8fce-60766c2cac91?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220105T044210Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWTXJ26R7U6%2F20220105%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=0da97030e5af5ca31d68af3d11d8fdbda814ce013541c4aeaa1866f811414207",
      "StackId": STACK_ID,
      "RequestId": "3929fbbf-739f-422e-8fce-60766c2cac91",
      "LogicalResourceId": "TagInstance",
      "ResourceType": "Custom::SynapseTagger",
      "ResourceProperties": {
        "ServiceToken": "arn:aws:lambda:us-east-1:1111111111:function:cfn-cr-synapse-tagger-SetInstanceTagsFunction-3WJHJ7EN7GG4",
      }
    }
    result = utils.get_stack_id(event)
    self.assertEqual(result, STACK_ID)
