#!/usr/bin/env python
import sys
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

os.chdir(base + "repo/twitterbot/")
import _settings as mpi # need to cd into this directory
os.environ['PATH'] += "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
t_keys = mpi.get_keys()
outdir = '/tmp/'
path = base + "repo/twitterbot/"


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
    try:
        head = requests.head(url, verify=verify, allow_redirects=allow_redirects)
        stat = (head.status_code == 200)
        type = (head.headers['content-type'].lower().find('text/html') > -1)
    except:
        stat = False
        type = False
    return stat and type


def find_links(base_url = 'http://www.unc.edu/', pr=0, debug=False):
    '''
    Make a set of all unique (valid HTML) links from a single web page
    '''
    if debug:
        vfy = False
    else:
        vfy = True
    if pr == 1: print('Finding links connected to ' + base_url + '. This may take a while.')
    links = set([])
    #try:
    page = requests.get(base_url, verify=vfy, allow_redirects=True)
    #except:
    if debug: print(base_url, 'Bad request, skipping')
    #else:
    try:
        doc = html.fromstring(page.text.encode('utf-8'))
    except:
        if debug: print(base_url, 'not HTML or no response, skipping')
    else:
        hrefs = list(set([a.get('href') for a in doc.cssselect('a')]))
        while len(hrefs) > 0:
            ln = hrefs.pop()
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
                links.add(url)
                if pr == 2: print(url)
    if pr == 1: print("Found", str(len(links)), "Links")
    links = ban_urls(links)
    return(links)



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
    #print("Image joined {}".format(url))
    return url


def addURLtolist(URL):
    '''
    Add the newest URLs to the file with old URLs
    '''
    with open(base + "repo/twitterbot/img_urls.txt", 
              'a', encoding='utf-8') as f:
        f.writelines(URL + '\n')


def addURLtoTweetedlist(URL):
    '''
    Add the newest URLs to the file with old URLs
    '''
    with open(base + "repo/twitterbot/img_urls_tweeted.txt", 
              'a', encoding='utf-8') as f:
        f.writelines(URL + '\n')


def alreadyTweetedlist():
    '''
    Add the newest URLs to the file with old URLs
    '''
    tweets = set([])
    with open(base + "repo/twitterbot/img_urls_tweeted.txt", 
              'r', encoding='utf-8') as f:
        for URL in f.readlines():
            tweets.add(URL.strip().replace('\n', '  ').replace('\r', '  '))
    return tweets


def cleanURLlist():
    '''
    Clean up the URL list
    '''
    fl = "repo/twitterbot/img_urls.txt"
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


def readimgURLfile():
    '''
    get URLs from the file with old URLs
    '''
    URLlist=[]
    fl = "repo/twitterbot/img_urls.txt"
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
    fl =  "repo/twitterbot/urls.txt"
    with open(base + fl, 'r', encoding='utf-8') as f:
        for URL in f.readlines():
            URLlist.append(URL)
        URLset = set(URLlist)
    return URLset


def get_imgURLs(base_url, debug = True):
    imrefs = None
    #print("getting images")
    try:
        page = requests.get(base_url, verify=True, allow_redirects=True, timeout=15)
    except:
        if debug: print(base_url, 'Bad request, skipping')
    else:
        try:
            theHTML = html.fromstring(page.text.encode('utf-8'))
        except:
            if debug: print(base_url, 'not HTML or no response, skipping')
            imraw = []
        else:
            imraw = ban_urls(list(set([a.get('src') for a in theHTML.xpath('//a//img')])))
        try:
            assert not isinstance(imraw, str)
        except:
            #print('raw image string {}'.format(imraw))
            imrefs = validate_image_link(base_url, imraw)
        else:
            #print('raw image list {}'.format(imraw))
            imrefs = set([validate_image_link(base_url, ln) for ln in imraw])
    #print(imrefs)
    return list(imrefs)


def get_text(theURL):
    #print('getting text')
    try:
        resp = requests.get(theURL)
        theHTML = html.fromstring(resp.text)
        alltheA = theHTML.cssselect('a')
        alltheP = theHTML.cssselect('p')
        theElems = ' '.join([a.text for a in alltheA if a.text is not None])
        thePars = ' '.join([p.text for p in alltheP if p.text is not None])
        ret = theElems + thePars
    except:
        ret = ''
    return ret
    #return thePars


def pick_suitable_URL(outlinks):
    '''
    Given a list of URLs, find one (at random) and find all images, text
     associated with that URL. If the text is suitably long, and there
     are images, then output the URL, a list of images, and the text
    '''
    li = 0
    lt = 0
    random.shuffle(outlinks)
    while (li < 1) | (lt < 400):
        try:
            thenewURL = outlinks.pop()
            #print("PSU {}".format(thenewURL))
        except:
            # return empty variables if no suitable links are found
            return '', [], []
        else:
            #print("Trying {}".format(thenewURL))
            theTxt = get_text(thenewURL)
            images = get_imgURLs(thenewURL)
            images = ban_urls(images)
            random.shuffle(images)
            li = len(images)
            lt = len(theTxt)
    return thenewURL, images, theTxt


def make_mask(im):
    imrgb = im.convert('RGBA')
    imgdat = np.array(imrgb)
    r,g,b,a = imgdat.T
    black = (0,0,0, 255)
    white = (255, 255, 255, 255)
    r,g,b,a = imgdat.copy().T
    #thresh = int(np.mean(imgdat))
    thresh = 100
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
                'feedback', 'izquotes', 'subscribe', 'header',
                'gift', '404', 'store', 'Banner', 'banner'
                ]
    for u in urls:
        keep = True
        for w in banwords:
            try:
                if u.lower().find(w) > -1:
                    keep = False
            except:
                u = ''
        if keep:
            newurls.append(u)
    return newurls



