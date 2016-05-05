#!/usr/bin/env python
# send a tweet from a text file using the Tweepy module

# -*- coding: utf-8 -*-
 
import mybotapi as mpi
import tweepy
import requests
import os
os.chdir("/Users/akeil/Documents/programming_examples/python/twitterbot/")
import mybotapi as mpi # need to cd into this directory


first_tweet = 'test_tweet.txt'


def tweet(textfile):
    auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
    auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
    api = tweepy.API(auth)
    with open(textfiletext, 'rb') as f:
        api.update_status(f.read())


    
#tweet(first_tweet)
