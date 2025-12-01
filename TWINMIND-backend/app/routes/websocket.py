from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json

from app.database.connection import SessionLocal
from app.models.chunk import Chunk   # FIXED IMPORT

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")


manager = ConnectionManager()


@router.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            raw_data = await websocket.receive_text()

            try:
                query_data = json.loads(raw_data)
            except Exception:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            query = query_data.get("query", "").strip()
            logger.info(f"WebSocket query received: '{query}'")

            if not query:
                await websocket.send_json({"type": "error", "message": "Empty query"})
                continue

            # Query DB
            db = SessionLocal()
            try:
                chunks = db.query(Chunk).limit(200).all()  # safeguard
            finally:
                db.close()

            query_lower = query.lower()
            matched = [
                c for c in chunks
                if query_lower in c.content.lower()
            ][:5]

            # Stream matched chunks
            for i, chunk in enumerate(matched):
                await websocket.send_json({
                    "type": "result",
                    "index": i + 1,
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "preview": chunk.content[:200]
                })

            # Completion message
            await websocket.send_json({
                "type": "complete",
                "total_results": len(matched)
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
        await websocket.close(code=1011)
