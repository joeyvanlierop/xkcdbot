import unittest
import praw
from bot.bot import Bot


class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot(config_path="test_config.json", section="test")

    def test_find_comic(self):
        self.assertIsNone(self.bot.find_comic(-1))
        self.assertEqual(self.bot.find_comic(327), {"month": "10", "num": 327, "link": "", "year": "2007", "news": "", "safe_title": "Exploits of a Mom",
                                                    "transcript": "[[A woman is talking on the phone, holding a cup]]\nPhone: Hi, this is your son's school. We're having some computer trouble.\nMom: Oh dear\u00e2\u0080\u0094did he break something?\nPhone: In a way\u00e2\u0080\u0094\nPhone: Did you really name your son \"Robert'); DROP TABLE Students;--\" ?\nMom: Oh, yes. Little Bobby Tables, we call him.\nPhone: Well, we've lost this year's student records. I hope you're happy.\nMom: And I hope you've learned to sanitize your database inputs.\n{{title-text: Her daughter is named Help I'm trapped in a driver's license factory.}}", "alt": "Her daughter is named Help I'm trapped in a driver's license factory.", "img": "https://imgs.xkcd.com/comics/exploits_of_a_mom.png", "title": "Exploits of a Mom", "day": "10"})

    def test_find_number(self):
        self.assertEqual(self.bot.find_numbers("Test"), [])
        self.assertEqual(self.bot.find_numbers("!123."), ["123"])
        self.assertEqual(self.bot.find_numbers("7/ !80. !99"), ["80", "99"])
        self.assertEqual(self.bot.find_numbers("!900 10000"), ["900"])
        self.assertEqual(self.bot.find_numbers("!Test !1234 5678 !-1"), ["1234"])