# This would be the flask server that will interact with the DAO
# Author: ChatGPT - Reference below

from flask import Flask, jsonify, request
from gamesDAO import gamesDAO
import requests
from apikeyconfig import apikey


app = Flask(__name__, static_url_path='', static_folder='.')

# Helper functions below. The first one here is to help us find the game by name
def search_game_by_name(game_name):
    url = "https://api.thegamesdb.net/v1.1/Games/ByGameName"
    params = {
        "apikey":apikey,
        "name": game_name
    }

    response = requests.get(url, params=params)
    return response.json()

# The second one here is to choose from the all of the results. 
def find_best_game_match(game_name, year_released=None):
    data = search_game_by_name(game_name)

    games = data.get("data", {}).get("games", [])

    if not games:
        return None

    # First we go by exact title matches
    exact_matches = []
    for game in games:
        api_title = game.get("game_title", "").strip().lower()
        if api_title == game_name.strip().lower():
            exact_matches.append(game)

    # If no exact matches are found, we go to all other results
    candidates = exact_matches if exact_matches else games

    # if the year is provided, we keep the games that have matching years
    if year_released is not None:
        year_matches = []
        for game in candidates:
            release_date = game.get("release_date")
            if release_date:
                try:
                    release_year = int(release_date[:4])
                    if release_year == int(year_released):
                        year_matches.append(game)
                except ValueError:
                    pass

        if year_matches:
            return year_matches[0]

    #return first candidate if no year match
    return candidates[0]

# Get all games
@app.route('/games', methods=['GET'])
def get_all_games():
    results = gamesDAO.getAll()
    return jsonify(results)

# Get one game by ID
@app.route('/games/<int:id>', methods=['GET'])
def find_by_id(id):
    found_game = gamesDAO.findByID(id)

    if found_game == {}:
        return jsonify({"message": "Game not found"}), 404

    return jsonify(found_game)

# Create a new game
@app.route('/games', methods=['POST'])
def create_game():
    if not request.json:
        return jsonify({"message": "Invalid or missing JSON body"}), 400

    game = {
        "name": request.json.get("name"),
        "genre": request.json.get("genre"),
        "year_released": request.json.get("year_released"),
        "developer": request.json.get("developer"),
        "platforms": request.json.get("platforms"),
        "boxcover_url": "/images/not-found.png"
    }

    created_game = gamesDAO.create(game)
    return jsonify(created_game), 201

# Update an existing game
@app.route('/games/<int:id>', methods=['PUT'])
def update_game(id):
    found_game = gamesDAO.findByID(id)

    if found_game == {}:
        return jsonify({"message": "Game not found"}), 404

    if not request.json:
        return jsonify({"message": "Invalid or missing JSON body"}), 400

    updated_game = {
        "name": request.json.get("name"),
        "genre": request.json.get("genre"),
        "year_released": request.json.get("year_released"),
        "developer": request.json.get("developer"),
        "platforms": request.json.get("platforms"),
        "boxcover_url": request.json.get("boxcover_url", found_game.get("boxcover_url"))
    }

    gamesDAO.update(id, updated_game)
    updated_game["id"] = id

    return jsonify(updated_game)

# Delete a game
@app.route('/games/<int:id>', methods=['DELETE'])
def delete_game(id):
    found_game = gamesDAO.findByID(id)

    if found_game == {}:
        return jsonify({"message": "Game not found"}), 404

    gamesDAO.delete(id)
    return jsonify({"message": "Game deleted successfully"})



# Testing
@app.route('/testmatch/<name>/<int:year>')
def test_match(name, year):
    match = find_best_game_match(name, year)
    if match is None:
        return jsonify({"message": "No match found"}), 404
    return jsonify(match)






if __name__ == '__main__':
    app.run(debug=True)

# Reference:
# https://chatgpt.com/share/69cd5c08-10c0-8384-87ea-192b926d634b
# I had some doubts on why the LLM suggested both POST and PUT and not just POST. But they explained
# that the difference lies in POST being to add a brand new game, whereas PUT is mainly to update it. 
# While I understand that POST can be used for both, they suggested this way is cleaner, hence why I 
# followed it.
# For the API Key - https://api.thegamesdb.net/