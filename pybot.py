#!/usr/bin/env python
# send a tweet from a text file using the Tweepy module
# finds a random Nietzche quote

# -*- coding: utf-8 -*-
 
import tweepy
import requests
from lxml import html
import os
if os.sys.platform == 'darwin':
    os.chdir("/Users/akeil/Documents/programming_examples/python/twitterbot/")
else:
    os.chdir("/home/akeil/Documents/programming_examples/python/twitterbot/")
import mybotapi as mpi # need to cd into this directory

t_keys = mpi.get_keys()

auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
api = tweepy.API(auth)





resp = requests.get("http://www.nietzschefamilycircus.com")

rt = html.fromstring(resp.text)
divs = rt.cssselect('div')
quote = [i.text for i in divs][7].replace('\n', '').replace('\t', '')


first_tweet = '/home/akeil/Documents/programming_examples/python/twitterbottest_tweet.txt'
with open(first_tweet, 'w') as f:
    f.write(quote)


with open(first_tweet, 'r') as f:
    print(f.read())

if quote.find('wom') < 0:
    print('tweeting: ' + quote)
    tweet = api.update_status(quote)
else: 
    print('not tweeting')


    