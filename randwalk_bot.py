#!/usr/bin/env python3.5
#not yet working
import os
import sys
from TwitterAPI import TwitterAPI
import numpy as np
from numpy import random
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
from subprocess import call

# ask if OSX
if os.sys.platform == 'darwin':
    base ="/Users/akeil"
else:
    base = "/home/akeil"
root = base + "/repo/twitterbot/"
os.chdir(root)

# set twitter api parameters
import _settings as mpi # need to cd into this directory
t_keys = mpi.get_keys()


def check_status(r):
    if r.status_code < 200 or r.status_code > 299:
        print(r.status_code)
        print(r.text)
        sys.exit(0)


def random_walk(numsteps):
    x = np.zeros(numsteps)
    y = np.zeros(numsteps)
    for i in range(numsteps):
        if random.binomial(1, 0.5) == 0.:
            y[i] = random.binomial(1, 0.99)*random.choice([-1, 1])
        else:
            x[i] = random.binomial(1, 0.99)*random.choice([-1, 1])
    lim = max(max(abs(np.cumsum(x))), max(abs(np.cumsum(y)))) + 1.
    return np.cumsum(x), np.cumsum(y), (-lim, lim), (-lim, lim)


def exp_fn_is_crazy(numsteps):
    x = range(numsteps)
    y = np.cumsum(np.exp(random.normal(0, 7, numsteps)))
    for i,val in enumerate(y.copy()):
        y[i] = val/(i+1)
    return x, y, (0, numsteps+1), (min(y), max(y))


def mc_chain(numsteps):
    x = range(numsteps)
    y = np.cumsum(random.normal(1, numsteps, numsteps)*random.choice([-1, 1], numsteps))
    return x, y, (0, numsteps+1), (min(y), max(y))


def brownian_motion(numsteps):
    x = random.normal(0, 1, numsteps)
    y = random.normal(0, 1, numsteps)
    lim = max(max(abs(np.cumsum(x))), max(abs(np.cumsum(y)))) + 1.
    return np.cumsum(x), np.cumsum(y), (-lim, lim), (-lim, lim)


# initialization function: plot the background of each frame
def init_plot():
  line.set_data([], [])
  return line,   
    

# animation function.  This is called sequentially
def anim_plot(i):
    line.set_data(x[:i],y[:i])
    return line,


def tweet_movie(fname, which_fun):
    bytes_sent = 0
    total_bytes = os.path.getsize(fname)
    file = open(fname, 'rb')

    api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])

    r = api.request('media/upload', {'command':'INIT', 'media_type':'video/mp4', 'total_bytes':total_bytes})
    check_status(r)

    media_id = r.json()['media_id']
    segment_id = 0

    while bytes_sent < total_bytes:
      chunk = file.read(4*1024*1024)
      r = api.request('media/upload', {'command':'APPEND', 'media_id':media_id, 'segment_index':segment_id}, {'media':chunk})
      check_status(r)
      segment_id = segment_id + 1
      bytes_sent = file.tell()
      print('[' + str(total_bytes) + ']', str(bytes_sent))

    r = api.request('media/upload', {'command':'FINALIZE', 'media_id':media_id})
    check_status(r)

    r = api.request('statuses/update', {'status': which_fun, 'media_ids':media_id})
    check_status(r)
    print("Tweeted about " + which_fun)
    return(r)


def tweet_gif(fname, which_fun):
    bytes_sent = 0
    total_bytes = os.path.getsize(fname)
    file = open(fname, 'rb')

    api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])

    r = api.request('media/upload', {'command':'INIT', 'media_type':'image/gif', 'total_bytes':total_bytes})
    check_status(r)

    media_id = r.json()['media_id']
    segment_id = 0

    while bytes_sent < total_bytes:
      chunk = file.read(4*1024*1024)
      r = api.request('media/upload', {'command':'APPEND', 'media_id':media_id, 'segment_index':segment_id}, {'media':chunk})
      check_status(r)
      segment_id = segment_id + 1
      bytes_sent = file.tell()
      print('[' + str(total_bytes) + ']', str(bytes_sent))

    r = api.request('media/upload', {'command':'FINALIZE', 'media_id':media_id})
    check_status(r)

    r = api.request('statuses/update', {'status': which_fun, 'media_ids':media_id})
    check_status(r)
    print("Tweeted about " + which_fun)
    return(r)


