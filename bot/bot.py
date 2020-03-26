"""
/u/BobbyTablesBot

A reddit bot for /r/xkcd made by /u/banana_shavings

General workflow:
* Login
* Open comment stream
* Analyze comments for numbers
* Validate that number is an existing xkcd comic
* Form comment
* Reply
"""

import re
import time
import logging
import textwrap
import praw
import requests
import urllib.parse
from random import randrange
from prawcore.exceptions import ServerError

from cfg.config import Config
from db.database import Database

RESPONSE_COUNT_LIMIT: int = 10
RESPONSE_CHAR_LIMIT: int = 10_000

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot():
    """
    Class that contains the methods for running the bot.

    Constructor arguments:
    :param config_path: Path to the config file within the cfg folder.
    :param config_section: config_section within the config file which hold the settings for the bot.
    :param database_path: Path to the database file within the db folder.
    """

    def __init__(self, config_name="config.json", config_section="default", database_name="database.db"):
        self.config = Config(config_name, config_section)
        self.database = Database(database_name)

    def main(self, error_sleep_time=15):
        """
        Starts running the bot.

        Authenticates a new reddit user.
        Cycles between running the comment stream function and the inbox stream function.
        """
        self.authenticate()
        subreddits = self.reddit.subreddit(self.config.subreddits)
        while True:
            comment_stream = subreddits.stream.comments(
                pause_after=-1, skip_existing=False)
            inbox_stream = self.reddit.inbox.stream(pause_after=-1)
            try:
                while True:
                    self.run_stream(inbox_stream, self.handle_inbox)
                    self.run_stream(comment_stream, self.handle_comment)
            except Exception as e:
                logger.error(e)
                time.sleep(error_sleep_time)

    def run_stream(self, stream, callback, sleep_time=5):
        """
        Iterates over a PRAW stream
        Runs the callback with the current item passed as the argument

        The stream should have 'pause_after=-1' so that multiple streams can be iterated
        """
        for item in stream:
            if item is None:
                break
            try:
                callback(item)
            except Exception as e:
                logger.error(f"Caught exception '{e}' while handling message item!")
            
        time.sleep(sleep_time)

    def authenticate(self):
        """Authenticates a reddit user with the credentials from the configuration file."""
        logger.info(f"Authenticating user: {self.config.username}")
        self.reddit = praw.Reddit(username=self.config.username,
                                  password=self.config.password,
                                  client_id=self.config.client_id,
                                  client_secret=self.config.client_secret,
                                  user_agent=self.config.user_agent)

    def handle_comment(self, comment, strict_match=True):
        """
        Resposible for calling all the functions which analyze and respond to comments in /r/xkcd

        :param strict_match: Passed as an argument to the match_numbers method
        """
        if not self.valid_comment(comment):
            return

        comment_id = comment.id
        body = comment.body
        comic_ids = self.match_numbers(body, strict_match)
        responses = []

        for comic_id in comic_ids:
            if len(responses) > RESPONSE_COUNT_LIMIT:
                logger.warning(
                    f"Exceeded the reponse count limit of {RESPONSE_COUNT_LIMIT} responses")
                break

            comic = self.get_comic(comic_id)

            if comic is None:
                continue

            response = self.format_response(comic)
            responses.append(response)
            self.database.add_id(comment_id, comic["num"])

        if len(responses) > 0:
            response = self.combine_responses(responses)
            self.reply(comment, response)

    def handle_inbox(self, item):
        """Resposible for calling all the functions which analyze and respond to inbox messages and username mentions."""
        logger.info("Received inbox item")

        # Private Message
        if isinstance(item, praw.models.Message):
            self.handle_private_message(item)

        # Username Mention
        if isinstance(item, praw.models.Comment):
            self.handle_username_mention(item)

    def handle_private_message(self, message):
        """
        Resposible for calling all the functions which analyze and respond to private messages.
        Adds a user to the blacklisted users database if the private message subject or is 'ignore me' (case-insensitive).
        """
        subject = message.subject.lower()
        body = message.body.lower()
        username = message.author.name
        logger.info(
            f"Received private message\nSubject: {subject}\nBody: {body}")

        if subject == "ignore me" or body == "ignore me":
            logger.info(f"{username} has requested to be blacklisted")
            self.database.add_blacklist(username)
            message.mark_read()

    def handle_username_mention(self, message):
        """
        Resposible for calling all the functions which analyze and respond to username mentions.
        Calls handle_comment with the strict matching off.
        """
        subject = message.subject.lower()
        body = message.body.lower()
        username = self.config.username.lower()
        comment = self.reddit.comment(message)

        if subject == "username mention" or username in body:
            logger.info(f"Received username mention\nBody: {body}")
            self.handle_comment(comment, False)
            message.mark_read()

    def valid_comment(self, comment):
        """
        Determines if a comment is valid.

        An valid comment is one that is not:
         - A comment posted by this bot.
         - A comment posted by a blacklisted user.
         - A comment that is saved.
        """
        if comment.author is None:
            return False

        bot_username = self.config.username
        username = comment.author.name
        saved = comment.saved

        if username == bot_username:
            logger.info(f"Found comment from bot: {comment}")
            return False
        elif saved:
            logger.info(f"Found previously saved comment: {comment}")
            return False
        elif self.database.is_blacklisted(username):
            logger.info(f"Found comment from blacklisted user: {username}")
            return False
        else:
            logger.info(f"Found valid comment: {comment}")
            return True

    def match_token(self, token, body, strict_match):
        """
        Matches all tokens that should be analyzed by the bot.

        :param strict_match: Decides whether to use strict matching or not
         - If using strict matching, all tokens must be preceded by an exclamation mark or a pound sign
         - If using non-strict matching, all tokens are valid
        """
        if strict_match:
            matches = re.findall(r"""(?i)(?x)       # Ignore case, comment mode
                                (?<= ! | \# )       # Must be preceded by an exclamation mark or a pound sign    
                                {}                  # Matches the following token
                                """.format(token), body)
            matches.extend(re.findall(r"""(?i)(?x)
                                (?<= relevant[ ]xkcd:[ ])
                                {}
                                """.format(token), body))
        else:
            matches = re.findall(r"""(?i)(?x)       # Ignore case, comment mode
                                {}                  # Matches the following token
                                """.format(token),  body)
        return matches

    def match_numbers(self, body, strict_match):
        """
        Matches all numbers (including !latest) that should be analyzed by the bot.

        :param strict_match: Decides whether to use strict matching or not
         - If using strict matching, all numbers must be preceded by an exclamation mark or a pound sign
         - If using non-strict matching, all numbers are valid
        """

        def strip_leading_zeroes(numbers):
            """Removes all leading zeroes from the numbers in the given list"""
            return [re.sub(r"^0+", "", number) for number in numbers]

        def remove_duplicates(numbers):
            """Removes all duplicate numbers in the given list"""
            unique_numbers = []
            seen = set()
            for num in numbers:
                if num not in seen:
                    unique_numbers.append(num)
                    seen.add(num)
            return unique_numbers

        def get_range_numbers(body, strict_match):
            """Matches all comic id ranges and returns a list of all the numbers in those ranges."""
            ranges = self.match_token(r"\d+\.{3}\d+", body, strict_match)

            ret = []
            for range_ in ranges:
                nums = re.findall(r"\d+", range_)

                if nums[0] >= nums[1]:
                    lo = nums[1]
                    hi = nums[0]
                else:
                    lo = nums[0]
                    hi = nums[1]

                lo = int(lo)
                hi = int(hi)

                for i in range(lo, hi+1):
                    ret.append(str(i))
            
            return ret

        numbers = self.match_token(r"\d+", body, strict_match)
        numbers.extend(get_range_numbers(body, strict_match))
        stripped_numbers = strip_leading_zeroes(numbers)

        if self.match_latest(body, strict_match):
            stripped_numbers.append(self.get_latest_comic())
        rand = self.match_random(body, strict_match)

        if rand:
            stripped_numbers.extend(rand)

        unique_numbers = remove_duplicates(stripped_numbers)
        return unique_numbers

    def match_latest(self, body, strict_match):
        """
        Matches 'latest' in the body and returns True if it is.

        :param strict_match: Using the same rules as match_numbers
        """
        latest = self.match_token('latest', body, strict_match)
        return bool(latest)

    def match_random(self, body, strict_match):
        """
        Matches 'random' in the body and returns a list of random comic indices

        :param strict_match: Using the same rules as match_numbers
        """
        random = self.match_token('random', body, strict_match)

        if not random:
            return None

        latest = self.get_latest_comic()
        res = []
        for _ in range(len(random)):
            res.append(randrange(1, latest))
        return res

    def get_comic(self, number):
        """
        Gets the JSON data of the comic with the given number.
        Returns none if there is no comic with the given number.
        """
        url = f"http://xkcd.com/{number}/info.0.json"
        response = requests.get(url)

        if number == "404":
            logger.info("Got comic with number 404")
            return {"title": "Not Found",
                    "alt": "&nbsp;",
                    "img": "https://www.explainxkcd.com/wiki/images/9/92/not_found.png",
                    "num": 404}
        elif response.status_code == 404:
            logger.warning(f"Comic {number} returned a 404 status code")
            return None
        elif response is None:
            logger.warning(f"Comic {number} returned none")
            return None
        else:
            logger.info(f"Got comic with number {number}")
            config = response.json()
            return config

    def get_latest_comic(self):
        """
        Returns the ID of the latest comic.
        """
        url = f"http://xkcd.com/info.0.json"
        response = requests.get(url)
        if response.status_code == 404:
            logger.warning(f"Latest comic returned a 404 status code")
            return None
        elif response is None:
            logger.warning(f"Latest comic returned none")
            return None
        else:
            logger.info(f"Got latest comic")
            config = response.json()
            return config["num"]

    def format_response(self, data):
        """Formats a comics json data into a detailed response and returns it."""
        title = data["title"]
        # Zero width space doesn't end the spoiler
        alt = data["alt"].replace("!<", "!\u200b<")
        # These will not break a markdown link
        img = urllib.parse.quote(data["img"], safe="/:")
        num = data["num"]
        link = f"http://xkcd.com/{num}"
        mobile = f"http://m.xkcd.com/{num}"
        explain = f"http://www.explainxkcd.com/wiki/index.php/{num}"
        comic_count = self.database.comic_id_count(num)
        total_count = self.database.total_reference_count()
        logger.info(f"Formatting response for comic: {num}")

        response = textwrap.dedent(f"""  
        **[{num}:]({link})** {title}  
        **Alt-text:** >!{alt}!<  
        [Image]({img})  
        [Mobile]({mobile})  
        [Explanation]({explain})  
        """)

        if comic_count > 0 and total_count > 0:
            percentage = comic_count / total_count * 100
            response_statistics = f"\n\tThis comic has been referenced {comic_count} time{'s' if comic_count > 1 else ''}, representing {percentage:.2f}% of all references."
            response += response_statistics

        return response

    def combine_responses(self, responses):
        """Combines all the responses into a single response with the closer at the end"""
        logger.info(f"Combining {len(responses)} responses")
        newline = "\n"
        closer = self._closer()

        # In case the method was called with more responses than the bot is configured to submit,
        # truncate this list.
        responses = responses[:RESPONSE_COUNT_LIMIT]

        responses.append(closer)
        response = newline.join(responses)

        return response

    def _closer(self):
        return textwrap.dedent(f"""
        ---  
        {self.config.closer}
        """)

    def reply(self, comment, response):
        """Replies to the given comment with the given response."""
        if len(response) >= RESPONSE_CHAR_LIMIT:
            logger.warning(f'Comment size {len(response)} exceeded {RESPONSE_CHAR_LIMIT} response char limit, '
                           f'saving and skipping.')
            comment.save()
            return

        logger.info(f"Saving and replying to {comment}")
        comment.reply(response)
        comment.save()


if __name__ == "__main__":
    bot = Bot()
    bot.main()
