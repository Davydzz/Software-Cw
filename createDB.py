import sqlite3

def create_table(connection, tableSQL):
    try:
        cur = connection.cursor()
        cur.execute(tableSQL)
    except:
        print("Failed to make table")


def create_connection(db):
    conn = None
    try:
        conn = sqlite3.connect(db)
        return conn
    except:
        print("Connection didnt work")

    return conn



def main():
    database = 'database.db'

    #Tables here

    eventsTable = """CREATE TABLE events(
                                    roomcode int NOT NULL,
                                    eventName text,
                                    feedbackFrequency text,
                                    hostUserID int,
                                    date DATETYPE NOT NULL,
                                    active bool NOT NULL,
                                    FOREIGN KEY(hostUserID) REFERENCES Users(userID),
                                    PRIMARY KEY (roomcode)
                                  );"""


    feedback_form = """CREATE TABLE FeedbackForm (
                                    feedbackFormID int PRIMARY KEY,
                                    eventID int,
                                    overallSentiment int,
                                    FOREIGN KEY(eventID) REFERENCES Event(EventID)
                                );"""

    event_membersTable = """CREATE TABLE event_members(
                                    roomcode int NOT NULL,
                                    userID text NOT NULL,
                                    PRIMARY KEY (roomcode,userID),
                                    FOREIGN KEY (userID) REFERENCES users(userID)
                                    ON DELETE CASCADE,
                                    FOREIGN KEY (roomcode) REFERENCES events(roomcode)
                                    ON DELETE CASCADE
                                  );"""


    feedbackTable = """CREATE TABLE feedback(
                                    feedbackID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    userID int,
                                    anonymous BOOLEAN,
                                    timestamp DATETIME,
                                    feedbackFormID int,
                                    roomcode int NOT NULL,
                                    feedbackText text NOT NULL,
                                    sentiment int NOT NULL,
                                    FOREIGN KEY(feedbackFormID) REFERENCES FeedbackForm(feedbackFormID),
                                    FOREIGN KEY (userID) REFERENCES users(userID)
                                    ON DELETE CASCADE ON UPDATE CASCADE,
                                    FOREIGN KEY (roomcode) REFERENCES events(roomcode)
                                    ON DELETE CASCADE
                                  );"""


    usersTable = """CREATE TABLE users(
                                    userID  INTEGER PRIMARY KEY AUTOINCREMENT,
                                    salt text,
                                    password text,
                                    firstName text,
                                    lastName text,
                                    email text
                                  );"""

    questions = """CREATE TABLE Question (
                                    questionID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    questionNumber int,
                                    type text,
                                    content text,
                                    feedbackFormID int,
                                    feedbackID int,
                                    FOREIGN KEY(feedbackFormID) REFERENCES FeedbackForm(feedbackFormID),
                                    FOREIGN KEY(feedbackID) REFERENCES Feedback(feedbackID)
                                );"""


    conn = create_connection(database)

    try:
        conn.execute('''DROP TABLE events''')
        conn.execute('''DROP TABLE users''')
        conn.execute('''DROP TABLE event_members''')
        conn.execute('''DROP TABLE feedback''')
        conn.execute('''DROP TABLE FeedbackForm''')
        conn.execute('''DROP TABLE Question''')
    except:
        pass



    # create tables
    if conn is not None:

        create_table(conn, eventsTable)

        create_table(conn, usersTable)

        create_table(conn, feedbackTable)

        create_table(conn, event_membersTable)

        create_table(conn, feedback_form)

        create_table(conn, questions)

        #This is needed for the foreign keys to work
        conn.execute("PRAGMA foreign_keys = ON")


        #Commit changes
        conn.commit()


    else:
        print("Error! cannot create the database connection.")



if __name__ == '__main__':
    main()
