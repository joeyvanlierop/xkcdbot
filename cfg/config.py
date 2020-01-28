import os
import json
import logging

logger = logging.getLogger(__name__)


class Config():
    def __init__(self, config_name, config_section):
        dirname  = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(dirname, config_name)

        with open(config_path, "r") as infile:
            logger.debug(f"Generating config")
            config = json.load(infile)[config_section] or {}
            self.username = config["username"]
            self.password = config["password"]
            self.client_id = config["client_id"]
            self.client_secret = config["client_secret"]
            self.user_agent = config["user_agent"]
            self.subreddits = "+".join(config["subreddits"])
            self.closer = "^" + \
                " | ".join(config["footers"]).replace(" ", "&nbsp;")
            logger.debug(f"Generated config for user: {self.username}")
