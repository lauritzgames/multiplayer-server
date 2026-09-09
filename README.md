# Multiplayer Server

This is the server for the multiplayer game.

The server uses Flask-SocketIO to handle connections and send player positions between clients.

## Requirements

Docker is recommended.

You can also run it with Python if you install the packages from `requirements.txt`.

## Run with Docker

Build and start the server:

```bash
docker compose up -d --build
```

The server runs on port `17829`.

## Stop the server

```bash
docker compose down
```

## Connect a Client

The game client connects to the server using Socket.IO over WebSocket.

The server address depends on where the server is hosted.

## Files

```text
multiplayer-server/
├── server.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── multiplayer/
```

## Features

• Multiplayer connections
• Real-time player movement
• WebSocket communication
• Automatic player removal when disconnected
• Docker support

## License

This project is for testing and development.
