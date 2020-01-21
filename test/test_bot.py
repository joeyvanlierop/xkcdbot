import unittest
import praw
from bot.bot import Bot


class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot(config_name="test_config.json", section="test")

    def test_find_comic(self):
        self.assertIsNone(self.bot.find_comic(-1))
        self.assertEqual(self.bot.find_comic(327), {"month": "10", "num": 327, "link": "", "year": "2007", "news": "", "safe_title": "Exploits of a Mom",
                                                    "transcript": "[[A woman is talking on the phone, holding a cup]]\nPhone: Hi, this is your son's school. We're having some computer trouble.\nMom: Oh dear\u00e2\u0080\u0094did he break something?\nPhone: In a way\u00e2\u0080\u0094\nPhone: Did you really name your son \"Robert'); DROP TABLE Students;--\" ?\nMom: Oh, yes. Little Bobby Tables, we call him.\nPhone: Well, we've lost this year's student records. I hope you're happy.\nMom: And I hope you've learned to sanitize your database inputs.\n{{title-text: Her daughter is named Help I'm trapped in a driver's license factory.}}", "alt": "Her daughter is named Help I'm trapped in a driver's license factory.", "img": "https://imgs.xkcd.com/comics/exploits_of_a_mom.png", "title": "Exploits of a Mom", "day": "10"})

    def test_find_number_strict(self):
        self.assertEqual(self.bot.find_numbers("Test", True), [])
        self.assertEqual(self.bot.find_numbers("!123.", True), ["123"])
        self.assertEqual(self.bot.find_numbers("7/ !080. !99", True), ["80", "99"])
        self.assertEqual(self.bot.find_numbers("!900 10000", True), ["900"])
        self.assertEqual(self.bot.find_numbers("!Test !001234 5678 !-1", True), ["1234"])

    def test_find_number_non_strict(self):
        self.assertEqual(self.bot.find_numbers("Test", False), [])
        self.assertEqual(self.bot.find_numbers("!123.", False), ["123"])
        self.assertEqual(self.bot.find_numbers("07/ !080. !00099", False), ["7", "80", "99"])
        self.assertEqual(self.bot.find_numbers("!900 010000", False), ["900", "10000"])
        self.assertEqual(self.bot.find_numbers("!Test !1234 5678 !-1", False), ["1234", "5678", "1"])