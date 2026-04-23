# This is mainly to test the DAO
# Author: Loic Bagnoud

from gamesDAO import gamesDAO

game = {
    "name": "Hades",
    "genre": "Roguelike",
    "year_released": 2020,
    "developer": "Supergiant Games",
    "platforms": "PC, Switch",
    "boxcover_url": "images/not-found.png"
}

createdGame = gamesDAO.create(game)
print("Created:", createdGame)

allGames = gamesDAO.getAll()
print("All games:", allGames)

foundGame = gamesDAO.findByID(createdGame["id"])
print("Found by ID:", foundGame)