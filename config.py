from dataIO import fileIO
import os

false_strings = ["false", "False", "f", "F", "0", ""]

if fileIO("config.json", "check"):
    config = fileIO("config.json", "load")
else:
    config = {
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
        "user_agent": os.environ["USER_AGENT"],
        "instances": [
            {
                "subreddits": os.environ["SUBREDDITS"].replace(" ", "").split(","),
                "users": os.environ.get("USERS", "").lower().replace(" ", "").split(","),  # optional
                "keywords": os.environ.get("KEYWORDS", "").lower().replace(" ", "").split(","),  # optional
                "webhook_url": os.environ["WEBHOOK_URL"]
            }
        ]
    }

config["subreddits"] = []
for instance in config["instances"]:
    config["subreddits"].extend(subreddit
                                for subreddit in instance["subreddits"]
                                if subreddit not in config["subreddits"])
config["users"] = []
for instance in config["instances"]:
    config["users"].extend(user
                           for user in instance["users"]
                           if user not in config["users"])
config["keywords"] = []
for instance in config["instances"]:
    config["keywords"].extend(keyword
                              for keyword in instance["keywords"]
                              if keyword not in config["keywords"])

if __name__ == '__main__':
    print(config["subreddits"])
    print(config["users"])
    print(config["keywords"])
