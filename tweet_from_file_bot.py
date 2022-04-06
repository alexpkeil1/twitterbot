#!/usr/bin/env python
# send a tweet from a text file using the Tweepy module
# now is a joke bot

# -*- coding: utf-8 -*-
 
import tweepy
import requests
import os
from numpy import random
if os.sys.platform == 'darwin':
    base ="/Users/akeil"
else:
    base = "/home/akeil"

os.chdir(base + "/repo/twitterbot/")
import _settings as mpi # need to cd into this directory
t_keys = mpi.get_keys()
outdir = '/tmp/'


first_tweet = base + "/repo/twitterbot/" + 'test_tweet.txt'
joke_tweet = base + "/repo/twitterbot/" + 'jokes.txt'
joke_file = outdir + 'jokefile'

joke_urls = ['http://www.textfiles.com/humor/TAGLINES/cookie.' + 
                str(i) for i in range(2, 8)]
joke_urls.append("http://www.textfiles.com/humor/TAGLINES/quotes.frt")


def get_jokes(joke_urls):
    random.shuffle(joke_urls)
    jokepage = ''.join(requests.get(
        joke_urls.pop()
        ).text).replace('\n', '').replace('\r', '')
    with open(joke_file, 'w+') as f:
        for joke in jokepage.split('%%'):
            if joke.strip() != '':
                f.writelines(joke.strip().replace('\t', ' ') + '\n')

def tweet(textfile):
    auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
    auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
    api = tweepy.API(auth)
    lines = []
    with open(textfile, 'rb') as f:
        for l in f:
            lines.append(l.decode('utf-8').strip())
    random.shuffle(lines)
    twt = ' '*180
    while len(twt) > 140:
        twt = lines.pop()
    api.update_status(twt)

get_jokes(joke_urls)
tweet(joke_file)
