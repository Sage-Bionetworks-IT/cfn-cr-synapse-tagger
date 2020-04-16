import unittest

import requests
import requests_mock

from set_bucket_tags import app


class TestGetSynapseEmail(unittest.TestCase):

  def test_valid_id(self):
    with requests_mock.Mocker() as mocker:
      valid_id = '3388489'
      url = f'https://repo-prod.prod.sagebase.org/repo/v1/userProfile/{valid_id}'
      mocker.get(
        url,
        status_code=200,
        text='{"ownerId":"3388489","firstName":"Jane","lastName":"Doe","userName":"janedoe","summary":"","position":"Researcher","location":"Seattle, Washington, USA","industry":"","company":"Sage Bionetworks","url":"","createdOn":"2019-04-16T19:08:04.000Z"}')
      result = app.get_synapse_email(valid_id)
      self.assertEqual(result, 'janedoe@synapse.org')


  def test_valid_not_found_id(self):
    with requests_mock.Mocker() as mocker, self.assertRaises(requests.exceptions.HTTPError):
      valid_id = '0123456'
      url = f'https://repo-prod.prod.sagebase.org/repo/v1/userProfile/{valid_id}'
      mocker.get(url, status_code=404, text='{"reason":"UserProfile cannot be found for: 0123456"}')
      app.get_synapse_email(valid_id)
