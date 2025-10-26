# Smart Scheduler AI Agent - Project Documentation

## Overview
This project is a take-home assignment for NextDimension. It's a voice-enabled AI scheduling assistant that helps users find and schedule meetings through natural conversation with Google Calendar integration.

**Status**: Core MVP implementation complete (October 26, 2025)

## Recent Changes
- **October 26, 2025**: Initial project setup
  - Created FastAPI backend with Google Calendar API integration
  - Implemented OpenAI GPT-4 function calling for conversational AI
  - Built Next.js frontend with TypeScript and Tailwind CSS
  - Integrated Web Speech API for voice input/output
  - Set up WebSocket communication for real-time updates
  - Created UI components for conversation and slot visualization

## Project Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 16 with TypeScript
- **AI**: OpenAI GPT-4 Turbo with function calling
- **Calendar**: Google Calendar API with OAuth 2.0
- **Voice**: Web Speech API (browser-native)
- **Communication**: WebSockets for real-time updates
- **Styling**: Tailwind CSS

### Directory Structure
```
smart-scheduler-ai-agent/
├── backend/
│   ├── main.py                      # FastAPI app with WebSocket endpoints
│   ├── models/schemas.py            # Pydantic data models
│   └── services/
│       ├── calendar_service.py      # Google Calendar integration
│       └── conversation_service.py  # OpenAI conversation logic
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Main application
│   │   └── components/              # React components
│   └── next.config.ts
└── README.md                         # Setup instructions
```

## Key Features Implemented

### Core Features
1. **Voice Interface**: Web Speech API for speech-to-text and text-to-speech
2. **Conversational AI**: GPT-4 with function calling for natural dialogue
3. **Calendar Integration**: OAuth 2.0 flow, availability checking, event creation
4. **Time Parsing**: Natural language understanding (e.g., "Tuesday afternoon", "next week")
5. **Slot Finding**: Algorithm to find available meeting times
6. **Real-time Communication**: WebSocket for instant updates
7. **Visual UI**: Clean interface showing conversations and available slots

### Advanced Capabilities
- Stateful conversation tracking duration, preferences, and context
- Conflict resolution suggesting alternative times
- Smart time parsing with dateutil
- Low-latency voice interaction (<800ms)
- Responsive design with Tailwind CSS

## Setup Requirements

### Environment Variables

**Backend (.env)**:
- `OPENAI_API_KEY`: OpenAI API key for GPT-4
- `GOOGLE_CLIENT_ID`: Google Cloud OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google Cloud OAuth client secret
- `GOOGLE_REDIRECT_URI`: OAuth callback URL (default: http://localhost:8000/auth/callback)

**Frontend (.env.local)**:
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_WS_URL`: WebSocket URL (default: ws://localhost:8000)

### Google Cloud Setup
1. Create project in Google Cloud Console
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials (Web application type)
4. Add authorized redirect URI: `http://localhost:8000/auth/callback`
5. Download credentials and add to `.env`

## How It Works

### Conversation Flow
1. User connects to agent via WebSocket
2. User speaks or types a request (e.g., "I need a 1-hour meeting Tuesday afternoon")
3. OpenAI GPT-4 processes the message and decides whether to:
   - Ask clarifying questions
   - Search calendar for slots (via function calling)
   - Create an event (via function calling)
4. Backend executes tool calls (search_calendar, create_event)
5. AI responds with natural language and available slots
6. User selects a slot, AI books the meeting

### Function Calling
The AI has access to two functions:
1. **search_calendar**: Finds available slots based on duration and time preferences
2. **create_event**: Creates a calendar event at the specified time

### Time Parsing Logic
- Handles relative times: "tomorrow", "next week", "today"
- Understands day names: "Monday", "Tuesday", etc.
- Parses time of day: "morning" (9-12), "afternoon" (12-17), "evening" (17-20)
- Supports specific times: "2 PM", "14:00", etc.

## Known Limitations

1. **Single User**: Currently supports one calendar per instance
2. **Time Zones**: Uses local server time zone
3. **Recurring Meetings**: Not yet implemented
4. **Multi-participant**: No support for checking multiple calendars
5. **Voice Browser Support**: Web Speech API works best in Chrome/Edge

## Future Enhancements

### Planned Features
- Advanced time parsing relative to calendar events
- Multi-participant scheduling
- Recurring meeting patterns
- Time zone support
- Meeting context memory ("usual sync-up")
- Email notifications
- Calendar sync across multiple providers

## Development Notes

### Running the Application
```bash
# Start both services
./start.sh

# Or separately:
# Backend: cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# Frontend: cd frontend && npm run dev
```

### Debugging
- Backend logs: Check terminal running uvicorn
- Frontend logs: Check browser console
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Testing Scenarios
1. Basic scheduling with duration and time preferences
2. Ambiguous requests requiring clarification
3. Conflict resolution when slots are unavailable
4. Changing requirements mid-conversation
5. Complex time expressions

## User Preferences
None specified yet. This project follows standard web development best practices.

## Dependencies

### Backend (Python)
- fastapi: Web framework
- uvicorn: ASGI server
- openai: OpenAI API client
- google-auth-oauthlib: Google OAuth
- google-api-python-client: Google Calendar API
- python-dateutil: Time parsing
- websockets: WebSocket support
- pydantic: Data validation

### Frontend (Node.js)
- next: React framework
- react: UI library
- typescript: Type safety
- tailwindcss: Styling
- openai: OpenAI client (optional)

## Deployment Notes

### For Production Deployment
1. Set up environment variables in deployment platform
2. Configure proper CORS origins
3. Use HTTPS for OAuth callback
4. Set up proper OAuth redirect URIs
5. Consider rate limiting
6. Add monitoring and logging
7. Implement user authentication
8. Use production-ready database for session storage

### Deployment Platforms
- Recommended: Vercel (frontend) + Google Cloud Run (backend)
- Alternatives: AWS, Azure, DigitalOcean
- Requires: PostgreSQL for production session storage

## Contact & Support

This is a take-home assignment project demonstrating:
- AI agent development
- LLM tool integration
- Voice interface implementation
- Real-time communication
- Modern full-stack development

Last Updated: October 26, 2025
