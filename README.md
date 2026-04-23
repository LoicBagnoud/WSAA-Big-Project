# WSAA-Big-Project

# Game Database Web Application

## Table of Contents
- [Overview](#overview)
- [What's currently possible](#whats-currently-possible)
- [What was Used](#What-was-used)
- [Some notes on the Project](#some-notes-on-the-project)
- [References](#references)
- [Project Structure](#project-structure)


## Overview
This project is a web application that allows users to create, view, update, and delete video game records stored in a database. The application also supports displaying box cover images for each game and provides a simple browser-based interface for interacting with the data. 

The way this works is by an API call that gets sent to [theGamesDB](https://thegamesdb.net/) to get us the images we need.

The purpose of this project was to develop a full-stack web application that combines backend development, database management, API handling, and frontend design.

Final Project:
https://sirktar.pythonanywhere.com/index.html

---

## What's currently possible
- View all games stored in the database
- Search for those games based on what's written
- Add new games
- Update existing game details
- Delete games
- Store and display box cover images
- Simple and user-friendly web interface
- Persistent database storage using SQLite

---

## What was Used
### Backend
- Python
- Flask
- SQLite

### Frontend
- HTML
- CSS
- JavaScript

### Other Tools
- GitHub
- PythonAnywhere
- VS Code
- Postman

---

## Some notes on the Project

This project is meant to be hosted on sqlite3. To run it on your local machine, make sure to: 

    1 - Run the init_db.py application first to that you have the database created

    3 - In the gamesDAO.py file, where it states the class, make sure that the db_file variable looks like this:
        
        **db_file = "games.db"** and not like this **db_file = "/home/sirktar/WSAA-Big-Project/games.db"**

        The code on github is what was uploaded to pythonanywhere to it's searching up there. For your local
        machine, make it search the games.db database you created with init_dp.py

    2 - Run server.py to host it on your local machine

Throughout this project, AI was used to aid with the coding. The front-end was entirely written by ChatGPT and the backend was written between myself and the AI.

Proper references will be provided to those chat logs so that one can inspect and investigate the vibe-coding process. 

I understand that further work could have gone into this, ranging from user authentication to limiting the amount of freedom one can take with what they can write. 

The application assumes that the user will write the names correctly and use the database in a normal manner. Additional mechanisms could have been applied here to prevent user error, including but not limited to:

- Creating additional tables for the developers and platforms to limit user choice and get better and more accurate images.
- Preventing duplicate games and having the server react to a duplication, prompting the user to choose another game.
- Autocompleting the name field with what is already found within the ThegamesDB
- And many others...

That would expand this project to be a replica of ThegamesDB which would go far beyond this small scope. 

---

## References: 

- API, backend and web application constructions chats: https://chatgpt.com/share/69cd5c08-10c0-8384-87ea-192b926d634b

- Main API that was used to get cover images: https://api.thegamesdb.net/

- Styling inspiration: https://rawg.io/

- Javascript, HTML and CSS code: https://chatgpt.com/share/69cfc0bc-c5ec-8384-9482-04af249039a8

- Sqlite3 syntax and documentation: https://docs.python.org/3/library/sqlite3.html

- "403" forbidden error when first attempting the API connection on pythonanywhere: https://help.pythonanywhere.com/pages/403ForbiddenError

## Project Structure

```Github unfortunately orders things by alphabetical order, so rather than switch things around into folders and break the code (given that it currently is pulling from the root), I will leave it as it and this map will outline the logic.

root-depository/
│
├── server.py              # This contains the Flask application and the main API logic for getting the covers.
├── gamesDAO.py            # This connects with the database and executes all our SQL commands on sqlite3
├── games.db               # This is the SQLite database
├── index.html             # Main front-end page
├── styles.css             # Front-end page styling
├── app.js                 # Front-end JavaScript logic
├── requirements.txt       # Necessary modules that were used for this
├── README.md              # Project documentation
└── images/
    └── not-found.png      # Default image used when no box cover is found
    └── background.jpg     # Background image that was used for the front-end