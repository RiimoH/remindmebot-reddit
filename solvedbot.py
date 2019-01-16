#!/usr/bin/env python3.7

import praw
import configparser
import




config = configparser.ConfigParser()
config.read("solvedbot.cfg")
cgf_reddit = config['Reddit']

reddit = praw.Reddit(client_id=cgf_reddit['client_id'],
                     client_secret=cgf_reddit['client_secret'],
                     password=cgf_reddit['password'],
                     user_agent='test_script solvedbot',
                     username=cgf_reddit['username'])
def main():
    print(reddit.user.me())

if __name__ == '__main__':
    main()
