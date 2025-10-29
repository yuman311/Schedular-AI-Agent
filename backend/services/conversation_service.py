import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from openai import OpenAI
from dateutil import parser
from dateutil.relativedelta import relativedelta
import re
from models.schemas import ConversationState, Message, MessageRole
from openai import AsyncOpenAI


class ConversationService:
    def __init__(self, calendar_service):
        self.calendar_service = calendar_service
        self.client = OpenAI(
        api_key= os.getenv("OPENAI_API_KEY"),
        base_url= 'https://truefoundry.innovaccer.com/api/llm/api/inference/openai/'
)
        self.conversation_history: List[Dict[str, str]] = []
        self.state = ConversationState()
        
        self.system_prompt = """You are a helpful AI scheduling assistant. Your job is to help users find and schedule meetings.

Your capabilities:
1. Extract meeting requirements (duration, preferred day/time, constraints)
2. Search for available time slots in the user's calendar
3. Suggest alternative times when preferred slots aren't available
4. Handle changing requirements mid-conversation
5. Be conversational, friendly, and helpful

Guidelines:
- Always confirm the meeting duration before searching for slots
- Ask clarifying questions when information is ambiguous
- Remember context from earlier in the conversation
- Suggest alternatives when preferred times are unavailable
- Parse natural language time expressions like "Tuesday afternoon", "next week", "before 5 PM"
- Be proactive in offering solutions

When you have enough information to search for slots, use the search_calendar function.
When the user confirms a time slot, use the create_event function.
"""
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_calendar",
                    "description": "Search for available meeting slots in the user's calendar based on duration and time preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "duration_minutes": {
                                "type": "integer",
                                "description": "Duration of the meeting in minutes"
                            },
                            "preferred_day": {
                                "type": "string",
                                "description": "Preferred day like 'Monday', 'Tuesday', 'next week', 'tomorrow', etc."
                            },
                            "time_of_day": {
                                "type": "string",
                                "description": "Time preference like 'morning', 'afternoon', 'evening', or specific time like '2 PM'"
                            },
                            "days_ahead": {
                                "type": "integer",
                                "description": "How many days ahead to search (default 7)"
                            }
                        },
                        "required": ["duration_minutes"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_event",
                    "description": "Create a calendar event at the specified time",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_time": {
                                "type": "string",
                                "description": "Start time in ISO format"
                            },
                            "duration_minutes": {
                                "type": "integer",
                                "description": "Duration in minutes"
                            },
                            "title": {
                                "type": "string",
                                "description": "Meeting title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Meeting description"
                            }
                        },
                        "required": ["start_time", "duration_minutes", "title"]
                    }
                }
            }
        ]
    
    def parse_time_preferences(self, preferred_day: Optional[str], time_of_day: Optional[str]) -> Dict[str, Any]:
        """Parse natural language time preferences into datetime objects"""
        now = datetime.now()
        start_date = now
        end_date = now + timedelta(days=7)
        time_range_start = "09:00"
        time_range_end = "17:00"
        
        if preferred_day:
            preferred_day_lower = preferred_day.lower()
            
            if "tomorrow" in preferred_day_lower:
                start_date = now + timedelta(days=1)
                end_date = start_date + timedelta(days=1)
            elif "next week" in preferred_day_lower:
                start_date = now + timedelta(days=7)
                end_date = start_date + timedelta(days=7)
            elif "today" in preferred_day_lower:
                start_date = now
                end_date = now + timedelta(days=1)
            else:
                days_of_week = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2, 
                    'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
                }
                for day_name, day_num in days_of_week.items():
                    if day_name in preferred_day_lower:
                        days_ahead = (day_num - now.weekday()) % 7
                        if days_ahead == 0:
                            days_ahead = 7
                        start_date = now + timedelta(days=days_ahead)
                        end_date = start_date + timedelta(days=1)
                        break
        
        if time_of_day:
            time_of_day_lower = time_of_day.lower()
            
            if "morning" in time_of_day_lower:
                time_range_start = "09:00"
                time_range_end = "12:00"
            elif "afternoon" in time_of_day_lower:
                time_range_start = "12:00"
                time_range_end = "17:00"
            elif "evening" in time_of_day_lower:
                time_range_start = "17:00"
                time_range_end = "20:00"
            else:
                time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_of_day_lower)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2)) if time_match.group(2) else 0
                    am_pm = time_match.group(3)
                    
                    if am_pm == 'pm' and hour < 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                    
                    time_range_start = f"{hour:02d}:{minute:02d}"
                    time_range_end = "17:00"
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "time_range_start": time_range_start,
            "time_range_end": time_range_end
        }
    
    def search_calendar(self, duration_minutes: int, preferred_day: Optional[str] = None, 
                       time_of_day: Optional[str] = None, days_ahead: int = 7) -> Dict[str, Any]:
        """Search for available calendar slots"""
        self.state.duration_minutes = duration_minutes
        
        time_prefs = self.parse_time_preferences(preferred_day, time_of_day)
        
        if not preferred_day:
            time_prefs["end_date"] = time_prefs["start_date"] + timedelta(days=days_ahead)
        
        available_slots = self.calendar_service.find_available_slots(
            duration_minutes=duration_minutes,
            start_date=time_prefs["start_date"],
            end_date=time_prefs["end_date"],
            time_range_start=time_prefs["time_range_start"],
            time_range_end=time_prefs["time_range_end"]
        )
        
        return {
            "available_slots": available_slots,
            "total_found": len(available_slots),
            "search_criteria": {
                "duration_minutes": duration_minutes,
                "preferred_day": preferred_day,
                "time_of_day": time_of_day
            }
        }
    
    def create_event(self, start_time: str, duration_minutes: int, 
                    title: str, description: str = "") -> Dict[str, Any]:
        """Create a calendar event"""
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        result = self.calendar_service.create_event(
            summary=title,
            start_time=start_dt,
            end_time=end_dt,
            description=description
        )
        
        return result
    
    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message and generate response using OpenAI"""
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history
        
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-4o",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            available_slots = []
            
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "search_calendar":
                        result = self.search_calendar(**function_args)
                        available_slots = result["available_slots"]
                        
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call.model_dump()]
                        })
                        
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })
                        
                        second_response = self.client.chat.completions.create(
                            model="openai/gpt-4o",
                            messages=[
                                {"role": "system", "content": self.system_prompt}
                            ] + self.conversation_history
                        )
                        
                        final_message = second_response.choices[0].message.content
                        
                    elif function_name == "create_event":
                        result = self.create_event(**function_args)
                        
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call.model_dump()]
                        })
                        
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })
                        
                        second_response = self.client.chat.completions.create(
                            model="openai/gpt-4o",
                            messages=[
                                {"role": "system", "content": self.system_prompt}
                            ] + self.conversation_history
                        )
                        
                        final_message = second_response.choices[0].message.content
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_message
                })
                
                return {
                    "message": final_message,
                    "available_slots": available_slots,
                    "state": self.state.model_dump()
                }
            
            else:
                assistant_message = response_message.content
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                return {
                    "message": assistant_message,
                    "available_slots": available_slots,
                    "state": self.state.model_dump()
                }
        
        except Exception as e:
            return {
                "message": f"I encountered an error: {str(e)}. Could you please try again?",
                "available_slots": [],
                "state": self.state.model_dump()
            }
    
    def reset(self):
        """Reset conversation state"""
        self.conversation_history = []
        self.state = ConversationState()
