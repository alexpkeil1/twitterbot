#!/usr/bin/env python

import requests
import os
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
from PIL import Image, ImageFilter
from lxml import html
from numpy import random
from TwitterAPI import TwitterAPI
from wordcloud import WordCloud, STOPWORDS
from urllib.parse import urljoin
from urllib.parse import urlparse


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


def site_root(url):
    '''
    Find the root name (hostname) of a url
    '''
    urlp = urlparse(url)
    if urlp.hostname is not None:
        rooturl = urlp.hostname
    else:
        rooturl = urlp.path
    return rooturl.replace('www.', '')


def valid_html(url, verify=True, allow_redirects=False):
    valid = False
    try:
        head = requests.head(url, verify=verify, allow_redirects=False)
        stat = (head.status_code == 200)
        type = (head.headers['content-type'].lower().find( 
                     'text/html') > -1)
    except: 
        True # fade to black
    else:
        if stat and type:
            valid = True
    return valid


def find_links(base_url = 'http://www.unc.edu/', pr=1, debug=False):
    '''
    Make a set of all unique (valid HTML) links from a single web page
    '''
    if debug:
        vfy = False
    else:
        vfy = True
    if pr == 1: print('Finding links connected to ' + base_url + '. This may take a while.')
    links = set([])
    try:
        page = requests.get(base_url, verify=vfy, allow_redirects=False)
    except:
        # extremely crude way to handle exceptions here
        # but I suppose OK since it doesn't matter why
        # the page did not load, only that it did not
        if debug: print(base_url, 'Bad request, skipping')
    else:
        try:
            doc = html.fromstring(page.text.encode('utf-8'))
        except:
            if debug: print(base_url, 'not HTML or no response, skipping')
        else:
            hrefs = list(set([a.get('href') for a in doc.cssselect('a')]))
            for ln in hrefs:
                try:
                    full_link = ln.find('http')
                except AttributeError:
                    url = base_url
                else:
                    if full_link == 0:
                        url = ln
                    else:
                        url = urljoin(base_url, ln)
                if url not in links: 
                    if valid_html(url, verify=vfy, allow_redirects=False): 
                        links.add(url)
                        if pr == 2: print(url)
    if pr == 1: print("Found", str(len(links)), "Links")
    return(links)


def get_random_images_and_text(outlinks):
    try:
        thenewURL = outlinks.pop()
    except:
        thenewURL = theURL
    else:
        theTxt = ''
        images = ''
        while (len(images) < 5) | (len(theTxt) < 400):
            theTxt = get_text(thenewURL)
            images = imgURLs(thenewURL)
            try:
                thenewURL = outlinks.pop()
            except:
                # default to the original URL
                thenewURL = theURL
                break
            images = list(set(images))
        return thenewURL, images, theTxt


def validate_image_link(base_url, imglink):
    try:
        full_link = imglink.find('http')
    except AttributeError:
        url = base_url
    else:
        if full_link == 0:
            url = imglink
        else:
            url = urljoin(base_url, imglink)
    return url


def addURLtolist(URL):
    '''
    Add the newest URLs to the file with old URLs
    '''
    with open(base + "Documents/programming_examples/python/twitterbot/img_urls.txt", 
              'a', encoding='utf-8') as f:
        f.writelines(URL + '\n')


def cleanURLlist():
    '''
    Clean up the URL list
    '''
    fl = "Documents/programming_examples/python/twitterbot/img_urls.txt"
    links = set([])
    with open(base + fl, 'r', encoding='utf-8') as f:
        for URL in f.readlines():
            links.add(URL.strip().replace('\n', '  ').replace('\r', '  '))
    links = sorted(list(links))
    links = ban_urls(links)
    with open(base + fl, 'w+', encoding='utf-8') as f:
        for URL in links:
            if URL is not '':
                f.writelines(URL + '\n')


def getimgURLS():
    '''
    get URLs from the file with old URLs
    '''
    URLlist=[]
    fl = "Documents/programming_examples/python/twitterbot/img_urls.txt"
    with open(base + fl, 'r', encoding='utf-8') as f:
        for URL in f.readlines():
            URLlist.append(URL)
    URLset = set(URLlist)
    return URLset


