import sqlite3

def create_table(connection, tableSQL):
    try:
        cur = connection.cursor()
        cur.execute(tableSQL)
    except Exception as e:
        print(e)
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
                                    feedbackFormID INTEGER NOT NULL,
                                    FOREIGN KEY(feedbackFormID) REFERENCES FeedbackForm(feedbackFormID),
                                    FOREIGN KEY(hostUserID) REFERENCES Users(userID),
                                    PRIMARY KEY (roomcode)
                                  );"""


    feedback_form = """CREATE TABLE FeedbackForm (
                                    feedbackFormID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    templateName text
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

    # Removed feedbackID since feedbackTable already contains feedbackID and feedbackformID
    questions = """CREATE TABLE Question (
                                    questionID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    questionNumber int,
                                    type text,
                                    content text,
                                    feedbackFormID int,
                                    FOREIGN KEY(feedbackFormID) REFERENCES FeedbackForm(feedbackFormID)
                                );"""
    
    # Instead of creating a separate column for the stars, we could convert the stars into a string equivalent
    # This could simplify the code for the future
    feedbackQuestions = """CREATE TABLE feedbackQuestions (
                                    questionID int,
                                    feedbackID int,
                                    answer text NOT NULL,
                                    PRIMARY KEY (questionID, feedbackID),
                                    FOREIGN KEY (questionID) REFERENCES Question(questionID)
                                    ON DELETE CASCADE,
                                    FOREIGN KEY (feedbackID) REFERENCES feedback(feedbackID)
                                    ON DELETE CASCADE


    );
    
    
    """


    conn = create_connection(database)

    try:
        conn.execute('''DROP TABLE events''')
        conn.execute('''DROP TABLE users''')
        conn.execute('''DROP TABLE event_members''')
        conn.execute('''DROP TABLE feedback''')
        conn.execute('''DROP TABLE FeedbackForm''')
        conn.execute('''DROP TABLE Question''')
        conn.execute('''DROP TABLE feedbackQuestions''')
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

        create_table(conn, feedbackQuestions)

        #This is needed for the foreign keys to work
        conn.execute("PRAGMA foreign_keys = ON")


        #Commit changes
        conn.commit()


    else:
        print("Error! cannot create the database connection.")



if __name__ == '__main__':
    main()