import tweepy
import requests
from lxml import html
from numpy import random
import os 


def maketweet(tweetit):
    if os.sys.platform == 'darwin':
        os.chdir("/Users/akeil/Documents/programming_examples/python/twitterbot/")
    else:
        os.chdir("/home/akeil/Documents/programming_examples/python/twitterbot/")
    import mybotapi as mpi # need to cd into this directory
    t_keys = mpi.get_keys()
    auth = tweepy.OAuthHandler(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'])
    auth.set_access_token(t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
    api = tweepy.API(auth)
    tweet = api.update_status(tweetit)


def lookuptweets():
    pasttweets = {}
    with open("/Users/akeil/Documents/programming_examples/python/twitterbot/tweets.txt", 'r', encoding='utf-8') as f:
        for l in f.readlines():
            pasttweets[l.strip().replace('\n', '  ')] = 1
    return pasttweets


def addtweettolist(tweetit):
    with open("/Users/akeil/Documents/programming_examples/python/twitterbot/tweets.txt", 'a', encoding = 'utf-8') as f:
        f.writelines(tweetit + '\n')


def find_tweet():
    classes = ['span', 'a', 'li', 'title', 'h1', 'p', 'guid', 'LI', 'BR']
    curtxt = ''
    for j in classes:
        for i in theHTML.cssselect(j):
            skip = 0
            try:
                silent = len(i.text)
            except TypeError:
                skip = 1     
            if skip == 0:
                cond1 = (len(i.text.strip()) > len(curtxt))
                cond2 = (len(i.text.strip()) <= 140)
                cond3 = (i.text.find("@a") == -1)
                cond4 = (i.text.find("you") == -1)
                cond5 = (random.rand() > 0.5)
                cond6 = (i.text.find("sorry") == -1)
                cond7 = (i.text.find("404") == -1)
                if (cond1 & 
                    cond2 & 
                    cond3 & 
                    cond4 & 
                    cond5 & 
                    cond6 & 
                    cond7 & 
                    True  ):
                    curtxt = i.text.strip().replace('\n', '  ')
    return curtxt[0:140]


urlList = ["http://www.cdc.gov/mmwr/index.html", 
           "http://www.nytimes.com/",
           "http://www.cdc.gov/",
           "http://www.newsobserver.com/news/local/community/chapel-hill-news/",
           "http://www.npr.org/rss/rss.php?id=1001",
           "https://www.nlm.nih.gov/medlineplus/feeds/news_en.xml"
           "https://www.nlm.nih.gov/medlineplus/groupfeeds/nih.xml"
           "https://www.nlm.nih.gov/medlineplus/groupfeeds/new.xml"
           "https://en.wikiquote.org/wiki/David_Hume"
           "http://rescomp.stanford.edu/~cheshire/EinsteinQuotes.html",
           "http://izquotes.com/author/dennis-lindley",
           "http://www.math.utah.edu/~cherk/mathjokes.html",
           "http://www.jupiterscientific.org/sciinfo/jokes/physicsjokes.html",
           "http://www.se16.info/hgb/statjoke.htm"]


pasttweets = lookuptweets()
tweetit = [key for i, key in enumerate(pasttweets.keys()) if i<1][0]


while tweetit in pasttweets:
    theURL = urlList[random.randint(len(urlList))]
    resp = requests.get(theURL)
    theHTML = html.fromstring(resp.text)
    tweetit = find_tweet()
    print(theURL,'\n', tweetit)

maketweet(tweetit)
addtweettolist(tweetit)

