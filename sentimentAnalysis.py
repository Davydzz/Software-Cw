import nltk
import sqlite3

from nltk.sentiment import SentimentIntensityAnalyzer
obj = SentimentIntensityAnalyzer()



def create_connection(databaseFile):
    """ 
    :param: databaseFile: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(databaseFile)
    except Error as e:
        print(e)

    return conn


# Input is sessionID, will probably be the pk

def getFromDB(sessionID, conn):

    connection = conn.cursor()
    # Skeleton for future database
    connection.execute("SELECT feedbackText FROM feedback WHERE feedbackFormID = (SELECT feedbackFormID from feedback WHERE eventID = ?) ", sessionID)
    userID, feedBackText = connection.fetchAll()
    return [userID, feedBackText]


def getSentimentScore(msgs, obj):

    sentimentList = []
    for user, msg in msgs:
        score = obj.polarity_scores(msg)
        sentimentList.append([user, score['compound']])

    return sentimentList

def addBackToTable(conn, sentimentList):
    
    totalScore = 0
    for user, score in sentimentList:
        totalScore
        insertStatement = "INSERT INTO feedback (sentiment) VALUES ? WHERE userID = ?"
        connection = conn.cursor()
        connection.execute(insertStatement, (score, user))

    #overallSentiment = 




def averageSentiment(list):
    
    return sum(list[1]) / len(list)



#obj.polarity_scores("Wow, NLTK is really powerful!")
#print(obj.polarity_scores("Wow, NLTK is really powerful!"))
#output= {'neg': 0.0, 'neu': 0.295, 'pos': 0.705, 'compound': 0.8012}
#print(type(output))
#print(obj.polarity_scores("I'm sad"))
#{'neg': 0.756, 'neu': 0.244, 'pos': 0.0, 'compound': -0.4767}

#print(obj.polarity_scores("This is literally the worst presentation I've ever witnessed. Give me back my time."))
#{'neg': 0.24, 'neu': 0.76, 'pos': 0.0, 'compound': -0.6249}

#print(obj.polarity_scores("I enjoyed the presentation but the sound was a bit quiet"))
#{'neg': 0.0, 'neu': 0.788, 'pos': 0.212, 'compound': 0.2846}

#print(obj.polarity_scores("I ran over your cat lol"))
#{'neg': 0.0, 'neu': 0.588, 'pos': 0.412, 'compound': 0.4215} ?????

conn = create_connection("database.db")
msgs = getFromDB(2, conn)
listSentiments = getSentimentScore(msgs, obj)