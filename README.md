#                               Bakkal - Movies for Moral Education

## Introduction

This is my final project for CS50x Course. The purpose of the project is to get feedbacks from users on movies based on moral criteria so the recommended movies can be used in moral education. 

This project was developed in a virtual environment.

In this project, I have made use of

- Flask
- Flask-Session
- JavaScript
- HTML
- CSS
- Bootstrap
- Sqlite3 for database
- JSON
- JQuery
- requests
- tempfile
- werkzeug.security  to generate hash for passwords
- cs50 Library for SQL
- flash


## Features

Users can 

- Create an account
- Login
- Logout
- Get a new password
- Update password
- Search movies
- Leave feedback
- See other users' feedbacks
- Edit  and delete their own feedbacks
- Add movies to their watch list
- Remove movies from their watch list
- Update password

Certain requirenmets are enforced when user wants to submit a form. 


### Routing

Some routes requires login. User needs to be able to authenticated to be able to access them.

### Data

Data is pulled from Movie Database in RapidApi.

### Database

Relational database is used. Database has got 3 tables - users, movies, and watchlist. User id is used as foreign key. 

### Sessions

When user enters the correct credentials, a session for the user is being created. When user logs out, the session gets cleared. 

## Possible improvements

1. When different users leave comment on the same movie, there appears more than one of that movie on All Feedbacks page. I want to see only one of them. 
2. Leave comment on other user's feedbacks
3. Sending email to user for autentication
4. Giving user an option to retrieve their account in case they forget username and password together
5. Reporting inappropriate feedbacks or comments to admin
6. Making the website look elegant 
7. Adding user profile
8. Letting user update their profile
9. Adding more descriptions and instructions on some pages

## Instructions to launch

1. Clone the code: git clone https://github.com/ekrembel/Bakkal.git
2. Create a virtual environment
3. Install the required packages
4. Run command flask run
5. Copy the url you get in the terminal and paste it in the browser
