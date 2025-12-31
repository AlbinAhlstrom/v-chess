from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.lobby_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str):
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)

    async def broadcast(self, game_id: str, message: str):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    continue

    async def connect_lobby(self, websocket: WebSocket):
        await websocket.accept()
        self.lobby_connections.append(websocket)

    def disconnect_lobby(self, websocket: WebSocket):
        if websocket in self.lobby_connections:
            self.lobby_connections.remove(websocket)

    async def broadcast_lobby(self, message: str):
        for connection in self.lobby_connections:
            try:
                await connection.send_text(message)
            except Exception:
                continue

manager = ConnectionManager()
