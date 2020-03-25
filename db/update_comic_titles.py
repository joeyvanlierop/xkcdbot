#!/usr/bin/env python3

import requests
import logging
from time import sleep
from db.database import Database

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

database = Database("database.db")

def update():
    """Updates database with new comics."""
    
    def format_comic_title(comic_title):
        """Removes spaces, converts to lower case and returns given comic title."""
        
        comic_title = comic_title.replace(" ", "")
        comic_title = comic_title.lower()
        return comic_title
        
    comic_num = database.comic_title_relations_count()

    logger.info("Updating comic titles in database...")
    while True:
        comic_num += 1

        if comic_num == 404:
            # not needed but is convenient because it keeps the count of
            # table entries consistent when initializing comic_num
            database.add_comic_title('', 404)
            continue

        url = f"http://xkcd.com/{comic_num}/info.0.json"
        response = requests.get(url)

        if response.status_code == 404:
            logger.info(f"Comic {comic_num} returned a 404 status code")
            return
        elif response is None:
            logger.info(f"Comic {comic_num} returned none")
            continue
        else:
            config = response.json()
            comic_title = format_comic_title(config["safe_title"])
            logger.info(f"Adding new comic {comic_title} : {comic_num} to database")
            database.add_comic_title(comic_title, comic_num)

if __name__ == "__main__":
    while True:
        update()
        sleep(86400)
