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
    os.chdir(base + "repo/twitterbot/")
    import _settings as mpi # need to cd into this directory
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
    with open(base + "repo/twitterbot/tweets.txt", 
              'r') as f:
        for l in f.readlines():
            pasttweets[l.strip().replace('\n', '  ').replace('\r', '  ')] = 1
    return pasttweets


def addtweettolist(tweetit):
    '''
    Add the newest tweet to the file with old tweets
    '''
    with open(base + "repo/twitterbot/tweets.txt", 
              'a') as f:
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
            except: 
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
                cond += (i.text.find("server") == -1)
                cond += (i.text.find("404") == -1)
                if (cond >= 12):
                    curtxt = i.text.encode('ascii', 'ignore').decode('utf-8')
    return curtxt.strip().replace('\n', '  ').replace('\r', '  ')


# list of URLs to search for tweetable text 
urlList = ["http://www.cdc.gov/mmwr/index.html", 
           "http://www.nytimes.com/",
           "http://www.sciencemag.org/",
           "http://www.pnas.org/",
           "http://www.economist.com/",
           "http://www.newsobserver.com/news/local/community/chapel-hill-news/",
           "https://www.nlm.nih.gov/medlineplus/feeds/news_en.xml"
           "https://www.nlm.nih.gov/medlineplus/groupfeeds/nih.xml"
           "https://www.nlm.nih.gov/medlineplus/groupfeeds/new.xml"
           "https://en.wikiquote.org/wiki/David_Hume"
           "http://rescomp.stanford.edu/~cheshire/EinsteinQuotes.html",
           "http://www.commondreams.org",
           "http://www-cs.stanford.edu/",
           "http://bayes.cs.ucla.edu/",
           "http://www.sph.unc.edu",
           "https://en.wikipedia.org/wiki/Epidemiology",
           "https://en.wikipedia.org/wiki/Causal_inference",
           "http://www.hsph.harvard.edu/",
           "http://izquotes.com/author/dennis-lindley",
           "http://www.math.utah.edu/~cherk/mathjokes.html",
           "http://library.umassmed.edu/ebpph/top25.cfm",
           "http://www.se16.info/hgb/statjoke.htm"]

def lookupURLs():
    '''
    From a stored file of old URLs searched, turn the old URLs into a set
    '''
    pastURLs = {}
    #with open(base + "repo/twitterbot/urls.txt", 
    with open(base + "repo/twitterbot/img_urls.txt", 
              'r') as f:
        for l in f.readlines():
            pastURLs[l.strip().replace('\n', '  ').replace('\r', '  ')] = 1
    return set(pastURLs)


def addURLstolist(URLlist):
    '''
    Add the newest URLs to the file with old URLs
    '''
    URLset = set(URLlist)
    with open(base + "repo/twitterbot/urls.txt", 
              'a') as f:
        for URL in URLset:
            f.writelines(URL + '\n')


def ban_urls(urls):
    newurls = []
    banwords = ["donate", "contact", "terms", "conditions", "podcasts"
                "twitter", "help", "about", "linkedin", "instagram"
                "facebook", "privacy-policy", "shop", "retail", 
                "products", "wifi", 'plugins', 'share', 'support',
                'registration', 'plugins', 'signup', 'giving',
                'promo', 'account', 'mail', 'itunes', 'sponsored',
                'product', 'corporate', '#'
                ]
    for u in urls:
        keep = True
        for w in banwords:
            if u.lower().find(w) > -1:
                keep = False
        if keep:
            newurls.append(u)
    return newurls


def sortURLs():
    '''
    Sort all of the URLs in a file
    '''
    pastURLs = {}
    with open(base + "repo/twitterbot/urls.txt", 
              'r') as f:
        for l in f.readlines():
            pastURLs[l.strip().replace('\n', '  ').replace('\r', '  ')] = 1
    sortedList = sorted(list(set(ban_urls(pastURLs))))
    with open(base + "repo/twitterbot/urls.txt", 
              'w') as f:
        for URL in sortedList:
            f.writelines(URL + '\n')


def get_newpages(theURL='', n=3, currlist=urlList):
    '''
    Follow n random external links from the page
    '''
    try:
        resp = requests.get(theURL, timeout=5)
    except:
         newpages = ['']
    else:
        theHTML = html.fromstring(resp.text.encode('ascii', 'ignore'))
        hrefs = [a.get('href') for a in theHTML.cssselect('a') if a.get('href') is not None]
        if len(hrefs)>0:
            newpages = list(set([page for page in hrefs if 
                    (page.find('http') == 0) & 
                    (page.find('#') == -1) &
                    (page.find('donate') == -1) &
                    (page.find('twitter.com') == -1) &
                    (page.find('t.co/') == -1) &
                    (page.find('...') == -1) &
                    (page.find('youtube') == -1) &
                    (page.find('facebook') == -1) &
                    (page.find('amazon') == -1) &
                    (page.find('.pdf') == -1) &
                    (page.find('.zip') == -1) &
                    (page.find('rss') == -1) &
                    (page.find('rss') == -1) &
                    (page.find('download') == -1) &
                    (page.find('ads') == -1) &
                    (page.find('\\x') == -1) &
                    (page not in currlist)
                    ]))
            newpages = ban_urls(newpages)
            random.shuffle(newpages)
        else:
            newpages = ['']
    return newpages[:n]


# initialize the tweetit value to a recent tweet
pasttweets = lookuptweets()
tweetit = [key for i, key in enumerate(pasttweets.keys()) if i < 1][0]

# occasionally sort the url list to keep it orderly
if random.random() > 0.95:
    sortURLs()
    print("Sorting URL list")

# use default list until the lookup list from past sites is large
filelist = list(lookupURLs())
#if(len(filelist)>900):
#    urlList = filelist

# Search listed sites at random until a block of text is suitably tweetable
while tweetit in pasttweets:
    theURL = urlList[random.randint(len(urlList))]
    allpages = get_newpages(theURL, 15, currlist=filelist)
    addURLstolist(allpages)
    allpages.append(theURL)
    possibleTweets = []
    for url in allpages:
        try:
            theText = requests.get(url, timeout=5).text
        except:
            True
        else:
            try: 
                theHTML = html.fromstring(theText.encode('ascii', 'ignore'))
            except: 
                theHTML = html.fromstring('''
                    <head></head><body><p>Something happened </p></body>
                    '''.encode('ascii', 'ignore'))
            twt = find_tweet(theHTML)
            time.sleep(0.1)
            if len(twt) > 40:
                possibleTweets.append(twt)
    random.shuffle(possibleTweets)
    while True:
        try:
            tweetit = possibleTweets.pop()
            print('Tweeting: ', tweetit)
        except:
            print('Exeption here: ', tweetit)
            try:
                possibleTweets.pop() # if this is empty, re-populate the list of URLs
            except IndexError:
                allpages = get_newpages(theURL, 15, currlist=filelist)
                break
        else:
            break


# Tweet the tweet, and add it to the list of old tweets
maketweet(tweetit)
addtweettolist(tweetit)
