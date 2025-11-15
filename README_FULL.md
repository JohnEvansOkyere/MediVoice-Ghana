# MediVoice GH - AI Voice Health Advisor for Ghana

**Author:** John Evans Okyere

An AI-powered voice health advisor designed specifically for Ghana. Users can describe their symptoms via voice or text, receive health information and advice, detect emergencies, and book medical appointments.

## Features

- **Voice Interaction**: Record symptoms via voice, get text AND voice responses
- **Symptom Analysis**: AI-powered symptom analysis using RAG (Retrieval-Augmented Generation)
- **Emergency Detection**: Automatic detection of emergency keywords with immediate alerts
- **Medical Knowledge Base**: 20+ common health conditions in Ghana (Malaria, Typhoid, Cholera, etc.)
- **Appointment Booking**: Integrated with n8n for automated appointment scheduling
- **Conversation History**: Track all past health consultations
- **Multi-channel**: Web interface + optional Telegram bot
- **LLM Fallback Chain**: Grok (xAI) → Groq (Llama 3.1) → Gemini Flash for reliability

## Tech Stack

### Backend
- **FastAPI** (Python 3.11+)
- **Neon Postgres** - Database
- **Redis (Upstash)** - Caching
- **ChromaDB** - Vector database for RAG
- **LangChain** - LLM orchestration

### AI/ML
- **LLMs**: Grok (xAI), Groq (Llama 3.1), Gemini Flash
- **STT**: Groq Whisper API
- **TTS**: Google Cloud TTS Standard
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** components

### Automation
- **n8n** - Appointment booking workflows

### Deployment
- **Backend**: Render (free tier)
- **Frontend**: Vercel (free tier)

## Project Structure

```
MediVoice-Ghana/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── voice.py         # Voice interaction
│   │   │       ├── appointments.py  # Appointment booking
│   │   │       ├── conversations.py # History
│   │   │       ├── telegram.py      # Telegram bot
│   │   │       └── health.py        # Health check
│   │   ├── services/
│   │   │   ├── llm_service.py       # LLM with fallback chain
│   │   │   ├── stt_service.py       # Speech-to-text
│   │   │   ├── tts_service.py       # Text-to-speech
│   │   │   ├── rag_service.py       # RAG + ChromaDB
│   │   │   └── cache_service.py     # Redis caching
│   │   ├── db/
│   │   │   ├── database.py          # Database connection
│   │   │   └── models.py            # SQLAlchemy models
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic schemas
│   │   ├── utils/
│   │   │   ├── auth.py              # JWT authentication
│   │   │   └── load_data.py         # Load medical data
│   │   ├── config.py                # Configuration
│   │   └── main.py                  # FastAPI app
│   ├── data/
│   │   └── medical_knowledge.json   # Medical knowledge base
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml                  # Render deployment config
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── history/                 # Conversation history
│   │   ├── appointments/            # Appointments page
│   │   ├── layout.tsx
│   │   ├── page.tsx                 # Main voice interface
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   │   └── button.tsx
│   │   └── voice-recorder.tsx       # Voice recording component
│   ├── lib/
│   │   ├── api.ts                   # API client
│   │   └── utils.ts                 # Utilities
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   ├── vercel.json                  # Vercel deployment config
│   └── .env.example
├── n8n-workflows/
│   └── appointment-booking.json     # n8n workflow
├── docker-compose.yml
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for local development)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd MediVoice-Ghana
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

**Required:**
- `DATABASE_URL` - Get from [Neon](https://neon.tech) (free tier)
- `REDIS_URL` - Get from [Upstash](https://upstash.com) (free tier)
- `GROQ_API_KEY` - Get from [Groq](https://console.groq.com)
- `GOOGLE_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com)
- `N8N_WEBHOOK_URL` - Your n8n webhook URL

**Optional:**
- `XAI_API_KEY` - Get from [xAI](https://x.ai) (for Grok)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to GCP service account JSON (for TTS)
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)

#### Load Medical Knowledge

```bash
python -m app.utils.load_data
```

#### Run Backend

```bash
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

API docs at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend
npm install
```

#### Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Run Frontend

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 4. n8n Setup (Optional but Recommended)

#### Using Docker

```bash
docker-compose up -d n8n
```

Access n8n at `http://localhost:5678`

Default credentials: `admin` / `admin`

#### Import Workflow

1. Go to n8n web interface
2. Click "Import from File"
3. Select `n8n-workflows/appointment-booking.json`
4. Configure email credentials in the workflow
5. Activate the workflow
6. Copy the webhook URL to your backend `.env` as `N8N_WEBHOOK_URL`

### 5. Docker Development (All-in-One)

```bash
docker-compose up
```

This starts:
- Backend at `http://localhost:8000`
- Redis at `localhost:6379`
- n8n at `http://localhost:5678`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

### Voice Interaction
- `POST /api/voice/interact` - Main endpoint for voice/text interaction
  - Body: `{ "audio_data": "base64_string" }` OR `{ "text_message": "string" }`
  - Returns: AI response with emergency detection

### Appointments
- `POST /api/appointments/book` - Book appointment
- `GET /api/appointments/my-appointments` - Get user's appointments
- `GET /api/appointments/{id}` - Get specific appointment

### Conversations
- `GET /api/conversations/history` - Get conversation history
- `GET /api/conversations/{id}` - Get specific conversation

### Telegram (Optional)
- `POST /api/telegram/webhook` - Telegram bot webhook
- `GET /api/telegram/info` - Setup instructions

