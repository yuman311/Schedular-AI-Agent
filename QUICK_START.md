# Quick Start Guide

## ⚡ Get Started in 5 Minutes

### Step 1: Get API Keys (5 minutes)

#### OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

#### Google Calendar Credentials
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "Google Calendar API"
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URI: `http://localhost:8000/auth/callback`
6. Copy Client ID and Client Secret

### Step 2: Configure Environment (2 minutes)

**Backend** (`backend/.env`):
```bash
cd backend
cp .env.example .env
# Edit .env with your actual keys
```

```env
OPENAI_API_KEY=sk-your-actual-key-here
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

**Frontend** (`frontend/.env.local`):
```bash
cd frontend
cp .env.example .env.local
```

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Step 3: Start the App (30 seconds)

**Option 1: Use the startup script**
```bash
./start.sh
```

**Option 2: Start manually**

Terminal 1:
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2:
```bash
cd frontend
npm run dev
```

### Step 4: Use the Agent (2 minutes)

1. Open http://localhost:5000
2. Click "Connect Calendar" → Complete OAuth
3. Click "Connect to Agent"
4. Click 🎤 and say: "I need a 1-hour meeting tomorrow afternoon"
5. The AI will respond with voice and show available slots!

---

## 🎯 First Conversation Example

```
You: "I need to schedule a meeting"
AI: "I'd be happy to help! How long should the meeting be?"

You: "1 hour"
AI: "Got it. Do you have a preferred day or time?"

You: "Tomorrow afternoon"
AI: "I found these available slots tomorrow afternoon:
     - 2:00 PM - 3:00 PM
     - 4:30 PM - 5:30 PM
     Which one works for you?"

You: "2 PM is perfect"
AI: "Great! I've scheduled your 1-hour meeting for tomorrow at 2:00 PM."
```

---

## 🔍 Troubleshooting

**"Error checking auth status"** in browser console
- Backend not running → Start backend first
- Wrong API URL → Check `frontend/.env.local`

**"Incorrect API key provided"**
- Check `backend/.env` has correct OpenAI key
- No extra spaces or quotes around the key

**"redirect_uri_mismatch"**
- In Google Cloud Console, verify redirect URI is exactly: `http://localhost:8000/auth/callback`

**Voice not working**
- Use Chrome or Edge browser
- Allow microphone permissions
- Must use localhost or HTTPS

---

## 📚 Full Documentation

- **Setup Guide**: See `SETUP_GUIDE.md` for detailed instructions
- **Project Summary**: See `PROJECT_SUMMARY.md` for architecture details
- **README**: See `README.md` for complete documentation

---

## ✅ You're Ready!

Once you see:
- ✅ Frontend running on http://localhost:5000
- ✅ Backend running on http://localhost:8000
- ✅ "Connected" status in the UI
- ✅ WebSocket connected

You can start scheduling meetings with voice! 🎉
