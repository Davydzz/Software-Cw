from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, g
import os
from user import User

import sqlite3
from dbConnection import DBConnection

from datetime import date

#https://www.youtube.com/watch?v=2Zz97NVbH0U&ab_channel=PrettyPrinted
#https://github.com/PrettyPrinted/youtube_video_code/tree/master/2020/02/10/Creating%20a%20Login%20Page%20in%20Flask%20Using%20Sessions/flask_session_example
#16/02/2021

#users = []
#newUserID = 0
#users.append(User(id=1, username='Anthony', password='password'))
#users.append(User(id=2, username='Becca', password='secret'))
#users.append(User(id=3, username='Carlos', password='somethingsimple')) #example

app = Flask(__name__) #instantiate flask object
app.secret_key = os.urandom(12)

db = DBConnection()

@app.before_request
def before_request():
    g.user = None
    g.room_code = None
    if "user_id" in session:
        thisUserID = session["user_id"]
        results = db.getUserFromUserID(thisUserID)
        print(results)
        thisUser = User(thisUserID, results[5], results[3])
        g.user = thisUser
    if "room_code" in session:
        g.room_code = session["room_code"]

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route("/profile") #user logged in, they can now create or join an event
def profile():
    if not g.user: #if not logged in
        #abort(403)
        return redirect(url_for("login"))
    return render_template("create_or_join.html")

@app.route("/attendee")
def attendee():
    #get what the feedback form looks like
    return render_template("deliver_feedback.html")

@app.route("/join", methods=["GET", "POST"])
def joinEvent():
    global db
    if request.method == "POST":
        session.pop("room_code",None) #remove room code if it is set
        roomCode = request.form["roomCode"]
        userID = None
        if "user_id" in session:
            userID = session["user_id"]
        if db.joinEvent(roomCode, userID):
            #redirect to deliver feedback page
            session["room_code"] = roomCode
            return redirect(url_for("attendee"))


    return render_template("join.html")

@app.route("/create", methods=["GET","POST"])
def createEvent():
    global db
    if request.method == "POST":
        session.pop("room_code",None) #remove room code if it is set
        eventName = request.form["eventName"]
        template = request.form["template"]
        feedbackFrequency = request.form["feedbackFrequency"]
        
        hour = request.form["hour"]
        minute = request.form["minute"]

        session["eventName"] = eventName
        session["template"] = template
        session["feedbackFrequency"] = feedbackFrequency
        session["hour"] = hour
        session["minute"] = minute #no idea if this is good coding

        #print(eventName, template, feedbackFrequency)
        #print(hour, minute)
        if template == "Create":
            return redirect(url_for("createTemplate"))
        else:
            pass


    return render_template("create_event.html")

@app.route('/login', methods=["GET","POST"])
def login():
    global db
    if request.method == "POST":
        session.pop("user_id",None) #remove user ID if it is set
        email = request.form["username"]
        password = request.form["password"]

        success, userID = db.confirmLogin(email, password)
        if success:
            session["user_id"] = userID
            return redirect(url_for("profile"))
        return redirect(url_for("login"))
        
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    global db
    
    if request.method == "POST":
        session.pop("user_id",None) #remove user ID if it is set
        username = request.form["username"]
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        email = request.form["email"]
        password = request.form["password"]
        passwordConfirm = request.form["passwordConfirm"]
        
        #generate a salt here
        if password == passwordConfirm:
            salt = "1234" #todo
            hashedPassword = salt + password #take the hash of this todo
            success, userID = db.addUser(salt, hashedPassword, firstName, lastName, email)
            if success:
                #successful registration
                session["user_id"] = userID
                return redirect(url_for("profile"))
            else:
                #email already exists
                print("EMAIL ALREADY EXISTS")
                return redirect(url_for("register"))
                
        else:
            print("PASSWORDS DON'T MATCH")
            #passwords don't match
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/createtemplate", methods=["GET","POST"])
#https://stackoverflow.com/questions/17752301/dynamic-form-fields-in-flask-request-form 24/02/2021
def createTemplate():
    global db

    if request.method == "POST":
        #result = {}
        #A hashmap will not preserve the index of the qs (txt and qT need to match)
        # Example=  {'txt': ['hello', 'hello1'], 'questionType': ['Text', 'Text']}
        # There is no link between "hello" and "Text"
        
        result = []
        try:           
            form = request.form
            #result["txt"] = []
            #result["questionType"] = []

            index = 0

            for key in form.keys():
                for value in form.getlist(key):

                    if key == "txt":
                        if value == "":
                            raise Exception
                        else:
                            result.append([value])
                    elif key == "questionType":
                        if value == "blank":
                            raise Exception
                        else:
                            result[index].append(value)
                            index +=1

                #index +=1
                    #result[key].append(value)
            print(result)

            #Now the txt and qT match up
            #[['hello', 'Text'], ['hello2', 'Text']]

            #add event to database
            today = date.today()
            bool, roomCode = db.createEvent(session["eventName"], session["feedbackFrequency"], session["user_id"], today , True) 
            #add feedback form to the database db.addFeedbackForm(...)
            db.addTemplate(result, roomCode)

            return redirect(url_for("liveFeedback"))
        except Exception as e:
            print(e)
            print("You failed")
    return render_template("addqs.html")

@app.route("/liveFeedback")
def liveFeedback():
    return render_template("livefeedback.html")

