import flask
from flask_socketio import SocketIO, emit
import json
import os
import time

flask_app = flask.Flask(__name__)

socketio = SocketIO(
    flask_app,
    cors_allowed_origins="*"
)

SERVERS_FILE = "multiplayer/servers.json"

PORT = int(os.getenv("PORT", "17829"))

PLAYER_TIMEOUT = 20

players = {}


def load_server():
    with open(SERVERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_server(data):
    temp_file = SERVERS_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    os.replace(temp_file, SERVERS_FILE)


def remove_inactive_players():
    current_time = time.time()

    for name in list(players):
        if current_time - players[name]["last_seen"] >= PLAYER_TIMEOUT:
            del players[name]


@socketio.on("join")
def join_player(data):
    name = data.get("name")

    if not name:
        return

    remove_inactive_players()

    if name in players:
        players[name]["last_seen"] = time.time()

    else:
        players[name] = {
            "name": name,
            "score": 0,
            "x": 400,
            "y": 300,
            "last_seen": time.time()
        }

    emit(
        "players",
        list(players.values()),
        broadcast=True
    )


@socketio.on("position")
def change_player_position(data):
    name = data.get("name")

    if name not in players:
        return

    players[name]["x"] = data.get(
        "x",
        players[name]["x"]
    )

    players[name]["y"] = data.get(
        "y",
        players[name]["y"]
    )

    players[name]["last_seen"] = time.time()

    emit(
        "players",
        list(players.values()),
        broadcast=True
    )


@socketio.on("disconnect")
def disconnect():
    pass


def save_players():
    server_data = {
        "players": list(players.values())
    }

    save_server(server_data)


@flask_app.route("/")
def index():
    remove_inactive_players()

    return flask.jsonify({
        "players": list(players.values())
    })


if __name__ == "__main__":
    server_data = load_server()

    for player in server_data["players"]:
        player["last_seen"] = time.time()
        players[player["name"]] = player

    socketio.run(
        flask_app,
        host="0.0.0.0",
        port=PORT,
        debug=False
    )
