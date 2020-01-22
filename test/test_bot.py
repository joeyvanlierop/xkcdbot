import unittest
import praw
from bot.bot import Bot, RESPONSE_CHAR_LIMIT, RESPONSE_COUNT_LIMIT


class CommentMock:
    def __init__(self):
        self.reply_called = 0
        self.save_called = 0

    def reply(self, response):
        self.reply_called += 1

    def save(self):
        self.save_called += 1


class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot(config_name="test_config.json", section="test")

    def test_find_comic(self):
        self.assertIsNone(self.bot.find_comic(-1))
        self.assertEqual(self.bot.find_comic(327), {"month": "10", "num": 327, "link": "", "year": "2007", "news": "", "safe_title": "Exploits of a Mom",
                                                    "transcript": "[[A woman is talking on the phone, holding a cup]]\nPhone: Hi, this is your son's school. We're having some computer trouble.\nMom: Oh dear\u00e2\u0080\u0094did he break something?\nPhone: In a way\u00e2\u0080\u0094\nPhone: Did you really name your son \"Robert'); DROP TABLE Students;--\" ?\nMom: Oh, yes. Little Bobby Tables, we call him.\nPhone: Well, we've lost this year's student records. I hope you're happy.\nMom: And I hope you've learned to sanitize your database inputs.\n{{title-text: Her daughter is named Help I'm trapped in a driver's license factory.}}", "alt": "Her daughter is named Help I'm trapped in a driver's license factory.", "img": "https://imgs.xkcd.com/comics/exploits_of_a_mom.png", "title": "Exploits of a Mom", "day": "10"})

    def test_find_number_strict(self):
        self.assertEqual(self.bot.find_numbers("Test", True), [])
        self.assertEqual(self.bot.find_numbers("!123 !123", True), ["123"])
        self.assertEqual(self.bot.find_numbers("7? !080. !99", True), ["80", "99"])
        self.assertEqual(self.bot.find_numbers("!900 10000", True), ["900"])
        self.assertEqual(self.bot.find_numbers("!Test !001234 5678 !-1", True), ["1234"])

    def test_find_number_non_strict(self):
        self.assertEqual(self.bot.find_numbers("Test", False), [])
        self.assertEqual(self.bot.find_numbers("!123.", False), ["123"])
        self.assertEqual(self.bot.find_numbers("07/ !080. !00099 99 0099", False), ["7", "80", "99"])
        self.assertEqual(self.bot.find_numbers("!900 010000", False), ["900", "10000"])
        self.assertEqual(self.bot.find_numbers("!Test !1234 5678 !-1", False), ["1234", "5678", "1"])

    def test_response_size_limited(self):
        comment = CommentMock()
        too_big_response = ''.join(['1' for _ in range(RESPONSE_CHAR_LIMIT + 1)])
        self.bot.reply(comment=comment, response=too_big_response)
        self.assertEqual(comment.reply_called, 0, f'Expected no reply() call, saw {comment.reply_called}')
        self.assertEqual(comment.save_called, 1, f'Expected 1 save() call, saw {comment.save_called}')

    def test_combine_responses_truncates_response(self):
        # There may be a less fragile way of constructing this test, but this will test the
        # functionality.
        too_many_responses = [f'1' for _ in range(RESPONSE_COUNT_LIMIT + 1)]
        expected_combined_response_length = \
            len('\n'.join(too_many_responses[:RESPONSE_COUNT_LIMIT])) + \
            len(self.bot._closer()) + len('\n')
        actual_combined_response = self.bot.combine_responses(responses=too_many_responses)
        self.assertEqual(
            len(actual_combined_response),
            expected_combined_response_length,
            f'Expected response of length {expected_combined_response_length}, found {len(actual_combined_response)}'
        )
