import json
import unittest

from set_bucket_tags import app


class TestHandler(unittest.TestCase):


  def test_add_owner_email_tag(self):
    synapse_username = 'janedoe'
    tags = [
      {
        'Key': 'aws:servicecatalog:provisioningPrincipalArn',
        'Value': 'arn:aws:sts::237179673806:assumed-role/ServiceCatalogEndusers/0123456'
      },
      {
        'Key': 'Department',
        'Value': 'some_department'
      },
      {
        'Key': 'Project',
        'Value': 'some_project'
      }
    ]
    email = 'janedoe@synapse.org'
    tags = app.add_owner_email_tag(tags=tags, email=email)
    keys = [tag['Key'] for tag in tags]
    self.assertIn('aws:servicecatalog:provisioningPrincipalArn', keys)
    self.assertIn('Department', keys)
    self.assertIn('Project', keys)
    self.assertIn('OwnerEmail', keys)
    owner_email = next((tag['Value'] for tag in tags if tag['Key'] == 'OwnerEmail'), None)
    self.assertEqual(owner_email, email)
