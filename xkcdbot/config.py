import os
import json

class Config():
    def __init__(self, filename, section):
        package_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(package_dir, filename)

        with open(filename, "r") as infile:
            config = json.load(infile)[section] or {}
            self.username = config["username"]
            self.password = config["password"]
            self.client_id = config["client_id"]
            self.client_secret = config["client_secret"]
            self.user_agent = config["user_agent"]
            self.subreddits = "+".join(config["subreddits"])
            self.closer = "^" + \
                " | ".join(config["footers"]).replace(" ", "&nbsp;")