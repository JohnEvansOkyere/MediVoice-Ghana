# MediVoice GH - Deployment Checklist

Use this checklist to deploy MediVoice GH to production.

## Pre-Deployment Checklist

### API Keys & Accounts Setup
- [ ] **Neon DB** account created
  - [ ] Database created
  - [ ] Connection string copied
- [ ] **Upstash Redis** account created
  - [ ] Redis database created
  - [ ] Redis URL copied
- [ ] **Groq** account created
  - [ ] API key generated
- [ ] **Google Gemini** account created
  - [ ] API key generated
- [ ] **Render** account created
- [ ] **Vercel** account created

### Optional Services
- [ ] **xAI Grok** account (optional, for primary LLM)
- [ ] **Google Cloud** project (optional, for TTS)
  - [ ] Text-to-Speech API enabled
  - [ ] Service account created
  - [ ] JSON key downloaded
- [ ] **Telegram** bot created (optional)
  - [ ] Bot token from @BotFather

### Code Preparation
- [ ] All code committed to GitHub
- [ ] `.gitignore` properly configured
- [ ] Environment example files present
- [ ] Medical knowledge data included
- [ ] Documentation complete

## Backend Deployment (Render)

### Step 1: Create Web Service
- [ ] Log into Render
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub repository
- [ ] Select repository

### Step 2: Configure Service
- [ ] **Name:** `medivoice-gh-backend`
- [ ] **Root Directory:** `backend`
- [ ] **Environment:** `Python 3`
- [ ] **Build Command:** `pip install -r requirements.txt`
- [ ] **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] **Plan:** Free

### Step 3: Environment Variables
Add all these variables:

**Required:**
- [ ] `DATABASE_URL` = Your Neon connection string
- [ ] `REDIS_URL` = Your Upstash Redis URL
- [ ] `GROQ_API_KEY` = Your Groq API key
- [ ] `GROQ_WHISPER_API_KEY` = Your Groq API key (same)
- [ ] `GOOGLE_API_KEY` = Your Gemini API key
- [ ] `N8N_WEBHOOK_URL` = Your n8n webhook URL (or dummy for now)
- [ ] `SECRET_KEY` = Generate with: `openssl rand -hex 32`
- [ ] `JWT_SECRET_KEY` = Generate with: `openssl rand -hex 32`
- [ ] `ALLOWED_ORIGINS` = `https://your-frontend.vercel.app` (update after frontend deploy)

**Optional:**
- [ ] `XAI_API_KEY` = Your xAI/Grok key
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` = Path to GCP JSON (if using TTS)
- [ ] `GCP_PROJECT_ID` = Your GCP project ID
- [ ] `TELEGRAM_BOT_TOKEN` = Your Telegram bot token

### Step 4: Deploy
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (~5 minutes)
- [ ] Check logs for errors
- [ ] Note your backend URL: `https://medivoice-gh-backend.onrender.com`

### Step 5: Test Backend
- [ ] Visit `https://your-backend.onrender.com`
- [ ] Should see welcome message
- [ ] Visit `https://your-backend.onrender.com/docs`
- [ ] API documentation should load
- [ ] Test `/api/health` endpoint

## Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy from Frontend Directory
```bash
cd frontend
vercel
```

### Step 3: Follow Prompts
- [ ] **Set up and deploy?** → Yes
- [ ] **Which scope?** → Your account
- [ ] **Link to existing project?** → No
- [ ] **What's your project's name?** → `medivoice-gh`
- [ ] **In which directory is your code located?** → `./`
- [ ] **Want to modify settings?** → No

### Step 4: Environment Variable
- [ ] Go to Vercel dashboard → Your project → Settings → Environment Variables
- [ ] Add: `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`
- [ ] Redeploy: `vercel --prod`

### Step 5: Test Frontend
- [ ] Visit your Vercel URL
- [ ] Create test account
- [ ] Test login
- [ ] Try voice/text interaction
- [ ] Check conversation history
- [ ] Test appointment booking

## Update CORS (Important!)

### Update Backend CORS
- [ ] Go to Render → Your service → Environment
- [ ] Update `ALLOWED_ORIGINS` to include your Vercel URL
- [ ] Example: `https://medivoice-gh.vercel.app,https://medivoice-gh-frontend.vercel.app`
- [ ] Save and redeploy

## n8n Setup (Optional)

### If Using Cloud n8n:
- [ ] Sign up at n8n.cloud
- [ ] Import workflow from `n8n-workflows/appointment-booking.json`
- [ ] Configure email credentials
- [ ] Activate workflow
- [ ] Copy webhook URL

### If Self-Hosting:
- [ ] Deploy n8n to a server (DigitalOcean, Railway, etc.)
- [ ] Set up SSL certificate
- [ ] Import workflow
- [ ] Configure credentials
- [ ] Activate workflow

