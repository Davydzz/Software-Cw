from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, g
import os
from user import User

import sys

import sqlite3
from dbConnection import DBConnection
import json

import time

from datetime import date, datetime

import base64
import hashlib

app = Flask(__name__) #instantiate flask object
app.secret_key = os.urandom(12)

db = DBConnection()

@app.before_request
def before_request():
    g.user = None
    g.room_code = None
    #store details about the user in the session
    if "user_id" in session:
        thisUserID = session["user_id"]
        results = db.getUserFromUserID(thisUserID)
        thisUser = User(thisUserID, results[5], results[3])
        g.user = thisUser
    #store details about the room code in the session
    if "room_code" in session:
        g.room_code = session["room_code"]

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route("/profile", methods=["GET","POST"])
def profile():
    global db
    if not g.user: 
        #if user not logged in, redirect them to the login page
        return redirect(url_for("login"))
    else:
        #user is logged in

        #store events user is hosting and attending
        hostRows, attendeeRows = db.getUserEvents(session["user_id"])

        #combine all events and store in 'displayResults'
        displayResults = []
        for hostEvent in hostRows:
            hostEvent.append("host")
            displayResults.append(hostEvent)
        for attendeeEvent in attendeeRows:
            attendeeEvent.append("attendee")
            displayResults.append(attendeeEvent)
        
        display = json.dumps(displayResults)
        g.jdump = display.replace("'","\\'")

        if request.method == "POST":
            chosenIndex = int(request.form["joinButton"]) #index of event in displayResults user clicked on

            result = displayResults[chosenIndex]
            roomcode = result[0]
            role = result[2]

            session["room_code"] = roomcode #store room code in session
            if role == "attendee":
                return redirect(url_for("attendee"))
            elif role == "host":
                return redirect(url_for("liveFeedback", roomCode = roomcode))

    return render_template("create_or_join.html")

@app.route("/attendee/", methods=["GET","POST"])
def attendee():
    global db
    #get the relevant feedback form for the event the user is attending
    feedbackQuestions, feedbackFormID, questionIDs = db.getFeedbackFormDetails(session["room_code"])

    feedbackQs = json.dumps(feedbackQuestions)
    g.jdump = feedbackQs.replace("'","\\'")

    if request.method == "POST":
        result = []
        try:
            anonymous = request.form["anonymous"] #a string, "True" for anonymous or "False" for not anonymous            
            form = request.form

            for key in form.keys():
                for value in form.getlist(key):
                    if key == "starRating":
                        if value == "":
                            #the user has not selected an option for the star rating
                            raise Exception
                        else:
                            result.append(value)
                    elif key == "text":
                        if value == "":
                            #the user has not input anything in the text feedback box
                            raise Exception
                        else:
                            result.append(value)
                            
            #convert the variable, 'anonymous' into a boolean
            if anonymous == "True":
                anonymous = True
            else:
                anonymous = False

            userID = None
            if ("user_id" in session) and (anonymous == False):
                #set the userID only if the user is logged into an account and has opted to not be anonymous
                userID = session["user_id"]

            #add feedback to the database
            successful, feedbackID = db.addFeedback(userID, anonymous, datetime.now(), feedbackFormID, session["room_code"], 0)

            #add each question in the feedback form to the database
            for i in range(len(questionIDs)):
                questionID = questionIDs[i]
                answer = result[i]
                questionType = feedbackQuestions[i][2]
                if questionType == "Star Rating":
                    answer = len(answer)
                db.addFeedbackQuestion(questionID, feedbackID, answer, session["room_code"],session["user_id"])

            g.feedbackresult = "Thanks! Your feedback has been submitted!"
        except Exception as e:
            g.feedbackresult = "Please complete all questions on the feedback form"

    return render_template("deliver_feedback.html")

@app.route("/join", methods=["GET", "POST"])
def joinEvent():
    global db
    if request.method == "POST":
        session.pop("room_code",None) #remove room code if it is already set
        roomCode = request.form["roomCode"]
        userID = None
        if "user_id" in session:
            userID = session["user_id"]
        if db.joinEvent(roomCode, userID): #add user to database
            #redirect to deliver feedback page
            session["room_code"] = roomCode
            return redirect(url_for("attendee"))

    return render_template("join.html")

