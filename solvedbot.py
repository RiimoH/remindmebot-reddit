#!/usr/bin/env python3.7

import praw
import configparser
import sqlite3
import datetime
from loguru import logger

'''
Solvedbot. A bot to notify interestees of reddit.com. Specially aimed at subreddits like r/tipofmytounge and r/whatisthisthing.
'''

# Initialize logging with loguru
logger.add('log_{time}.log', rotation="5MB")
logger.debug("Debugfile for solvedbot.py")


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

    def fetch(self, parent_id):
        # After a Solution has been found, this function fetches all users to notify from the database and returns them like [(parent_id, comment_id, users , date),]
        self.cursor.execute('SELECT user FROM data WHERE parent_id = ?', (parent_id,))
        data = self.cursor.fetchall()
        users = {x[0] for x in data}
        return users

    def delete(self, parent_id):
        # removes all entries from the database, containing the parent_id.
        self.cursor.execute('DELETE FROM data WHERE parent_id = ?', (parent_id,))
        return True


class Handler:
    '''
    Handler Class, concerned about finding, replying, and saving Comments, containing the Keyword.
    '''

    def reply(self, comment):
        # Replies to the comment input.
        answer = f"""::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Your notification was registered! We will notify you when the keyword "Found!" is mentioned.

If you want to be notified too, please use the link below!

[NotifyMe!](https://www.reddit.com/message/compose?to=solvednotification&subject=Reminder&message=I%20want%20to%20be%20notified%2C%20when%20this%20thread%20is%20solved!%0A%0A{comment.submission}%0A%0ADo%20not%20manipulate%20this%20message!)

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"""
        comment.reply(answer)
        return True

    def sendMessage(self, parent_id, users):
        # Notifies all Notifees that a Solution has been found.
        for user in users:

            body = f"""::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Hello {user}

You wanted to be notified, as soon as a Solution is found.

Good News, now it is! Check out the link below.

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
    keyword_searching = cgf_settings['keyword_searching']
    keyword_found = cgf_settings['keyword_found']
    subreddit = reddit.subreddit(cgf_settings['subreddit'])

    # Main Loop
    try:
        while True:
            for comment in subreddit.stream.comments():
                if comment.author == 'solvednotification':
                    continue
                else:
                    text = str(comment.body)
                    parent_id = str(comment.submission)
                    comment_id = str(comment)
                    author = str(comment.author)

                    if keyword_searching in text:
                        database.add(parent_id, comment_id, author)
                        handler.reply(comment)
                    elif keyword_found in text:
                        users = database.fetch(parent_id)
                        handler.sendMessage(parent_id, users)
                        database.delete(parent_id)
    except KeyboardInterrupt:
        logger.info('Bot terminated. User input.')


# Run main
if __name__ == '__main__':
    main(reddit, cgf_settings)
