#!/usr/bin/env python

##############################################################################
# Author: Alex Keil
# Program: find_and_tweet_quotes.py
# Language: python 3.5 (should also work on python 2.7), tested on OS-X 
#           and Xubuntu
# Date: Wednesday, May 4, 2016 at 6:03:05 PM
# Project: twitterbot
# Tasks: scrape webpages for tweetable text, tweet it
# Keywords: Web scraping, bot, launchd, cron
# Released under GNU GPL: http://www.gnu.org/copyleft/gpl.html
###############################################################################

import tweepy
import requests
from lxml import html
from numpy import random
import time
import os 


if os.sys.platform == 'darwin':
    base = "/Users/akeil/"
else:
    base = "/home/akeil/"

def maketweet(tweetit):
    '''
    Tweet the contents of a string variable
    '''
    os.chdir(base + "Documents/programming_examples/python/twitterbot/")
    import mybotapi as mpi  # need to cd into this directory
    t_keys = mpi.get_keys()
    auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
    auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
    api = tweepy.API(auth)
    tweet = api.update_status(tweetit)


def lookuptweets():
    '''
    From a stored file of old tweets, turn the old tweets into a dictionary
    '''
    pasttweets = {}
    with open(base + "Documents/programming_examples/python/twitterbot/tweets.txt", 
              'r', encoding='utf-8') as f:
        for l in f.readlines():
            pasttweets[l.strip().replace('\n', '  ').replace('\r', '  ')] = 1
    return pasttweets


def addtweettolist(tweetit):
    '''
    Add the newest tweet to the file with old tweets
    '''
    with open(base + "Documents/programming_examples/python/twitterbot/tweets.txt", 
              'a', encoding='utf-8') as f:
        f.writelines(tweetit + '\n')


def find_tweet(theHTML):
    '''
    Search a webpage html for something that is adequately tweetable.
     There is a random component to the choice, so the same page will
     not always result in the same tweet
    '''
    classes = ['span', 'a', 'li', 'h1', 'p', 'guid', 'LI', 'BR', 'description']
    curtxt = ''
    for j in classes:
        for i in theHTML.cssselect(j):
            skip = 0
            try:
                silent = len(i.text)
            except TypeError: 
                True
            except ValueError: 
                True
            else:
                # filter out some things from the html
                cond = (len(i.text.strip()) > (len(curtxt) - 20))
                cond += (random.rand() > 0.3)
                cond += (len(i.text.strip()) > 5)
                cond += (len(i.text.strip()) <= 140)
                cond += (i.text.find("@") == -1)
                cond += (i.text.find("[0-9][0-9][0-9]") == -1)
                cond += (i.text.find("you") == -1)
                cond += (i.text.find("URL") == -1)
                cond += (i.text.find(".com") == -1)
                cond += (i.text.find("sorry") == -1)
                cond += (i.text.find("404") == -1)
                if (cond >= 11):
                    curtxt = i.text.strip().replace('\n', '  ').replace('\r', '  ')
    return curtxt.encode().decode('utf-8')

# list of URLs to search for tweetable text 
urlList = ["http://www.cdc.gov/mmwr/index.html", 
           "http://www.nytimes.com/",
           "http://www.cdc.gov/",
           "http://www.newsobserver.com/news/local/community/chapel-hill-news/",
           "https://www.nlm.nih.gov/medlineplus/feeds/news_en.xml"
           "https://www.nlm.nih.gov/medlineplus/groupfeeds/nih.xml"
           "https://www.nlm.nih.gov/medlineplus/groupfeeds/new.xml"
           "https://en.wikiquote.org/wiki/David_Hume"
           "http://rescomp.stanford.edu/~cheshire/EinsteinQuotes.html",
           "http://www.commondreams.org",
           "http://www.unc.edu",
           "http://www-cs.stanford.edu/",
           "http://http://bayes.cs.ucla.edu/",
           "http://www.sph.unc.edu",
           "http://www.harvard.edu",
           "https://en.wikipedia.org/wiki/Epidemiology",
           "http://www.hsph.harvard.edu/",
           "http://izquotes.com/author/dennis-lindley",
           "http://www.math.utah.edu/~cherk/mathjokes.html",
           "http://www.se16.info/hgb/statjoke.htm"]
           
           
def get_newpages(theURL='', n=3):
    '''
    Follow n random external links from the page
    '''
    try:
        resp = requests.get(theURL)
    except SSLError:
         newpages = ['']
    except ValueError:
         newpages = ['']
    else:
        theHTML = html.fromstring(resp.text)
        hrefs = [a.get('href') for a in theHTML.cssselect('a') if a.get('href') is not None]
        if len(hrefs)>0:
            newpages = [page for page in hrefs if 
                    (page.find('http:') == 0) & 
                    (page.find('#') == -1) &
                    (page.find('.pdf') == -1) &
                    (page.find('.zip') == -1) &
                    (page.find('rss') == -1) &
                    (page.find('?') == -1)
                    ]
                
            random.shuffle(newpages)
        else:
            newpages = ['']
    return newpages[:n]


# initialize the tweetit value to a recent tweet
pasttweets = lookuptweets()
tweetit = [key for i, key in enumerate(pasttweets.keys()) if i < 1][0]

# Search listed sites at random until a block of text is suitably tweetable
while tweetit in pasttweets:
    theURL = urlList[random.randint(len(urlList))]
    print(theURL)
    allpages = get_newpages(theURL, 15)
    allpages.append(theURL)
    possibleTweets = []
    for url in allpages:
        print(url)
        try:
            theText = requests.get(url).text
        except SSLError:
            True
        else:
            theHTML = html.fromstring(theText)
            twt = find_tweet(theHTML)
            time.sleep(0.1)
            if len(twt) > 40:
                possibleTweets.append(twt)
    random.shuffle(possibleTweets)
    tweetit = possibleTweets[0]
print(possibleTweets)

# Tweet the tweet, and add it to the list of old tweets
maketweet(tweetit)
addtweettolist(tweetit)
