import os
import requests
from datetime import date, time
import json
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import login_required, lookup

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

# Make sure API Key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API KEY not set")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    else:
        # Get and store user input 
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")

        # Generate a hash for the password
        user_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        db.execute("INSERT INTO users (email, hash, firstname, lastname) VALUES (:email, :user_hash, :firstname, :lastname);", email=email, user_hash=user_hash, firstname=firstname, lastname=lastname) 

        flash("Welcome to SafeWatch!")

        return render_template("login.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        session["username"] = request.form.get("username")
        
        rows = db.execute("SELECT * FROM users WHERE email = :email;", email=session["username"])

        # Ensure username exists and password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
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
        # movie_id = request.form.get("movie_id")
        movie_name = request.form.get("movieName")
        if movie_name == "":
            message = "Please enter a key word to search!"
            return render_template("search.html", message=message) 
        data = lookup(movie_name)
        return render_template("search.html", data=data)
        if data == None:
            message = "No results"
            return render_template("search.html", message=message)              
        else:
            return render_template("search.html", data=data)
        # elif movie_id != None:
        #     return render_template("comment.html", movie_id=movie_id)

  

@app.route("/comment", methods=["GET", "POST"])
@login_required
def comment():
    if request.method == "GET":
        return render_template("comment.html")

    else:
        user_data = db.execute("SELECT user_id FROM users WHERE email == :email;", email=session["username"])
        user_id = user_data[0]["user_id"]
        movie_id = request.form.get("movie_id")
        comment = request.form.get("comment")

        db.execute("INSERT INTO movies (user_id, comment, imdbId) VALUES (:user_id, :comment, :imdbId);", user_id=user_id, comment=comment, imdbId=movie_id)

        flash("Your comment has been added!")
        return redirect("/")