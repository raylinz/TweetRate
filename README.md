# TweetRate

## Introduction

### Functions and Frontend Display
This web application monitors the real-time arriving rate of tweets related to two potential candidates of 2016 U.S. presidential election: Hillary Clinton, the most-likely nominated presidential candidate representing the Democratic Party, and Donald Trump, the front-runner among Republican candidates. The frontend HTML webpage displays a dynamic bar chart with 2 bars whose heights indicate the “tweet rate” for Hillary Clinton and Donald Trump respectively. “Tweet rate” is defined as the average number of tweets generated per minute on Twitter. Being consistent with the commonly known “Blue for Democratic, Red for Republican”, the blue bar visualizes the “tweet rate” for Democratic Party’s candidate Hillary Clinton, and the red bar illustrates the “tweet rate” for Republican Party’s candidate Donald Trump.

![Tweet Rate for Hillary Clinton and Donald Trump](/hillary_mark.png)
![Tweet Rate for Hillary Clinton and Donald Trump](/trump_mark.png)

The dynamic bar chart automatically refreshes with newly arrived data once every second. The vertical axis of this dynamic bar chart automatically adjusts its scale according to the stream data. If the current second’s “twitter rate” for any candidate contributes to a 10% increase in the average “tweet rate” within the past minute, the frontend web browser would give an alert message that says “Go Hillary!” or “Go Trump!”. 

Similarly, if the current second’s “twitter rate” for any candidate causes a 10% decline in the average “tweet rate” within the past minute, the frontend web browser would give an alert message that says “Hillary drops…” or “Trump drops…”. 
The design of the frontend gives credit to the online sampel code on [Canvasjs.com][3]. 

### How Backend Works
The backend Python script uses [Twitter’s Public streams API][1] to poll real-time tweets related to Hillary Clinton by setting up a keyword filter that contains either “hillary” or “clinton”, or both. Similarly, the backend script collects tweets related to Donald Trump by setting up a keyword filter that contains either “donald” or “trump”, or both. The text content and the arriving time of every matched tweet would then get stored in [Redis][2] for one minute. 

Another backend Python script would fetch and use the most recent one-minute data from Redis to calculate the “tweet rate”, defined as average number of tweets generated per minute, for Hillary Clinton and Donald Trump respectively. Once the “tweet rate” obtained from the current second is computed for each candidate, the real-time rate (number of tweets per minute) value would be sent to the frontend webpage by Websocketd on port 8080 through a webscket. If there are any alert messages to get displayed on the web browser, such messages would also be passed on to the frontend webpage through this websocket. 

## Data

The Python script raylin_rate.py collects real-time tweets by polling [Twitter’s Public streams API][1]. With a keyword filter, raylin_rate.py only keeps tweets that contain at least one of the following keywords: “hillary”, “clinton”, “donald”, “trump”. Then raylin_rate.py would send the key-value pair, {selected_tweet’s_text_content: arriving_time} for each selected tweet, to Redis, the in-memory database system. As the parameter in raylin_rate.py (k) is set to 60 (sec), Redis would keep each tweet’s information in memory for 60 seconds (i.e. 1 minute). 

The other Python script, raylin_rate_avg.py, identifies tweets that are related to Hillary Clinton if keyword “hillary” or “clinton” (or both) is included in tweets. Similarly, it identifies tweets related to Donald Trump by checking if keyword “donald” or “trump” (or both) shows up in tweets. Next, raylin_rate_avg.py would calculate the “twitter rate” for the two candidates respectively through the method as described in the next section. 

## Rate Calculation 

“Tweet rate” is defined as the average number of tweets generated per minute. 

As the parameter “interval” is set to 1 (sec) in raylin_rate_avg.py, raylin_rate_avg.py would calculate “tweet rate” once per second, using the data stored in [Redis][2] from the past one minute. 

For each candidate:

- rate = 1+ [60(sec) / average_time_length_between_two_tweets_arrived_from_past_one_minute]

Where: 

- average_time_length_between_two_tweets_arrived_from_past_one_minute 
= [max(arriving_time_in_Redis) – min(arriving_time_in_Redis)] / (number_of_tweets_in_Redis – 1)

## Alert System 

The frontend web browser would give alert messages in the following cases. 

For each candidate, if “tweet rate” calculated at the current second is more than 10% higher than the previous second’s “tweet rate”, i.e. if the tweets generated within the current second contribute to an increase of more than 10% in average number of tweets per minute, the web browser would give the alert message: “Go Hillary!” or “Go Trump!” 

If “tweet rate” calculated at the current second is more than 10% smaller than the previous second’s “tweet rate”, i.e. if the tweets generated within the current second contribute to a decline of more than 10% in average number of tweets per minute, the web browser would give the alert message: “Hillary drops…” or “Trump drops…”

The threshold, 10%, is tuned on a trial-and-error basis. Such threshold could be modified by changing the value of the variable “alert_threshold” in raylin_rate_avg.py. 

## Instructions

### Installation Requirements 

Before launching this application, please install the following Python packages with pip: 

- redis==2.10.5
- socketIO_client==0.5.6

Please also install the [Redis in-memory database system][2] with Homebrew: 

- brew install redis

### Obtaining Twitter Authentication 

- Visit https://apps.twitter.com/ to create an application so as to obtain a consumer key and a consumer secret. 
- Once being directed to your application’s page, create an access token in the section of "Your access token" where you could obtain an access token and an access token secret. 
- Feed your consumer key, consumer secret, access token, and access token secret in raylin_rate.py, matching the 4 variables defined at the beginning of raylin_rate.py: consumer_key, consumer_secret, access_token, access_token_secret. 

### How to Run 

- Make sure the following 6 files are placed in the same directory: raylin_rate.py, raylin_rate_avg.py, raylin_rate.html, canvasjs.min.js, poll_api.sh, redis_to_websocket.sh
- Feed your Twitter authentication information to raylin_rate.py. As described in the previous subsection, set:
consumer_key = “your consumer key”;
consumer_secret = “your consumer secret;
access_token = “your access token”;
access_token_secret = “your access token secret”.
Save raylin_rate.py. 
- Open a terminal, change directory to the current file that contains the above 6 files. Next, type the following command to mark poll_api.sh executable: 

```sh
$ chmod +x poll_api.sh
```
- Then type the following command to run poll_api.sh
```sh
$ ./poll_api.sh
```
- Open another terminal, change directory to the current file that contains the 6 files. Next, type the following command to run redis_to_websocket.sh: 
```sh
$ sh redis_to_websocket.sh
```
- Open raylin_rate.html with Chrome or other web browser. 


   
   [1]: <https://dev.twitter.com/streaming/public>
   [2]: <http://redis.io/>
   [3]: <http://canvasjs.com/editor/?id=http://canvasjs.com/example/gallery/dynamic/realtime_column/>
   
