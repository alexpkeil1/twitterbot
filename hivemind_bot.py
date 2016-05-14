#!/usr/bin/env python
from TwitterAPI import TwitterAPI
from mpl_toolkits.basemap import Basemap
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

root = base + "/Documents/programming_examples/python/twitterbot/"
os.chdir(root)
# set twitter api parameters
import mybotapi as mpi # need to cd into this directory
t_keys = mpi.get_keys()
api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])

def process_search(searchURL):
    headers = {'user-agent': 'random_image_bot/0.10'}
    try:
        resp = requests.get(searchURL, headers=headers)
    except: 
        print('failed at searching... oh well')
    try:    
        thePage = html.fromstring(resp.text.encode("ascii","ignore"))
    except: 
        print('failed at converting html... oh well')
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


def plot_tweets(lat, long, text):
    plt.style.use('ggplot')
    lon_0 = min(long) + 1*np.sign(long[0]) #further west if negative, further east if not
    lon_1 = max(long) - 1*np.sign(long[0])
    lat_0 = min(lat) - 1*np.sign(lat[0])
    lat_1 = max(lat) + 1*np.sign(lat[0])
    # create figure and axes instances
    plt.clf()
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111)
    # create polar stereographic Basemap instance.
    m = Basemap(llcrnrlat=lat_0,urcrnrlat=lat_1, llcrnrlon=lon_0,urcrnrlon=lon_1, resolution='l')
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    p = ax.plot(long, lat, 'p')
    if text is not None:
        for i, ht in enumerate(text):
            ax.annotate(ht, (long[i], lat[i]))
    plt.savefig('/tmp/twitmap.png')


def locationator(r = {}, ntweets=10):
    lat,long,hash,tweet = [],[],[],[]
    count = 0
    for tweet in r:
        try:
            silent = False
            lat.append(tweet['coordinates']['coordinates'][1])
            long.append(tweet['coordinates']['coordinates'][0])
        except:
            silent = True
        else:
            if not silent:
                count += 1
                try:
                    hash.append(tweet['entities']['hashtags'][0]['text'])
                    hash.append(tweet['entities']['hashtags'][0]['text'])
                except:
                    silent = True
                else:
                    print(tweet['text'], str(count))
                    hash.append('')
            if len(lat) > ntweets:
                hash = hash[::-1][1:]
                print(len(lat), len(long), len(hash))
                break
    return lat,long,hash,tweet


def tweet_fig(outtext):
    with open('/tmp/twitmap.png', 'rb') as file:
        data = file.read()
        r = api.request('statuses/update_with_media', {'status': outtext}, {'media[]':data})
        return r.status_code

def tweet_text(outtext):
    r = api.request('statuses/update', {'status': outtext})
    return r.status_code


api_choice = random.choice(3)


if api_choice == 0:
    print('Hashtag map')
    which_api = 'statuses/filter' 
    terms =  {'locations':'-130,30,-60,47'}
    r = api.request(which_api,terms)
    lat,long,hash,tweet = locationator(r)
    badwords = bad_words()
    for i,w in enumerate(hash.copy()):
        if w in badwords:
            hash[i] = ''
    outtext = '#hashtagmap'
    plot_tweets(lat, long, hash)
    tweet_fig(outtext)

elif api_choice == 1:
    rand_word = get_common_word()
    print('Streaming search lottery:', rand_word)
    which_api = 'statuses/filter' 
    terms =  {'track': rand_word, 'locations':'-130,30,-60,47'}
    r = api.request(which_api,terms)
    lat,long,hash,tweet = locationator(r,10)
    if len(lat) == 0:
        outtext = '*sigh* Nobody tweets about ' + rand_word + ' anymore'
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
    lat,long,hash,tweet = locationator(r,10)
    if len(lat) == 0:
        outtext = '*sigh* Nobody tweets about ' + rand_word + ' anymore'
        tweet_text(outtext)
    else:
        outtext = 'Tweets about ' + rand_word
        plot_tweets(lat, long, None)
        tweet_fig(outtext)


print(str(api_choice),outtext)


