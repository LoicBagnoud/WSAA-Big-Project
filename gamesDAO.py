# This is the DAO that will connect with the MYSQL Database
# Copied the format mainly from the DAO by Andrew Beatty.
# Author: Loic Bagnoud

import mysql.connector
import dbconfig as cfg

class GamesDAO:
    connection = ""
    cursor = ""
    host = ""
    user = ""
    password = ""
    database = ""

    def __init__(self):
        self.host = cfg.mysql['host']
        self.user = cfg.mysql['user']
        self.password = cfg.mysql['password']
        self.database = cfg.mysql['database']

    def getcursor(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        self.cursor = self.connection.cursor()
        return self.cursor

    def closeAll(self):
        self.cursor.close()
        self.connection.close()

    def getAll(self):
        cursor = self.getcursor()
        sql = "select * from games"
        cursor.execute(sql)
        results = cursor.fetchall()
        returnArray = []

        for result in results:
            returnArray.append(self.convertToDictionary(result))

        self.closeAll()
        return returnArray

    def findByID(self, id):
        cursor = self.getcursor()
        sql = "select * from games where id = %s"
        values = (id,)

        cursor.execute(sql, values)
        result = cursor.fetchone()
        self.closeAll()

        if result is None:
            return {}

        return self.convertToDictionary(result)

    def create(self, game):
        cursor = self.getcursor()
        sql = "insert into games (name, genre, year_released, developer, platforms, boxcover_url) values (%s, %s, %s, %s, %s, %s)"
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
        sql = "update games set name = %s, genre = %s, year_released = %s, developer = %s, platforms = %s, boxcover_url = %s where id = %s, "
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
        sql = "delete from games where id = %s"
        values = (id,)

        cursor.execute(sql, values)
        self.connection.commit()
        self.closeAll()

        print("delete done")

    def convertToDictionary(self, resultLine):
        attkeys = ['id', 'name', 'genre', 'year_released', 'developer', 'platforms','boxcover_url']
        game = {}
        currentkey = 0
        for attrib in resultLine:
            game[attkeys[currentkey]] = attrib
            currentkey = currentkey + 1
        return game


gamesDAO = GamesDAO()