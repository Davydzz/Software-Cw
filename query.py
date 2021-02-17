import sqlite3


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
    conn = create_connection(database)



    if conn is not None:

        conn.execute("INSERT INTO users VALUES ('1','1234','password','Fname','Lname','email')")

        conn.commit()


        for row in conn.execute('''SELECT * FROM users;'''):
            print(row)


        conn.execute("DELETE FROM users WHERE USERID = '1'")


        for row in conn.execute('''SELECT * FROM users;'''):
            print(row)



    else:
        print("Error! cannot create the database connection.")



if __name__ == '__main__':
    main()