### Health Check
- `GET /api/health` - API health check

## Deployment

### Backend Deployment (Render)

1. Create account on [Render](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Use `backend` as root directory
5. Add environment variables from `.env.example`
6. Deploy!

Or use the included `render.yaml`:

```bash
# From project root
render deploy
```

### Frontend Deployment (Vercel)

1. Install Vercel CLI: `npm i -g vercel`
2. From frontend directory:

```bash
cd frontend
vercel
```

3. Follow prompts
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your Render backend URL

Or connect via [Vercel Dashboard](https://vercel.com)

### Database Migration (Production)

On Render, add build command:

```bash
pip install -r requirements.txt && python -m app.utils.load_data
```

## API Keys Setup Guide

### 1. Neon Postgres (Free)
- Sign up at [neon.tech](https://neon.tech)
- Create new project
- Copy connection string to `DATABASE_URL`

### 2. Upstash Redis (Free)
- Sign up at [upstash.com](https://upstash.com)
- Create Redis database
- Copy Redis URL to `REDIS_URL`

### 3. Groq API (Free)
- Sign up at [console.groq.com](https://console.groq.com)
- Generate API key
- Add to `GROQ_API_KEY` and `GROQ_WHISPER_API_KEY`

### 4. Google Gemini (Free)
- Go to [Google AI Studio](https://makersuite.google.com)
- Create API key
- Add to `GOOGLE_API_KEY`

### 5. Google Cloud TTS (Optional - has free tier)
- Create project at [Google Cloud Console](https://console.cloud.google.com)
- Enable Cloud Text-to-Speech API
- Create service account and download JSON key
- Set `GOOGLE_APPLICATION_CREDENTIALS` to JSON file path

### 6. xAI Grok (Optional - paid)
- Sign up at [x.ai](https://x.ai)
- Get API key
- Add to `XAI_API_KEY`

## Medical Knowledge Base

The system includes information on:

- **Infectious Diseases**: Malaria, Typhoid, Cholera, Dengue, Tuberculosis, Hepatitis B
- **Chronic Conditions**: Hypertension, Diabetes, Asthma
- **Common Illnesses**: Pneumonia, Gastroenteritis, UTI, Common Cold, Anemia
- **First Aid**: Cuts/wounds, burns, fever, dehydration
- **Emergency Guidelines**: When to call 112

Add more medical knowledge in `backend/data/medical_knowledge.json`

## Emergency Detection

The system automatically detects emergency keywords:
- Severe bleeding
- Chest pain
- Difficulty breathing
- Unconsciousness
- Severe pain
- Poisoning
- And more...

When detected, it immediately alerts the user to call 112.

## Telegram Bot Setup (Optional)

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get bot token
3. Add to `.env` as `TELEGRAM_BOT_TOKEN`
4. Set webhook:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_BACKEND_URL>/api/telegram/webhook"
```

5. Test by messaging your bot on Telegram

## Customization

### Add More Diseases

Edit `backend/data/medical_knowledge.json`:

```json
{
  "text": "Disease info: symptoms, treatment, prevention...",
  "metadata": {
    "source": "WHO Guidelines",
    "disease": "Disease Name",
    "category": "category_name"
  }
}
```

Reload data: `python -m app.utils.load_data`

### Customize LLM Responses

Edit prompts in `backend/app/services/llm_service.py` → `_build_prompt()`

### Add Languages

Currently English-only. To add Twi/Ga/other languages:
1. Update STT service language parameter
2. Add translated prompts to LLM service
3. Update TTS voice selection

## Monitoring

View LLM performance:

```sql
SELECT provider, COUNT(*), AVG(response_time_ms), SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes
FROM llm_logs
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY provider;
```

## Security Notes

- All API endpoints (except auth) require JWT authentication
- Passwords are bcrypt hashed
- CORS configured for your frontend domain
- Rate limiting recommended for production (add middleware)

## Limitations

- **NOT a replacement for medical professionals**
- Information only - not diagnosis or treatment
- English language only (for now)
- Free tier API rate limits
- No image analysis (future feature)

## Troubleshooting

### Backend won't start
- Check all required env vars are set
- Verify database connection: `DATABASE_URL`
- Check Redis connection: `REDIS_URL`

### Voice recording not working
- Ensure HTTPS in production (required for microphone access)
- Check browser permissions

### LLM responses failing
- Check API keys are valid
- Verify rate limits not exceeded
- Check logs for specific provider errors

### Appointments not sending
- Verify n8n webhook URL is correct
- Check n8n workflow is activated
- Test webhook manually with curl

## Future Enhancements

- [ ] Multi-language support (Twi, Ga, Hausa, etc.)
- [ ] Image upload for rashes/wounds
- [ ] SMS integration for appointment confirmations
- [ ] Integration with Ghana Health Service databases
- [ ] Pharmacy locator
- [ ] Medicine information lookup
- [ ] Health tips and preventive care reminders

## Contributing

This is a prototype for testing in Ghana. Contributions welcome!

## License

MIT License - see LICENSE file

## Disclaimer

**IMPORTANT**: MediVoice GH is an informational tool only. It does NOT provide medical diagnosis or treatment. Always consult qualified healthcare professionals for medical advice. In emergencies, call 112 immediately.

## Contact

**Author**: John Evans Okyere

For questions, issues, or collaboration, please open an issue on GitHub.

---

**Built with ❤️ for Ghana**
