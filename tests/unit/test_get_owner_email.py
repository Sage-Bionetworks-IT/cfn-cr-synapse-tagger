import unittest

import requests
import requests_mock

from set_bucket_tags import app


class TestHandler(unittest.TestCase):


  def test_valid_synapse_id(self):
    valid_id = '3388489'
    with requests_mock.Mocker() as mocker:
      url = f'https://repo-prod.prod.sagebase.org/repo/v1/userProfile/{valid_id}'
      mocker.get(
        url,
        status_code=200,
        text='{"ownerId":"3388489","firstName":"Jane","lastName":"Doe","userName":"janedoe","summary":"","position":"Researcher","location":"Seattle, Washington, USA","industry":"","company":"Sage Bionetworks","url":"","createdOn":"2019-04-16T19:08:04.000Z"}')
      result = app.get_owner_email(valid_id)
    self.assertEqual(result, 'janedoe@synapse.org')


  def test_valid_sagebase_email(self):
    valid_id = 'jane.doe@sagebase.org'
    result = app.get_owner_email(valid_id)
    self.assertEqual(result, valid_id)


  def test_invalid_string(self):
    with self.assertRaises(ValueError):
      invalid_id = 'foobar'
      result = app.get_owner_email(invalid_id)
