import re
import praw
import json
import requests
import inspect

reddit = praw.Reddit()

def find_numbers(s):
    nums = re.findall("\d+", s)
    return nums

def find_comic(n):
    url = f"http://xkcd.com/{n}/info.0.json"
    response = requests.get(url)
    
    if response.status_code == 404:
        return None
    else:
        data = response.json()
        return data

def format_data(data):
    title = data["title"]
    alt = data["alt"]
    img = data["img"]
    num = data["num"]
    link = f"http://xkcd.com/{num}"
    mobile = f"http://m.xkcd.com/{num}"
    explain = f"http://www.explainxkcd.com/wiki/index.php/{num}"

    comment = f"""
    **[{num}:]({link})** {title}  
 
    **Alt-text:** {alt}  

    [Image]({img})  

    [Mobile]({mobile})

    [Explanation]({explain})

    ---

    ^[xkcd.com](https://www.xkcd.com) ^| ^[Feedback?](https://reddit.com/message/compose/?to=banana_shavings&subject=BobbyTablesBot) ^| ^[Stop Replying](https://reddit.com/message/compose/?to=BobbyTablesBot&subject=Ignore%20Me)
    """

    return inspect.cleandoc(comment)


for comment_id in reddit.subreddit('xkcd').stream.comments():
    comment = praw.models.Comment(reddit=reddit, id=comment_id)
    body = comment.body
    
    comic_ids = find_numbers(body)

    for comic_id in comic_ids:
        comic = find_comic(comic_id)
        comment = format_data(comic)
        print(comment)

    print("\n")