import os
import json
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Config():
    def __init__(self, config_path, config_section):
        config_path = os.path.abspath(config_path)

        with open(config_path, "r") as infile:
            logger.info(f"Loading config from: {config_path}")
            config = json.load(infile)[config_section] or {}
            self.username = config["username"]
            self.password = config["password"]
            self.client_id = config["client_id"]
            self.client_secret = config["client_secret"]
            self.user_agent = config["user_agent"]
            self.subreddits = "+".join(config["subreddits"])
            self.closer = "^" + \
                " | ".join(config["footers"]).replace(" ", "&nbsp;")
            logger.info(f"Loaded config for user: {self.username}")
