#!/usr/bin/env python
# send a tweet from a text file using the Tweepy module

# -*- coding: utf-8 -*-
 
import tweepy
import requests
import os
from numpy import random
if os.sys.platform == 'darwin':
    base ="/Users/akeil"
else:
    base = "/home/akeil"

os.chdir(base + "/Documents/programming_examples/python/twitterbot/")
import mybotapi as mpi # need to cd into this directory


first_tweet = base + "/Documents/programming_examples/python/twitterbot/" + 'test_tweet.txt'
joke_tweet = base + "/Documents/programming_examples/python/twitterbot/" + 'jokes.txt'


def tweet(textfile):
    auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
    auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
    api = tweepy.API(auth)
    lines = []
    with open(textfile, 'rb') as f:
        for l in f:
            lines.append(l.decode('utf-8').strip())
    random.shuffle(lines)
    api.update_status(lines.pop())

tweet(joke_tweet)
