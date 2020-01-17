"""
/u/BobbyTableBot

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
import config


def authenticate(section="DEFAULT"):
    username = config.username
    password = config.password
    client_id = config.client_id
    client_secret = config.client_secret
    user_agent = config.user_agent

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         username=username,
                         password=password,
                         user_agent=user_agent)

    return reddit

def valid_comment(comment):
    username = config.username
    author = comment.author
    saved = comment.saved

    if author == username:
        return False
    elif saved:
        return False
    # elif(user is blacklisted)
    #   TODO
    else:
        return True


def find_numbers(body):
    numbers = re.findall("\d+", body)
    return numbers


def find_comic(number):
    url = f"http://xkcd.com/{number}/info.0.json"
    response = requests.get(url)

    if response.status_code == 404:
        return None
    else:
        data = response.json()
        return data


def format_comment(data):
    title = data["title"]
    alt = data["alt"]
    img = data["img"]
    num = data["num"]
    link = f"http://xkcd.com/{num}"
    mobile = f"http://m.xkcd.com/{num}"
    explain = f"http://www.explainxkcd.com/wiki/index.php/{num}"
    closer = config.closer

    response = f"""
    **[{num}:]({link})** {title}  

    **Alt-text:** {alt}  

    [Image]({img})  

    [Mobile]({mobile})

    [Explanation]({explain})

    ---

    {closer}
    """

    return inspect.cleandoc(response)

def reply(comment, response):
    comment.reply(response)
    comment.save()


if __name__ == "__main__":
    reddit = authenticate()

    for comment_id in reddit.subreddit('xkcd').stream.comments():
        comment = reddit.comment(comment_id)

        if not valid_comment(comment):
            continue

        body = comment.body
        comic_ids = find_numbers(body)

        for comic_id in comic_ids:
            comic = find_comic(comic_id)
            response = format_comment(comic)
            reply(comment, response)
