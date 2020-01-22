import unittest
import datetime
from datetime import datetime
from db.database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.database = Database(":memory:")

    def test_blacklist(self):
        self.database.add_blacklist("username1")
        self.database.add_blacklist("username2")
        self.assertTrue(self.database.is_blacklisted("username1"))
        self.assertTrue(self.database.is_blacklisted("username2"))
        self.assertFalse(self.database.is_blacklisted("username3"))
        self.assertFalse(self.database.is_blacklisted(""))

    def test_statistics(self):
        self.database.add_id("abc", "1")
        self.database.add_id("def", "2")
        self.database.add_id("ghi", "2")
        self.database.add_id("jkl", "3")
        self.database.add_id("mno", "3")
        self.database.add_id("pqr", "3")
        self.database.add_id("stu", "3")
        self.assertEqual(self.database.comic_id_count("0"), 0)
        self.assertEqual(self.database.comic_id_count("1"), 1)
        self.assertEqual(self.database.comic_id_count("2"), 2)
        self.assertEqual(self.database.comic_id_count("3"), 4)
