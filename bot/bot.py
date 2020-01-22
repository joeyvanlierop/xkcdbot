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

import os
import re
import praw
import time
import requests
import textwrap
from collections import OrderedDict
from prawcore.exceptions import ServerError
from cfg.config import Config
from db.database import Database


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

    def main(self):
        """
        Starts running the bot.

        Authenticates a new reddit user.
        Cycles between running the comment stream function and the inbox stream function.
        """
        self.authenticate()
        subreddits = self.reddit.subreddit(self.config.subreddits)
        comment_stream = subreddits.stream.comments(
            pause_after=-1, skip_existing=True)
        inbox_stream = self.reddit.inbox.stream(pause_after=-1)

        while True:
                self.run_stream(inbox_stream, self.handle_inbox)
                self.run_stream(comment_stream, self.handle_comment)
                

    def run_stream(self, stream, callback, sleep_time=5, error_sleep_time=30):
        """
        Iterates over a PRAW stream
        Runs the callback with the current item passed as the argument

        The stream should have 'pause_after=-1' so that multiple streams can be iterated
        """
        try:
            for item in stream:
                if item is None:
                    break
                callback(item)
        except ServerError as e:
            print(e)
            time.sleep(error_sleep_time)
        finally:
            time.sleep(sleep_time)

    def authenticate(self):
        """Authenticates a reddit user with the credentials from the configuration file."""
        self.reddit = praw.Reddit(username=self.config.username,
                             password=self.config.password,
                             client_id=self.config.client_id,
                             client_secret=self.config.client_secret,
                             user_agent=self.config.user_agent)

    def handle_comment(self, comment, strict_match=True):
        """Resposible for calling all the functions which analyze and respond to comments in /r/xkcd"""
        if not self.valid_comment(comment):
            return

        comment_id = comment.id
        body = comment.body
        comic_ids = self.find_numbers(body, strict_match)
        responses = []

        for comic_id in comic_ids:
            comic = self.find_comic(comic_id)

            if comic is None:
                continue

            response = self.format_response(comic)
            responses.append(response)
            self.database.add_id(comment_id, comic_id)

        if len(responses) > 0:
            response = self.combine_responses(responses)
            self.reply(comment, response)

    def handle_inbox(self, item):
        """Resposible for calling all the functions which analyze and respond to inbox messages and username mentions."""
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

        if subject == "ignore me" or body == "ignore me":
            self.database.add_blacklist(username)
            message.mark_read()

    def handle_username_mention(self, message):
        """
        Resposible for calling all the functions which analyze and respond to username mentions.
        Calls handle_comment with the strict matching off.
        """
        subject = message.subject.lower()
        comment = self.reddit.comment(message)

        if subject == "username mention":
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
        bot_username = self.config.username
        username = comment.author.name
        saved = comment.saved

        if username == bot_username:
            return False
        elif saved:
            return False
        elif self.database.is_blacklisted(username):
            return False
        else:
            return True

    def find_numbers(self, body, strict_match):
        """
        Finds all numbers that should be analyzed by the bot.
        
        :param
        """
        def strip_leading_zeroes(numbers):
            """Removes all leading zeroes from the numbers in the given list"""
            return [re.sub(r"^0+", "", number) for number in numbers]

        def remove_duplicates(numbers):
            """Removes all duplicate numbers in the given list"""
            unique_numbers = []
            
            for number in numbers:
                if number not in unique_numbers:
                    unique_numbers.append(number)

            return unique_numbers

        if strict_match:
            numbers = re.findall(r"""(?i)(?x)       # Ignore case, comment mode
                                (?<= ! | \# )       # Must be preceded by an exclamation mark or a pound sign    
                                \d+                 # Matches the following numbers
                                """, body)
        else:
            numbers = re.findall(r"""(?i)(?x)       # Ignore case, comment mode   
                                \d+                 # Matches the following numbers
                                """, body)

        stripped_numbers = strip_leading_zeroes(numbers)
        unique_numbers = remove_duplicates(stripped_numbers)
        return unique_numbers

    def find_comic(self, number):
        """
        Finds the json data of the comic with the given number.
        Returns none if there is no comic with the given number.
        """
        url = f"http://xkcd.com/{number}/info.0.json"
        response = requests.get(url)

        if response.status_code == 404:
            return None
        elif response is None:
            return None
        else:
            config = response.json()
            return config

    def format_response(self, data):
        """Formats a comics json data into a detailed response and returns it."""
        title = data["title"]
        alt = data["alt"]
        img = data["img"]
        num = data["num"]
        link = f"http://xkcd.com/{num}"
        mobile = f"http://m.xkcd.com/{num}"
        explain = f"http://www.explainxkcd.com/wiki/index.php/{num}"

        response = f"""
        **[{num}:]({link})** {title}  
        **Alt-text:** >!{alt}!<  
        [Image]({img})  
        [Mobile]({mobile})  
        [Explanation]({explain})  
        """

        return textwrap.dedent(response)

    def combine_responses(self, responses):
        """Combines all the responses into a single response with the closer at the end"""
        newline = "\n"
        closer = textwrap.dedent(f"""
        ---  
        {self.config.closer}
        """)

        responses.append(closer)
        response = newline.join(responses)

        return response

    def reply(self, comment, response):
        """Replies to the given comment with the given response."""
        comment.reply(response)
        comment.save()


if __name__ == "__main__":
    bot = Bot()
    bot.main()
