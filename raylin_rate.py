#!/bin/bash
from __future__ import absolute_import, print_function
from sys import stdout
import time
import json
import redis
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# Visit https://apps.twitter.com/ to create an application so as to obtain a consumer key and a consumer secret. 
# The consumer key and secret will be generated after the app is created.
consumer_key=" "
consumer_secret=" "

# where you could create an access token in the section of "Your access token" 
# Obtain an access token and an access token secret. 
access_token=" "
access_token_secret=" "


# Connect to Redis:
global conn  # create a global variable in this Python script
conn = redis.Redis()


# To calculate the time difference between each incoming tweet,
# we set the last (most recent previous tweet)'s incoming time to be 0.
global last # create a global variable
last = 0


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        global conn
        global last

        # Load tweets data in json format
        data_json = json.loads(data)

        # Idea of the following loop (try) comes from course instructor's Github:
        # https://github.com/mikedewar/RealTimeStorytelling/tree/master/2
        try:

            # Send Twitter text and time difference to Redis
            # Let redis dictionary back track until k seconds, the larger k is, the less sensitive the alert is.
            # Try k = 200 first, since messages about Trump and Hillary come in very frequently.
            # Select the 'text' part (content of each tweet) for each selected tweets,
            # store the tweet content part ('text') in redis as redis' keys
            # time.time() is the value of current time, in terms of how many seconds from 1970-Jan-01
            k = 60 # eject the item in redis stored 5 min ago
            conn.setex(data_json['text'], time.time(), k)
            stdout.flush()
        except:
            pass
        return True


    # on_error(): credit to tweepy library sample code:
    # https://github.com/tweepy/tweepy/blob/v3.2.0/examples/streaming.py
    def on_error(self, status):
        print(status)




# Credit of the following definition of main(): tweepy sample code on github:
# https://github.com/tweepy/tweepy/blob/v3.2.0/examples/streaming.py
if __name__ == '__main__':
    # Create new object l from the previously defined class: StdOutListener(StreamListener)
    l = StdOutListener()

    # While polling Tweeter Streaming API, provide the following Tweeter API authentification information
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Create a new stream of tweets:
    stream = Stream(auth, l)

    # Create a filter that selects tweets containing at least one of the following keywords: trump, donald, hillary, clinton.
    # async = True, so that the stream will run on a new thread
    stream.filter(track=['trump', 'donald', 'hillary', 'clinton'], async=True)


