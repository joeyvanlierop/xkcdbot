import unittest
import praw
from db.database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.database = Database(database_name=":memory:")

    def test_blacklist(self):
        self.database.add_blacklist("username1")
        self.database.add_blacklist("username2")
        self.assertTrue(self.database.is_blacklisted("username1"))
        self.assertTrue(self.database.is_blacklisted("username2"))
        self.assertFalse(self.database.is_blacklisted("username3"))
        self.assertFalse(self.database.is_blacklisted(""))

    def test_id_statistics(self):
        self.database.increment_id("1")
        self.database.increment_id("2")
        self.database.increment_id("2")
        self.database.increment_id("3")
        self.database.increment_id("3")
        self.database.increment_id("3")
        self.assertIsNone(self.database.get_id_statistics("0"))
        self.assertEqual(self.database.get_id_statistics("1")[0], 1)
        self.assertEqual(self.database.get_id_statistics("2")[0], 2)
        self.assertEqual(self.database.get_id_statistics("3")[0], 3)
