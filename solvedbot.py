#!/usr/bin/env python3.7

import praw
import configparser
from loguru import logger

# Initialize logging with loguru
logger.add('log_{time}.log', rotation="5MB")
logger.debug("Debugfile for solvedbot.py, created {date} {time}")


# Read Configs from .cfg file
config = configparser.ConfigParser()
config.read("solvedbot.cfg")
cgf_reddit = config['Reddit']
cgf_settings = config['Settings']
cgf_sql = config['SQL']


# Log into Reddit PRAW Agent.
reddit = praw.Reddit(client_id=cgf_reddit['client_id'],
                     client_secret=cgf_reddit['client_secret'],
                     password=cgf_reddit['password'],
                     user_agent='test_script solvedbot',
                     username=cgf_reddit['username'])


def search_keyword_comment(new, keyword):
    # Iterating through submissions and searching for the keyword in replies.
    list_of_comments = []
    for submission in new:
        for comment in submission.comments.list():
            if keyword in comment.body:
                logger.info(f'{keyword} found in comment: {comment}\tby User: {comment.author} \tin submission: {submission}')
                list_of_comments.append(comment)

    return list_of_comments

def reply_to_keyword(comments):
    # Replies to all comments found to contain the Keyword.
    for comment in comments:
        answer = f"""::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Your notification was registered! We will notify you when either keyword "Found!" or "Solved!" are mentioned.

If you want to be notified too, please use the link below!

[NotifyMe!](http://www.reddit.com/message/compose/?to=solvednotification&subject=Reminder&message=[http://www.reddit.com/{comment.submission}])

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"""
        comment.reply(answer)
    return True


# Main function, logged with loguru.
@logger.catch
def main(reddit, cgf_settings):
    
    # Fetching submissions by new, with limit of 5.
    subreddit = reddit.subreddit(cgf_settings['list_of_subreddits'])
    new = subreddit.new(limit=5)

    list_of_comments = search_keyword_comment(new, cgf_settings['keyword_searched_for'])
    reply_to_keyword(list_of_comments)

    logger.info('Programm ended. No issues.')



# Run main
if __name__ == '__main__':
    main(reddit, cgf_settings)
