# This is to create a specific Table for sqlite3
# Author: ChatGPT and Myself for SQLlite Syntax


# We first import the module
import sqlite3

# We make our connection and we get our cursor
connection = sqlite3.connect("games.db")
cursor = connection.cursor()

# This is our SQL Command to create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    genre TEXT,
    year_released INTEGER,
    developer TEXT,
    platforms TEXT,
    boxcover_url TEXT DEFAULT 'images/not-found.png'
);
""")

# Execute the the table and close the cursor
connection.commit()
connection.close()

# Small print to test on the console and terminal
print("games table created successfully")

# References:
# ChatGPT - https://chatgpt.com/share/69cfc0bc-c5ec-8384-9482-04af249039a8
# Sqllite Documentation - https://docs.python.org/3/library/sqlite3.html