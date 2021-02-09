import nltk

from nltk.sentiment import SentimentIntensityAnalyzer
obj = SentimentIntensityAnalyzer()
#obj.polarity_scores("Wow, NLTK is really powerful!")
print(obj.polarity_scores("Wow, NLTK is really powerful!"))