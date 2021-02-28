import sqlite3

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
    def addFeedback(self, userID, anonymous, timestamp, feedbackFormID, roomcode, feedbackText, sentiment): #used for registration
        conn = self.createConnection(self.database)

        if conn is not None:
            insertStatement = ("INSERT INTO feedback (userID, anonymous, timestamp, feedbackFormID, roomcode, feedbackText, sentiment) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (userID, anonymous, timestamp, feedbackFormID, roomcode, feedbackText, sentiment))
            conn.execute(insertStatement)
            id = conn.execute('select last_insert_rowID();')
            id = id.fetchone()
            id = id[0]
            conn.commit()
            return True,id

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

    def confirmLogin(self, email, password):
        conn = self.createConnection(self.database)
        getSaltStatement = ("SELECT salt FROM users WHERE email = '%s';" % email)
        saltFound = False
        for row in conn.execute(getSaltStatement):
            saltFound = True
            salt = row[0]
        if not saltFound:
            return False, None
        hashedPassword = salt + password #todo: hash this
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

    def createEvent(self, eventName, feedbackFrequency, hostUserID, date, active):

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
            insertStatement = ("INSERT INTO events (roomcode, eventName, feedbackFrequency, hostUserID, date, active) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (roomcode, eventName, feedbackFrequency, hostUserID, date, active))
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
                #then add userID to event_members
                addUserToEventsStatement = ("INSERT INTO event_members (roomcode, userID) VALUES ('%s', '%s')" % (roomCode, userID))
                conn.execute(addUserToEventsStatement)
                conn.commit()
            return True

        print("Room code doesn't exist")
        return False

    # Fix bug tmr morning
    def addTemplate(self, result, roomCode, templateName):

        conn = self.createConnection(self.database)
        #added templateName to differenciate in the drop down menu
        addFeedbackForm = ("INSERT INTO FeedbackForm(templateName,eventID, overallSentiment) VALUES (?,?,?);")
        addQuestion = ("INSERT INTO Question(questionNumber, type, content, feedbackFormID) VALUES (?,?,?,?);")
        getFeedbackFormID = ("SELECT feedbackFormID FROM FeedbackForm WHERE eventID = ?")

        conn.execute(addFeedbackForm, (templateName, roomCode, 0))
        for row in conn.execute(getFeedbackFormID, (roomCode,)):
            feedBackID = row[0]
        questionNo = 1
        
        try:
            for elem in result:
                conn.execute(addQuestion,(questionNo, elem[1], elem[0],feedBackID)) #it dies on this line
                questionNo +=1
            
            conn.commit()
            return True
        except Exception as e:
            print(e)
            print("Template creation failure")
            return False