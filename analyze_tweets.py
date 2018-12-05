
'''
##########################
#### HELPER FUNCTIONS ####
##########################
'''

#FUNCTION: Read tweets into dictionary from JSON files
def read_tweets(tweet_files, json):
	print("Creating dictionary...")
	
	#Read the specified files
	tweets = []
	for file in tweet_files:
		with open(file, 'r') as f:
			for line in f.readlines():
				tweets.append(json.loads(line))
	return tweets

#FUNCTION: Create a dataframe from the tweets dictionary
def create_df(tweets, pd):
	#Load key pieces of data in a dataframe
	print("Creating data frame...")
	df = pd.DataFrame()
	df['text'] = list(map(lambda tweet: tweet['text'], tweets))
	df['favorite_count'] = list(map(lambda tweet: tweet['favorite_count'], tweets))
	df['retweet_count'] = list(map(lambda tweet: tweet['retweet_count'], tweets))
	df['user_name'] = list(map(lambda tweet: tweet['user']['screen_name'],tweets))
	df['user_followers'] = list(map(lambda tweet: tweet['user']['followers_count'],tweets))

	return df

#FUNCTION: Print key statistics about a dataframe of tweets
def print_stats(df):
	#Print key statistics
	print("*********** Key Statistics ***********")
	print("Number of Tweets: " + str(len(df.index)))
	print("Number of Favorites: " + str(sum(df['favorite_count'])))
	print("Number of Retweets: " + str(sum(df['retweet_count'])))
	print("Number of Distinct Users: " + str(len(set(df['user_name']))))
	print("First-Order Reach (Followers of Users): "+ str(sum(df['user_followers'])))
	print("**************************************")

#FUNCTION: Creates horizontal bar chart based on dictionary data
def hbar_chart(data, title, x_axis):
	import matplotlib.pyplot as plt
	import numpy as np

	plt.rcdefaults()
	fig, ax = plt.subplots(figsize=(12,8))
	myValues = list(data.values())[0:25]
	myDimensions = list(data.keys())[0:25]
	y_pos = np.arange(len(myDimensions))
	ax.barh(y_pos, myValues, color = 'green')
	ax.set_yticks(y_pos)
	ax.set_yticklabels(myDimensions)
	plt.xlabel(x_axis)
	plt.title(title)
	plt.gca().invert_yaxis()
	plt.show()

	return myValues, myDimensions


'''
##########################
### Analysis Functions ###
##########################
'''

#FUNCTION: Get Frequency of Words by Prevalence
def getWordFreq(tweet_text, re, min=25):
	#Imports
	from collections import Counter

	#Create a new Text Blob that compiles all the tweets into a single block of text
	text_string = ''
	for each in tweet_text:
		text_string = text_string + each
	text_string = text_string.lower()

	#Get Word Frequencies
	frequency = {}
	match_pattern = re.findall(r'\b[a-z]{8,15}\b', text_string)
	counts = Counter(match_pattern)
	frequency = dict(counts)

	#Sort the list
	output_dict = {}
	sorted_list = sorted(frequency, key=frequency.__getitem__, reverse=True)
	for word in sorted_list:
		if frequency[word] > min:
			output_dict[word] = frequency[word]

	return output_dict



#FUNCTION: Get Frequency of Words by Prevalence for a set of users
def getWordFreqUsers(df, user_list, re):
	
	#Imports
	from collections import Counter
	frequency = {}
	words_seen = []
	all_users = []

	#populate the all_users list
	for each in df['user_name']:
		all_users.append(each.lower())

	#Loop through rows in dataframe and count words
	for index,row in df.iterrows():
		if row['user_name'] in user_list:
			# Get the tweet text
			tweet_text = row['text']
			tweet_text = tweet_text.lower()

			#Separate into words
			words = re.findall(r'\b[a-z]{8,15}\b', tweet_text)
			for word in words:
				if word not in all_users:
					if word not in words_seen:
						frequency[word] = 1
						words_seen.append(word)
					else:
						frequency[word] = frequency[word] + 1

	#Sort the list
	output_dict = {}
	sorted_list = sorted(frequency, key=frequency.__getitem__, reverse=True)
	for word in sorted_list:
		output_dict[word] = frequency[word]

	return output_dict



