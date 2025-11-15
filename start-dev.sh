#!/bin/bash

# MediVoice GH - Development Startup Script
# Author: John Evans Okyere

set -e

echo "🏥 MediVoice GH - Starting Development Environment"
echo "=================================================="
echo ""

# Check if .env exists in backend
if [ ! -f backend/.env ]; then
    echo "❌ Error: backend/.env not found!"
    echo "👉 Copy backend/.env.example to backend/.env and add your API keys"
    exit 1
fi

# Check if .env.local exists in frontend
if [ ! -f frontend/.env.local ]; then
    echo "⚠️  Warning: frontend/.env.local not found"
    echo "👉 Creating from .env.example..."
    cp frontend/.env.example frontend/.env.local
fi

echo "✅ Environment files found"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

# Check Node version
NODE_VERSION=$(node --version)
echo "📦 Node version: $NODE_VERSION"
echo ""

# Start backend
echo "🚀 Starting Backend..."
cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "   Activating virtual environment..."
    source venv/bin/activate
else
    echo "   Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "   Installing dependencies..."
    pip install -r requirements.txt
fi

# Load medical data if ChromaDB doesn't exist
if [ ! -d "data/chromadb" ]; then
    echo "   Loading medical knowledge base..."
    python -m app.utils.load_data
fi

# Start backend in background
echo "   Starting FastAPI server..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo ""
echo "🌐 Starting Frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install
fi

echo "   Starting Next.js development server..."
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

cd ..

echo ""
echo "=================================================="
echo "✅ MediVoice GH is now running!"
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Frontend: http://localhost:3000"
echo ""
echo "To stop the servers, press Ctrl+C or run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Happy coding! 🇬🇭"
echo "=================================================="

# Wait for user to stop
wait
