from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json
from app.database.connection import SessionLocal
from app.models.document import Chunk

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
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
            data = await websocket.receive_text()
            query_data = json.loads(data)
            query = query_data.get("query", "")
            
            logger.info(f"WebSocket query: {query}")
            
            # Simulate streaming response
            db = SessionLocal()
            chunks = db.query(Chunk).all()
            db.close()
            
            # Search matching chunks
            query_lower = query.lower()
            matched = [c for c in chunks if query_lower in c.content.lower()][:5]
            
            # Stream results
            for i, chunk in enumerate(matched):
                response = {
                    "type": "result",
                    "index": i + 1,
                    "content": chunk.content[:200],
                    "document_id": chunk.document_id
                }
                await websocket.send_json(response)
            
            # Send completion
            await websocket.send_json({
                "type": "complete",
                "total_results": len(matched)
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1000)