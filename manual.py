import praw
import main
from config import config

if __name__ == '__main__':
    r = praw.Reddit(client_id=config["client_id"],
                    client_secret=config["client_secret"],
                    password=config["password"],
                    user_agent=config["user_agent"],
                    username=config["username"])

    # comment_id = "t1_e3df491"
    # comment = next(r.info([comment_id]))
    # main.process_comment(comment, main.ProcessReason.manual)

    submission_id = "t3_92x5ph"
    submission = next(r.info([submission_id]))
    main.process_submission(submission, main.ProcessReason.manual)