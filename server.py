import flask
from flask_socketio import SocketIO, emit
from flask import request
import json
import os
import time

flask_app = flask.Flask(__name__)

socketio = SocketIO(
    flask_app,
    cors_allowed_origins="*",
    async_mode="threading"
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

    for player_id, player in list(players.items()):

        if current_time - player["last_seen"] >= PLAYER_TIMEOUT:

            del players[player_id]

            socketio.emit(
                "player_left",
                {
                    "id": player_id
                }
            )


@socketio.on("join")
def join_player(data):

    player_id = request.sid

    players[player_id] = {
        "id": player_id,
        "name": data.get("name", "Player"),
        "score": 0,
        "x": 400,
        "y": 300,
        "last_seen": time.time()
    }

    emit(
        "joined",
        {
            "id": player_id
        }
    )

    socketio.emit(
        "players",
        list(players.values())
    )


@socketio.on("position")
def change_player_position(data):

    player_id = data.get("id")

    player = players.get(player_id)

    if player is None:
        return

    player["x"] = data.get("x", player["x"])
    player["y"] = data.get("y", player["y"])
    player["last_seen"] = time.time()

    socketio.emit(
        "player_moved",
        {
            "id": player_id,
            "x": player["x"],
            "y": player["y"],
            "sent": data.get("sent")
        },
        skip_sid=request.sid
    )


@socketio.on("disconnect")
def disconnect():
    pass


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

        player_id = player.get("id")

        if player_id:
            players[player_id] = player

    socketio.run(
        flask_app,
        host="0.0.0.0",
        port=PORT,
        debug=False,
        allow_unsafe_werkzeug=True
    )
