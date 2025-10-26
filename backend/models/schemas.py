from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = datetime.now()


class ConversationState(BaseModel):
    duration_minutes: Optional[int] = None
    preferred_day: Optional[str] = None
    preferred_time: Optional[str] = None
    time_constraints: List[str] = []
    meeting_title: Optional[str] = None
    meeting_description: Optional[str] = None
    confirmed_slot: Optional[Dict[str, Any]] = None


class TimeSlot(BaseModel):
    start: datetime
    end: datetime
    available: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScheduleRequest(BaseModel):
    duration_minutes: int
    preferred_day: Optional[str] = None
    preferred_time: Optional[str] = None
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None


class ScheduleResponse(BaseModel):
    available_slots: List[Dict[str, Any]]
    message: str
    total_slots_found: int
