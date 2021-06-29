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


os.chdir(base + "repo/twitterbot/")
import _settings as mpi # need to cd into this directory
os.environ['PATH'] += "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

t_keys = mpi.get_keys()
outdir = '/tmp/'


path = base + "repo/twitterbot/"
with open('{}img_urls.txt'.format(path)) as fu:
    lns = 0
    for line in fu.readlines():
        lns += 1


theElems = ''
loops = 0
while len(theElems.split(' ')) < 400:
    rdln = random.random_integers(lns)
    lns2 = 0
    with open('{}img_urls.txt'.format(path)) as fu:
        for line in fu.readlines():
            if lns2 == rdln:
                theURL = line
            lns2 += 1
    resp = requests.get(theURL)
    theHTML = html.fromstring(resp.text)
    alltheA = theHTML.cssselect('a')
    theElems = ' '.join([a.text for a in alltheA if a.text is not None])
    loops += 1
    print(len(theElems.split(' ')))


if random.random()<0.5:
    col = 'white'
else:
    col = 'black'

if random.random()<0.5:
    col = 'white'
else:
    col = 'black'

wordcloud = WordCloud(
#                max_font_size=80, 
                relative_scaling=0, 
                prefer_horizontal=random.uniform(0.5, 1), 
                stopwords='',
                background_color=col,
                max_words=200
                ).generate(theElems)
plt.figure()
plt.imshow(wordcloud)
plt.axis("off")
outfile = '{}wordle.png'.format(outdir)
plt.savefig(outfile)




api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
print("After {} loops, tweeting a wordle for {}".format(loops, theURL))
    
with open(outfile, 'rb') as file:
    data = file.read()
    r = api.request('statuses/update_with_media', {'status': 'What is being discussed at {}? '.format(theURL)}, {'media[]':data})
    print(r.status_code)    
