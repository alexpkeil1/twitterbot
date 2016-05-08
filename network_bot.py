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
 
import requests
import os
import pygraphviz as pgv
from TwitterAPI import TwitterAPI
from urllib.parse import urljoin
from urllib.parse import urlparse
from lxml import html
from numpy import random

# ask if OSX
if os.sys.platform == 'darwin':
    base ="/Users/akeil/"
else:
    base = "/home/akeil/"

root = base + "Documents/programming_examples/python/twitterbot/"
os.chdir(root)

# set twitter api parameters
import mybotapi as mpi # need to cd into this directory
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


def find_links(base_url = 'http://www.unc.edu/', pr=True, debug=False):
    '''
    Make a set of all unique (valid HTML) links from a single web page
    '''
    if debug:
        vfy = False
    else:
        vfy = True
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
            doc = html.fromstring(page.text)
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
                if valid_html(url, verify=vfy, allow_redirects=False):
                    if url not in links: links.add(url)
                if pr: print(url)
    return(links)


def get_levels(base_url = 'http://andrewgelman.com/', level = 0):
    '''
    Todo: implement *something* to avoid spider traps
    '''
    # level 0, create a set of all the links from the base url
    relDB = {}
    relDB[base_url] = find_links(base_url)
    # level 1, add a node for all subnodes of base url, add link sets for each
    if level > 0:
        for subnode in relDB[base_url]:
            relDB[subnode] = find_links(subnode)
    # level 2+, for each set of links for each subnode, create or add to existing
    #  nodes
    while level > 1:
        for node in relDB.copy():
            for subnode in relDB[node].copy():
                if find_links(subnode) is not None:
                    if subnode not in relDB:
                        relDB[subnode] = find_links(subnode)
                    else:
                        relDB[subnode] |= find_links(subnode)
        level -= 1
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
    with open(base + "Documents/programming_examples/python/twitterbot/urls.txt", 
              'r', encoding='utf-8') as f:
        for l in f.readlines():
            pastURLs[l.strip().replace('\n', '  ').replace('\r', '  ')] = 1
    return set(pastURLs)


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



def network_plot(startURL, DB):
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
    outfile = '/tmp/img.png'
    G.draw(outfile, prog='neato')
    return outfile
    

urls = ['https://www.gop.com/',
        'https://democrats.org/',
        'http://www.foxnews.com/',
        'http://www.msnbc.com/',
        'http://www.who.int/en/',
        'http://www.un.org/en/index.html',
        'http://www.kochind.com/',
        'http://www.greenpeace.org/usa/']


#urls = list(lookupURLs())
random.shuffle(urls)

startURL = urls[0]
#startURL = 'https://www.gop.com/'
relationalDB = get_levels(base_url = startURL, level = 2)
countDB, trimmedDB = trim_db(relationalDB)


outfile = network_plot(startURL, trimmedDB)


api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
with open(outfile, 'rb') as file:
    data = file.read()
    r = api.request('statuses/update_with_media', {'status': '2-degree network: ' + startURL}, {'media[]':data})
    print(r.status_code) 
