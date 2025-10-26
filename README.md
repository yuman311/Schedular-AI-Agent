# Smart Scheduler AI Agent

A voice-enabled AI scheduling assistant that helps users find and schedule meetings through natural conversation with Google Calendar integration.

## 🌟 Features

- **Voice-Enabled Interface**: Speak naturally to schedule meetings using Web Speech API for STT/TTS
- **Intelligent Conversation**: Powered by OpenAI GPT-4 with function calling for natural dialogue
- **Google Calendar Integration**: Real-time availability checking and event creation
- **Smart Time Parsing**: Understands natural language like "Tuesday afternoon", "next week", "before 5 PM"
- **Conflict Resolution**: Suggests alternative times when preferred slots are unavailable
- **Real-time Updates**: WebSocket connection for instant responses
- **Visual Slot Display**: Clean UI showing available meeting times

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with WebSocket support
- **AI Engine**: OpenAI GPT-4 Turbo with function calling
- **Calendar**: Google Calendar API via OAuth 2.0
- **Features**:
  - Stateful conversation management
  - Intelligent time parsing with dateutil
  - Available slot finding algorithm
  - Real-time WebSocket communication

### Frontend (Next.js)
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Voice**: Web Speech API (built-in browser API)
- **Features**:
  - Real-time conversation display
  - Voice input/output with <800ms latency
  - Available slots visualization
  - Google Calendar OAuth flow

## 📋 Prerequisites

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/)
2. **Google Cloud Project**: 
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials (Web application)
   - Add authorized redirect URI: `http://localhost:8000/auth/callback`

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd smart-scheduler-ai-agent
```

### 2. Backend Setup

```bash
cd backend

# Create .env file
cp .env.example .env

# Edit .env and add your credentials:
# OPENAI_API_KEY=your_openai_api_key
# GOOGLE_CLIENT_ID=your_google_client_id
# GOOGLE_CLIENT_SECRET=your_google_client_secret
# GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 3. Frontend Setup

```bash
cd frontend

# Create .env.local file
cp .env.example .env.local

# Edit .env.local and add:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 4. Install Dependencies

The dependencies are already installed in this Replit environment. If running locally:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 5. Run the Application

#### Option 1: Using the Start Script (Recommended)
```bash
./start.sh
```

#### Option 2: Run Services Separately

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Access the Application

- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 How to Use

### Initial Setup
1. Open the application at http://localhost:5000
2. Click "Connect Calendar" to authenticate with Google Calendar
3. Follow the OAuth flow to grant calendar access
4. Click "Connect to Agent" to start the WebSocket connection

### Using the Agent

#### Voice Input (Recommended)
1. Click "🎤 Start Voice Input"
2. Speak your request (e.g., "I need to schedule a 1-hour meeting on Tuesday afternoon")
3. The agent will respond with voice and text
4. Continue the conversation naturally

#### Text Input
1. Type your message in the input box
2. Press Enter or click "Send"
3. The agent will respond in the conversation window

### Example Conversations

**Basic Scheduling:**
```
You: I need to schedule a meeting
Agent: I'd be happy to help! How long should the meeting be?
You: 1 hour
Agent: Got it. Do you have a preferred day or time?
You: Tuesday afternoon
Agent: I found these available slots on Tuesday afternoon:
     - 2:00 PM - 3:00 PM
     - 4:30 PM - 5:30 PM
     Which one works for you?
