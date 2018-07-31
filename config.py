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
        "subreddit": os.environ["SUBREDDITS"].replace(" ", "").split(","),
        "users": os.environ["USERS"].lower().replace(" ", "").split(","),
        "webhook_url": os.environ["WEBHOOK_URL"]
    }