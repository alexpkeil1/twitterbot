![logo](https://raw.githubusercontent.com/alexpkeil1/twitterbot/master/bleepboopbeep.jpeg)
# twitterbot

Using twitter API to create tweets. Examples include Tweepy and TwitterAPI modules. See [dottodot] (http://www.dototot.com/how-to-write-a-twitter-bot-with-python-and-tweepy/) for a quick introduction.

[Here](https://twitter.com/PyBotMcBotface) is my somewhat odd example of an arbitrary mixture of these programs at work, using launchd (OS-X) and cron (Xubuntu) to automate it.

I use a file called mybotapi.py that holds my private Twitter info, it is structured roughly like this:
```python
def get_keys():
    dict = {}
    dict['CONSUMER_KEY'] = 'foo'#keep the quotes, replace this with your consumer key
    dict['CONSUMER_SECRET'] = 'bar'#keep the quotes, replace this with your consumer secret key
    dict['ACCESS_KEY'] = 'food-bart'#keep the quotes, replace this with your access token
    dict['ACCESS_SECRET'] = 'fo'#keep the quotes, replace this with your access token secret
    return dict
```
Many of the programs make reference to this file, included as a module.

Many of the examples will not run, as is, and must be customized to a given user's environment. Some are works in progress and not yet completed.
