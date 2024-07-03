import unittest

from set_tags import utils


class TestMergeTags(unittest.TestCase):

  def test_happy_case(self):
    tags = []
    result = utils.merge_tags([{'Key':'foo','Value':'bar'}],[{'Key':'foo2','Value':'bar2'}])
    self.assertEqual(result, [{'Key':'foo','Value':'bar'},{'Key':'foo2','Value':'bar2'}])

  def test_collision(self):
    tags = []
    result = utils.merge_tags([{'Key':'foo','Value':'bar'}],[{'Key':'foo','Value':'bar2'}])
    self.assertEqual(result, [{'Key':'foo','Value':'bar2'}])


