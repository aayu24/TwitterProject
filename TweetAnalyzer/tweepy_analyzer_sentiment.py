from tweepy import API
from tweepy import Cursor 
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob

import twitter_credentials
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import re #regular expressions

class TwitterClient():

	def __init__(self, twitter_user=None):
		self.auth = TwitterAuthenticator().authenticate_app()
		self.twitter_client = API(self.auth) #to get the api of the twitter client
		self.twitter_user = twitter_user


	def get_twitter_client_api(self):
		return self.twitter_client
	
	def get_user_timeline_tweets(self, num_tweets):
		tweets = []
		for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
			tweets.append(tweet)
		return tweets

	def get_friendlist(self, num_friends):
		friend_list = []
		for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
			friend_list.append(friend)
		return friend_list

	def get_home_timeline_tweets(self, num_tweets):
		home_timeline_tweets = []
		for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
			home_timeline_tweets.append(tweet)
		return home_timeline_tweets



class TwitterAuthenticator():

	def authenticate_app(self):
		auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET) #object of class OAuthHandler - properly authenticate our code
		auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
		return auth

class TweetStreamer():

	def __init__(self):
		self.twitter_authenticator = TwitterAuthenticator()

	def stream_tweets(self, fetched_tweets_filename, keyword_list):
		
		listener = TweetListener(fetched_tweets_filename)
		auth = self.twitter_authenticator.authenticate_app()
		stream = Stream(auth, listener) 
		
		stream.filter(track=keyword_list)


#class to print recieved tweets to stdout
class TweetListener(StreamListener): #INHERIT FROM STREAMLISTENER CLASS
	
	def __init__(self,fetched_tweets_filename):
		self.fetched_tweets_filename = fetched_tweets_filename
	
	def on_data(self, data):
		try:
			print(data)
			with open(self.fetched_tweets_filename, 'a') as f:
				f.write(data)
			return True
		except BaseException as e:
			print("Error_on_data: %s" % str(e))
		return True

	def on_error(self, status):
	   if status == 420:
		return False  #Returning false on data method incase rate limit exceeded
	   print(status) 


class TweetAnalyzer():
	'''
	For analyzing and categorizing content from tweets
	'''
	def clean_tweet(self, tweet): #cleaning the tweet so that only text remains
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

	def analyze_sentiment(self, tweet):
		analysis = TextBlob(self.clean_tweet(tweet))

		if analysis.sentiment.polarity > 0: #sentiment is positive
			return 1
		elif analysis.sentiment.polarity == 0: #sentiment is neutral
			return 0
		else:
			return -1	#sentiment is negative
		
	def tweets_to_dataframe(self, tweets):
		df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
		
		df['id'] = np.array([tweet.id for tweet in tweets])
		df['len'] = np.array([len(tweet.text) for tweet in tweets]) 
		df['date'] = np.array([tweet.created_at for tweet in tweets])
		df['source'] = np.array([tweet.source for tweet in tweets])
		df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
		df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

		return df 


if __name__ == '__main__':

	twitter_client = TwitterClient()
	tweet_analyzer = TweetAnalyzer()
	api = twitter_client.get_twitter_client_api()
	tweets = api.user_timeline(screen_name="realDonaldTrump", count=200) 
	
	df=tweet_analyzer.tweets_to_dataframe(tweets)
	df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['Tweets']])
	
	print(df.head(10))