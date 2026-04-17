import unittest
from change_owner import update_bucket_policy

class TestUpdateBucketPolicy(unittest.TestCase):

    def test_duplicate_target_user_id(self):
        policy = {
            "Statement": [
                {
                    "Principal": {
                        "AWS": [ # This case tests when the target user ID appears multiple times in the policy
                            "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/1234567",
                            "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/1234567",
                            "arn:aws:iam::111111111111:role/SomeOtherRole",
                        ]
                    }
                }
            ]
        }

        updated = update_bucket_policy(
            bucket_policy=policy,
            target_user_id="1234567",
            new_assumed_role_arn="arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
        )

        self.assertTrue(updated)
        # The new ARN should only appear once, and the other role should remain
        self.assertEqual(
            policy["Statement"][0]["Principal"]["AWS"],
            [
                "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
                "arn:aws:iam::111111111111:role/SomeOtherRole",
            ]
        )


    def test_happy_case(self):
        policy = {
            "Statement": [
                {
                    "Principal": {
                        "AWS": [
                            "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/1234567",
                            "arn:aws:iam::111111111111:role/SomeOtherRole",
                        ]
                    }
                }
            ]
        }

        updated = update_bucket_policy(
            bucket_policy=policy,
            target_user_id="1234567",
            new_assumed_role_arn="arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
        )

        self.assertTrue(updated)
        self.assertEqual(
            policy["Statement"][0]["Principal"]["AWS"],
            [
                "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
                "arn:aws:iam::111111111111:role/SomeOtherRole",
            ],
        )


    def test_target_not_found(self):
        policy = {
            "Statement": [
                {
                    "Principal": {
                        "AWS": [
                            "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/2222222",
                            "arn:aws:iam::111111111111:role/SomeOtherRole",
                        ]
                    }
                }
            ]
        }

        updated = update_bucket_policy(
            bucket_policy=policy,
            target_user_id="1234567",
            new_assumed_role_arn="arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
        )

        self.assertFalse(updated)
        self.assertEqual(
            policy["Statement"][0]["Principal"]["AWS"],
            [
                "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/2222222",
                "arn:aws:iam::111111111111:role/SomeOtherRole",
            ],
        )


    def test_aws_principal_array(self):
        policy = {
            "Statement": [
                {
                    "Principal": {
                        "AWS": [ # This case tests when the AWS principal is an array
                            "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/1234567",
                            "arn:aws:iam::111111111111:role/SomeOtherRole",
                        ]
                    }
                },
                {
                    "Principal": "*"
                }
            ]
        }

        updated = update_bucket_policy(
            bucket_policy=policy,
            target_user_id="1234567",
            new_assumed_role_arn="arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
        )

        self.assertTrue(updated)
        self.assertEqual(
            policy["Statement"][0]["Principal"]["AWS"],
            [
                "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
                "arn:aws:iam::111111111111:role/SomeOtherRole",
            ]
        )
        self.assertEqual(policy["Statement"][1]["Principal"], "*")

    def test_target_not_found_string(self):
        policy = {
            "Statement": [
                {
                    "Principal": { # This case tests when the AWS principal is a string instead of an array
                        "AWS": "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/1234567"
                    }
                },
                {
                    "Principal": "*"
                }
            ]
        }

        updated = update_bucket_policy(
            bucket_policy=policy,
            target_user_id="1234567",
            new_assumed_role_arn="arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
        )

        self.assertTrue(updated)
        self.assertEqual(
            policy["Statement"][0]["Principal"]["AWS"],
            [
                "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321"
            ]
        )
        self.assertEqual(policy["Statement"][1]["Principal"], "*")


    def test_principal_string(self):
        policy = {
            "Statement": [
                {
                    "Principal": "*"
                }
            ]
        }

        updated = update_bucket_policy(
            bucket_policy=policy,
            target_user_id="1234567",
            new_assumed_role_arn="arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
        )

        self.assertFalse(updated)
        self.assertEqual(policy["Statement"][0]["Principal"], "*")
