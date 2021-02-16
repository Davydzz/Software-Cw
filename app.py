from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, g
import os
from user import User

#https://www.youtube.com/watch?v=2Zz97NVbH0U&ab_channel=PrettyPrinted
#https://github.com/PrettyPrinted/youtube_video_code/tree/master/2020/02/10/Creating%20a%20Login%20Page%20in%20Flask%20Using%20Sessions/flask_session_example
#16/02/2021

users = []
newUserID = 4
users.append(User(id=1, username='Anthony', password='password'))
users.append(User(id=2, username='Becca', password='secret'))
users.append(User(id=3, username='Carlos', password='somethingsimple')) #example

app = Flask(__name__) #instantiate flask object
app.secret_key = os.urandom(12)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session["user_id"]][0]
        g.user = user

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/profile") #user logged in, they can now create or join an event
def profile():
    if not g.user: #if not logged in
        #abort(403)
        return redirect(url_for('login'))
    return render_template("create_or_join.html")

@app.route("/join")
def joinEvent():
    return render_template("join.html")

@app.route("/create")
def createEvent():
    return render_template("create_event.html")

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        session.pop("user_id",None) #remove user ID if it is set
        username = request.form["username"]
        password = request.form["password"]

        user = [x for x in users if x.username == username] #find user in list of users
        if user != []: #no matching username
            user = user[0] #only one user should be returned
            if user and user.password == password:
                #user and pass match, login
                session["user_id"] = user.id
                return redirect(url_for("profile"))
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        session.pop("user_id",None) #remove user ID if it is set
        username = request.form["username"]
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        email = request.form["email"]
        password = request.form["password"]
        passwordConfirm = request.form["passwordConfirm"]
        matches = [x for x in users if x.username == username]
        if matches != []:
            #username is already taken
            return redirect(url_for("register"))
        elif password != passwordConfirm:
            #passwords don't match
            return redirect(url_for("register"))
        else:
            #add this user to users
            global newUserID
            users.append(User(id=newUserID, username=username, password=password))
            #add to db as well todo
            
            #log user in
            session["user_id"] = newUserID
            newUserID += 1
            return redirect(url_for("profile"))

    return render_template("register.html")

