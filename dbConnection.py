import sqlite3
import hashlib
import nltk
import datetime,time
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
obj = SentimentIntensityAnalyzer()

class DBConnection:
    def __init__(self):
        self.database = "database.db"

    #create a connection with the input name of the database
    def createConnection(self,db):
        conn = None
        try:
            conn = sqlite3.connect(db)
            conn.execute("PRAGMA foreign_keys = ON")
        except:
            print("Connection failed")
        return conn

    #attempt to add user to database, used in registration
    def addUser(self, salt, password, fName, lName, email):
        #create connection to database
        conn = self.createConnection(self.database)
        existingUserStatement = "SELECT * FROM users WHERE email = ?;" #? = email

        #check user is not already in db
        for row in conn.execute(existingUserStatement,(email,)):
            #user already exists in the database
            return False, None

        if conn is not None:
            #insert user into database
            insertStatement = ("INSERT INTO users (salt, password, firstName, lastName, email) VALUES (?, ?, ?, ?, ?);")
            conn.execute(insertStatement,(salt, password, fName, lName, email))
            conn.commit()
            userID = self.getIDFromEmail(email)
            return True, userID

    #add user feedback to feedback table of database
    def addFeedback(self, userID, anonymous, timestamp, feedbackFormID, roomcode, sentiment): 
        #create connection to database
        conn = self.createConnection(self.database)

        if conn is not None:
            if userID == None:
                #insert feedback for an anonymous or not logged in user
                insertStatement = "INSERT INTO feedback (anonymous, timestamp, feedbackFormID, roomcode, sentiment) VALUES (?, ?, ?, ?, ?);" # (anonymous, timestamp, feedbackFormID, roomcode, sentiment)
                conn.execute(insertStatement,(anonymous, timestamp, feedbackFormID, roomcode, sentiment))
            else:
                #insert non-anonymous feedback for a logged in user
                insertStatement = "INSERT INTO feedback (userID, anonymous, timestamp, feedbackFormID, roomcode, sentiment) VALUES (?, ?, ?, ?, ?, ?);" # (userID, anonymous, timestamp, feedbackFormID, roomcode, sentiment)
                conn.execute(insertStatement,(userID, anonymous, timestamp, feedbackFormID, roomcode, sentiment))
            #store the feedbackID that has been added
            id = conn.execute('select last_insert_rowID();')
            id = id.fetchone()
            id = id[0]
            conn.commit()
            return True,id

       #add user's response for feedback questions to the database
    def addFeedbackQuestion(self, questionID, feedbackID, answer, room, user):
        #create connection to database
        conn = self.createConnection(self.database)
        if conn is not None:
            cur = conn.cursor()
            checkIfAddedBefore= ("SELECT feedbackID FROM feedback WHERE userID = ? AND roomcode = ?;")
            insertStatement =  ("INSERT INTO feedbackQuestions (questionID, feedbackID, answer) VALUES (?, ?, ?);" )
            updateAnswer = ("UPDATE feedbackQuestions SET answer = ? WHERE feedbackID = ? AND questionID = ?;")
            #check if the user has submitted feedback for this event already
            cur.execute(checkIfAddedBefore, (user,room))
            possibleBefore = cur.fetchall()
            #if the user has submitted at least one feedback for the event already
            if len(possibleBefore) > 1:
                #update their feedback in the database
                conn.execute(updateAnswer, (answer, possibleBefore[0][0], questionID))
            else:
                #add their feedback to the database
                conn.execute(insertStatement, (questionID, feedbackID, answer))
            
            conn.commit()
            return True
        return False

    #return all events that the user is a host or an attendee of
    def getUserEvents(self, userID):
        #create connection to database
        conn = self.createConnection(self.database)
        if conn is not None:
            hostStatement = "SELECT roomcode, eventName FROM events WHERE hostUserID = ?;" #? = userID
            attendeeStatement = "SELECT events.roomcode, events.eventName FROM events INNER JOIN event_members ON events.roomcode = event_members.roomcode WHERE event_members.userID = ? AND events.active = 1;" #? = userID
            
            hostRows = []
            attendeeRows = []
            #get all events that the user is hosting
            for row in conn.execute(hostStatement,(userID,)):
                hostRows.append([row[0], row[1]])

            #get all events that the user is attending
            for row in conn.execute(attendeeStatement,(userID,)):
                attendeeRows.append([row[0], row[1]])
            return hostRows, attendeeRows

    #check a user's login details
    def confirmLogin(self, email, password):
        #create connection to database
        conn = self.createConnection(self.database)
        getSaltStatement = "SELECT salt FROM users WHERE email = ?;"
        saltFound = False
        #look for a user in the database and return their corresponding salt
        for row in conn.execute(getSaltStatement,(email,)):
            saltFound = True
            salt = row[0]

        if not saltFound:
            #the user could not be found in the database
            return False, None
        
        toHash = salt + password
        #calculate the hashed password from the user input
        hashedPassword = hashlib.sha256(bytes(toHash,"utf-8")).hexdigest()
        existingUserStatement = "SELECT * FROM users WHERE email = ? AND password = ?;"
        
        for row in conn.execute(existingUserStatement,(email, hashedPassword)):
            #input password matches the email in the database
            return True, row[0]
        return False, None

    #return userID from a given email
    def getIDFromEmail(self,email):
        #create connection to database
        conn = self.createConnection(self.database)
        getUserStatement = "SELECT userID FROM users WHERE email = ?;"
        for row in conn.execute(getUserStatement,(email,)):
            return row[0]

    #return details about user from their userID
    def getUserFromUserID(self, uID):
        #create connection to database
        conn = self.createConnection(self.database)
        getUserStatement = "SELECT * FROM users WHERE userID = ?;"
        for row in conn.execute(getUserStatement,(uID,)):
            return row

    #return feedback form ID from a template name
    def getFeedbackFormID(self, templateName):
        #create connection to database
        conn = self.createConnection(self.database)
        getFeedbackFormID = "SELECT feedbackFormID FROM FeedbackForm WHERE templateName = ?"
        for row in conn.execute(getFeedbackFormID,(templateName,)):
            return row[0]

    #add event to database
    def createEvent(self, eventName, feedbackFrequency, hostUserID, date, active, feedbackFormID):
        #with 10,000 events the collision rate is just over 1%
        validCode = False
        while not (validCode):
            validCode = True
            from random import randint
            #generate a roomcode between 100000 and 999999
            roomcode = (randint(100000,999999))
            roomcode = str(roomcode)

            #create connection to database
            conn = self.createConnection(self.database)
            existingEventStatement = "SELECT * FROM events WHERE roomcode = ?;" #? = roomcode
            for row in conn.execute(existingEventStatement,(roomcode,)):
                #an event with this roomcode already exists meaning that the roomcode is invalid
                validCode = False
        if conn is not None:
            #insert the event into the database
            insertStatement = ("INSERT INTO events (roomcode, eventName, feedbackFrequency, hostUserID, date, active, feedbackFormID) VALUES (?, ?, ?, ?, ?, ?, ?)")
            conn.execute(insertStatement,(roomcode, eventName, feedbackFrequency, hostUserID, date, active, feedbackFormID))
            conn.commit()
            return True, roomcode

    #add user to database as an attendee
    def joinEvent(self, roomCode, userID):
        #connect to db
        conn = self.createConnection(self.database)

        
        eventExistsStatement = "SELECT * FROM events WHERE roomCode = ?;" #? = roomCode
        roomCodeExists = False
        for row in conn.execute(eventExistsStatement,(roomCode,)):
            #roomcode exists in database
            roomCodeExists = True

        if roomCodeExists:
            if userID != None:
                try:
                    #if user is logged in, add them to database as an attendee
                    addUserToEventsStatement = "INSERT INTO event_members (roomcode, userID) VALUES (?, ?);" # ?1 = roomCode, ?2 = userID)
                    conn.execute(addUserToEventsStatement,(roomCode, userID))
                    conn.commit()
                except:
                    #user is already in the room
                    return True
            return True

        #room code doesn't exist
        return False

    #add template feedback form to database
    def addTemplate(self, result, templateName):
        #create connection to database
        conn = self.createConnection(self.database)
        #added templateName to differenciate in the drop down menu
        addFeedbackForm = ("""INSERT INTO FeedbackForm(templateName) VALUES (?);""")
        
        addQuestion = ("INSERT INTO Question(questionNumber, type, content, feedbackFormID) VALUES (?,?,?,?);")

        feedbackID = -1
        conn.execute(addFeedbackForm, (templateName,))
        id = conn.execute('select last_insert_rowID();')
        id = id.fetchone()
        feedbackID = id[0]
        questionNo = 1
        
        try:
            for elem in result:
                #add questions in feedback form to database
                conn.execute(addQuestion,(questionNo, elem[1], elem[0],feedbackID)) 
                questionNo +=1
            conn.commit()
            return feedbackID
        except Exception as e:
            return False
    
    #get feedback templates from database
    def returnTemplates(self):
        #create connection to database
        conn = self.createConnection(self.database)
        cur = conn.cursor()
        listTemplates = []
        getAllTemplates = ("SELECT templateName from FeedbackForm")
        cur.execute(getAllTemplates)
        rows = cur.fetchall()
        #cur.fetchAll returns a list of tuples, since they're all one element
        #tuples, convert it into a list
        for elem in rows:
            listTemplates.append(elem[0])

        return listTemplates

    #return all questions associated with the feedback form of a given event
    def getFeedbackFormDetails(self, eventID):
        #create connection to database
        conn = self.createConnection(self.database)
        getQuestionsStatement = "SELECT * FROM Question INNER JOIN events ON Question.feedbackFormID = events.feedbackFormID WHERE events.roomcode = ?;" #? =  eventID
        feedbackQuestions = []
        questionIDs = []
        #get questions for the feedback form associated with the event roomcode
        for row in conn.execute(getQuestionsStatement,(eventID,)):
            questionIDs.append(row[0])
            questionNumber = row[1]
            questionType = row[2]
            questionName = row[3]
            feedbackFormID = row[4]
            feedbackQuestions.append([questionNumber, questionName, questionType])
        
        return feedbackQuestions, feedbackFormID, questionIDs

    #get feedback template questions from a given name
    def getFeedbackTemplate(self, templateName):
        #create connection to database
        conn = self.createConnection(self.database)
        getQuestionsStatement = "SELECT * FROM Question WHERE feedbackFormID = (SELECT feedbackFormID from feedbackform WHERE templateName = ?);" #? = templateName
        feedbackQuestions = []
        for row in conn.execute(getQuestionsStatement,(templateName,)):
            questionNumber = row[1]
            questionType = row[2]
            questionName = row[3]
            feedbackQuestions.append([questionNumber, questionName, questionType])

        return feedbackQuestions
    
    #get sentiment score of feedback for questions of a given event
    def getAnswers(self, roomCode):
        #create connection to database
        conn = self.createConnection(self.database)
        getQuestionID = ("SELECT questionID from Question WHERE feedbackFormID = (SELECT feedbackFormID FROM events WHERE roomcode= ?);") #? = roomCode
        getQuestions = ("SELECT content,type from Question WHERE questionID = ?")
        getAnswers= ("SELECT answer from feedbackQuestions WHERE questionID = ?")
        questionAns = []

        #loop through each question in feedback form for the given event
        for elem in conn.execute(getQuestionID,(roomCode,)):
            questionID = elem[0]
            #loop through name and question type for each question
            for qs in conn.execute(getQuestions, (questionID,)):
                question = qs[0]
                type = qs[1]
                #loop through answers for the given question
                for ans in conn.execute(getAnswers, (questionID,)):
                    answer = ans[0]
                    score = obj.polarity_scores(answer)
                    final = score['compound']
                    questionAns.append([question,type, answer, final])

        return questionAns
    
    #get sentiment score of feedback for questions of a given event along with the time that the feedback was submited
    def getAnswersDate(self, roomCode):
        #create connection to database
        conn = self.createConnection(self.database)

        getQuestionID = ("SELECT questionID from Question WHERE feedbackFormID = (SELECT feedbackFormID FROM events WHERE roomcode= ?);") #? = roomCode
        getQuestions = ("SELECT content,type from Question WHERE questionID = ?;")
        getFeedbackID= ("SELECT feedBackID from feedbackQuestions WHERE questionID = ?;")
        getAnswers=  ("SELECT answer,feedback.feedBackID from feedbackQuestions INNER JOIN feedback ON feedbackQuestions.feedbackID = feedback.feedbackID WHERE feedbackQuestions.questionID = ? AND feedback.roomcode = ?;")
        getTimeStamp = ("SELECT timestamp from feedback WHERE feedBackID = ?;")

        questionAns = []
        nonCompounded= []

        #loop through each question in feedback form for the given event
        for elem in conn.execute(getQuestionID,(roomCode,)):
            questionID = elem[0]
            #loop through name and question type for each question
            for qs in conn.execute(getQuestions, (questionID,)):
                question = qs[0]
                type = qs[1]
                #loop through answers for the given question
                for ans in conn.execute(getAnswers, (questionID,roomCode)):
                    answer = ans[0]
                    feedBackID = ans[1]

                    #Get the time that this feedback was submited using the feedback's feedbackID
                    for stamp in conn.execute(getTimeStamp, (feedBackID,)):
                        timestamp = stamp[0]

                    #The timestamp is translated from the date format used in the database into unix epoch which is more 
                    #convinient for time comparisons
                    date_time_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                    timestamp = time.mktime(date_time_obj.timetuple())

                    score = obj.polarity_scores(answer)
                    final = score['compound']
                    nonCompounded.append(score)
                    questionAns.append([question,type, answer, final, timestamp])

        return questionAns, nonCompounded