def tweet_gifsm(fname, which_fun):
    api = TwitterAPI(t_keys['CONSUMER_KEY'], t_keys['CONSUMER_SECRET'], t_keys['ACCESS_KEY'], t_keys['ACCESS_SECRET'])
    total_bytes = os.path.getsize(fname)
    with open(fname, 'rb') as file:
        data = file.read()
        r = api.request('media/upload', {'command':'INIT', 'media_type':'image/gif', 'total_bytes':total_bytes})
        check_status(r)
        media_id = r.json()['media_id']
        r = api.request('media/upload', {'command':'APPEND', 'media_id':media_id, 'segment_index':0}, {'media':file})
        check_status(r)
        r = api.request('media/upload', {'command':'FINALIZE', 'media_id':media_id})
        check_status(r)
    print(r.status_code)
    print(r.text)



funs = ['random_walk', 'mc_chain', 'brownian_motion', 'exp_fn_is_crazy']
fun_dict = {}
fun_dict[funs[0]] = random_walk
fun_dict[funs[1]] = mc_chain
fun_dict[funs[2]] = brownian_motion
fun_dict[funs[3]] = exp_fn_is_crazy
#random function
which_fun = random.choice(funs)
print(which_fun)

numframes = random.choice(range(1, 800))
x, y, xlim, ylim = fun_dict[which_fun](numframes)

#random style
sty = random.choice(plt.style.available)


#matplotlib.rcParams['animation.frame_format'] = 'jpeg'
#matplotlib.rcParams['animation.bitrate'] = 768

plt.style.use(sty)
fig = plt.figure(figsize=(6,4))
ax = plt.axes(xlim=xlim, ylim=ylim)
plt.axis('off')
line, = ax.plot([],[], lw=2, color = (random.random(), random.random(), random.random()))

anim = animation.FuncAnimation(fig, anim_plot, init_func=init_plot,
        frames=len(x), blit=True, interval=20, repeat_delay=50)
        
# twitter is fairly strict on the types of codecs allowed 
# had to install ffmpeg wit this:
# brew install ffmpeg --with-fdk-aac --with-ffplay --with-freetype --with-libass 
#                     --with-libquvi --with-libvorbis --with-libvpx --with-opus 
#                     --with-x265 --with-h264

#brew reinstall ffmpeg --with-x264
# man ffmpeg, or ffmpeg --help, ffmpeg -codecs

vidname = '/tmp/anim.mp4'
gifname = '/tmp/anim.gif'

# these args from here: http://pimentoso.blogspot.com/2016/01/convert-videos-for-twitter-using-ffmpeg.html
ffmpeg_args = '-r 40'
ffmpeg_args = ' '.join([ffmpeg_args, '-c:v libx264']).strip()
#ffmpeg_args = ' '.join([ffmpeg_args, '-r 30 -c:v libx264 -b:v 1M -vf scale=640:-1']).strip()

# from https://twittercommunity.com/t/unable-to-upload-video-to-twitter/61721/3
ffmpeg_args = ' '.join([ffmpeg_args, '-pix_fmt yuv420p']).strip()

print(ffmpeg_args)

anim.save(vidname, writer='ffmpeg', extra_args=ffmpeg_args.split(' '))


gif_args = '-pix_fmt rgb8 -r 40'
gif_args = ' '.join([gif_args, '-loop 0']).strip()

try:
    os.remove(gifname)
except:
    print("GIF does not yet exist")

cl = ["ffmpeg", "-i", vidname]
for arg in gif_args.split(' '): 
    cl.append(arg)

cl.append(gifname)
print(gif_args)
call(cl)


if numframes < 800:
    print("Tweeting gif")
    tweet_gif(gifname, which_fun)
else:
    print("Tweeting mp4")
    tweet_movie(vidname, which_fun)
    
