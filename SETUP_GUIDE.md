# Smart Scheduler AI Agent - Detailed Setup Guide

## Step-by-Step Setup Instructions

### 1. Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to API keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)
6. Save it securely - you'll need it for the `.env` file

### 2. Set Up Google Cloud Project

#### 2.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Name your project (e.g., "Smart Scheduler")
5. Click "Create"

#### 2.2 Enable Google Calendar API
1. In your Google Cloud project, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and click "Enable"

#### 2.3 Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" for user type
   - Fill in app name: "Smart Scheduler"
   - Add your email as developer contact
   - Skip optional fields
   - Add scopes: `calendar.readonly` and `calendar.events`
   - Add test users (your Google account email)
   - Click "Save and Continue"

4. Back to creating OAuth client ID:
   - Application type: "Web application"
   - Name: "Smart Scheduler Client"
   - Authorized redirect URIs: Add `http://localhost:8000/auth/callback`
   - Click "Create"

5. **Save your credentials**:
   - Copy the Client ID
   - Copy the Client Secret
   - You'll need both for the `.env` file

### 3. Configure Environment Variables

#### Backend Configuration

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your credentials:
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
   ```

#### Frontend Configuration

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Create `.env.local` file:
   ```bash
   cp .env.example .env.local
   ```

3. Edit `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000
   ```

### 4. Install Dependencies

If running on Replit, dependencies are already installed. If running locally:

#### Backend
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### 5. Start the Application

#### Option A: Using the Start Script (Recommended)
From the project root:
```bash
./start.sh
```

This will start both the backend and frontend automatically.

#### Option B: Manual Start

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

### 6. First-Time Usage

1. **Open the application**: Navigate to http://localhost:5000

2. **Authenticate with Google Calendar**:
   - Click the "Connect Calendar" button
   - You'll be redirected to Google's login page
   - Sign in with your Google account
   - Review the permissions (read and write calendar events)
   - Click "Allow"
   - You'll be redirected back to the application

3. **Connect to the AI Agent**:
   - Click "Connect to Agent" button
   - You're now ready to start scheduling!

4. **Test the Voice Interface**:
   - Click "🎤 Start Voice Input"
   - Allow microphone access when prompted by your browser
   - Speak naturally: "I need to schedule a 1-hour meeting"
   - The AI will respond with voice and text

## Troubleshooting Common Issues

### OpenAI API Issues

**Error: "Incorrect API key provided"**
- Double-check your API key in `backend/.env`
- Make sure there are no extra spaces or quotes
- Verify your OpenAI account has credits

**Error: "Rate limit exceeded"**
- You've exceeded your OpenAI API quota
- Wait a few minutes or upgrade your OpenAI plan

### Google Calendar Issues

**Error: "redirect_uri_mismatch"**
- In Google Cloud Console, check OAuth redirect URIs
- Must exactly match: `http://localhost:8000/auth/callback`
- No trailing slashes

**Error: "This app isn't verified"**
- This is normal for development
- Click "Advanced" then "Go to Smart Scheduler (unsafe)"
- This is safe because it's your own app

**Error: "Access blocked: This app's request is invalid"**
- Check that you've enabled Google Calendar API
- Verify OAuth consent screen is configured
- Make sure test users are added (your email)

### Voice Interface Issues

**Voice recognition not working**
- Web Speech API requires Chrome or Edge browser
- Must use HTTPS or localhost
- Check browser microphone permissions
- Try refreshing the page

**No audio output**
- Check system volume and browser audio settings
- Verify speech synthesis is supported in your browser
- Try a different browser (Chrome recommended)

### Connection Issues

**Backend not starting**
- Port 8000 might be in use: `lsof -i :8000` then `kill <PID>`
- Check for Python errors in the terminal
- Verify all environment variables are set

**Frontend not starting**
- Port 5000 might be in use
- Try deleting `node_modules` and running `npm install` again
- Check for syntax errors in the terminal

**WebSocket connection failed**
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify firewall isn't blocking WebSocket connections

### Browser Compatibility

**Recommended**: Chrome or Edge (best Web Speech API support)

**Firefox**: Voice recognition may not work (limited Web Speech API support)

**Safari**: Voice features may have limited functionality

## Security Best Practices

1. **Never commit `.env` files**
   - Already in `.gitignore`
   - Contains sensitive API keys

2. **Rotate API keys regularly**
   - Especially if you suspect they've been compromised

3. **Use separate Google Cloud projects**
   - Development vs. Production
   - Different credentials for each environment

4. **Token storage**
   - OAuth tokens stored in `backend/token.pickle`
   - This file is also in `.gitignore`
   - For production, use encrypted database storage

## Testing the Application

### Basic Test Flow

1. **Authentication Test**:
   ```
   - Click "Connect Calendar"
   - Complete OAuth flow
   - Verify "Connected" status shows
   ```

2. **Simple Scheduling Test**:
   ```
   User: "I need to schedule a meeting"
   Agent: "How long should the meeting be?"
   User: "1 hour"
   Agent: "Do you have a preferred day or time?"
   User: "Tomorrow afternoon"
   Agent: [Shows available slots]
   User: "The 2 PM slot works"
   Agent: "Meeting scheduled successfully!"
   ```

3. **Voice Test**:
   ```
   - Click voice input button
   - Speak: "Find a 30-minute slot for next Monday"
   - Verify AI responds with voice
   - Check conversation appears in text
   ```

4. **Conflict Resolution Test**:
   ```
   User: "Schedule a meeting for 9 AM tomorrow"
   Agent: [If slot is taken] "9 AM is unavailable. How about 9:30 AM or 10 AM?"
   ```

### Advanced Testing Scenarios

1. **Complex Time Parsing**:
   - "Find a slot next Tuesday afternoon"
   - "I need a meeting sometime next week"
   - "Schedule a 45-minute call for the morning of June 20th"

2. **Changing Requirements**:
   - Start with 30 minutes
   - Mid-conversation change to 1 hour
   - Verify agent adapts

3. **Multiple Constraints**:
   - "I'm free next week but not Wednesday"
   - "Find a morning slot, preferably after 9 AM"

## Next Steps

After successful setup, you can:

1. **Customize the AI prompt** in `backend/services/conversation_service.py`
2. **Adjust time ranges** (default 9 AM - 5 PM)
3. **Modify UI styling** in frontend components
4. **Add more features** (recurring meetings, multiple calendars, etc.)

## Getting Help

If you encounter issues:

1. Check the terminal logs for backend errors
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Ensure Google Calendar API is enabled
5. Test API endpoints at http://localhost:8000/docs

## Production Deployment

For deploying to production:

1. Use environment variable management (e.g., Vercel Env Vars, AWS Secrets Manager)
2. Set up proper HTTPS with valid SSL certificates
3. Update OAuth redirect URIs to your production domain
4. Implement rate limiting and error monitoring
5. Use a proper database for token storage
6. Add user authentication
7. Set up logging and monitoring

---

**You're all set!** Enjoy using your Smart Scheduler AI Agent. 🎉
