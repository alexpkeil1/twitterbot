#!/usr/bin/env python
###########################################################################
# Author: Alex Keil
# Program: network_bot.py
# Language: Python 3.5 (Tested on OS-X)
# Date: Saturday, May 7, 2016 at 11:53:10 AM
# Project: twitterbot
# Description: For a given 'seed' url, find the network of links
#  from the page for N layers
# Keywords: crawler, graphical networks
# Released under GNU Gen. Pub. Lic.: http://www.gnu.org/copyleft/gpl.html
###########################################################################
# -*- coding: utf-8 -*-
import tempdir
import time
import requests
import os
import pygraphviz as pgv
from TwitterAPI import TwitterAPI
from urllib.parse import urljoin
from urllib.parse import urlparse
from lxml import html
from numpy import random

tic = time.time()

# ask if OSX
if os.sys.platform == 'darwin':
    base ="/Users/akeil/"
else:
    base = "/home/akeil/"

root = base + "repo/twitterbot/"
os.chdir(root)

# set twitter api parameters
import _settings as mpi # need to cd into this directory
t_keys = mpi.get_keys()


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


def get_levels(base_url = 'http://andrewgelman.com/', level = 0, pr=0):
    '''
    Todo: implement *something* to avoid spider traps
    '''
    # level 0, create a set of all the links from the base url
    print('Finding 1 degree links for first url...')
    relDB = {}
    relDB[base_url] = find_links(base_url)
    # level 1, add a node for all subnodes of base url, add link sets for each
    if level > 0:
        print('Finding 2 degree links to first url...')
        for subnode in relDB[base_url]:
            relDB[subnode] = find_links(subnode, pr=pr)
    # level 2+, for each set of links for each subnode, create or add to existing
    #  nodes
    #add some more if there are not many
    if(len(relDB) < 8):
        level += 1
    if(len(relDB) < 4):
        level += 1
    ct = 3
    while level > 1:
        print('Finding ', ct , ' degree links to first url...')
        ct += 1
        for node in relDB.copy():
            for subnode in relDB[node].copy():
                if subnode not in relDB:
                    fl = find_links(subnode, pr=pr)
                    if fl is not None:
                        relDB[subnode] = fl
        level -= 1
    addURLstolist(list(relDB.keys())) # add main links to master list
    return relDB


# go only to roots
def trim_db(relDB):
    '''
    Create a new database from a larger database of links, where the
     nodes and subnodes are only the site roots
    '''
    newDB = {}
    countDB = {}
    for node in relDB:
        setlinks = set([])
        if relDB[node] is not None:
            for subnode in relDB[node]:
                setlinks.add(site_root(subnode))
                if site_root(subnode) not in countDB:
                    countDB[site_root(subnode)] = 1
                else:
                    countDB[site_root(subnode)] += 1
            relDB[node] = setlinks
            if site_root(node) in newDB:
                newDB[site_root(node)] |= relDB[node]
            else:
                newDB[site_root(node)] = relDB[node]
    return countDB, newDB


def lookupURLs():
    '''
    From a stored file of old URLs searched, turn the old URLs into a set
    '''
    pastURLs = {}
    with open(base + "repo/twitterbot/urls.txt", 
              'r', encoding='utf-8') as f:
        for l in f.readlines():
            pastURLs[l.strip().replace('\n', '  ').replace('\r', '  ')] = 1
    return set(pastURLs)


def addURLstolist(URLlist):
    '''
    Add the newest URLs to the file with old URLs
    '''
    URLset = set(URLlist)
    with open(base + "repo/twitterbot/urls.txt", 
              'a', encoding='utf-8') as f:
        for URL in URLset:
            f.writelines(URL + '\n')


def get_all_nodes(DB):
    '''
    Finding all unique urls for the given relational DB (dictionary)
    '''
    all_uniques = set([])
    for key, val in DB.items():
        all_uniques.add(key)
        for v in val:
           all_uniques.add(v)
    return all_uniques


def get_all_edges(DB):
    '''
    output a list of tuples with all pairwise connections
     in a given relational db (dictionary)
    '''
    all_pair_tuples = []
    for key, val in DB.items():
        pt = [(key, v) for v in val]
        all_pair_tuples += pt
    return all_pair_tuples    



def network_plot(startURL, DB, neatoloc = '/usr/local/bin'):
    # using pygraphviz
    G = pgv.AGraph(strict=False, directed=True)
    G.add_node(site_root(startURL))
    G.add_edges_from(get_all_edges(DB))
    # graph
    G.graph_attr['label'] = "2-degree network: " + site_root(startURL)
    G.graph_attr['labelloc'] = 't'
    G.graph_attr['overlap'] = 'false'
    # nodes
    G.node_attr['shape'] = 'none'
    G.node_attr['ratio'] = 'compress'
    G.node_attr['root'] = site_root(startURL)
    # edges
    G.edge_attr['color'] = 'blue'
    # plot it
    outfile = tempdir.tempfile.gettempdir() + '/img.png'
    if outfile == 'img.png': outfile = '/tmp' + outfile
    os.environ['PATH'] += ":" + neatoloc  # need to find neato, this brings in the correct path
    G.draw(outfile, prog='neato')
    print('image at: ' + outfile)
    return outfile
    

# urls = ['https://www.gop.com/', 'https://democrats.org/']


# pick a URL at random, form a relational database
countDB = {}
while len(countDB) < 10:
    urls = list(lookupURLs())
    random.shuffle(urls)
    startURL = urls[0]
    # startURL = 'https://www.gop.com/'
    relationalDB = get_levels(base_url = startURL, level = 1, pr=0)
    countDB, trimmedDB = trim_db(relationalDB)


outfile = network_plot(startURL, trimmedDB, neatoloc = '/usr/local/bin')


api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
with open(outfile, 'rb') as file:
    data = file.read()
    r = api.request('statuses/update_with_media', {'status': '2-degree network: ' + startURL}, {'media[]':data})
    if r.status_code == 200: print("Success")
    else: print("Sadly, this went untweeted")

toc = time.time()
print("total minutes runtime: " + str(round((toc-tic)/60, 3)))