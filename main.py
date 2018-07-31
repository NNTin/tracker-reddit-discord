import praw
import re
from config import config
from datetime import datetime
from urllib.parse import quote_plus
from discord import Webhook, RequestsWebhookAdapter, Embed
import discord
import random
from enum import Enum


# todo: when implemented condition which comment/submission are special
# todo: provide reason why comment/submission is special
class ProcessReason(Enum):
    tracked_user = 1
    said_keyword = 2


class ObjectType(Enum):
    comment = 1
    submission = 2


def process_comment(comment):
    custom_print(title=None,
                 body=comment.body,
                 author=comment.author.name,
                 subreddit=str(comment.subreddit),
                 URL=comment.permalink,
                 object_type=ObjectType.comment)
    pass


def process_submission(submission):
    pass


def custom_print(title, body, author, subreddit, URL, object_type):
    print("Title: {title}\n"
          "Body: {body}\n"
          "author: {author}\n"
          "subreddit: {subreddit}\n"
          "URL: {URL}\n"
          "is comment: {object_type}".format(title=title,
                                             body=body,
                                             author=author,
                                             subreddit=subreddit,
                                             URL=URL,
                                             object_type=(object_type == ObjectType.comment)))
    pass


def webhook_send(message):
    colors = [0x7f0000, 0x535900, 0x40d9ff, 0x8c7399, 0xd97b6c, 0xf2ff40, 0x8fb6bf, 0x502d59, 0x66504d,
              0x89b359, 0x00aaff, 0xd600e6, 0x401100, 0x44ff00, 0x1a2b33, 0xff00aa, 0xff8c40, 0x17330d,
              0x0066bf, 0x33001b, 0xb39886, 0xbfffd0, 0x163a59, 0x8c235b, 0x8c5e00, 0x00733d, 0x000c59,
              0xffbfd9, 0x4c3300, 0x36d98d, 0x3d3df2, 0x590018, 0xf2c200, 0x264d40, 0xc8bfff, 0xf23d6d,
              0xd9c36c, 0x2db3aa, 0xb380ff, 0xff0022, 0x333226, 0x005c73, 0x7c29a6]

    embed=Embed(colour=random.choice(colors),
                url='https://placeholder.com',
                title=message,
                description=message)

    embed.set_author(name=message,
                     url="http://placeholder.com",
                     icon_url="https://cdn1.iconfinder.com/data/icons/iconza-circle-social/64/697029-twitter-512.png")
    embed.set_footer(text=message,
                     icon_url='https://cdn1.iconfinder.com/data/icons/iconza-circle-social/64/697029-twitter-512.png')

    regex = r"discordapp\.com\/api\/webhooks\/(?P<id>\d+)\/(?P<token>.+)"
    match = re.search(regex, config["webhook_url"])

    webhook = Webhook.partial(match.group("id"), match.group("token"), adapter=RequestsWebhookAdapter())
    try:
        webhook.send(embed=embed)
    except discord.errors.HTTPException as error:
        print('---------Error---------')
        print('discord.errors.HTTPException')
        print("You've found an error. Please contact the owner (https://discord.gg/JV5eUB) "
              "and send him what follows below:")
        print(error)
        print('-----------------------')


if __name__ == '__main__':
    r = praw.Reddit(client_id=config["client_id"],
                    client_secret=config["client_secret"],
                    password=config["password"],
                    user_agent=config["user_agent"],
                    username=config["username"])

    subreddit = r.subreddit("+".join(config["subreddit"]))

    comment_stream = subreddit.stream.comments(pause_after=-1)
    submission_stream = subreddit.stream.submissions(pause_after=-1)

    if True:  # todo: change if to while
        for comment in comment_stream:
            if comment is None:
                break
            # todo: implement condition which comments are special
            process_comment(comment=comment)
            break  # todo: remove line
        for submission in submission_stream:
            if submission is None:
                break
            # todo: implement condition which submissions are special
            process_submission(submission=submission)
            break  # todo: remove line
