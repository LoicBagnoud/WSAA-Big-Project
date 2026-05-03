# This would be the flask server that will interact with the DAO
# Author: ChatGPT - Reference below

# First we're going to import everything we need, including our DAO and the API key for GamesDB
from flask import Flask, jsonify, request
from gamesDAO import gamesDAO
import requests

# This key is not in github. But it's been directly put inside pythonanywhere
from apikeyconfig import apikey


# We start with creating the Flask App
app = Flask(__name__, static_url_path='', static_folder='.')

# These helper functions exist to help us get the specific cover images for the games, by making an API Call
# The logic is that we make a search by the game name to the GamesDB to see if they have the specific cover
def search_game_by_name(game_name):
    url = "https://api.thegamesdb.net/v1.1/Games/ByGameName"
    params = {
        "apikey":apikey,
        "name": game_name
    }

    response = requests.get(url, params=params)
    return response.json()

# This second function is to help us narrow down the results as there are multiple "Sonics" and "Marios" for instance.
# As such, we go by year as a Castlevania game released in 1999 can only be Symphony of the Night for example. This is not
# 100% the case with all games, but it works for most 
def find_best_game_match(game_name, year_released=None):
    data = search_game_by_name(game_name)


    # We start with a conditional. First check and see if what gets brought back from the search
    # If nothing comes back, we get a none and we move on
    games = data.get("data", {}).get("games", [])

    if not games:
        return None

    # First we go by exact title matches (i.e is there exactly a game called Mario? Just Mario?)
    exact_matches = []
    for game in games:
        api_title = game.get("game_title", "").strip().lower()
        if api_title == game_name.strip().lower():
            exact_matches.append(game)

    # If no exact matches are found, we go to all other results
    candidates = exact_matches if exact_matches else games

    # if the year is provided, we keep the games that have matching years. In GamesDB they have dates in the datetime
    # format. FOr us it really doesn't matter much, we really just want the year, hence the release_year = int(release_date[:4]).
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

    # Return first candidate if there's no year match
    return candidates[0]

# This is another helper function for getting the boxart. We'll use the one that was use above for support. 
def find_boxcover_for_game(game_name, year_released=None):
    try:
        best_match = find_best_game_match(game_name, year_released)

        # If there'ss no match, we get the no image found file that sit's in a folder in the repository
        if best_match is None:
            return {
                "boxcover_url": "/images/not-found.png",
                "warning": "No image found. Are you sure you've added the correct game? Check the game title."
            }

        # GamesDB has IDs for its games. So we need this in case, the games being searched has no ID or doesn't exist
        # That way, we default back to the "no image found"
        game_id = best_match.get("id")

        if not game_id:
            return {
                "boxcover_url": "/images/not-found.png",
                "warning": "No image found. Are you sure you've added the correct game? Check the game title."
            }

        url = "https://api.thegamesdb.net/v1/Games/Images"
        params = {
            "apikey": apikey,
            "games_id": game_id
        }


        # This is the other API endpoint that gets the images. 
        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        print("IMAGES RESPONSE:", data)


        # This constructs the URL, which in turn will lead us to the images. 
        base_url = data.get("data", {}).get("base_url", {}).get("medium", "")
        images = data.get("data", {}).get("images", {}).get(str(game_id), [])

        print("GAME ID:", game_id)
        print("BASE URL:", base_url)
        print("IMAGES:", images)


        # Because the data in GamesDB has front, back, cover, game images, this loops through the information and gets us specifically
        # The front boxart.
        for image in images:
            if image.get("type") == "boxart" and image.get("side") == "front":
                filename = image.get("filename")
                if filename and base_url:
                    return {
                        "boxcover_url": base_url + filename,
                        "warning": None
                    }

        return {
            "boxcover_url": "/images/not-found.png",
            "warning": "No box art found for that game."
        }

        # Just in case no boxart actually exists. We default once again to the no image found
    except Exception as e:
        print("Error finding box cover:", e)
        return {
            "boxcover_url": "/images/not-found.png",
            "warning": "No image found. Are you sure you've added the correct game? Check the game title."
        }


# This is our DAO call to get games
@app.route('/games', methods=['GET'])
def get_all_games():
    results = gamesDAO.getAll()
    return jsonify(results)

# To get one game by ID
@app.route('/games/<int:id>', methods=['GET'])
def find_by_id(id):
    found_game = gamesDAO.findByID(id)

    if found_game == {}:
        return jsonify({"message": "Game not found"}), 404

    return jsonify(found_game)

# To create a new game
@app.route('/games', methods=['POST'])
def create_game():
    try:
        if not request.json:
            return jsonify({"message": "Invalid or missing JSON body"}), 400

        print("Incoming JSON:", request.json)

        cover_result = find_boxcover_for_game(
            request.json.get("name"),
            request.json.get("year_released")
        )
        print("Cover URL:", cover_result)

        game = {
            "name": request.json.get("name"),
            "genre": request.json.get("genre"),
            "year_released": request.json.get("year_released"),
            "developer": request.json.get("developer"),
            "platforms": request.json.get("platforms"),
            "boxcover_url": cover_result["boxcover_url"]
        }
        print("Game to save:", game)

        created_game = gamesDAO.create(game)
        created_game["warning"] = cover_result["warning"]

        print("Created game:", created_game)

        return jsonify(created_game), 201

    except Exception as e:
        print("POST /games error:", e)
        return jsonify({"message": str(e)}), 500

# To update an existing game
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

# To delete a game
@app.route('/games/<int:id>', methods=['DELETE'])
def delete_game(id):
    found_game = gamesDAO.findByID(id)

    if found_game == {}:
        return jsonify({"message": "Game not found"}), 404

    gamesDAO.delete(id)
    return jsonify({"message": "Game deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)

# Reference:
# https://chatgpt.com/share/69cfc0bc-c5ec-8384-9482-04af249039a8 - REFER TO NOTE IN README
# I had some doubts on why the LLM suggested both POST and PUT and not just POST. But they explained
# that the difference lies in POST being to add a brand new game, whereas PUT is mainly to update it.
# While I understand that POST can be used for both, they suggested this way is cleaner, hence why I
# followed it.
# For the API Key - https://api.thegamesdb.net/