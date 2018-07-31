import praw
import re
from config import config
from datetime import datetime
from urllib.parse import quote_plus
from discord import Webhook, RequestsWebhookAdapter, Embed
import discord
import random
from enum import Enum

debug_mode = False


class ProcessReason(Enum):
    tracked_user = 1
    said_keyword = 2


class ObjectType(Enum):
    comment = 1
    submission = 2


def process_comment(comment, process_reason):
    if debug_mode:
        custom_print(title=None,
                     body=comment.body,
                     author=comment.author.name,
                     subreddit=str(comment.subreddit),
                     URL=comment.permalink,
                     object_type=ObjectType.comment)

    webhook_send(title=None,
                 body=comment.body,
                 author=comment.author.name,
                 subreddit=str(comment.subreddit),
                 URL=comment.permalink,
                 object_type=ObjectType.comment,
                 process_reason=process_reason)


def process_submission(submission, process_reason):
    if debug_mode:
        custom_print(title=submission.title,
                     body=submission.selftext if submission.is_self
                     else submission.url,
                     author=submission.author.name,
                     subreddit=str(submission.subreddit),
                     URL=submission.permalink,
                     object_type=ObjectType.submission)

    webhook_send(title=submission.title,
                 body=submission.selftext if submission.is_self
                 else submission.url,
                 author=submission.author.name,
                 subreddit=str(submission.subreddit),
                 URL=submission.permalink,
                 object_type=ObjectType.submission,
                 process_reason=process_reason)


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


def webhook_send(title, body, author, subreddit, URL, object_type, process_reason):
    colors = [0x7f0000, 0x535900, 0x40d9ff, 0x8c7399, 0xd97b6c, 0xf2ff40, 0x8fb6bf, 0x502d59, 0x66504d,
              0x89b359, 0x00aaff, 0xd600e6, 0x401100, 0x44ff00, 0x1a2b33, 0xff00aa, 0xff8c40, 0x17330d,
              0x0066bf, 0x33001b, 0xb39886, 0xbfffd0, 0x163a59, 0x8c235b, 0x8c5e00, 0x00733d, 0x000c59,
              0xffbfd9, 0x4c3300, 0x36d98d, 0x3d3df2, 0x590018, 0xf2c200, 0x264d40, 0xc8bfff, 0xf23d6d,
              0xd9c36c, 0x2db3aa, 0xb380ff, 0xff0022, 0x333226, 0x005c73, 0x7c29a6]

    truncated_body = (body[:1800] + '..') if len(body) > 1900 else body

    embed = Embed(colour=random.choice(colors),
                  title="**/u/{author}** {action} in **/r/{subreddit}**".format(author=author, subreddit=subreddit,
                                                                                action="commented in a thread"
                                                                                if object_type==ObjectType.comment
                                                                                else "created a thread"),
                  url="https://np.reddit.com" + URL,
                  description=truncated_body if object_type == ObjectType.comment
                  else "**{title}**\n{body}".format(title=title, body=truncated_body),
                  timestamp=datetime.utcnow())

    # todo: embed.set_author could be used to provide information about process reason
    # todo: not sure if needed, still thinking about formatting

    embed.set_footer(text="thread created on"
                     if object_type == ObjectType.submission
                     else "comment created on",
                     icon_url='https://i.imgur.com/oElfmvz.png')

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
    finally:
        print("{process_reason}: /u/{author} {action} in /r/{subreddit}: \n"
              "{URL}".format(process_reason="Keyword detected"
                             if process_reason==ProcessReason.said_keyword
                             else "Author detected",
                             author=author, subreddit=subreddit,
                             action="commented in a thread"
                             if object_type==ObjectType.comment
                             else "created a thread",
                             URL="https://np.reddit.com" + URL))


if __name__ == '__main__':
    r = praw.Reddit(client_id=config["client_id"],
                    client_secret=config["client_secret"],
                    password=config["password"],
                    user_agent=config["user_agent"],
                    username=config["username"])

    subreddit = r.subreddit("+".join(config["subreddit"]))

    comment_stream = subreddit.stream.comments(pause_after=-1)
    submission_stream = subreddit.stream.submissions(pause_after=-1)

    processed_comments = 0
    processed_submissions = 0
    while True:  # todo: change if to while
        for comment in comment_stream:
            # break  # todo: remove this

            if comment is None:
                break
            else:
                processed_comments += 1

            try:
                comment_author = comment.author.name.lower()
            except AttributeError:
                # author is deleted, don't care about this comment
                continue

            if comment_author in config["users"]:
                process_comment(comment=comment, process_reason=ProcessReason.tracked_user)
                continue

            if any(keyword in comment.body.lower() for keyword in config["keywords"]):
                process_comment(comment=comment, process_reason=ProcessReason.said_keyword)
                continue

            # break  # todo: remove line

        for submission in submission_stream:
            if submission is None:
                break
            else:
                processed_submissions += 1

            try:
                thread_author = submission.author.name.lower()
            except AttributeError:
                # author is deleted, don't care about this thread
                continue

            if thread_author in config["users"]:
                process_submission(submission=submission, process_reason=ProcessReason.tracked_user)

            if any(keyword in submission.title.lower() for keyword in config["keywords"]):
                process_submission(submission=submission, process_reason=ProcessReason.said_keyword)
                continue

            if submission.is_self:
                if any(keyword in submission.selftext.lower() for keyword in config["keywords"]):
                    process_submission(submission=submission, process_reason=ProcessReason.said_keyword)
                    continue
            # break  # todo: remove line
        if debug_mode:
            print("processed comments: {processed_comments}, processed submissions: {processed_submissions}"
                  .format(processed_comments=processed_comments, processed_submissions=processed_submissions))
