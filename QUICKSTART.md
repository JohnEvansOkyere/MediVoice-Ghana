# MediVoice GH - Quick Start Guide

Get MediVoice GH running locally in 10 minutes!

## Prerequisites Check

```bash
python --version  # Should be 3.11+
node --version    # Should be 18+
docker --version  # Optional
```

## 1. Get API Keys (5 minutes)

### Required (Free):
1. **Groq** - https://console.groq.com → Get API key
2. **Google Gemini** - https://makersuite.google.com → Get API key
3. **Neon DB** - https://neon.tech → Create project → Copy connection string
4. **Upstash Redis** - https://upstash.com → Create database → Copy Redis URL

### Optional:
- **xAI Grok** - https://x.ai (paid, but optional)
- **Google Cloud TTS** - https://console.cloud.google.com (for voice responses)

## 2. Backend Setup (3 minutes)

```bash
# Clone and enter backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

Edit `.env` with your API keys:
```bash
# Required
DATABASE_URL=postgresql://your-neon-connection-string
REDIS_URL=redis://your-upstash-url
GROQ_API_KEY=your-groq-key
GOOGLE_API_KEY=your-gemini-key
GROQ_WHISPER_API_KEY=your-groq-key  # Same as GROQ_API_KEY
N8N_WEBHOOK_URL=http://localhost:5678/webhook/appointment-booking

# Generate secrets (run these commands):
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

```bash
# Load medical data
python -m app.utils.load_data

# Start backend
uvicorn app.main:app --reload
```

Backend running at: http://localhost:8000
API docs: http://localhost:8000/docs

## 3. Frontend Setup (2 minutes)

```bash
# New terminal, go to frontend
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
# Start frontend
npm run dev
```

Frontend running at: http://localhost:3000

## 4. Test It Out!

1. Go to http://localhost:3000
2. Click "Sign Up" and create an account
3. Log in
4. Try asking: "I have a fever and headache"
5. See the AI response!

## 5. Optional: n8n for Appointments

```bash
# In project root
docker-compose up -d n8n
```

1. Go to http://localhost:5678
2. Login: admin / admin
3. Import workflow from `n8n-workflows/appointment-booking.json`
4. Activate workflow
5. Copy webhook URL to backend `.env`

## Common Issues

### Backend errors?
- Make sure all API keys are set in `.env`
- Check database URL is correct
- Verify Redis URL is correct

### Frontend can't connect?
- Check backend is running on port 8000
- Verify NEXT_PUBLIC_API_URL in `.env.local`

### Voice recording not working?
- Use Chrome/Edge (best support)
- Allow microphone permissions
- HTTPS required in production

## Next Steps

- Read [README_FULL.md](README_FULL.md) for detailed documentation
- Customize medical knowledge in `backend/data/medical_knowledge.json`
- Deploy to Render (backend) and Vercel (frontend)

## Production Deployment

### Backend (Render)
```bash
# Create Web Service on Render
# Connect GitHub repo
# Set root directory: backend
# Add environment variables from .env
# Deploy!
```

### Frontend (Vercel)
```bash
cd frontend
vercel
# Follow prompts
# Add NEXT_PUBLIC_API_URL with Render backend URL
```

## Support

Having issues? Check:
- API keys are valid
- Database and Redis are accessible
- All dependencies installed correctly
- Python 3.11+ and Node 18+

---

**You're all set! Start helping people in Ghana! 🇬🇭**
