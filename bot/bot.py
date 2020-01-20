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
    def __init__(self, config_path="config.json", section="default", blacklisted_path="blacklisted.db"):
        self.config = Config(config_path, section)

    def main(self):
        reddit = self.authenticate()
        subreddits = reddit.subreddit(self.config.subreddits)
        comment_stream = subreddits.stream.comments(
            pause_after=-1, skip_existing=False)
        inbox_stream = reddit.inbox.stream(pause_after=-1)

        while True:
            self.run_comment_stream(reddit, comment_stream)
            self.run_inbox_stream(reddit, inbox_stream)

    def run_comment_stream(self, reddit, stream):
        for comment in stream:
            if comment is None:
                break
            elif not self.valid_comment(comment):
                continue

            body = comment.body
            comic_ids = self.find_numbers(body)

            for comic_id in comic_ids:
                comic = self.find_comic(comic_id)

                if comic is None:
                    continue

                response = self.format_comment(comic)
                self.reply(comment, response)

    def run_inbox_stream(self, reddit, stream):
        for message in stream:
            if message is None:
                break

            if message.body.lower() == "Ignore Me".lower():
                print(message.author)
                # print("\n")

    # def get_blacklisted(self):
    #     return self.config["blacklisted"]

    # def add_blacklist(self, author):
    #     blacklisted = self.get_blacklisted()
    #     new_blacklisted = blacklisted.append(author)

    # def should_blacklist(self, author, message):
    #     if message.lower() == "Ignore me".lower():
    #         blacklisted = self.get_blacklisted()

    #         if author not in blacklisted:
    #             self.add_blacklist(author)

    # def is_blacklisted(self, username):
    #     with open("config.yaml") as file:
    #         config = yaml.load(file, Loader=yaml.FullLoader)
    #         blacklisted = config[self.section]["blacklisted"] or []
    #         return username in blacklisted

    def authenticate(self):
        reddit = praw.Reddit(username=self.config.username,
                             password=self.config.password,
                             client_id=self.config.client_id,
                             client_secret=self.config.client_secret,
                             user_agent=self.config.user_agent)
        return reddit

    def valid_comment(self, comment):
        username = self.config.username
        author = comment.author
        saved = comment.saved

        if author == username:
            return False
        elif saved:
            return False
        # elif self.is_blacklisted(username):
        #     return False
        else:
            return True

    def find_numbers(self, body):
        numbers = re.findall(r"""(?i)(?x)       # Ignore case, comment mode
                            (?<= ! | \# )       # Must be preceded by an exclamation mark or a pound sign    
                            \d+                 # Matches the following numbers
                            """, body)
        return numbers

    def find_comic(self, number):
        url = f"http://xkcd.com/{number}/info.0.json"
        response = requests.get(url)

        if response.status_code == 404:
            return None
        else:
            config = response.json()
            return config

    def format_comment(self, data):
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
        print(response)
        # comment.reply(response)
        # comment.save()


if __name__ == "__main__":
    bot = Bot()
    bot.main()
