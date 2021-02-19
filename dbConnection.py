import sqlite3

class DBConnection:
    def __init__(self):
        self.database = "database.db"

    def createConnection(self,db):
        conn = None
        try:
            conn = sqlite3.connect(db)
        except:
            print("Connection didn't work")
        return conn

    def addUser(self, salt, password, fName, lName, email): #used for registration
        #check user is not already in db
        conn = self.createConnection(self.database)
        existingUserStatement = ("SELECT * FROM users WHERE email = '%s'" % email)
        for row in conn.execute(existingUserStatement):
            print(row)
            #already exists
            return False, None
        
        if conn is not None:
            insertStatement = ("INSERT INTO users (salt, password, firstName, lastName, email) VALUES ('%s', '%s', '%s', '%s', '%s')" % (salt, password, fName, lName, email))
            conn.execute(insertStatement)
            conn.commit()
            userID = self.getIDFromEmail(email)
            return True, userID

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

    def createEvent(self):
        pass
        #room code
        #event name
        #feedback frequency
        #hostuserID
        #date text
        #active bool

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
