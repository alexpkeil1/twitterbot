#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
##############################################################################
# Author: Alex Keil
# Program: random_ocr_bot.py
# Language: Python 3.5 (Tested on OS-X, Xubuntu)
# Date: Wednesday, May 4, 2016 at 6:23:09 PM
# Project: twitter bot
# Description: send a tweet with an OCR word using the TwitterAPI module
# Keywords:
# Released under GNU Gen. Pub. Lic.: http://www.gnu.org/copyleft/gpl.html
##############################################################################
import pytesseract
from PIL import Image #py 3 version (pillow)
from PIL import ImageFilter
from subprocess import call
import numpy as np
import requests
import matplotlib.pyplot as plt
import string
import os
from TwitterAPI import TwitterAPI
import os
import time
if os.sys.platform == 'darwin':
    base = "/Users/akeil/"
else:
    base = "/home/akeil/"
os.chdir(base + "repo/twitterbot/")
import _settings as mpi # need to cd into this directory
os.environ['PATH'] += "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

t_keys = mpi.get_keys()
outdir = '/tmp/'

# some testing of version
try:
    os.mkdir(outdir+'rwfigs')
except:
    print("Directory exists")

# find all words in english dictionary - read into python dictionary
resp = requests.get("http://ejohn.org/files/dict/ospd4.txt")
english = {}
for word in resp.text.split('\n'):
    english[word.upper()] = 1


def process_local_image(path):
    '''
    Sharpen image for OCR. Perform OCR and output rendered text.
    '''
    image = Image.open(path)
    image.filter(ImageFilter.SHARPEN) # required when running on osx
    return pytesseract.image_to_string(image, config="-- psm 8")


#random drawing algorithm
def random_walker(parms = (1, 1), totl = 5, plotter=True):
    '''
    Draw a set of characters of lenght totl using a random walk.
    (optionally) turn the figure into an image for OCR
    '''
    x, y, ltr = [1], [1], [1]
    lastxstep, lastystep = 0, 0
    nlines = 20
    for step in range(1, totl*nlines):
        if step % nlines == 0:
            ltr.append(ltr[step-1] + 1)
            x.append(max(x) + 5)
            y.append(1)
            lastxstep, lastystep = 0, 0
        else:
            xs1 = np.random.random() * parms[0]
            ys1 = np.random.random() * parms[1] / totl
            xs2 = np.sign(np.random.random() - 0.5)
            ys2 = np.sign(np.random.random() - 0.5)
            xstep = xs1 * xs2
            ystep = ys1 * ys2
            x.append(x[step-1] + xstep + lastxstep)
            y.append(y[step-1] + ystep + lastystep)
            ltr.append(ltr[step-1])
            lastxstep, lastystep = xstep, ystep
    if plotter:
        fig = plt.figure(1)
        fig.set_size_inches(totl, 1)
        for l in range(1, totl+1):
            plt.plot([x[i] for i,j in enumerate(ltr) if j==l],
                     [y[i] for i,j in enumerate(ltr) if j==l], 
                     color='k', linewidth=2)
        plt.xlim((min(x), max(x)))
        plt.ylim((min(y), max(y)))
        plt.axis('off')
        plt.savefig(outdir + 'rwfig.png', dpi=100)
        fig.clf(1)
    return x, y, ltr


# Finding computer language by brute force
# repeat the creation of letters until a recognizable word occurs
p = (np.random.random()*2, np.random.random()*2)
mydict = {}
split = 0.8
print('starting ocr ' + ':'.join([str(i) for i  in time.localtime()]))
ct = 0
while len(mydict)<1:
    numletters = np.random.randint(3)+5
    x,y,ltr = random_walker(p, totl=numletters, plotter=True)
    outtext = process_local_image(outdir + 'rwfig.png')
    while not ct:
      print('First ocr done')
      ct +=1
    if ((outtext.upper() in english) & (len(outtext) == numletters)):
        if outtext not in mydict:
            mydict[outtext] = (x,y)
        outfile = outdir + 'rwfigs/' + outtext + '.png'
        call(['cp', outdir + 'rwfig.png',  outfile])
    else:
        if np.random.random() > 0.9:
            p = ((np.random.random()-1) * (1 - split) + split*p[0],
                 (np.random.random()-1) * (1 - split) + split*p[1])
        else:
            p = ((np.random.random()-1) * split + (1 - split)*p[0], 
                 (np.random.random()-1) * split + (1 - split)*p[1])




# now tweet the result
# dictionary with private keys (not in public repository)
api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
print("Tweeting about " + outtext)
    
with open(outfile, 'rb') as file:
    data = file.read()
    r = api.request('statuses/update_with_media', {'status': 'Machines speaking machine: ' + outtext}, {'media[]':data})
    print(r.status_code)    