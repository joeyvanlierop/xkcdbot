import unittest
import textwrap

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
        self.bot = Bot("./cfg/test_config.json", "test", ":memory:")

    def test_get_comic(self):
        self.assertIsNone(self.bot.get_comic(-1))
        self.assertEqual(self.bot.get_comic(327), {"month": "10", "num": 327, "link": "", "year": "2007", "news": "",
                                                   "safe_title": "Exploits of a Mom",
                                                   "transcript": "[[A woman is talking on the phone, holding a cup]]\nPhone: Hi, this is your son's school. We're having some computer trouble.\nMom: Oh dear\u00e2\u0080\u0094did he break something?\nPhone: In a way\u00e2\u0080\u0094\nPhone: Did you really name your son \"Robert'); DROP TABLE Students;--\" ?\nMom: Oh, yes. Little Bobby Tables, we call him.\nPhone: Well, we've lost this year's student records. I hope you're happy.\nMom: And I hope you've learned to sanitize your database inputs.\n{{title-text: Her daughter is named Help I'm trapped in a driver's license factory.}}",
                                                   "alt": "Her daughter is named Help I'm trapped in a driver's license factory.",
                                                   "img": "https://imgs.xkcd.com/comics/exploits_of_a_mom.png",
                                                   "title": "Exploits of a Mom", "day": "10"})

    def test_match_numbers_strict(self):
        self.assertEqual(self.bot.match_numbers("Test", True), [])
        self.assertEqual(self.bot.match_numbers("!123 !123", True), ["123"])
        self.assertEqual(self.bot.match_numbers(
            "7? !080. !99", True), ["80", "99"])
        self.assertEqual(self.bot.match_numbers("!900 10000", True), ["900"])
        self.assertEqual(self.bot.match_numbers(
            "!Test !001234 5678 !-1", True), ["1234"])
        self.assertEqual(
            len(self.bot.match_numbers("!random random", True)), 1)
        self.assertEqual(self.bot.match_numbers(
            "!3 relevant xkcd: 6, !relevant xkcd: 5 1", True), ["3", "6", "5"])
        self.assertEqual(self.bot.match_numbers("!9 !23...25 #9...7", True), [
                         "9", "23", "24", "25", "7", "8"])
        self.assertEqual(self.bot.match_numbers("https://www.google.com/maps/dir/Okay,+Oklahoma,+USA/Whynot,+North+Carolina+27341,+USA/@35.283469,-92.0617932,6z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x87b60bd75e51d2d3:0x120194060a920373!2m2!1d-95.3182985!2d35.8506548!1m5!1m1!1s0x8853609903e1db5b:0x15b011f26e28c49e!2m2!1d-79.7480465!2d35.5402827!3e0", True), [])
        self.assertEqual(self.bot.match_numbers(
            "number is mid!1string", True), [])
        self.assertEqual(self.bot.match_numbers(
            "!12 hello https://www.google.com/!1", True), ["12"])
        self.assertEqual(self.bot.match_numbers("#1mid#6number", True), ["1"])

    def test_find_numbers_non_strict(self):
        self.assertEqual(self.bot.match_numbers("Test", False), [])
        self.assertEqual(self.bot.match_numbers("!123.", False), ["123"])
        self.assertEqual(self.bot.match_numbers(
            "07/ !080. !00099 99 0099", False), ["7", "80", "99"])
        self.assertEqual(self.bot.match_numbers(
            "!900 010000", False), ["900", "10000"])
        self.assertEqual(self.bot.match_numbers(
            "!Test !1234 5678 !-1", False), ["1234", "5678", "1"])
        self.assertEqual(
            len(self.bot.match_numbers("!random random", False)), 2)
        self.assertEqual(self.bot.match_numbers(
            "!3 relevant xkcd: 6, !relevant xkcd: 5 1", False), ["3", "6", "5", "1"])
        self.assertEqual(self.bot.match_numbers("9 23...25 9...7", False), [
                         "9", "23", "25", "7", "24", "8"])

    def test_response_size_limited(self):
        comment = CommentMock()
        too_big_response = ''.join(
            ['1' for _ in range(RESPONSE_CHAR_LIMIT + 1)])
        self.bot.reply(comment=comment, response=too_big_response)
        self.assertEqual(comment.reply_called, 0,
                         f'Expected no reply() call, saw {comment.reply_called}')
        self.assertEqual(comment.save_called, 1,
                         f'Expected 1 save() call, saw {comment.save_called}')

    def test_combine_responses_truncates_response(self):
        # There may be a less fragile way of constructing this test, but this will test the functionality.
        too_many_responses = [f'1' for _ in range(RESPONSE_COUNT_LIMIT + 1)]
        expected_combined_response_length = \
            len('\n'.join(too_many_responses[:RESPONSE_COUNT_LIMIT])) + \
            len(self.bot._closer()) + len('\n')
        actual_combined_response = self.bot.combine_responses(
            responses=too_many_responses)
        self.assertEqual(
            len(actual_combined_response),
            expected_combined_response_length,
            f'Expected response of length {expected_combined_response_length}, found {len(actual_combined_response)}'
        )

    def test_urlescape(self):
        expected = textwrap.dedent("""
        **[859:](http://xkcd.com/859)** (  
        **Alt-text:** >!Brains aside, I wonder how many poorly-written xkcd.com-parsing scripts will break on this title (or ;;"\'\'{<<[\' this mouseover text."!<  
        [Image](https://imgs.xkcd.com/comics/%28.png)  
        [Mobile](http://m.xkcd.com/859)  
        [Explanation](http://www.explainxkcd.com/wiki/index.php/859)  
        """)
        self.assertEqual(self.bot.format_response(
            self.bot.get_comic(859)), expected)

    def test_match_titles(self):
        self.assertEqual(self.bot.match_titles("!6 #irony #36blownApart !1000comics"), [
                         "6", "irony", "36blownApart", "1000comics"])
        self.assertEqual(self.bot.match_titles(
            "#dummy!Title"), ["dummy!Title"])

    def test_get_comic_by_title(self):
        self.bot.database.add_comic_title("irony", 6)
        self.assertEqual(self.bot.get_comic_by_title("IrOnY"), {"month": "1", "num": 6, "link": "", "year": "2006", "news": "", "safe_title": "Irony",
                                                                "transcript": "Narrator: When self-reference, irony, and meta-humor go too far\nNarrator: A CAUTIONARY TALE\nMan 1: This statement wouldn't be funny if not for irony!\nMan 1: ha ha\nMan 2: ha ha, I guess.\nNarrator: 20,000 years later...\n[[desolate badlands landscape with an imposing sun in the sky]]\n{{It's commonly known that too much perspective can be a downer.}}", "alt": "It's commonly known that too much perspective can be a downer.", "img": "https://imgs.xkcd.com/comics/irony_color.jpg", "title": "Irony", "day": "1"})
        self.assertIsNone(self.bot.get_comic_by_title("dummy"))
