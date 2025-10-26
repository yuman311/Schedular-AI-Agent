#!/bin/bash

echo "Starting Smart Scheduler AI Agent..."
echo "=================================="

cd backend
echo "Starting FastAPI backend on port 8000..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ../frontend
echo "Starting Next.js frontend on port 5000..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo "   - Backend API: http://localhost:8000"
echo "   - Frontend: http://localhost:5000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

wait
