from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
import json
from typing import Dict, List
from datetime import datetime
import uvicorn

from services.calendar_service import CalendarService
from services.conversation_service import ConversationService
from models.schemas import Message, ConversationState

load_dotenv()

app = FastAPI(title="Smart Scheduler AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

calendar_service = CalendarService()
active_conversations: Dict[str, ConversationService] = {}


@app.get("/")
async def root():
    return {
        "message": "Smart Scheduler AI Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/login",
            "websocket": "/ws/{client_id}"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "calendar_connected": calendar_service.is_authenticated()
    }


@app.get("/auth/login")
async def login():
    """Initiate Google Calendar OAuth flow"""
    auth_url = calendar_service.get_auth_url()
    return {"auth_url": auth_url}


@app.get("/auth/callback")
async def auth_callback(code: str):
    """Handle OAuth callback from Google"""
    try:
        calendar_service.handle_auth_callback(code)
        return RedirectResponse(url="http://localhost:3000?auth=success")
    except Exception as e:
        return RedirectResponse(url=f"http://localhost:3000?auth=error&message={str(e)}")


@app.get("/auth/status")
async def auth_status():
    """Check if user is authenticated with Google Calendar"""
    return {
        "authenticated": calendar_service.is_authenticated(),
        "timestamp": datetime.now().isoformat()
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time conversation"""
    await websocket.accept()
    
    if client_id not in active_conversations:
        active_conversations[client_id] = ConversationService(calendar_service)
    
    conversation = active_conversations[client_id]
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Smart Scheduler AI Agent",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                user_message = message_data.get("content", "")
                
                await websocket.send_json({
                    "type": "processing",
                    "message": "Processing your request...",
                    "timestamp": datetime.now().isoformat()
                })
                
                response = await conversation.process_message(user_message)
                
                await websocket.send_json({
                    "type": "response",
                    "content": response["message"],
                    "conversation_state": response.get("state", {}),
                    "available_slots": response.get("available_slots", []),
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_data.get("type") == "reset":
                conversation.reset()
                await websocket.send_json({
                    "type": "reset_complete",
                    "message": "Conversation reset successfully",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
        if client_id in active_conversations:
            del active_conversations[client_id]
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
