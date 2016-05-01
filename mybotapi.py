#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import tweepy
import time
import sys
import requests
from TwitterAPI import TwitterAPI

  
#enter the corresponding information from your Twitter application:
CONSUMER_KEY = 'Pg5QBoiOOKD0rv1wkJWSvCape'#keep the quotes, replace this with your consumer key
CONSUMER_SECRET = 'PcksTh8dRgebvfScD2jjlYu1yRsjT5Yzuhqc5Ii6PIOxwy3yiA'#keep the quotes, replace this with your consumer secret key
ACCESS_KEY = '726821204334628864-lvFIom98ak8BuRFM2knxHXPkefyo9fZ'#keep the quotes, replace this with your access token
ACCESS_SECRET = 't4kRFCyXwtGCaIg7ySEV0zI1HSFzozd1UsOSBouE0liTz'#keep the quotes, replace this with your access token secret


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
tweepyapi = tweepy.API(auth)

api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
 