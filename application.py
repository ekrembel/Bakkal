import os
import requests
from datetime import date, time
import json
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import login_required, search_by_id, search_by_name, message

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure system to use filesystem instead of signed cookies
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure cs50 Library to use SQLite database
db = SQL("sqlite:///movies.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    else:
         
        cancel = request.form.get("cancel")
        if cancel:
            return redirect("/")

        # Get and store user input
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Generate a hash for the password
        user_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        db.execute("INSERT INTO users (email, hash, username) VALUES (:email, :user_hash, :username);", email=email, user_hash=user_hash, username=username) 

        flash("Welcome to Bakkal!")

        return render_template("login.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        # Get user name
        session["username"] = request.form.get("username")
        
        # Query database for user info
        rows = db.execute("SELECT * FROM users WHERE username = :username;", username=session["username"])
        # Check if user info exists in database
        if len(rows) == 0:
            # Inform  user
            message = "User does not exist."
            return render_template("login.html", loginFailed=message)
        # Ensure username exists and password is correct
        elif not check_password_hash(rows[0]["hash"], request.form.get("password")):
            loginFailed = "Username or password is incorrect!"
            return render_template("login.html", loginFailed=loginFailed)

        session["user_id"] = rows[0]["hash"]
        
        return redirect("/")             

    else:
        return render_template("login.html") 

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():

    if request.method == "GET":
        return render_template("search.html")

    else:
        # Get user input
        movie_id = request.form.get("movie_id")     
        # Check if user input is not a movie id       
        if not movie_id:
            # Get user input
            movie_name = request.form.get("movieName")
            # Pull movie info by keyword
            movies = search_by_name(movie_name)
            # Inform user if no results
            if movies == None:
                message = "No results"
                return render_template("search.html", message=message)              
            else:
                return render_template("search.html", movies=movies)
        # If user input is a movie id        
        else:
            return render_template("feedback.html", movie_id=movie_id)

  

@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    if request.method == "GET":
        return render_template("feedback.html")

    else:
        # Query database for user id
        user_data = db.execute("SELECT user_id FROM users WHERE username == :username;", username=session["username"])
        user_id = user_data[0]["user_id"]

        # Get user input
        movie_id = request.form.get("movie_id")
        # Query database for feedback
        check = db.execute("SELECT * FROM movies WHERE imdbId=:imdbId AND user_id=:user_id;", imdbId=movie_id, user_id=user_id)
        # Check if user has already submitted feedback on the movie
        if len(check) == 0:
            # Pull movie info
            movie = search_by_id(movie_id)
            title = movie["Title"]
            image = movie["Poster"]
            # Get user input
            feedback = request.form.get("feedback")
            header = request.form.get("header")
            ifRecommend = request.form.get("recommend")
            # Insert user feedback to database
            db.execute("INSERT INTO movies (user_id, feedback, imdbId, feedback_type, feedback_header, title, image) VALUES (:user_id, :feedback, :imdbId, :feedback_type, :feedback_header, :title, :image);", user_id=user_id, feedback=feedback, imdbId=movie_id, feedback_type=ifRecommend, feedback_header=header, title=title, image=image)

            # Inform user
            flash("Your feedback has been added! Thank you!")
            return redirect("/myFeedbacks")
        else:
            # Inform user
            message = "You have already submitted a feedback for this movie. You can edit your feedback."    
            return render_template("myFeedbacks.html", message=message)    

@app.route("/check", methods=["GET", "POST"])
@login_required
def check():
    if request.method == "GET":
        return render_template("check.html")
    else:
        # Get user input
        movie_id = request.form.get("movie_id")
        # Query database for feedbacks
        feedbacks = db.execute("SELECT * FROM movies JOIN users ON movies.user_id = users.user_id WHERE imdbId = :imdbId;", imdbId=movie_id)
        # Pull movie info by movie id
        data = search_by_id(movie_id)
        # Inform user if there is no feedbacks
        if len(feedbacks) == 0:
            message = "No feedbacks yet!"
            return render_template("check.html", message=message, data=data)
        else:
            return render_template("check.html", feedbacks=feedbacks, data=data)

@app.route("/myFeedbacks", methods=["GET", "POST"])
@login_required
def myFeedbacks():
    if request.method == "GET":
        # Query database for user feedbacks
        movies = db.execute("SELECT * FROM movies JOIN users ON movies.user_id = users.user_id WHERE username=:username;", username=session["username"])
        # Inform user if user has no feedbacks
        if len(movies) == 0:
            return message("You have no feedbacks!")

        else:    
            return render_template("myFeedbacks.html", movies=movies)


@app.route("/allFeedbacks")
@login_required
def allFeedbacks():
    # Query database for user feedbacks
    movies = db.execute("SELECT DISTINCT * FROM movies JOIN users ON movies.user_id = users.user_id;")
    if len(movies) == 0:
        # Inform user if user has no feedbacks
        return message("There is no feedbacks yet!")
    else:    
        return render_template("allFeedbacks.html", movies=movies)

@app.route("/edit", methods=["POST"])
@login_required
def edit():   
    if request.method == "POST":
        # Get user input 
        movie_id = request.form.get("edit")
        # Query database for user feedback
        movie = db.execute("SELECT * FROM movies WHERE imdbId=:imdbId;", imdbId=movie_id)
        return render_template("edit.html", feedback=movie)

@app.route("/edited", methods=["POST"])
@login_required
def edited():
    if  request.method == "POST":
        # Get user input
        delete = request.form.get("delete")

        if delete == None:
            # Get user input
            new_header = request.form.get("editHeader")
            new_feedback = request.form.get("editFeedback")
            new_recommend = request.form.get("editRecommend")
            movie_id_edit = request.form.get("editMovieId") 

            # Update user feedback on database and inform user
            db.execute("UPDATE movies SET feedback_header=:header, feedback=:feedback, feedback_type=:feedback_type WHERE imdbId=:imdbId;", header=new_header, feedback=new_feedback, feedback_type=new_recommend, imdbId=movie_id_edit)
            flash("Your feedback has been updated!")
            return render_template("myFeedbacks.html")
        else:
            # Query database for user id
            user = db.execute("SELECT * FROM users JOIN movies ON users.user_id=movies.user_id WHERE username=:username;", username=session["username"])
            user_id = user[0]["user_id"]
            # Delete feedback from database and inform user
            db.execute("DELETE FROM movies WHERE imdbId=:imdbId AND user_id=:user_id;", imdbId=delete, user_id=user_id)                        
            flash("Your feedback has been deleted!")
            return render_template("myFeedbacks.html")                   


@app.route("/watchList", methods=["GET" ,"POST"])
@login_required
def watchList():
    # Query database for user id
    user_id_dict = db.execute("SELECT user_id FROM users WHERE username=:username;", username=session["username"]) 
    user_id = user_id_dict[0]["user_id"] 

    if request.method == "GET":
        # Query database for user watch list
        movies = db.execute("SELECT * FROM mylist WHERE user_id=:user_id;", user_id=user_id)
        if len(movies) == 0:
            # Inform user if user has nothing to watch
            return message("Your watch list is empty.")
        else:    
            return render_template("watchList.html", movies=movies)

    else:
        # Get user input
        movie_id = request.form.get("movie_id")
        # Get movie info
        movie = search_by_id(movie_id)
        title = movie["Title"]
        image = movie["Poster"]  
        # Query database for user watch list
        movie_listed = db.execute("SELECT * FROM mylist WHERE imdbId=:imdbId AND user_id=:user_id;", imdbId=movie_id, user_id=user_id) 
        # Inform user and prevent from leaving multiple feedbacks on the same movie
        if len(movie_listed) > 0:
            return message("You already have this movie in your watch list")
            
            
        else:
            # Update user watch list on database and inform user
            db.execute("INSERT INTO mylist (user_id, imdbId, title, image) VALUES (:user_id, :imdbId, :title, :image);", user_id=user_id, imdbId=movie_id, title=title, image=image)
            flash("Added to your watch list!")
            return redirect("/watchList")


@app.route("/remove", methods=["POST"])
@login_required
def remove():
    # Query database for user id
    user_id_dict = db.execute("SELECT user_id FROM users WHERE username=:username;", username=session["username"]) 
    user_id = user_id_dict[0]["user_id"]
    # Get user input
    movie_id = request.form.get("movie_id")
    # Remove movie from watch list on database
    db.execute("DELETE FROM mylist WHERE imdbId=:imdbId AND user_id=:user_id;", imdbId=movie_id, user_id=user_id)
    flash("Removed!")
    return redirect("/watchList")


@app.route("/updatePassword", methods=["GET", "POST"])
@login_required
def updatePassword():
    if request.method == "GET":
        return render_template("updatePassword.html")
    else:
        # Get user input
        current_password = request.form.get("currentPassword")
        new_password = request.form.get("newPassword")

        # Query database for user hash
        user_data = db.execute("SELECT hash FROM users WHERE username=:username;", username=session["username"])
        user_hash = user_data[0]["hash"]
        # Check if user input matches user hash
        if check_password_hash(user_hash, current_password):
            # Generate new hash for new password
            new_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            # Update user hash on database and inform user
            db.execute("UPDATE users SET hash=:new_hash WHERE username=:username;", new_hash=new_hash, username=session["username"])
            flash("Your password has been updated!")
            return redirect("/")
        else:
            # Inform user
            return message("Password doesn't match!")    

@app.route("/forgotPassword", methods=["GET", "POST"])
def forgotPassword():
    if request.method == "GET":
        return render_template("forgotPassword.html")

    else:
        # Get user input
        email = request.form.get("email")
        new_password = request.form.get("newPassword")

        # Query database for user info
        user_data = db.execute("SELECT * FROM users WHERE email=:email;", email=email)
        # Check if user input is in database
        if (len(user_data) > 0):

            # Generate new hash for new password
            new_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            # Update user hash on database and inform user
            db.execute("UPDATE users SET hash=:new_hash WHERE email=:email;", new_hash=new_hash, email=email)
            flash("Your password has been updated!")
            return render_template("login.html")
        else:
            # Inform user email not registered
            return message("Email doesn't match!")     


@app.route("/deleteAccount", methods=["GET", "POST"])
@login_required
def deleteAccount():
    if request.method == "GET":
        return render_template("deleteAccount.html")

    else:
        # Get user input
        current_password = request.form.get("password")

        # Query database for user hash and user id
        user_data = db.execute("SELECT * FROM users WHERE username=:username;", username=session["username"])
        user_hash = user_data[0]["hash"]
        user_id = user_data[0]["user_id"]

        # Delete user account if user hash matches user input
        if check_password_hash(user_hash, current_password):
            db.execute("DELETE FROM mylist WHERE user_id=:user_id", user_id=user_id)
            db.execute("DELETE FROM movies WHERE user_id=:user_id", user_id=user_id)
            db.execute("DELETE FROM users WHERE user_id=:user_id", user_id=user_id)
            session.clear()
            # Inform user
            flash("Your account has been deleted!")
            return render_template("login.html")
        else:
            # Inform user that input does not match
            return message("Password doesn't match!") 


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logged out!")
    return redirect("/")