def getallURLS():
    '''
    get URLs from the file with old URLs
    '''
    URLlist=[]
    fl =  "Documents/programming_examples/python/twitterbot/urls.txt"
    with open(base + fl, 'r', encoding='utf-8') as f:
        for URL in f.readlines():
            URLlist.append(URL)
        URLset = set(URLlist)
    return URLset


def imgURLs(base_url, debug = True):
    imrefs = None
    try:
        page = requests.get(base_url, verify=True, allow_redirects=False)
    except:
        if debug: print(base_url, 'Bad request, skipping')
    else:
        try:
            theHTML = html.fromstring(page.text.encode('utf-8'))
        except:
            if debug: print(base_url, 'not HTML or no response, skipping')
        else:
            imrefs = ban_urls(list(set([a.get('src') for a in theHTML.xpath('//a//img')])))
    return imrefs


def get_text(theURL):
    resp = requests.get(theURL)
    theHTML = html.fromstring(resp.text)
    alltheA = theHTML.cssselect('a')
    alltheP = theHTML.cssselect('p')
    theElems = ' '.join([a.text for a in alltheA if a.text is not None])
    thePars = ' '.join([p.text for p in alltheP if p.text is not None])
    return theElems + thePars
    #return thePars


def make_mask(im):
    imrgb = im.convert('RGBA')
    imgdat = np.array(imrgb)
    r,g,b,a = imgdat.T
    black = (0,0,0, 255)
    white = (255, 255, 255, 255)
    r,g,b,a = imgdat.copy().T
    thresh = int(np.mean(imgdat))
    #thresh = 50
    col_index = ((r < thresh) | 
                 (g < thresh) | 
                 (b < thresh) |
                 (a < 255)
                 )
    col_index2 = ((r >= thresh) | 
                 (g >= thresh) | 
                 (b >= thresh) |
                 (a >= 255)
                 )
    # mask darker colors
    imgdat[col_index2.T] = white
    imgdat[col_index.T] = black
    # mask lighter colors
    #imgdat[col_index2.T] = black
    #imgdat[col_index.T] = white
    #return Image.fromarray(imgdat)
    return imgdat


def cover_img(top_img, bottom_img):
    for i in range(bottom_img.shape[0]):
        for j in range(bottom_img.shape[1]):
            #if background is white
            #if any(top_img[i,j,:3] < np.array([255,255,255])):
            # if background is black
            if any(top_img[i,j,:3] > np.array([0,0,0])):
                bottom_img[i,j,:] = top_img[i,j,:]
    return bottom_img


def bad_words():
    resp = requests.get("http://pastebin.com/raw/0L6nxiXE")
    badwords = set([])
    for word in resp.text.split('\n'):
        badwords.add(word)
    return badwords


def ban_urls(urls):
    newurls = []
    banwords = ["donat", "contact", "terms", "conditions", "podcasts"
                "twitter", "help", "about", "linkedin", "instagram"
                "facebook", "privacy-policy", "shop", "retail", 
                "products", "wifi", 'plugins', 'share', 'support',
                'registration', 'plugins', 'signup', 'giving',
                'promo', 'account', 'mail', 'itunes', 'sponsored',
                'product', 'corporate', '#', 'media', 'secure',
                'doubleclick', 'iads', 'financials', 'logo',
                'feedback', 'izquotes', 'subscribe'
                ]
    for u in urls:
        keep = True
        for w in banwords:
            if u.lower().find(w) > -1:
                keep = False
        if keep:
            newurls.append(u)
    return newurls



def get_image_size(imgURL):
    try:
        im = Image.open(urllib.request.urlopen(imgURL))
    except:
        return (0, 0)
    else:
        return im.size


def get_all_the_stuff(urls):
    link = False
    while not link:
        try:
            urls = ban_urls(urls)
            random.shuffle(urls)
            theURL = urls.pop()
            outlinks = [theURL] + list(find_links(theURL))
            random.shuffle(outlinks)
            baseURL, images, theTxt = get_random_images_and_text(outlinks)
        except:
            pass
        else:
            ret_images=[]
            for im in images:
                sz = get_image_size(im)
                if (sz[0]>300) or (sz[1]>300):
                    ret_images += im
            if (len(ret_images) > 0) and (len(theTxt) > 10):
                link = True
    return baseURL, ret_images, theTxt


