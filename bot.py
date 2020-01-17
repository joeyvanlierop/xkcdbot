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
import praw
import json
import requests
import inspect
import yaml


class Bot():
    def __init__(self, path="config.yaml", section="default"):
        with open(path) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

            self.username = config[section]["username"]
            self.password = config[section]["password"]
            self.client_id = config[section]["client_id"]
            self.client_secret = config[section]["client_secret"]
            self.user_agent = config[section]["user_agent"]
            self.section = section
            self.subreddits = "+".join(config[section]["subreddits"])
            self.closer = "^" + \
                " | ".join(config[section]["footers"]).replace(" ", "&nbsp;")

    #
    def main(self):
        reddit = self.authenticate()
        subreddits = reddit.subreddit(self.subreddits)

        for comment_id in subreddits.stream.comments():
            comment = reddit.comment(comment_id)

            if not self.valid_comment(comment):
                continue

            body = comment.body
            comic_ids = self.find_numbers(body)

            for comic_id in comic_ids:
                comic = self.find_comic(comic_id)
                response = self.format_comment(comic)
                self.reply(comment, response)

    def authenticate(self):
        reddit = praw.Reddit(username=self.username,
                             password=self.password,
                             client_id=self.client_id,
                             client_secret=self.client_secret,
                             user_agent=self.user_agent)
        return reddit

    def valid_comment(self, comment):
        username = self.username
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

    def is_blacklisted(self, username):
        with open("config.yaml") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
            blacklisted = config[self.section]["blacklisted"] or []
            return username in blacklisted

    def find_numbers(self, body):
        # numbers = re.findall("\d+(?=\W)", body)
        numbers = [20]
        return numbers

    def find_comic(self, number):
        url = f"http://xkcd.com/{number}/info.0.json"
        response = requests.get(url)

        if response.status_code == 404:
            return None
        else:
            config = response.json()
            return config

    def format_comment(self, config):
        title = config["title"]
        alt = config["alt"]
        img = config["img"]
        num = config["num"]
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

        {self.closer}
        """

        return inspect.cleandoc(response)

    def reply(self, comment, response):
        comment.reply(response)
        comment.save()


if __name__ == "__main__":
    bot = Bot()
    bot.main()
