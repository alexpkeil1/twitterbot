#!/opt/anaconda3/envs/twitterbot/bin/python
from TwitterAPI import TwitterAPI
#from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt
import os
import numpy as np
from numpy import random
import requests
from lxml import html

# ask if OSX
if os.sys.platform == 'darwin':
    base ="/Users/akeil"
else:
    base = "/home/akeil"




root = base + "/repo/twitterbot/"
os.chdir(root)
# set twitter api parameters
import _settings as mpi # need to cd into this directory
t_keys = mpi.get_keys()
api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])

def process_search(searchURL):
    headers = {'user-agent': 'hivemind_bot/0.10'}
    try:
        resp = requests.get(searchURL, headers=headers)
    except: 
        print('failed at searching... oh well')
    try:    
        thePage = html.fromstring(resp.text.encode("ascii","ignore"))
    except: 
        print('failed at converting html... oh well')
    else:
        return thePage


def bad_words():
    resp = requests.get("http://pastebin.com/raw/0L6nxiXE")
    badwords = set([])
    for word in resp.text.split('\n'):
        badwords.add(word)
    return badwords


def get_dictionary():
    resp = requests.get("http://ejohn.org/files/dict/ospd4.txt")
    english = set([])
    for word in resp.text.split('\n'):
        english.add(word)
    return english


def get_common_word():
    dictionary = get_dictionary()
    common_words_html = process_search(searchURL = 'http://www.wordfrequency.info/free.asp?s=y')
    common_words = set([a.text.strip() for a in common_words_html.cssselect('td') if a.text is not None])
    common_words = set.intersection(common_words, dictionary)
    return random.choice(list(common_words))


def get_word():
    '''
    return a random word from the english dictionary
    '''
    english = get_dictionary()
    return random.choice(list(english))


def plot_tweets(lat=[0], long=[0], text='', heat=False):
    plt.style.use('ggplot')
    lon_0 = -125 #further west if negative, further east if not
    lon_1 = -66
    lat_0 = 25
    lat_1 = 52
    # create figure and axes instances
    plt.clf()
    dim = 6
    fig = plt.figure(figsize=(dim,(225/494)*dim))
    #ax = fig.add_subplot(111)
    ax = fig.add_axes([0,0 ,1,1])
    # create polar stereographic Basemap instance.
    m = Basemap(llcrnrlat=lat_0,urcrnrlat=lat_1, llcrnrlon=lon_0, urcrnrlon=lon_1, resolution='l')
    m.drawcoastlines()
    m.drawcountries()
    if random.random() > 0.5: 
        m.fillcontinents(color='tan')
    elif random.random() > 0.5: 
        m.bluemarble()
    elif random.random() > 0.5: 
        m.shadedrelief()
    elif random.random() > 0.5: 
        m.etopo()
    elif random.random() > 0.5: 
        m.drawmapboundary(fill_color='aqua')
    if heat:
        for i, l in enumerate(lat):
            lat[i] = lat[i] + random.random()*0.1
            long[i] = long[i] + random.random()*0.1
            p = ax.plot(long, lat, 'p')
    else:
        p = ax.plot(long, lat, 'p')
    if text is not None:
        for i, ht in enumerate(text):
            if len(lat) > i:
                ax.annotate(ht, (long[i], lat[i]), rotation=random.random()*45.)
    plt.savefig('/tmp/twitmap.png')


def locationator(r = {}, ntweets=10):
    lat,long,hash,tweet = [],[],[],[]
    count = 0
    for tweet in r:
        try:
            silent = False
            lat.append(tweet['coordinates']['coordinates'][1])
            long.append(tweet['coordinates']['coordinates'][0])
            hash.append(tweet['entities']['hashtags'][0]['text'])
            hash.append(tweet['entities']['hashtags'][0]['text'])
        except:
            silent = True
            while len(hash) > len(long):
                hash = hash[::-1][1:][::-1]
            while len(hash) < len(long):
                hash.append('')
        else:
            count += 1
            print(tweet['text'], str(count))
            while len(hash) > len(long):
                hash = hash[::-1][1:][::-1]
            while len(hash) < len(long):
                hash.append('')
            if len(lat) > ntweets:
                print(len(lat), len(long), len(hash))
                break
    return lat,long,hash,tweet


def tweet_fig(outtext):
    with open('/tmp/twitmap.png', 'rb') as file:
        data = file.read()
        r = api.request('statuses/update_with_media', {'status': outtext}, {'media[]':data})
        return r.status_code

def tweet_text(outtext):
    True
    r = api.request('statuses/update', {'status': outtext})
    return r.status_code


api_choice = random.choice(4)


if api_choice == 0:
    print('Hashtag map')
    which_api = 'statuses/filter' 
    terms =  {'locations':'-130,30,-60,47'}
    r = api.request(which_api,terms)
    lat,long,hash,tweet = locationator(r, 25)
    badwords = bad_words()
    for i,w in enumerate(hash.copy()):
        if w in badwords:
            hash[i] = ''
    outtext = '#hashtagmap'
    plot_tweets(lat, long, hash, True)
    tweet_fig(outtext)

elif api_choice == 1:
    rand_word = get_common_word()
    print('Streaming search lottery:', rand_word)
    which_api = 'statuses/filter' 
    terms =  {'track': rand_word, 'locations':'-130,30,-60,47'}
    r = api.request(which_api,terms)
    lat,long,hash,tweet = locationator(r,20)
    badwords = bad_words()
    for i,t in enumerate(tweet.copy()):
        for w in t:
            if w in badwords:
                tweet[i] = ''
    if len(lat) == 0:
        outtext = '*sigh* Nobody talks about "' + rand_word + '" anymore'
        tweet_text(outtext)
    else:
        outtext = 'Tweets about ' + rand_word
        plot_tweets(lat, long, None)
        tweet_fig(outtext)
    
elif api_choice == 2:
    rand_word = get_word()
    print('REST search lottery:', rand_word)
    which_api = 'search/tweets' 
    terms = {'q': rand_word, 'result_type': 'recent',
                             'count': '100','locations':'-130,30,-60,47'}
    r = api.request(which_api,terms)
    lat,long,hash,tweet = locationator(r,100)
    badwords = bad_words()
    for i,t in enumerate(tweet.copy()):
        for w in t:
            if w in badwords:
                tweet[i] = ''
    if len(lat) == 0:
        outtext = 'Nobody talks about "' + rand_word + '." Except me. #'  + rand_word
        tweet_text(outtext)
    else:
        outtext = 'Tweets about ' + rand_word
        plot_tweets(lat, long, None)
        tweet_fig(outtext)

if api_choice == 3:
    print('All the tweets')
    which_api = 'statuses/filter' 
    terms =  {'locations':'-130,30,-60,47'}
    r = api.request(which_api,terms)
    numtweets = 500
    lat,long,hash,tweet = locationator(r, numtweets)
    badwords = bad_words()
    for i,w in enumerate(hash.copy()):
        if w in badwords:
            hash[i] = ''
    outtext = 'The last ' + str(numtweets)
    plot_tweets(lat, long, None, True)
    tweet_fig(outtext)


print(str(api_choice),outtext)


