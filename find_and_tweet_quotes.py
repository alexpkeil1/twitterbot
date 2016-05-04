import tweepy
import requests
from lxml import html
from numpy import random
import os 

os.chdir("/Users/akeil/Documents/programming_examples/python/twitterbot/")
import mybotapi as mpi # need to cd into this directory


def maketweet(tweetit):
    t_keys = mpi.get_keys()

    auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
    auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
    api = tweepy.API(auth)
    tweet = api.update_status(tweetit)



urlList = ["http://www.cdc.gov/mmwr/index.html", 
           "http://www.nytimes.com/",
           "http://www.cdc.gov/",
           "http://www.newsobserver.com/news/local/community/chapel-hill-news/",
           "http://www.npr.org/rss/rss.php?id=1001",
           "https://www.nlm.nih.gov/medlineplus/feeds/news_en.xml"
           "https://www.nlm.nih.gov/medlineplus/groupfeeds/nih.xml"
           "https://www.nlm.nih.gov/medlineplus/groupfeeds/new.xml"]

theURL = urlList[random.randint(len(urlList))]
print(theURL)

resp = requests.get(theURL)


theHTML = html.fromstring(resp.text)

curtxt = ''
for j in ['span', 'a', 'li', 'title', 'h1', 'p', 'guid']:
    for i in theHTML.cssselect(j):
        skip = 0
        try:
            silent = len(i.text)
        except TypeError:
            skip = 1     
        if skip == 0:
            if ((len(i.text.strip()) > len(curtxt)) & 
                (len(i.text.strip()) <= 140) & 
                (i.text.find("@a") == -1) & 
                (i.text.find("you") == -1) & 
                (random.rand() > 0.5)):
                curtxt = i.text.strip()


tweetit = curtxt[0:140]
print(tweetit)
pasttweets = {}
with open("/Users/akeil/Documents/programming_examples/python/twitterbot/tweets.txt", 'r') as f:
    for l in f.readlines():
        pasttweets[l.strip()] = 1


with open("/Users/akeil/Documents/programming_examples/python/twitterbot/tweets.txt", 'a') as f:
    f.writelines(tweetit + '\n')


if tweetit not in pasttweets:
    maketweet(tweetit)

