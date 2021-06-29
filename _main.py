#!/opt/anaconda3/envs/twitterbot/bin/python

import importlib
from random import choice 
import os

## bring in API keys
#import _settings

if os.sys.platform == 'darwin':
    base ="/Users/akeil"
else:
    base = "/home/akeil"




root = base + "/repo/twitterbot/"



bots = ["nietzsche", "hivemind", "network", "quote", "random_image", "random_ocr", "randwalk", "tweet_from_file", 'wordle']
whichbot = root+choice(bots)+"_bot.py"

print(whichbot)

exec(open(whichbot).read())
