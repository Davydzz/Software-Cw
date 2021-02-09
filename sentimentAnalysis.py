import nltk
import sqlite3

from nltk.sentiment import SentimentIntensityAnalyzer
obj = SentimentIntensityAnalyzer()
#obj.polarity_scores("Wow, NLTK is really powerful!")
#print(obj.polarity_scores("Wow, NLTK is really powerful!"))
#output= {'neg': 0.0, 'neu': 0.295, 'pos': 0.705, 'compound': 0.8012}

#print(obj.polarity_scores("I'm sad"))
#{'neg': 0.756, 'neu': 0.244, 'pos': 0.0, 'compound': -0.4767}

#print(obj.polarity_scores("This is literally the worst presentation I've ever witnessed. Give me back my time."))
#{'neg': 0.24, 'neu': 0.76, 'pos': 0.0, 'compound': -0.6249}

#print(obj.polarity_scores("I enjoyed the presentation but the sound was a bit quiet"))
#{'neg': 0.0, 'neu': 0.788, 'pos': 0.212, 'compound': 0.2846}

#print(obj.polarity_scores("I ran over your cat lol"))
#{'neg': 0.0, 'neu': 0.588, 'pos': 0.412, 'compound': 0.4215} ?????

