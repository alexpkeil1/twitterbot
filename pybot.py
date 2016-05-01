#!/usr/bin/env python
# send a tweet from a text file using the Tweepy module

# -*- coding: utf-8 -*-
 
import mybotapi as mpi
import tweepy

auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
api = tweepy.API(auth)


first_tweet = 'test_tweet.txt'

with open(first_tweet, 'rb') as f:
    api.update_status(f.read())


    