import mybotapi as mpi
import tweepy
import requests
from lxml import html

resp = requests.get("http://www.cdc.gov/mmwr/index.html")


theHTML = html.fromstring(resp.text)

curtxt = ''
for i in theHTML.cssselect('span'):
    skip = 0
    try:
        len(i.text)
    except TypeError:
        skip = 1     
    if skip == 0:
        if len(i.text) > len(curtxt):
            curtxt = i.text


tweetit = curtxt[0:140]

t_keys = mpi.get_keys()

auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
api = tweepy.API(auth)
tweet = api.update_status(tweetit)
