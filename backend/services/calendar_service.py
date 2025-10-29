import os
import pickle
from datetime import datetime, timedelta, time, timezone
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarService:
    """
    Google Calendar wrapper with correct timezone handling.

    Key ideas:
    - Work in the user's local tz for UI/slot generation.
    - Convert to UTC only for comparisons and freeBusy queries.
    - Create events in the user's tz so the Calendar shows the intended local time.
    """
    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    def __init__(self, user_tz: Optional[str] = None):
        # Default to IST for you; override via env or constructor
        self.user_tz_name = user_tz or os.getenv("USER_TZ", "Asia/Kolkata")
        self.USER_TZ = ZoneInfo(self.user_tz_name)
        self.creds: Optional[Credentials] = None
        self.service = None
        self.load_credentials()

    # ---------------------- TZ helpers ---------------------- #
    def _localize_naive(self, dt: datetime) -> datetime:
        """Treat naive datetimes as local user tz."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.USER_TZ)
        return dt

    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        """Convert any aware/naive (assumed already localized) to UTC."""
        if dt.tzinfo is None:
            raise ValueError("Expected tz-aware datetime before converting to UTC.")
        return dt.astimezone(timezone.utc)

    @staticmethod
    def _iso_utc_z(dt: datetime) -> str:
        """RFC3339 with 'Z'."""
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    # ---------------------- Auth ---------------------- #
    def load_credentials(self):
        token_path = Path(__file__).resolve().parent.parent / "token.pickle"
        if token_path.exists():
            with open(token_path, "rb") as token:
                self.creds = pickle.load(token)

        if self.creds and self.creds.valid:
            self.service = build("calendar", "v3", credentials=self.creds)
        elif self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            with open(token_path, "wb") as token:
                pickle.dump(self.creds, token)
            self.service = build("calendar", "v3", credentials=self.creds)

    def get_auth_url(self) -> str:
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
                ],
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback"),
        )
        auth_url, _ = flow.authorization_url(
            prompt="consent", access_type="offline", include_granted_scopes="true"
        )
        return auth_url

    def handle_auth_callback(self, code: str):
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
                ],
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback"),
        )
        flow.fetch_token(code=code)
        self.creds = flow.credentials

        token_path = Path(__file__).resolve().parent.parent / "token.pickle"
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "wb") as token:
            pickle.dump(self.creds, token)

        self.service = build("calendar", "v3", credentials=self.creds)

    def is_authenticated(self) -> bool:
        return self.creds is not None and self.creds.valid

    # ---------------------- Calendar operations ---------------------- #
    def get_busy_times(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get busy time slots from Google Calendar."""
        if not self.is_authenticated():
            return []

        # Localize inputs, then convert to UTC for API
        start_local = self._localize_naive(start_time)
        end_local = self._localize_naive(end_time)
        time_min = self._iso_utc_z(self._to_utc(start_local))
        time_max = self._iso_utc_z(self._to_utc(end_local))

        try:
            body = {
                "timeMin": time_min,
                "timeMax": time_max,
                "timeZone": "UTC",
                "items": [{"id": "primary"}],
            }
            result = self.service.freebusy().query(body=body).execute()
            return result.get("calendars", {}).get("primary", {}).get("busy", [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def _parse_busy(self, busy: List[Dict[str, str]]) -> List[Tuple[datetime, datetime]]:
        """Parse busy ranges (strings with Z) into UTC-aware datetimes."""
        ranges: List[Tuple[datetime, datetime]] = []
        for b in busy:
            b_start = datetime.fromisoformat(b["start"].replace("Z", "+00:00")).astimezone(timezone.utc)
            b_end = datetime.fromisoformat(b["end"].replace("Z", "+00:00")).astimezone(timezone.utc)
            ranges.append((b_start, b_end))
        return ranges

    def find_available_slots(
        self,
        duration_minutes: int,
        start_date: datetime,
        end_date: datetime,
        time_range_start: str = "09:00",
        time_range_end: str = "17:00",
    ) -> List[Dict[str, Any]]:
        """
        Find available slots using LOCAL working hours in user_tz.
        Returns up to 10 slots. Output 'start'/'end' are RFC3339 UTC strings; formatted fields are in user_tz.
        """
        if not self.is_authenticated():
            return []

        # Normalize bounds to local tz
        start_local = self._localize_naive(start_date).astimezone(self.USER_TZ)
        end_local = self._localize_naive(end_date).astimezone(self.USER_TZ)

        # Fetch busy in UTC covering the UTC span
        busy_ranges = self._parse_busy(self.get_busy_times(start_local, end_local))

        available: List[Dict[str, Any]] = []

        start_hour, start_minute = map(int, time_range_start.split(":"))
        end_hour, end_minute = map(int, time_range_end.split(":"))

        cur_day = start_local.date()
        last_day = end_local.date()

        step = timedelta(minutes=30)
        slot_len = timedelta(minutes=duration_minutes)

        while cur_day <= last_day:
            # Day window in LOCAL tz
            day_start_local = datetime.combine(
                cur_day, time(start_hour, start_minute, tzinfo=self.USER_TZ)
            )
            day_end_local = datetime.combine(
                cur_day, time(end_hour, end_minute, tzinfo=self.USER_TZ)
            )

            # Clamp to overall local range
            if day_start_local < start_local:
                day_start_local = start_local
            if day_end_local > end_local:
                day_end_local = end_local

            if day_start_local >= day_end_local:
                cur_day += timedelta(days=1)
                continue

            current_local = day_start_local
            while current_local + slot_len <= day_end_local:
                slot_end_local = current_local + slot_len

                # Compare in UTC
                current_utc = current_local.astimezone(timezone.utc)
                slot_end_utc = slot_end_local.astimezone(timezone.utc)

                free = True
                for b_start_utc, b_end_utc in busy_ranges:
                    if not (slot_end_utc <= b_start_utc or current_utc >= b_end_utc):
                        free = False
                        break

                if free:
                    available.append(
                        {
                            "start": self._iso_utc_z(current_utc),
                            "end": self._iso_utc_z(slot_end_utc),
                            "duration_minutes": duration_minutes,
                            # Display for humans in local tz:
                            "formatted_start": current_local.strftime("%A, %B %d at %I:%M %p"),
                            "formatted_end": slot_end_local.strftime("%I:%M %p"),
                        }
                    )

                current_local += step

            cur_day += timedelta(days=1)

        return available[:10]

    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an event at the intended LOCAL time (user_tz). We send dateTime in local tz + timeZone=user_tz
        so Google renders exactly what the user picked.
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Calendar")

        start_local = self._localize_naive(start_time).astimezone(self.USER_TZ)
        end_local = self._localize_naive(end_time).astimezone(self.USER_TZ)

        event = {
            "summary": summary,
            "description": description or "",
            "start": {"dateTime": start_local.isoformat(), "timeZone": self.user_tz_name},
            "end": {"dateTime": end_local.isoformat(), "timeZone": self.user_tz_name},
        }

        try:
            created = self.service.events().insert(calendarId="primary", body=event).execute()
            return {
                "success": True,
                "event_id": created.get("id"),
                "html_link": created.get("htmlLink"),
            }
        except HttpError as error:
            print(f"An error occurred: {error}")
            return {"success": False, "error": str(error)}
