import sqlite3
import hashlib
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
obj = SentimentIntensityAnalyzer()

class DBConnection:
    def __init__(self):
        self.database = "database.db"

    def createConnection(self,db):
        conn = None
        try:
            conn = sqlite3.connect(db)
            conn.execute("PRAGMA foreign_keys = ON")
        except:
            print("Connection didn't work")
        return conn

    def addUser(self, salt, password, fName, lName, email): #used for registration
        #check user is not already in db
        conn = self.createConnection(self.database)
        existingUserStatement = ("SELECT * FROM users WHERE email = '%s'" % email)
        for row in conn.execute(existingUserStatement):
            #print(row)
            #already exists
            return False, None

        if conn is not None:
            insertStatement = ("INSERT INTO users (salt, password, firstName, lastName, email) VALUES ('%s', '%s', '%s', '%s', '%s')" % (salt, password, fName, lName, email))
            conn.execute(insertStatement)
            conn.commit()
            userID = self.getIDFromEmail(email)
            return True, userID


    #feedbackFormID refers to the feedback form that the feedback belongs to
    def addFeedback(self, userID, anonymous, timestamp, feedbackFormID, roomcode, sentiment): 
        conn = self.createConnection(self.database)

        if conn is not None:
            if userID == None:
                insertStatement = ("INSERT INTO feedback (anonymous, timestamp, feedbackFormID, roomcode, sentiment) VALUES ('%s', '%s', '%s', '%s', '%s')" % (anonymous, timestamp, feedbackFormID, roomcode, sentiment))
            else:
                insertStatement = ("INSERT INTO feedback (userID, anonymous, timestamp, feedbackFormID, roomcode, sentiment) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (userID, anonymous, timestamp, feedbackFormID, roomcode, sentiment))
            conn.execute(insertStatement)
            id = conn.execute('select last_insert_rowID();')
            id = id.fetchone()
            id = id[0]
            conn.commit()
            return True,id

    def addFeedbackQuestion(self, questionID, feedbackID, answer):
        conn = self.createConnection(self.database)
        if conn is not None:
            insertStatement =  ("INSERT INTO feedbackQuestions (questionID, feedbackID, answer) VALUES ('%s', '%s', '%s')" % (questionID, feedbackID, answer))
            conn.execute(insertStatement)
            conn.commit()
            return True
        return False
        
    def createFeedbackForm(self, eventID, overallSentiment):
        conn = self.createConnection(self.database)

        if conn is not None:
            insertStatement = ("INSERT INTO feedbackform (eventID, overallSentiment) VALUES ('%s', '%s')" % (eventID, overallSentiment))
            conn.execute(insertStatement)
            id = conn.execute('select last_insert_rowID();')
            id = id.fetchone()
            id = id[0]
            conn.commit()
            return True,id

    def getUserEvents(self, userID):
        #return all events that the user is a host or an attendee of
        conn = self.createConnection(self.database)
        

        if conn is not None:
            hostStatement = ("SELECT roomcode, eventName FROM events WHERE hostUserID = '%s';" % userID)
            attendeeStatement = ("SELECT events.roomcode, events.eventName FROM events INNER JOIN event_members ON events.roomcode = event_members.roomcode WHERE event_members.userID = '%s' AND events.active = 'True';" % userID)
            
            hostRows = []
            attendeeRows = []
            for row in conn.execute(hostStatement):
                hostRows.append([row[0], row[1]])

            for row in conn.execute(attendeeStatement):
                attendeeRows.append([row[0], row[1]])
            return hostRows, attendeeRows


    def confirmLogin(self, email, password):
        conn = self.createConnection(self.database)
        getSaltStatement = ("SELECT salt FROM users WHERE email = '%s';" % email)
        saltFound = False
        for row in conn.execute(getSaltStatement):
            saltFound = True
            salt = row[0]
        if not saltFound:
            return False, None
        toHash = salt + password
        hashedPassword = hashlib.sha256(bytes(toHash,"utf-8")).hexdigest()
        existingUserStatement = ("SELECT * FROM users WHERE email = '%s' AND password = '%s'" % (email, hashedPassword))
        for row in conn.execute(existingUserStatement):
            #password matches the email
            return True, row[0]
        return False, None

    def getIDFromEmail(self,email):
        conn = self.createConnection(self.database)
        getUserStatement = ("SELECT userID FROM users WHERE email = '%s';" % email)
        for row in conn.execute(getUserStatement):
            return row[0]

    def getUserFromUserID(self, uID):
        conn = self.createConnection(self.database)
        getUserStatement = ("SELECT * FROM users WHERE userID = '%s';" % uID)
        for row in conn.execute(getUserStatement):
            return row


    def getFeedbackFormID(self, templateName):
        conn = self.createConnection(self.database)
        getFeedbackFormID = "SELECT feedbackFormID FROM FeedbackForm WHERE templateName = ?"
        for row in conn.execute(getFeedbackFormID,(templateName,)):
            return row[0]

    def createEvent(self, eventName, feedbackFrequency, hostUserID, date, active, feedbackFormID):

        #With 10,000 events the collision rate is just over 1%
        validCode = False
        while not (validCode):
            validCode = True
            from random import randint
            roomcode = (randint(100000,999999))
            roomcode = str(roomcode)

            conn = self.createConnection(self.database)
            existingEventStatement = ("SELECT * FROM events WHERE roomcode = '%s'" % roomcode)
            for row in conn.execute(existingEventStatement):
                validCode = False
        if conn is not None:
            insertStatement = ("INSERT INTO events (roomcode, eventName, feedbackFrequency, hostUserID, date, active, feedbackFormID) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (roomcode, eventName, feedbackFrequency, hostUserID, date, active, feedbackFormID))
            conn.execute(insertStatement)
            conn.commit()
            return True, roomcode

    def joinEvent(self, roomCode, userID):
        #connect to db
        conn = self.createConnection(self.database)

        #if room code exists in events
        eventExistsStatement = ("SELECT * FROM events WHERE roomCode = '%s';" % roomCode)
        roomCodeExists = False
        for row in conn.execute(eventExistsStatement):
            roomCodeExists = True

        if roomCodeExists:
            if userID != None:
                try:
                    #then add userID to event_members
                    addUserToEventsStatement = ("INSERT INTO event_members (roomcode, userID) VALUES ('%s', '%s')" % (roomCode, userID))
                    conn.execute(addUserToEventsStatement)
                    conn.commit()
                except:
                    print("You are already in the room")
            return True

        print("Room code doesn't exist")
        return False

    # Fix bug tmr morning
    def addTemplate(self, result, templateName):

        conn = self.createConnection(self.database)
        #added templateName to differenciate in the drop down menu
        addFeedbackForm = ("INSERT INTO FeedbackForm(templateName, overallSentiment) VALUES (?,?);")
        
        addQuestion = ("INSERT INTO Question(questionNumber, type, content, feedbackFormID) VALUES (?,?,?,?);")
        #getFeedbackFormID = ("SELECT feedbackFormID FROM FeedbackForm WHERE eventID = ?")

        feedbackID = -1
        conn.execute(addFeedbackForm, (templateName, 0))
        id = conn.execute('select last_insert_rowID();')
        id = id.fetchone()
        feedbackID = id[0]
        # for row in conn.execute(getFeedbackFormID, (roomCode,)):
        #     feedBackID = row[0]
        questionNo = 1
        
        try:
            for elem in result:
                conn.execute(addQuestion,(questionNo, elem[1], elem[0],feedbackID)) 
                questionNo +=1
            
            conn.commit()
            return feedbackID
        except Exception as e:
            print(e)
            print("Template creation failure")
            return False
    
    def returnTemplates(self):

        conn = self.createConnection(self.database)
        cur = conn.cursor()
        listTemplates = []
        getAllTemplates = ("SELECT templateName from FeedbackForm")
        cur.execute(getAllTemplates)
        rows = cur.fetchall()
        #cur.fetchAll returns a list of tuples, since they're all one element
        #tuples, we convert it into a normal list
        
        for elem in rows:
            listTemplates.append(elem[0])

        #print(rows)
        return listTemplates

    def getFeedbackFormDetails(self, eventID):
        #get feedback form for this event ID
        #get all questions where feedback ID is NULL and feedback form ID matches
        #return these questions
        conn = self.createConnection(self.database)
        getQuestionsStatement = ("SELECT * FROM Question INNER JOIN events ON Question.feedbackFormID = events.feedbackFormID WHERE events.roomcode = '%s';" % eventID)
        feedbackQuestions = []
        questionIDs = []
        for row in conn.execute(getQuestionsStatement):
            questionIDs.append(row[0])
            questionNumber = row[1]
            questionType = row[2]
            questionName = row[3]
            feedbackFormID = row[4]
            feedbackQuestions.append([questionNumber, questionName, questionType])
        
        return feedbackQuestions, feedbackFormID, questionIDs

    def getFeedbackTemplate(self, templateName):

        conn = self.createConnection(self.database)
        getQuestionsStatement = ("SELECT * FROM Question WHERE feedbackFormID = (SELECT feedbackFormID from feedbackform WHERE templateName = '%s');" % templateName)
        feedbackQuestions = []
        for row in conn.execute(getQuestionsStatement):
            questionNumber = row[1]
            questionType = row[2]
            questionName = row[3]
            feedbackQuestions.append([questionNumber, questionName, questionType])

        return feedbackQuestions
    

    def getAnswers(self, roomCode):

        conn = self.createConnection(self.database)
        getQuestionID = ("SELECT questionID from Question WHERE feedbackFormID = (SELECT feedbackFormID FROM events WHERE roomcode= '%s');" %roomCode)
        getQuestions = ("SELECT content,type from Question WHERE questionID = ?")
        getAnswers= ("SELECT answer from feedbackQuestions INNER JOIN feedback ON feedbackQuestions.feedbackID = feedback.feedbackID WHERE feedbackQuestions.questionID = ? AND feedback.roomcode = ?")
        questionAns = []

        for elem in conn.execute(getQuestionID):
            questionID = elem[0]

            for qs in conn.execute(getQuestions, (questionID,)):
                question = qs[0]
                type = qs[1]
                
                for ans in conn.execute(getAnswers, (questionID, roomCode)):
                    answer = ans[0]
                    score = obj.polarity_scores(answer)
                    final = score['compound']
                    questionAns.append([question,type, answer, final])

        return questionAns
