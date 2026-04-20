# This is to create a specific Table for sqlite3
# Author: ChatGPT

import sqlite3

connection = sqlite3.connect("games.db")
cursor = connection.cursor()

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

connection.commit()
connection.close()

print("games table created successfully")

# References:
# ChatGPT - https://chatgpt.com/share/69cfc0bc-c5ec-8384-9482-04af249039a8