You: 2 PM works great
Agent: Perfect! I've scheduled your 1-hour meeting for Tuesday at 2:00 PM.
```

**Complex Time Parsing:**
```
You: Find a 45-minute slot sometime next week
Agent: I'll search for 45-minute slots next week. Do you prefer morning, afternoon, or evening?
You: Morning, preferably after 9 AM
Agent: Here are available morning slots next week after 9 AM...
```

**Conflict Resolution:**
```
You: I need a meeting tomorrow at 3 PM
Agent: Unfortunately, 3 PM tomorrow is already booked. Would 2:30 PM or 4:00 PM work instead?
```

## 🎯 Key Features Implemented

### ✅ Core Requirements
- [x] Voice-enabled conversation with <800ms latency
- [x] Google Calendar API integration
- [x] OpenAI GPT-4 with function calling
- [x] Stateful multi-turn conversation
- [x] Natural language time parsing
- [x] Available slot finding
- [x] Event creation

### ✅ Advanced Features
- [x] Conflict resolution with alternative suggestions
- [x] Smart time parsing ("Tuesday afternoon", "next week", etc.)
- [x] WebSocket real-time communication
- [x] Clean, responsive UI
- [x] Conversation state management
- [x] Visual slot display

### 🔮 Potential Enhancements
- [ ] Multi-participant scheduling
- [ ] Recurring meeting support
- [ ] Time zone handling
- [ ] Email notifications
- [ ] Calendar sync across multiple providers
- [ ] Meeting context memory ("usual sync-up")
- [ ] Advanced time parsing (relative to calendar events)

## 🛠️ Technical Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI GPT-4 Turbo**: Conversational AI
- **Google Calendar API**: Calendar integration
- **WebSockets**: Real-time communication
- **Python-dateutil**: Time parsing
- **Pydantic**: Data validation

### Frontend
- **Next.js 16**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Web Speech API**: Voice input/output
- **WebSocket Client**: Real-time updates

## 📁 Project Structure

```
smart-scheduler-ai-agent/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   └── services/
│       ├── calendar_service.py    # Google Calendar integration
│       └── conversation_service.py # AI conversation logic
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Main application page
│   │   └── components/
│   │       ├── AuthStatus.tsx     # Calendar auth status
│   │       ├── ConversationDisplay.tsx  # Chat interface
│   │       ├── VoiceInterface.tsx # Voice input/output
│   │       └── AvailableSlots.tsx # Slot visualization
│   └── next.config.ts             # Next.js configuration
├── start.sh                        # Startup script
└── README.md                       # This file
```

## 🔐 Security Notes

- Never commit `.env` files or credentials to version control
- Google Calendar credentials are stored locally in `token.pickle`
- OpenAI API key should be kept secure
- OAuth tokens are refreshed automatically

## 🐛 Troubleshooting

### Backend Issues
- **"Not authenticated with Google Calendar"**: Click "Connect Calendar" in the UI
- **OpenAI API errors**: Check your API key in `backend/.env`
- **Port 8000 in use**: Stop other services or change the port in `main.py`

### Frontend Issues
- **WebSocket connection failed**: Ensure backend is running on port 8000
- **Voice input not working**: Use Chrome/Edge browser with HTTPS or localhost
- **CORS errors**: Check that backend CORS settings allow your frontend origin

### Voice Issues
- **No voice recognition**: Web Speech API requires HTTPS (or localhost)
- **Voice not speaking**: Check browser audio settings and permissions
- **High latency**: Check internet connection; try text input instead

## 📝 Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-...
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🎥 Demo Video

[Create a 2-3 minute screen recording showing:]
1. Initial setup and Google Calendar authentication
2. Voice-enabled scheduling conversation
3. Handling different time preferences
4. Conflict resolution when slots are unavailable
5. Successful meeting creation

## 🤝 Contributing

This is a take-home assignment project. For production use, consider:
- Adding comprehensive error handling
- Implementing rate limiting
- Adding user authentication
- Supporting multiple calendars
- Adding tests
- Implementing CI/CD

## 📄 License

This project is created as a take-home assignment for NextDimension.

## 👨‍💻 Developer

Built with ❤️ as a demonstration of:
- AI agent development
- LLM tool integration
- Voice interface design
- Real-time communication
- Modern web development practices

---

**Need Help?** Check the API documentation at http://localhost:8000/docs when the backend is running.
