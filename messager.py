#!/usr/bin/env python3.7

import praw
import configparser
import sqlite3
import datetime
import re
from loguru import logger

'''
Solvedbot. A bot to notify interestees of reddit.com. Specially aimed at subreddits like r/tipofmytounge and r/whatisthisthing.
This part is for handling private messages to the bot only. They appear through the link provided by the main bot solvedbot.py
'''

# Initialize logging with loguru
logger.add('log_{time}.log', rotation="5MB")
logger.debug("Debugfile for messager.py")


# Read Configs from .cfg file
config = configparser.ConfigParser()
config.read("solvedbot.cfg")
cgf_reddit = config['Reddit']
cgf_settings = config['Settings']
# cgf_sql = config['SQL']


# Log into Reddit PRAW Agent.
reddit = praw.Reddit(client_id=cgf_reddit['client_id'],
                     client_secret=cgf_reddit['client_secret'],
                     password=cgf_reddit['password'],
                     user_agent='test_script solvedbot',
                     username=cgf_reddit['username'])


class Connect:
    """
    DB connection class
    """
    def __init__(self):
        self.connection = sqlite3.connect('solvedbot.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS data(parent_id TEXT, comment_id TEXT, user TEXT, date TEXT)")

    def add(self, parent_id, comment_id, user):
        # Handles Database entries

        date = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        self.cursor.execute(
            f"INSERT INTO data(parent_id, comment_id, user, date) VALUES(?,?,?,?)",
            (parent_id, comment_id, user, date)
        )
        self.connection.commit()
        return True

class Handler:
    '''
    Handler Class, concerned about finding, replying, and saving Comments, containing the Keyword.
    '''

    def sendMessage(self, parent_id, user):
        # Notifies all Notifees that a Solution has been found.

        body = f"""::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Hello {user}

Success! You will be notified when the following thread is solved!

[Link](http://www.reddit.com/{parent_id}/)

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"""

        reddit.redditor(user).message(subject='SolvedBot Notification', message=body)
        return True


# Main function, logged with loguru.
@logger.catch
def main(reddit, cgf_settings):
    # Instanciating
    handler = Handler()
    database = Connect()

    # Fetching variables
    inbox = reddit.inbox.unread()

    # Main Loop
    try:
        while True:
            for message in inbox:
                if message.subject == 'NotifyMe!'
                    body = str(message.body)
                    try:
                        parent_id = re.search('\n\n(.+?)\n\n', body).group(1)
                    except AttributeError:
                        continue
                    
                    comment_id = str(message)
                    author = str(message.author)

                    database.add(parent_id,comment_id,author)
                    handler.sendMessage(parent_id, user)
                else:
                    # maybe inform redditor of error or something...
    except KeyboardInterrupt:
        logger.info('Bot terminated. User input.')


# Run main
if __name__ == '__main__':
    main(reddit, cgf_settings)
