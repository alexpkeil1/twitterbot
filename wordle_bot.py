#!/usr/bin/env python

import matplotlib.pyplot as plt
from wordcloud import WordCloud
import requests
from lxml import html
from numpy import random
from TwitterAPI import TwitterAPI
import os


if os.sys.platform == 'darwin':
    base = "/Users/akeil/"
else:
    base = "/home/akeil/"


os.chdir(base + "Documents/programming_examples/python/twitterbot/")
import mybotapi as mpi  # need to cd into this directory
os.environ['PATH'] += "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

t_keys = mpi.get_keys()
outdir = '/tmp/'


path = base + "Documents/programming_examples/python/twitterbot/"
with open('{}urls.txt'.format(path)) as fu:
    lns = 0
    for line in fu:
        lns += 1
    rdln = random.random_integers(lns)


print(lns)
theElems = ''
while len(theElems.split(' ')) < 100:
    lns2 = 0
    with open('{}urls.txt'.format(path)) as fu:
        for line in fu:
            if lns2 == rdln:
                theURL = line
            lns2 += 1
    resp = requests.get(theURL)
    theHTML = html.fromstring(resp.text)
    alltheA = theHTML.cssselect('a')
    theElems = ' '.join([a.text for a in alltheA if a.text is not None])


wordcloud = WordCloud(
#                max_font_size=80, 
                relative_scaling=0, 
                prefer_horizontal=.98, 
                stopwords='',
                background_color='white',
                max_words=60
                ).generate(theElems)
plt.figure()
plt.imshow(wordcloud)
plt.axis("off")
outfile = '{}wordle.png'.format(outdir)
plt.savefig(outfile)



api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
print("Tweeting about " + outtext)
    
with open(outfile, 'rb') as file:
    data = file.read()
    r = api.request('statuses/update_with_media', {'status': theURL}, {'media[]':data})
    print(r.status_code)    