#FUNCTION: Get Users by Frequency of tweet
def getUserFreq(df, min=10):
	#Imports
	from collections import Counter

	#Instance Variables
	frequency = {}
	output_dict = {}
	user_list = df['user_name']

	#Get the counts
	counts = Counter(user_list)
	frequency = dict(counts)

	#Sort the dictionary
	sorted_list = sorted(frequency, key=frequency.__getitem__, reverse=True)
	for user in sorted_list:
		if frequency[user] > min:
			output_dict[user] = frequency[user]

	return output_dict



#FUNCTION: Get Users by Volume of Reach
def getUserReach(df, min=10):

	#Instance Variables
	frequency = {}
	output_dict = {}

	#Create a dataframe for lookups
	lookup = {}
	for index, row in df.iterrows():
		lookup[row['user_name']] = row['user_followers']

	#Get the reach counts
	users_seen = []
	for user in df['user_name']:
		if user not in users_seen:
			frequency[user] = lookup[user]
			users_seen.append(user)
		else:
			frequency[user] = frequency[user]+ lookup[user]


	#Sort the dictionary
	sorted_list = sorted(frequency, key=frequency.__getitem__, reverse=True)
	for user in sorted_list:
		if frequency[user] > min:
			output_dict[user] = frequency[user]

	return output_dict


#FUNCTION: Get Users by Word
def getUserWord(df, word, minV=10):

	#Instance Variables
	frequency = {}
	output_dict = {}
	users_seen = []
	user_name = ''

	#Create a dataframe for lookups
	for index, row in df.iterrows():
		if word in row['text'] :
			user_name = row['user_name']
			if user_name not in users_seen:
				frequency[user_name] = 1
				users_seen.append(user_name)
			else:
				frequency[user_name] = frequency[user_name] + 1


	#Sort the dictionary
	sorted_list = sorted(frequency, key=frequency.__getitem__, reverse=True)
	for user in sorted_list:
		output_dict[user] = frequency[user]

	return output_dict




'''
MAIN FUNCTION FOR EXECUTION OF CODE
'''
def main():
	## SETUP ##

	#Imports
	print("Importing tools...")
	import pandas as pd
	import json as js
	import re as re
	import matplotlib as mpl
	import matplotlib.pyplot as plt
	import numpy as np

	#Instance Variables
	tweet_files = ['healthtech/ht.json', 'digitalhealth/dh.json']

	#Populate Data Frame & Print Stats
	tweets = read_tweets(tweet_files, js)
	df = create_df(tweets, pd)
	print_stats(df)

	## ANALYSIS ##
	
	'''## Get word frequency and plot ##
	wordFrequency = getWordFreq(df['text'],re)
	hbar_chart(wordFrequency, "Top Words in Tweet Text", "Word Prevalence")

	#Get user frequency and plot
	userFrequency = getUserFreq(df)
	hbar_chart(userFrequency, "Number of Tweets by User", "Number of Tweets")
	
	#User Reach
	userReach = getUserReach(df)
	topUserValues, topUsers = hbar_chart(userReach, "Reach by User", "Reach (# of Followers x # of Tweets)")

	#Word Frequency for Top Users
	userWordFreqUsers = getWordFreqUsers(df, topUsers, re)
	hbar_chart(userWordFreqUsers, "Top Words for Top Users", "Word Prevalence")'''

	#Word Frequency for Top Users
	UserWord = getUserWord(df, "wearable", re)
	hbar_chart(UserWord, "Top Users for Word", "Tweet Count")




if __name__ == "__main__":
	main()