def get_image_size(imgURL):
    '''
    Find size for an image at a given URL, return 0,0 if any errors arise
    '''
    try:
        #print(imgURL)
        im = Image.open(urllib.request.urlopen(imgURL))
    except:
        return (0, 0)
    else:
        return im.size[0], im.size[1]


def get_all_the_stuff(urls):
    '''
    For a list of URLs, do the following:
        cull from the list any urls with some words indicating dumb links
        randomly choose from the list one of the urls
        get all links from that URL, combine into a list
        given that list, enumerate the text and images from each URL
    '''
    link = False
    urls = ban_urls(urls)
    random.shuffle(urls)
    while not link:
        # take a single URL at random
        theURL = random.choice(urls)
        # find all links associated with that link
        outlinks = [theURL] + list(find_links(theURL))
        outlinks = ban_urls(outlinks)
        # find a suitable page from the list of links
        baseURL, images, theTxt = pick_suitable_URL(outlinks)
        try:
            assert(baseURL != '')
        except:
            print("Error description:", sys.exc_info()[0])
            pass
        else:
            #print("Getting images and links")
            ret_images=[]
            try:
                assert not isinstance(images, str)
            except:
                #print("Image is a string")
                dim0, dim1 = get_image_size(images)
                #print('Dims {}X{}'.format(dim0, dim1))
                if (dim0 > 150) or (dim1 > 150):
                    #print("adding image")
                    ret_images = images
                if len(theTxt) > 10:
                    #print('Found 1 suitable image')
                    link = True
            else:
                #print("Images in a list")
                for im in images:
                    #print(im)
                    dim0, dim1 = get_image_size(im)
                    #print('Dims {}X{}'.format(dim0, dim1))
                    if (dim0 > 150) or (dim1 > 150):
                        #print("adding image")
                        ret_images += [im]
                if (len(ret_images) > 0) and (len(theTxt) > 10):
                    link = True
                    #print('Found {} suitable images'.format(len(ret_images)))
                #else:
                    #print('Found {} suitable images'.format(len(ret_images)))                    
    return baseURL, ret_images, theTxt


def makeWC(theText, mask_image, mw):
    SW = STOPWORDS.copy()
    mywords = ['and', 'the', 'to', 'by', 'in', 'of', 'up',
           'Facebook', 'Twitter', 'Pinterest', 'Flickr',
           'Google', 'Instagram', 'login', 'Login', 'Log',
           'website', 'Website', 'Contact', 'contact',
           'twitter', 'Branding', 'Tweet', 'pic', 'location',
           'Details'
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
    wc_background = wc_background.filter(ImageFilter.SMOOTH)
    return wc_background


# check the list of urls, if there are enough, pull from there, otherwise use 
# default list
try:
    cleanURLlist()
    urls = list(readimgURLfile()) # urls from known image file
except:
    urls = ''
if (len(urls) < 100) and (random.random() < 0.85):
    # seed urls
    urls = [
        'http://www.worldwildlife.org/',
        'https://www.oxfam.org/en/frontpage',
        'http://www.doctorswithoutborders.org/',
        'http://www.ewb-usa.org/',
        'https://www.splcenter.org/',
        'http://www.ucsusa.org/',
        'http://www.nature.com/index.html',
        'http://www.idealist.org/',
        'http://blogs.nature.com/scientificdata/',
        'http://en.unesco.org/',
        'https://www.farmaid.org/',
        'https://www.hrw.org/',
        'http://www.ufw.org/'
        ]
    if random.random() > 0.95:
        print("Using all URLs")
        urls = list(getallURLS())
    else:
        print("Using seed URLs")
else:
    print("Using image URLs")

urls = ban_urls(urls)
if len(sys.argv) > 1:
    print(sys.argv)
    urls = [sys.argv[1], sys.argv[1]]
baseURL, images, theTxt = get_all_the_stuff(urls)
print('Found {} images and {} words at {}'.format(len(images), len(theTxt), 
        baseURL))

# keep the really good ones
if (len(images) > 5) and (len(theTxt) > 500):
    print("Adding {} to URL file".format(baseURL))
    addURLtolist(baseURL)
    

# find an image of a big enough size
#print("Images:")
#print(images)

while len(images) == 0:
    baseURL, images, theTxt = get_all_the_stuff(urls)
    print("{} images at {}".format(len(images, baseURL)))

assert not isinstance(images, str)
while len(images) > 0:
    random.shuffle(images)
    imgURL = images.pop()
    print(imgURL)
    if imgURL not in alreadyTweetedlist():
        im = Image.open(urllib.request.urlopen(imgURL))
        if ((im.size[0] >= 500) | (im.size[1] >= 500)) and (im.size[0] + im.size[1] >= 700):
            print(im.size)
            chosen = True
            break
    
print("Image selected")
addURLtoTweetedlist(imgURL)
# embiggen 
origsize = im.size
while (im.size[0] < 600) | (im.size[1] < 600):
    im = im.resize((int(im.size[0]*1.2), int(im.size[1]*1.2)), Image.ANTIALIAS)

# emsmallen
while (im.size[0] > 1600) | (im.size[1] > 1600):
    im = im.resize((int(im.size[0]*0.9), int(im.size[1]*0.9)), Image.ANTIALIAS)


# turn into mask
maskim = make_mask(im)


#sometimes use the mask, sometimes the original image
if (random.random() < 0.6) and ((origsize[0] >= 600) or (origsize[1] >= 600)):
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
    r = api.request('statuses/update_with_media', {'status': '{}'.format(baseURL)}, {'media[]':bytearray(data)})
    print(r.status_code)    
