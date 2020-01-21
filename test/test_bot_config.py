import unittest
import praw
from cfg.config import Config


class TestBotConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config(config_name="test_config.json", section="test")

    def test_constructor(self):
        self.assertEqual(self.config.username, "username")
        self.assertEqual(self.config.password, "password")
        self.assertEqual(self.config.client_id, "client_id")
        self.assertEqual(self.config.client_secret, "client_secret")
        self.assertEqual(self.config.user_agent, "user_agent")
        self.assertEqual(self.config.subreddits, "subreddit1+subreddit2+subreddit3")
        self.assertEqual(self.config.closer, "^footer1&nbsp;|&nbsp;footer2&nbsp;|&nbsp;footer3")