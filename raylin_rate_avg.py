#!/usr/bin/python 

from __future__ import absolute_import, print_function
from sys import stdout
import json
import redis
import time
import math
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

redis_time_span = 60 # Redis ejects items stored 1 min ago

# Connect to Redis:
conn = redis.Redis()


# Initialize counter that indicates if the current second's tweet stream has faster avg rate than the prev second
counter_h = 0 # for Hillary
counter_t = 0 # for Trump
consecutive_n = 1
# Initialize the level, level takes 3 possible values: 'normal', 'spike', 'plummet'
# if rate goes down (tweets coming in faster) for consecutive "consecutive_n" seconds: level = 'spike'
# if rate goes up (tweets coming in slower) for consecutive "consecutive_n" seconds: level = 'plummet'
# else: level = 'normal'
level_h = 'normal'
level_t = 'normal'



# The following while loop extract data from Redis (in json or i.e. dictionary format),
# and calculate rate change for tweet streams of Hillary & Trump.
# Execute this while loop once a second.

# Base case: initialize to anything, say every minute there's 1 tweet arriving about Hillary and Trump respectively 
rate_h_prev = 1
rate_t_prev = 1


interval = 1 # Execute the following while loop once every second
while 1:

    # Create key_text as a list of all currently stored keys (tweet's content) in redis
    try:
        key_text = conn.keys()
    except:
        key_text = []

    # Create time_list as a list of the arriving time of all currently stored tweets in redis
    try:
        time_list = conn.mget(key_text)
    except:
        time_list=[]

    # Note: key_text and time_list are two lists that have the same length.
    # key_text[i] gives the ith tweet's content (message) in the current 1-second's redis,
    # time_list[i] gives the ith tweet's arriving time in the current 1-second's redis.


    # The following "try" gives credit to the course instructor's code on github:
    # https://github.com/mikedewar/RealTimeStorytelling/blob/master/2/avg.py
    try:
        # Convert every entry in time_list (arriving time of each tweet) to float
        time_arrive = [float(w) for w in time_list]
    except TypeError:
        # print (key_text)
        continue


    # Define rate = average number of tweets generated per minute. 
    # rate = 1+ [60(sec) / average_time_length_between_two_tweets_arrived_from_past_one_minute]


    time_h = []
    time_t = []

    if len(key_text):
        for k in xrange(len(key_text)):
            # Create empty list time_h and time_t to store arriving time of each Hillary-related tweets, and for each Trump-related tweets respectively
            if 'hillary' in key_text[k] or 'clinton' in key_text[k]:
                time_h.append(time_arrive[k])
            if 'trump' in key_text[k] or 'donald' in key_text[k]:
                time_t.append(time_arrive[k])

    # Calculate rate for Hillary's tweet stream:
    # rate_h is the rate for Hillary's tweets within the current second.
    if len(time_h) > 1: # there're at least 2 Hillary-related tweets arriving within the past minute
        # rate of Hillary = [(last-arrived Hillary tweet's time) - (earliest-arrived Hillary tweet's time)] / [(number of Hillary's tweets) - 1]
        # in this case, rate_h always <= 1
        rate_h = float((max(time_h) - min(time_h)))/float(len(time_h)-1)
        rate_h = 1.0 + (60.0/float(rate_h)) # how many tweets that are related to Hillary for each minute.
    elif len(time_h) == 1: # there's exactly one Hillary-related tweet arriving within the past minute
        rate_h = 1 # avg rate is 1 tweet per minute
    else: # no Hillary-related tweet arriving within the past min
        rate_h = 0.001 # avg rate is almost 0 tweet per minute
     

    # Calculate rate for Trump's tweet stream:
    # rate_t is the rate for Trump's tweets within the current second.
    if len(time_t) > 1: # there're at least 2 Trump-related tweets arriving within the past minute
        # rate of Trump = [(last-arrived Trump tweet's time) - (earliest-arrived Trump tweet's time)] / [(number of Trump's tweets) - 1]
        # in this case, rate_t always <= 1
        rate_t = float((max(time_t) - min(time_t)))/float((len(time_t)-1))
        rate_t = 1.0 + (60.0/float(rate_t)) # how many tweets that are related to Trump for each minute.
    elif len(time_t) == 1: # there's exactly one Trump-related tweet arriving within the past minute
        rate_t = 1 # avg rate is 1 tweet per minute 
    else: # no Trump-related tweet arriving within the past minute
        rate_t = 0.001 # avg rate is almost 0 tweet per minute
       


    alert_threshold = 0.05   # set the alert threshold to be 5% above or below the avg rate within the past one minute. 
    # for Hillary:
    if (rate_h - rate_h_prev)/(rate_h_prev) > alert_threshold:
        level_h = 'spike'
    elif (rate_h_prev - rate_h)/(rate_h_prev) > alert_threshold:
        level_h = 'plummet'
    else:
        level_h = 'normal'


    # for Trump:
    if (rate_t - rate_t_prev)/(rate_t_prev) > alert_threshold:
        level_t = 'spike'
    elif (rate_t_prev - rate_t)/(rate_t_prev) > alert_threshold:
        level_t = 'plummet'
    else:
        level_t = 'normal'


    print (json.dumps({'speed_h': rate_h, 'level_h': level_h, 'speed_t': rate_t, 'level_t': level_t}))
    stdout.flush()

    rate_h_prev = rate_h
    rate_t_prev = rate_t

    time.sleep(interval)  # Execute the current while loop once every second
















