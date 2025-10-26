import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json


class CalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
              'https://www.googleapis.com/auth/calendar.events']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.load_credentials()
    
    def load_credentials(self):
        """Load saved credentials from token file"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if self.creds and self.creds.valid:
            self.service = build('calendar', 'v3', credentials=self.creds)
        elif self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
            self.service = build('calendar', 'v3', credentials=self.creds)
    
    def get_auth_url(self) -> str:
        """Generate OAuth authorization URL"""
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
        )
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def handle_auth_callback(self, code: str):
        """Handle OAuth callback and save credentials"""
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
        )
        
        flow.fetch_token(code=code)
        self.creds = flow.credentials
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.creds is not None and self.creds.valid
    
    def get_busy_times(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get busy time slots from Google Calendar"""
        if not self.is_authenticated():
            return []
        
        try:
            body = {
                "timeMin": start_time.isoformat() + 'Z',
                "timeMax": end_time.isoformat() + 'Z',
                "items": [{"id": "primary"}]
            }
            
            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result.get('calendars', {}).get('primary', {}).get('busy', [])
            
            return busy_times
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def find_available_slots(
        self,
        duration_minutes: int,
        start_date: datetime,
        end_date: datetime,
        time_range_start: str = "09:00",
        time_range_end: str = "17:00"
    ) -> List[Dict[str, Any]]:
        """Find available time slots based on criteria"""
        if not self.is_authenticated():
            return []
        
        busy_times = self.get_busy_times(start_date, end_date)
        available_slots = []
        
        current_date = start_date.date()
        end = end_date.date()
        
        while current_date <= end:
            start_hour, start_minute = map(int, time_range_start.split(':'))
            end_hour, end_minute = map(int, time_range_end.split(':'))
            
            day_start = datetime.combine(current_date, datetime.min.time()).replace(
                hour=start_hour, minute=start_minute
            )
            day_end = datetime.combine(current_date, datetime.min.time()).replace(
                hour=end_hour, minute=end_minute
            )
            
            current_time = day_start
            
            while current_time + timedelta(minutes=duration_minutes) <= day_end:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                is_available = True
                for busy in busy_times:
                    busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                    busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                    
                    if not (slot_end <= busy_start or current_time >= busy_end):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        "start": current_time.isoformat(),
                        "end": slot_end.isoformat(),
                        "duration_minutes": duration_minutes,
                        "formatted_start": current_time.strftime("%A, %B %d at %I:%M %p"),
                        "formatted_end": slot_end.strftime("%I:%M %p")
                    })
                
                current_time += timedelta(minutes=30)
            
            current_date += timedelta(days=1)
        
        return available_slots[:10]
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a calendar event"""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Calendar")
        
        event = {
            'summary': summary,
            'description': description or '',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return {
                "success": True,
                "event_id": event.get('id'),
                "html_link": event.get('htmlLink')
            }
        except HttpError as error:
            print(f"An error occurred: {error}")
            return {
                "success": False,
                "error": str(error)
            }
