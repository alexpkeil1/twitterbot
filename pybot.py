#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import mybotapi as mpi
import pytesseract
from PIL import Image #py 3 version (pillow)
from PIL import ImageFilter #py 3 version (pillow)
from subprocess import call
import numpy as np
import requests
import matplotlib.pyplot as plt
import time
import string
import os

outdir = '/tmp/'
#outdir = ''

os.mkdir(outdir+'rwfigs')

resp = requests.get("https://raw.githubusercontent.com/jonbcard/scrabble-bot/master/src/dictionary.txt")
english = {}
for word in resp.text.split('\n'):
    english[word] = 1


def process_local_image(path):
    image = Image.open(path)
    image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image, config="-psm 8")

#train up a random drawing algorithm
def random_walker(parms = (1, 1), totl = 5, plotter=True):
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
        plt.savefig(outdir + 'rwfig.jpg', dpi=100)
        fig.clf(1)
    return x, y, ltr


p = (np.random.random()*2, np.random.random()*2)
x,y,ltr = random_walker(p, totl=5, plotter=True)
outtext = process_local_image(outdir + 'rwfig.jpg')

mydict = {}
#while outtext.upper() not in english:
split = 0.8
while len(mydict)<1:
    numletters = np.random.randint(6)+6
    x,y,ltr = random_walker(p, totl=numletters, plotter=True)
    outtext = process_local_image(outdir + 'rwfig.jpg')
    if (((outtext.upper() in english) | (outtext in string.ascii_letters))
         & (outtext != '')):
        print(p, outtext)
        if outtext not in mydict:
            mydict[outtext] = (x,y)
        outfile = outdir + 'rwfigs/' + outtext + '.jpg'
        call(['cp', outdir + 'rwfig.jpg',  outfile])
        if np.random.random() > 0.9:
            p = ((np.random.random()-1) * split + (1 - split)*p[0], 
                 (np.random.random()-1) * split + (1 - split)*p[1])
        else:
            p = ((np.random.random()-1) * (1 - split) + split*p[0], 
                 (np.random.random()-1) * (1 - split) + split*p[1])
    else:
        if np.random.random() > 0.9:
            p = ((np.random.random()-1) * (1 - split) + split*p[0],
                 (np.random.random()-1) * (1 - split) + split*p[1])
        else:
            p = ((np.random.random()-1) * split + (1 - split)*p[0], 
                 (np.random.random()-1) * split + (1 - split)*p[1])
         


#filename=open(argfile,'r')
#f=filename.readlines()
#filename.close()



 



#for line in f:
    #api.update_status(line)
    #time.sleep(900)#Tweet every 15 minutes
    
api = mpi.api
    
file = open(outfile, 'rb')
data = file.read()
r = api.request('statuses/update_with_media', {'status': 'Machines speaking machine: ' + outtext}, {'media[]':data})
print(r.status_code)    