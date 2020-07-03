import os
import requests
import urllib.parse

from flask import request, redirect, render_template, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def search_by_name(name):
    """Look up quote for symbol."""

    # Contact API
    try:
        url = "https://movie-database-imdb-alternative.p.rapidapi.com/"
        
        querystring = {"page":1 ,"r":"json","s": name}

        headers = {
            'x-rapidapi-host': "movie-database-imdb-alternative.p.rapidapi.com",
            'x-rapidapi-key': "1bd81643f7msh84a60c3a642fe03p13d292jsn5e60be7005e8"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
    except requests.RequestException:
        return None

    # Parse response
    try:
        r = response.json()
        movies = r["Search"]
        return movies
    except (KeyError, TypeError, ValueError):
        return None 

def search_by_id(imdb_id):
    """Look up movie for imdb id."""

    # Contact API
    try:
        url = "https://movie-database-imdb-alternative.p.rapidapi.com/"

        querystring =  {"i":imdb_id,"r":"json"}

        headers = {
            'x-rapidapi-host': "movie-database-imdb-alternative.p.rapidapi.com",
            'x-rapidapi-key': "1bd81643f7msh84a60c3a642fe03p13d292jsn5e60be7005e8"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
    except requests.RequestException:
        return None

    # Parse response
    try:
        r = response.json()
        return r
    except (KeyError, TypeError, ValueError):
        return None  

def message(message):
    return render_template("message.html", message=message)                   