import flask
import json
import os
import time

flask_app = flask.Flask(__name__)

SERVERS_FILE = "multiplayer/servers.json"

PORT = int(os.getenv("PORT", "5000"))

PLAYER_TIMEOUT = 20


def load_server():
    with open(SERVERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_server(data):
    temp_file = SERVERS_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    os.replace(temp_file, SERVERS_FILE)


def remove_inactive_players(server_data):
    current_time = time.time()

    server_data["players"] = [
        player
        for player in server_data["players"]
        if current_time - player["last_seen"] < PLAYER_TIMEOUT
    ]


@flask_app.route("/")
def index():
    server_data = load_server()

    remove_inactive_players(server_data)
    save_server(server_data)

    return flask.jsonify(server_data)


@flask_app.route("/player/<string:player_name>", methods=["POST"])
def change_player_position(player_name):
    server_data = load_server()

    remove_inactive_players(server_data)

    data = flask.request.get_json()

    if data is None:
        return flask.jsonify({
            "error": "No JSON data provided"
        }), 400

    for player in server_data["players"]:
        if player["name"] == player_name:

            player["x"] = data.get("x", player["x"])
            player["y"] = data.get("y", player["y"])

            player["last_seen"] = time.time()

            save_server(server_data)

            return flask.jsonify({
                "message": "Player updated successfully.",
                "player": player
            })

    return flask.jsonify({
        "error": "Player not found"
    }), 404


@flask_app.route("/player/<string:player_name>/join", methods=["POST"])
def join_player(player_name):
    server_data = load_server()

    remove_inactive_players(server_data)

    for player in server_data["players"]:
        if player["name"] == player_name:

            player["last_seen"] = time.time()

            save_server(server_data)

            return flask.jsonify({
                "message": "Player already exists.",
                "player": player
            })

    player = {
        "name": player_name,
        "score": 0,
        "x": 400,
        "y": 300,
        "last_seen": time.time()
    }

    server_data["players"].append(player)

    save_server(server_data)

    return flask.jsonify({
        "message": "Player joined successfully.",
        "player": player
    })


if __name__ == "__main__":
    flask_app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )