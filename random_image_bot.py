__version__ = 0.1

import requests
from PIL import Image
import random
from lxml import html
import shutil
import os
from TwitterAPI import TwitterAPI


def rand_words(numwords, dictionary):
    return ' '.join(random.sample(list(dictionary), numwords)).lower()


def image_search_url(terms):
    baseurl = 'https://www.google.com/search?&safe=active&tbm=isch&tbs=isz:l&q='
    return baseurl + '+'.join(terms.split(' '))


def process_search(searchURL):
    headers = {'user-agent': 'random_image_bot/0.10'}
    try:
        resp = requests.get(searchURL, headers=headers)
    except: 
        print('failed at searching... oh well')
    try:    
        thePage = html.fromstring(resp.text.encode('utf-8'))
    except: 
        print('failed at converting html... oh well')
    return thePage


def get_img_urls(thePage):
    hrefs = list(set([a.get('src') for a in thePage.cssselect('img')]))
    img_urls = []
    for ln in hrefs:
        try:
            full_link = ln.find('http')
        except :
            print('no images')
        img_urls.append(ln)
    return img_urls


def dl_image(img):
    loc = '/tmp/tmpfileasdfaeasfasdfasdgasdg'
    with open(loc, 'wb') as f:
        img.raw.decode_content = True
        shutil.copyfileobj(img.raw, f)
    return loc


def make_png(loc):
    '''
    Save image as png
    '''
    newloc = '/tmp/img_searchiwoeruowlkjalsjkdf.png'
    image = Image.open('/tmp/tmpfileasdfaeasfasdfasdgasdg')
    image.save(newloc, format='png')
    return newloc


def tweet_with_image(tweet_text, png_file):
    # now tweet it
    # ask if OSX
    if os.sys.platform == 'darwin':
        base ="/Users/akeil/"
    else:
        base = "/home/akeil/"
    root = base + "repo/twitterbot/"
    os.chdir(root)
    # set twitter api parameters
    import mybotapi as mpi # need to cd into this directory
    t_keys = mpi.get_keys()
    api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
    with open(png_file, 'rb') as file:
        data = file.read()
        r = api.request('statuses/update_with_media', {'status': tweet_text}, {'media[]':data})
        if r.status_code == 200: 
            print("Success; Tweeted: " + tweet_text)
        else: print("Sadly, this went untweeted")


if __name__=="__main__":
    #get English dictionary
    resp = requests.get("http://ejohn.org/files/dict/ospd4.txt")
    english = {}
    for word in resp.text.split('\n'):
        english[word.upper()] = 1
    tweet_text = rand_words(random.choice([1,2]), english)
    #tweet_text = rand_words(1, english)
    searchURL = image_search_url(tweet_text)
    thePage = process_search(searchURL)
    imgs = get_img_urls(thePage)
    tweet_image = random.choice(imgs)
    img = requests.get(tweet_image, stream=True)
    path = dl_image(img)
    png_file = make_png(path)
    print(png_file)
    print(searchURL)
    tweet_with_image(tweet_text, png_file)


