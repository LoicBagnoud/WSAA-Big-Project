# This is the DAO that will connect with the MYSQL Database
# Copied the format mainly from the DAO by Andrew Beatty.
# Author: Loic Bagnoud

import sqlite3

class GamesDAO:
    connection = None
    cursor = None
    db_file = "/home/sirktar/WSAA-Big-Project/games.db"

    def __init__(self):
        pass

    def getcursor(self):
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()
        return self.cursor

    def closeAll(self):
        self.cursor.close()
        self.connection.close()

    def getAll(self):
        cursor = self.getcursor()
        sql = "SELECT * FROM games"
        cursor.execute(sql)
        results = cursor.fetchall()
        returnArray = []

        for result in results:
            returnArray.append(self.convertToDictionary(result))

        self.closeAll()
        return returnArray

    def findByID(self, id):
        cursor = self.getcursor()
        sql = "SELECT * FROM games WHERE id = ?"
        values = (id,)

        cursor.execute(sql, values)
        result = cursor.fetchone()
        self.closeAll()

        if result is None:
            return {}

        return self.convertToDictionary(result)

    def create(self, game):
        cursor = self.getcursor()
        sql = """
            INSERT INTO games (name, genre, year_released, developer, platforms, boxcover_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (
            game.get("name"),
            game.get("genre"),
            game.get("year_released"),
            game.get("developer"),
            game.get("platforms"),
            game.get("boxcover_url")
        )

        cursor.execute(sql, values)
        self.connection.commit()
        newid = cursor.lastrowid
        game["id"] = newid
        self.closeAll()
        return game

    def update(self, id, game):
        cursor = self.getcursor()
        sql = """
            UPDATE games
            SET name = ?, genre = ?, year_released = ?, developer = ?, platforms = ?, boxcover_url = ?
            WHERE id = ?
        """
        values = (
            game.get("name"),
            game.get("genre"),
            game.get("year_released"),
            game.get("developer"),
            game.get("platforms"),
            game.get("boxcover_url"),
            id
        )

        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()

    def delete(self, id):
        cursor = self.getcursor()
        sql = "DELETE FROM games WHERE id = ?"
        values = (id,)

        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()

        print("delete done")

    def convertToDictionary(self, resultLine):
        attkeys = ['id', 'name', 'genre', 'year_released', 'developer', 'platforms', 'boxcover_url']
        game = {}
        currentkey = 0
        for attrib in resultLine:
            game[attkeys[currentkey]] = attrib
            currentkey += 1
        return game


gamesDAO = GamesDAO()

# References:
# https://docs.python.org/3/library/sqlite3.html - Had to make some alterations to the Syntax as well how to call the cursor, getALL, etc.