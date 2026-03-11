import unittest
from change_owner import update_bucket_policy

class TestUpdateBucketPolicy(unittest.TestCase):
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
          policy,
          "1234567",
          "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
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
          policy,
          "1234567",
          "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
      )

      self.assertFalse(updated)
      self.assertEqual(
          policy["Statement"][0]["Principal"]["AWS"],
          [
              "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/2222222",
              "arn:aws:iam::111111111111:role/SomeOtherRole",
          ],
      )


  def test_it_4887(self):
      policy = {
          "Statement": [
              {
                  "Principal": {
                      "AWS": [
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
          policy,
          "1234567",
          "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
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

  def test_it_4887_string(self):
      policy = {
          "Statement": [
              {
                  "Principal": {
                      "AWS": "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/1234567"
                  }
              },
              {
                  "Principal": "*"
              }
          ]
      }

      updated = update_bucket_policy(
          policy,
          "1234567",
          "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321",
      )

      self.assertTrue(updated)
      self.assertEqual(
          policy["Statement"][0]["Principal"]["AWS"],
          [
              "arn:aws:sts::111111111111:assumed-role/ServiceCatalogEndusers/7654321"
          ]
      )
      self.assertEqual(policy["Statement"][1]["Principal"], "*")
