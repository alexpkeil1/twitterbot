#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import mybotapi as mpi


api = mpi.tweepyapi


first_tweet = 'test_tweet.txt'

with open(first_tweet, 'rb') as f:
    api.update_status(f.read())


    
#data = file.read()
#r = api.request('statuses/update_with_media', {'status': 'Machines speaking machine: ' + outtext}, {'media[]':data})
#print(r.status_code)    