def makeWC(theText, mask_image, mw):
    SW = STOPWORDS.copy()
    mywords = ['and', 'the', 'to', 'by', 'in', 'of', 'up',
           'Facebook', 'Twitter', 'Pinterest', 'Flickr',
           'Google', 'Instagram', 'login', 'Login', 'Log',
           'website', 'Website', 'Contact', 'contact',
           'twitter', 'Branding'
           ] + list(bad_words())
    [SW.add(w) for w in mywords]
    wordcloud = WordCloud(
                relative_scaling=0, 
                prefer_horizontal=random.uniform(0.5, 1), 
                stopwords=SW,
                background_color='black',
                max_words=mw, 
                mask = mask_image
                ).generate(theText)
    return wordcloud


def cloud_cover(wc, orig_image):
    wc_masked = wc.to_image().convert('RGBA')
    wc_new = cover_img( np.array(wc_masked), np.array(orig_image.convert('RGBA')))
    wc_background = Image.fromarray(wc_new)
    wc_background = wc_background.filter(ImageFilter.SMOOTH_MORE)
    return wc_background


# check the list of urls, if there are enough, pull from there, otherwise use 
# default list
try:
    cleanURLlist()
    urls = list(getimgURLS()) # urls from known image file
except:
    urls = ''

if (len(urls) < 100) and (random.random() < 0.85):
    # seed urls
    urls = [
        'http://www.worldwildlife.org/',
        'https://www.oxfam.org/en/frontpage',
        'http://www.doctorswithoutborders.org/',
        'http://www.gettyimages.com/',
        'http://www.ewb-usa.org/',
        'https://www.splcenter.org/',
        'http://www.ucsusa.org/',
        'http://www.nature.com/index.html',
        'http://www.idealist.org/'
        ]
    if random.random() > 0.75:
        urls = list(getallURLS())
else:
    print("Using image URLs")

urls = ban_urls(urls)

baseURL, images, theTxt = get_all_the_stuff(urls)
print('Found {} images and {} words'.format(len(images), len(theTxt)))

# keep the really good ones
if (len(images) > 20) and (len(theTxt) > 500):
    addURLtolist(baseURL)
    

# find an image of a big enough size
chosen = False
random.shuffle(images)
img = images.pop()
imgURL1 = validate_image_link(baseURL, img)
while not chosen:
    try:
        random.shuffle(images)
        img = images.pop()
        imgURL = validate_image_link(baseURL, img)
        #print(imgURL)
        imsize = get_image_size(imgURL)
    except:
        if imgURL == imgURL1:
            baseURL, images, theTxt = get_all_the_stuff(urls)
            print("starting over with {}".format(baseURL))
    else:
        if ((imsize[0] >= 400) | (imsize[1] >= 400)):
            chosen = True
        else:
            if imgURL == imgURL1:
                chosen = True

# embiggen 
im = Image.open(urllib.request.urlopen(imgURL))
origsize = im.size
while (im.size[0] < 600) | (im.size[1] < 600):
    im = im.resize((int(im.size[0]*1.2), int(im.size[1]*1.2)), Image.ANTIALIAS)

# emsmallen
while (im.size[0] > 1600) | (im.size[1] > 1600):
    im = im.resize((int(im.size[0]*0.9), int(im.size[1]*0.9)), Image.ANTIALIAS)


# turn into mask
maskim = make_mask(im)


#sometimes use the mask, sometimes the original image
if (random.random() < 0.95) and ((origsize[0] >= 400) or (origsize[1] >= 400)):
    print("Saving cloud + image")
    cloud = makeWC(theTxt, mask_image=maskim, mw=60)
    data = cloud_cover(cloud, im)
elif (random.random() < 0.9):
    print("Saving cloud + mask")
    cloud = makeWC(theTxt, mask_image=maskim, mw=100)
    data = cloud_cover(cloud, Image.fromarray(maskim))
else:
    cloud = makeWC(theTxt, mask_image=maskim, mw=150)
    print("Saving cloud only")
    data = cloud.to_image()
#data.show()

plt.figure()
plt.imshow(data)
plt.axis("off")
outfile = '{}wordle_mask.png'.format(outdir)
plt.savefig(outfile)

#data.show()


api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
print("Tweeting a wordle on {}, from {}".format(imgURL, baseURL))

with open(outfile, 'rb') as file:
    data = file.read()    
    r = api.request('statuses/update_with_media', {'status': '{}'.format(baseURL)}, {'media[]':data})
    print(r.status_code)    
