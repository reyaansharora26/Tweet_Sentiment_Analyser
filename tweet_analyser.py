#!/bin/user/pythonAdd commentMore actions

#import required libraries
import utils as ut
import signal
import sys
import time
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

# Open the file
#f=open(ut.FILEPATH, 'w')

class TwitterClient (object):

	def __init__(self):
		# Get access to twitter api
		self.auth = ut.fetch_secret()
		# Check for Error
		if self.auth == -1:
			print("Error: Authentication Failure..\nShutting Down...")
			sys.exit(-1)

		# create tweepy API object to fetch tweets
		self.api = tweepy.API(self.auth)

	def clean_tweet(self, tweet):
		"""
		Utility function to clean tweet text by removing links, special characters
		using simple regex statements.
		"""
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
 
	def get_tweet_sentiment(self, tweet):
		'''
		Utility function to classify sentiment of passed tweet
		using textblob's sentiment method
		'''
        # create TextBlob object of passed tweet text
		analysis = TextBlob(self.clean_tweet(tweet))

        # set sentiment
		if analysis.sentiment.polarity > 0:
			return 'positive'
		elif analysis.sentiment.polarity == 0:
			return 'neutral'
		else:
			return 'negative'

	def get_tweets(self, query, count = 10):
		'''
		Main function to fetch tweets and parse them.
		'''
		# empty list to store parsed tweets
		tweets = []
 		
		try:
			# call twitter api to fetch tweets
			fetched_tweets = self.api.search(q = query, count = count)

			# parsing tweets one by one
			for tweet in fetched_tweets:
    			# empty dictionary to store required params of a tweet
				parsed_tweet = {}

    			# saving text of tweet
				parsed_tweet['text'] = tweet.text
    			# saving sentiment of tweet
				parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

    			# appending parsed tweet to tweets list
				if tweet.retweet_count > 0:
        			# if tweet has retweets, ensure that it is appended only once
					if parsed_tweet not in tweets:
						tweets.append(parsed_tweet)
				else:
					tweets.append(parsed_tweet)

			# return parsed tweets
			return tweets


		except tweepy.TweepError as e:
		# print error (if any)
			print("Error : " + str(e))

# Signal Handler
def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
	signal.signal(signal.SIGINT, original_sigint)
	global f
	try:
		if input("\nReally quit? (y/n)> ").lower().startswith('y'):
			print("Shutting down...")
#			f.close()
#			ut.GetNumOfTweets()
			#stream.disconnect()
			sys.exit(1)

	except KeyboardInterrupt:
		print("Ok ok, quitting")
#		f.close()
		sys.exit(1)

# restore the exit gracefully handler here    
signal.signal(signal.SIGINT, exit_gracefully)

if  __name__ == '__main__':

	# store the original SIGINT handler
	original_sigint = signal.getsignal(signal.SIGINT)

	# Take input query from user 
	myquery = input("\nEnter Query: ")

	# creating object of TwitterClient Class
	api = TwitterClient()

    # calling function to get tweets
	tweets = api.get_tweets(query = myquery, count = 20000)

	# picking positive tweets from tweets
	ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']

    # percentage of positive tweets
	print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))

    # picking negative tweets from tweets
	ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']

    # percentage of negative tweets
	print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))

    # percentage of neutral tweets
	print("Neutral tweets percentage: {} %".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)))

	# printing first 5 positive tweets
	print("\n\nPositive tweets:")
	for tweet in ptweets[:10]:
		print(tweet['text'])
 
	# printing first 5 negative tweets
	print("\n\nNegative tweets:")
	for tweet in ntweets[:10]:
		print(tweet['text'])
