"""
VALCORE1 Network Protocol
JSON message schema and validation using Pydantic
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """Base message model"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    source: str  # "client" or "server"
    type: str    # Message type
    payload: Dict[str, Any]


class VoiceInputMessage(BaseModel):
    """Voice input from client"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    source: str = "client"
    type: str = "voice_input"
    payload: Dict[str, Any]  # {text, room, speaker_verified, session_id}

    class Config:
        schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-11-14T10:30:45.123Z",
                "source": "client",
                "type": "voice_input",
                "payload": {
                    "text": "Hey Val, what time is it?",
                    "room": "general",
                    "speaker_verified": True,
                    "session_id": "default"
                }
            }
        }


class LLMResponseMessage(BaseModel):
    """LLM response from server"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    source: str = "server"
    type: str = "llm_response"
    payload: Dict[str, Any]  # {response, model, latency_ms, room}

    class Config:
        schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440001",
                "timestamp": "2025-11-14T10:30:46.456Z",
                "source": "server",
                "type": "llm_response",
                "payload": {
                    "response": "It's 10:30 AM",
                    "model": "qwen2.5:14b",
                    "latency_ms": 1250,
                    "room": "general"
                }
            }
        }


class CommandMessage(BaseModel):
    """System command"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    source: str
    type: str = "command"
    payload: Dict[str, Any]  # {command, parameters}

    class Config:
        schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440002",
                "timestamp": "2025-11-14T10:30:47.789Z",
                "source": "client",
                "type": "command",
                "payload": {
                    "command": "switch_room",
                    "parameters": {"room": "truck"}
                }
            }
        }


class ErrorMessage(BaseModel):
    """Error message"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    source: str
    type: str = "error"
    payload: Dict[str, Any]  # {error_type, message, traceback}

    class Config:
        schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440003",
                "timestamp": "2025-11-14T10:30:48.012Z",
                "source": "server",
                "type": "error",
                "payload": {
                    "error_type": "ConnectionError",
                    "message": "Failed to connect to LLM",
                    "traceback": "..."
                }
            }
        }


class HealthCheckMessage(BaseModel):
    """Health check ping/pong"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    source: str
    type: str = "health_check"
    payload: Dict[str, Any]  # {status, uptime_seconds, etc}

    class Config:
        schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440004",
                "timestamp": "2025-11-14T10:30:49.345Z",
                "source": "server",
                "type": "health_check",
                "payload": {
                    "status": "ok",
                    "uptime_seconds": 3600,
                    "model_loaded": True
                }
            }
        }


def create_message(msg_type: str, source: str, payload: Dict) -> BaseMessage:
    """
    Create a message of the specified type

    Args:
        msg_type: Message type
        source: Source ("client" or "server")
        payload: Message payload

    Returns:
        Appropriate message object
    """
    if msg_type == "voice_input":
        return VoiceInputMessage(source=source, payload=payload)
    elif msg_type == "llm_response":
        return LLMResponseMessage(source=source, payload=payload)
    elif msg_type == "command":
        return CommandMessage(source=source, payload=payload)
    elif msg_type == "error":
        return ErrorMessage(source=source, payload=payload)
    elif msg_type == "health_check":
        return HealthCheckMessage(source=source, payload=payload)
    else:
        return BaseMessage(source=source, type=msg_type, payload=payload)


def serialize_message(message: BaseMessage) -> str:
    """
    Serialize message to JSON string

    Args:
        message: Message object

    Returns:
        JSON string
    """
    return message.json()


def deserialize_message(json_str: str) -> BaseMessage:
    """
    Deserialize JSON string to message object

    Args:
        json_str: JSON string

    Returns:
        Message object
    """
    import json
    data = json.loads(json_str)

    msg_type = data.get('type')
    source = data.get('source')
    payload = data.get('payload', {})

    return create_message(msg_type, source, payload)