@app.route("/create", methods=["GET","POST"])
def createEvent():
    global db
    templateList = db.returnTemplates() #store list of all templates in database

    if request.method == "POST":
        session.pop("room_code",None) #remove room code if it is already set
        eventName = request.form["eventName"]
        template = request.form["template"]
        feedbackFrequency = request.form["feedbackFrequency"]
        
        hour = request.form["hour"]
        minute = request.form["minute"]

        session["eventName"] = eventName
        session["template"] = template
        session["feedbackFrequency"] = feedbackFrequency
      
        if template == "Create":
            return redirect(url_for("createTemplate"))
        else:
            today = date.today()
            feedbackFormID = db.getFeedbackFormID(template)
            bool, roomCode = db.createEvent(session["eventName"], session["feedbackFrequency"], session["user_id"], today , True, feedbackFormID) 
            session["room_code"] = roomCode
            return redirect(url_for("liveFeedback", roomCode = session["room_code"]))

    return render_template("create_event.html", list = templateList)

@app.route('/login', methods=["GET","POST"])
def login():
    global db
    if request.method == "POST":
        session.pop("user_id",None) #remove user ID if it is already set
        email = request.form["username"]
        password = request.form["password"]
        success, userID = db.confirmLogin(email, password) #returns true if successful, false otherwise
        if success:
            session["user_id"] = userID
            #redirect to user's profile if successful login
            return redirect(url_for("profile"))
        #redirect to login page if unsuccessful login
        return redirect(url_for("login"))
        
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    global db
    if request.method == "POST":
        session.pop("user_id",None) #remove user ID if it is already set
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        email = request.form["email"]
        password = request.form["password"]
        passwordConfirm = request.form["passwordConfirm"]
        
        if password == passwordConfirm:
            salt = str(base64.b64encode(os.urandom(16)),"utf-8") #generate a salt
            toHash = salt + password #concatenate salt and input password
            hashedPassword = hashlib.sha256(bytes(toHash,"utf-8")).hexdigest() #hash the concatenation
            success, userID = db.addUser(salt, hashedPassword, firstName, lastName, email) #attempt to add the user to the database
            if success:
                #successful registration, redirect to user's profile
                session["user_id"] = userID
                return redirect(url_for("profile"))
            else:
                #email already exists, redirect to registration page
                return redirect(url_for("register"))   
        else:
            #passwords don't match, redirect to registration page
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/createtemplate", methods=["GET","POST"])
def createTemplate():
    global db
    if request.method == "POST":        
        result = []
        try:
            name = request.form["templateName"]           
            form = request.form

            index = 0
            for key in form.keys():
                for value in form.getlist(key):
                    if key == "txt":
                        if value == "":
                            #There is a question that has not been given a question name
                            raise Exception
                        else:
                            result.append([value])
                    elif key == "questionType":
                        if value == "blank":
                            #There is a quetion that has not been assigned a question type
                            raise Exception
                        else:
                            result[index].append(value)
                            index +=1
            
            today = date.today()
            #add template to database
            feedbackFormID = db.addTemplate(result, name) 

            #add event to database
            bool, roomCode = db.createEvent(session["eventName"], session["feedbackFrequency"], session["user_id"], today , True, feedbackFormID) 
            
            session["room_code"] = roomCode
            roomcode = session["room_code"]
            return redirect(url_for("liveFeedback", roomCode = roomcode))
        except Exception as e:
            return render_template("addqs.html")
    return render_template("addqs.html")

@app.route("/liveFeedback/<roomCode>", methods=["GET","POST"])
def liveFeedback(roomCode):
    global db

    #get feedback questions and sentiment score
    feedbackQuestions, nonCompounded = db.getAnswersDate(roomCode)

    getQs = json.dumps(feedbackQuestions)
    g.jdump = getQs.replace("'","\\'")
    g.compDump = json.dumps(nonCompounded)
    return render_template("livefeedback.html")

@app.route("/chart/<roomCode>", methods=["GET","POST"])
def chart(roomCode):
    global db
    #get feedback questions and sentiment score
    feedbackQuestions, nonCompounded = db.getAnswersDate(roomCode)

    getQs = json.dumps(feedbackQuestions)
    g.jdump = getQs.replace("'","\\'")
    g.compDump = json.dumps(nonCompounded)

    return render_template("chart.html")

