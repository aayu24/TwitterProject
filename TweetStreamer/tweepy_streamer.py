from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import twitter_credentials

class TweetStreamer():

	def stream_tweets(self, fetched_tweets_filename, keyword_list):
		
		listener = StdOutListener(fetched_tweets_filename)
		auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET) #object of class OAuthHandler - properly authenticate our code
		auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
	
		stream = Stream(auth, listener) 
		#stream- object of class Stream
		#listener- object which specifies how do I deal with the data and how do I deal with the errors
	
		#filter the tweets based on a list of keywords = track
		stream.filter(track=keyword_list)


#class to print tweets
class StdOutListener(StreamListener): #INHERIT FROM STREAMLISTENER CLASS
	
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
	   print(status) #status-variable containg actual error


if __name__ == '__main__':

	keyword_list = ["narendra modi", "rajiv gandhi", "youtube"]
	fetched_tweets_filename = "tweets.json"

	tweet_streamer = TweetStreamer()
	tweet_streamer.stream_tweets(fetched_tweets_filename, keyword_list)    
	
	