### Update Backend:
- [ ] Go to Render → Environment
- [ ] Update `N8N_WEBHOOK_URL` with your n8n webhook URL
- [ ] Save and redeploy

## Telegram Bot Setup (Optional)

- [ ] Set webhook URL:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_BACKEND_URL>/api/telegram/webhook"
```
- [ ] Test by sending message to your bot

## Post-Deployment Tests

### Functional Testing
- [ ] User registration works
- [ ] User login works
- [ ] Voice recording works (requires HTTPS)
- [ ] Text input works
- [ ] AI responses are generated
- [ ] Emergency detection triggers
- [ ] Conversation history saves
- [ ] Appointments can be booked
- [ ] Telegram bot responds (if configured)

### Performance Testing
- [ ] Page load time < 3s
- [ ] API response time < 5s
- [ ] Voice interaction complete < 10s

### Security Testing
- [ ] Cannot access protected routes without login
- [ ] JWT expires correctly
- [ ] CORS blocks unauthorized domains
- [ ] SQL injection protected
- [ ] XSS protected

## Monitoring Setup

### Render
- [ ] Enable email alerts for deployment failures
- [ ] Set up uptime monitoring

### Vercel
- [ ] Configure deployment notifications
- [ ] Enable analytics (optional)

### Database
- [ ] Set up Neon monitoring
- [ ] Configure backups

### Application
- [ ] Check LLM logs table for errors:
```sql
SELECT * FROM llm_logs WHERE success = false ORDER BY created_at DESC LIMIT 10;
```

## Custom Domain (Optional)

### Frontend Domain
- [ ] Purchase domain (e.g., medivoice.gh)
- [ ] Add to Vercel: Settings → Domains
- [ ] Configure DNS records
- [ ] Wait for SSL certificate

### Backend Domain
- [ ] Add custom domain in Render
- [ ] Configure DNS CNAME record
- [ ] Update CORS settings

## Documentation Updates

- [ ] Update README with live URLs
- [ ] Add API documentation link
- [ ] Update screenshots if any
- [ ] Create user guide

## Launch Checklist

### Pre-Launch
- [ ] All features tested
- [ ] Medical information reviewed
- [ ] Disclaimer displayed prominently
- [ ] Terms of service created (optional)
- [ ] Privacy policy created (optional)

### Launch
- [ ] Announce on social media
- [ ] Share with test users
- [ ] Monitor for errors
- [ ] Gather feedback

### Post-Launch
- [ ] Monitor usage analytics
- [ ] Check error logs daily
- [ ] Respond to user feedback
- [ ] Plan improvements

## Scaling Considerations

### When You Outgrow Free Tier:

**Render ($7/month Starter):**
- 512 MB RAM → 2 GB RAM
- No sleep/spin down
- Better performance

**Neon ($19/month Scale):**
- 500 MB → 10 GB storage
- Better performance
- Autoscaling

**Upstash ($10/month Pay-as-you-go):**
- 10K commands/day → unlimited
- Better performance

**Vercel ($20/month Pro):**
- More bandwidth
- Better analytics
- Team collaboration

## Troubleshooting

### Backend not responding
- [ ] Check Render logs
- [ ] Verify all env vars set
- [ ] Check database connection
- [ ] Verify Redis connection

### Frontend not connecting
- [ ] Check NEXT_PUBLIC_API_URL is correct
- [ ] Verify CORS settings in backend
- [ ] Check browser console for errors

### LLM responses failing
- [ ] Check API keys are valid
- [ ] Verify rate limits
- [ ] Check provider status pages
- [ ] Review LLM logs table

### Database errors
- [ ] Check connection string
- [ ] Verify database is running
- [ ] Check for migration issues

## Success Metrics

Track these metrics:
- [ ] Daily active users
- [ ] Conversations per day
- [ ] Emergency detections
- [ ] Appointments booked
- [ ] Average response time
- [ ] LLM provider success rates
- [ ] User satisfaction feedback

## Backup Plan

### Database Backups
- [ ] Neon automatic backups enabled
- [ ] Manual backup procedure documented
- [ ] Recovery tested

### Code Backups
- [ ] Code on GitHub
- [ ] Tagged releases
- [ ] Documentation preserved

---

## Final Checks

- [ ] **All backend endpoints working** ✓
- [ ] **All frontend pages working** ✓
- [ ] **Medical knowledge loaded** ✓
- [ ] **Emergency detection active** ✓
- [ ] **Authentication secure** ✓
- [ ] **Documentation complete** ✓
- [ ] **Disclaimer visible** ✓

---

**Status: READY FOR PRODUCTION** 🚀

**Deployed by:** _______________
**Date:** _______________
**Backend URL:** _______________
**Frontend URL:** _______________

---

Built with ❤️ for Ghana 🇬🇭
