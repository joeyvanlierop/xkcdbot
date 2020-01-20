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
import requests
import inspect
from cfg.config import Config


class Bot():
    """
    Class that contains the methods for running the bot.

    Constructor arguments:
    :param config_path: Path to the config file within the cfg folder.
    :param section: Section within the config file which hold the settings for the bot.
    :param backlisted_path: Path to the database which holds the blacklisted users.
    """

    def __init__(self, config_path="config.json", section="default", blacklisted_path="blacklisted.db"):
        self.config = Config(config_path, section)

    def main(self):
        """
        Starts running the bot.

        Authenticates a new reddit user.
        Cycles between running the comment stream function and the inbox stream function.
        """
        self.reddit = self.authenticate()

        subreddits = self.reddit.subreddit(self.config.subreddits)
        comment_stream = subreddits.stream.comments(
            pause_after=-1, skip_existing=True)
        inbox_stream = self.reddit.inbox.stream(pause_after=-1)

        while True:
            self.run_stream(inbox_stream, self.handle_inbox)
            self.run_stream(comment_stream, self.handle_comment)

    def run_stream(self, stream, callback):
        """
        Iterates over a PRAW stream
        Runs the callback with the current item passed as the argument

        The stream should have 'pause_after=-1' so that multiple streams can be iterated
        """
        for item in stream:
            print(callback)
            if item is None:
                break
            callback(item)

    def authenticate(self):
        """Returns a new authenticated reddit user with the credentials from the configuration file."""
        reddit = praw.Reddit(username=self.config.username,
                             password=self.config.password,
                             client_id=self.config.client_id,
                             client_secret=self.config.client_secret,
                             user_agent=self.config.user_agent)
        return reddit

    def handle_comment(self, comment, strict_match=True):
        """Resposible for calling all the functions which analyze and respond to comments in /r/xkcd"""
        if not self.valid_comment(comment):
            return

        body = comment.body
        comic_ids = self.find_numbers(body)

        for comic_id in comic_ids:
            comic = self.find_comic(comic_id)

            if comic is None:
                continue

            response = self.format_comment(comic)
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
        Adds a user to the blacklisted users database if the private message subject is 'ignore me'.
        """
        subject = message.subject.lower()
        author = message.author()

        if subject == "ignore me":
            self.add_blacklist(author)

    def handle_username_mention(self, comment):
        """
        Resposible for calling all the functions which analyze and respond to username mentions.
        Calls handle_comment with the strict matching off.
        """
        subject = comment.subject.lower()
        comment = self.reddit.comment(comment)

        if subject == "username mention":
            self.handle_comment(comment, strict_match=False)

    def add_blacklist(self, username):
        """
        Adds a user to the blacklisted user database
        Will not add if the user is already present in the database
        """
        if not self.is_blacklisted(username):
            # TODO
            return False

    def is_blacklisted(self, username):
        """Returns true if the given username exists in the blacklisted user database"""
        # TODO
        return False

    def valid_comment(self, comment):
        """
        Determines if a comment is valid.

        An valid comment is one that is not:
         - A comment posted by this bot.
         - A comment posted by a blacklisted user.
         - A comment that is saved.
        """
        print(type(comment))
        username = self.config.username
        author = comment.author
        saved = comment.saved

        if author == username:
            return False
        elif saved:
            return False
        elif self.is_blacklisted(username):
            return False
        else:
            return True

    def find_numbers(self, body):
        """Finds all numbers that should be analyzed by the bot."""
        numbers = re.findall(r"""(?i)(?x)       # Ignore case, comment mode
                            (?<= ! | \# )       # Must be preceded by an exclamation mark or a pound sign    
                            \d+                 # Matches the following numbers
                            """, body)
        return numbers

    def find_comic(self, number):
        """
        Finds the json data of the comic with the given number.
        Returns none if there is no comic with the given number.
        """
        url = f"http://xkcd.com/{number}/info.0.json"
        response = requests.get(url)

        if response.status_code == 404:
            return None
        else:
            config = response.json()
            return config

    def format_comment(self, data):
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

        **Alt-text:** {alt}  

        [Image]({img})  

        [Mobile]({mobile})

        [Explanation]({explain})

        ---

        {self.config.closer}
        """

        return inspect.cleandoc(response)

    def reply(self, comment, response):
        """Replies to the given comment with the given response."""
        print(response)
        # comment.reply(response)
        # comment.save()


if __name__ == "__main__":
    bot = Bot()
    bot.main()
