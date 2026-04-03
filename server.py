# This would be the flask server that will interact with the DAO
# Author: ChatGPT - Reference below

from flask import Flask, jsonify, request
from gamesDAO import gamesDAO

app = Flask(__name__, static_url_path='', static_folder='.')

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

if __name__ == '__main__':
    app.run(debug=True)


# Reference:
# https://chatgpt.com/share/69cd5c08-10c0-8384-87ea-192b926d634b
# I had some doubts on why the LLM suggested both POST and PUT and not just POST. But they explained
# that the difference lies in POST being to add a brand new game, whereas PUT is mainly to update it. 
# While I understand that POST can be used for both, they suggested this way is cleaner, hence why I 
# followed it.