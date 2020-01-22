"""
Temporary class for repopulating the statistics class with the new data
Will be deleted shortly
This script is garbage and no one should ever look at it
"""

import re
import praw
from datetime import datetime
from bot.bot import Bot
from cfg.config import Config
from db.database import Database

database_name = "populated_database.db"
database = Database(database_name)
config_name = "config.json"
config_section = "default"
config = Config(config_name, config_section)
reddit = praw.Reddit(username=config.username,
                     password=config.password,
                     client_id=config.client_id,
                     client_secret=config.client_secret,
                     user_agent=config.user_agent)

redditor = reddit.redditor(config.username)
comments = redditor.comments.new(limit=None)
oldest = []

for comment in comments:
    oldest.append(comment)

oldest.reverse()

for comment in oldest:
    comment_id = comment.id
    comic_ids = re.findall(r"(?<=\[)\d+", comment.body)
    created = datetime.fromtimestamp(comment.created)

    for comic_id in comic_ids:
        database.add_id(comment_id, comic_id, created)
