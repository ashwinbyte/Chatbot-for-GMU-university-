# GMU Resource Chatbot v2 — Complete Run & Deploy Guide

---

## PART 1 — RUN LOCALLY

### Step 1 — Set up Python environment

```bash
cd gmu_chatbot_v2        # your project folder
python -m venv .venv

# Activate:
# Mac/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
```

### Step 2 — Add your Gemini API key

```bash
cp .env.example .env
```

Open `.env` and replace `your_gemini_api_key_here` with your real key.
Get a free key from: https://aistudio.google.com

### Step 3 — Scrape the GMU websites (one time only)

```bash
python scraper.py
```

This visits all 26 GMU websites and saves content to scraped_content/.
Takes 2-3 minutes. Re-run monthly to refresh content.

### Step 4 — Build the vector database (one time only)

```bash
python -c "from src.embeddings import setup_vector_database; setup_vector_database()"
```

This converts all scraped content into vectors and stores in ChromaDB.
Takes a few minutes first time. Never needs to run again unless you re-scrape.

### Step 5 — Start the FastAPI backend

```bash
python main.py
```

Open in browser:
- http://localhost:8000         → health check
- http://localhost:8000/docs    → interactive API docs (show this in interviews!)
- http://localhost:8000/redoc   → alternative docs

### Step 6 — Start the React frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

Your full chatbot is now running locally!

---

## PART 2 — DEPLOY TO THE INTERNET (FREE)

### Backend → Deploy on Render.com

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "GMU Chatbot v2 - RAG + FastAPI + React"
git remote add origin https://github.com/YOUR_USERNAME/gmu-chatbot-backend.git
git push -u origin main
```

2. Go to https://render.com → Sign up with GitHub

3. Click New → Web Service

4. Connect your GitHub repository

5. Fill in settings:
   - Name:           gmu-chatbot-api
   - Region:         US East (Ohio) — closest to GMU in Virginia
   - Branch:         main
   - Runtime:        Python 3
   - Build Command:  pip install -r requirements.txt
   - Start Command:  gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   - Instance Type:  Free

6. Add Environment Variables (click "Add Environment Variable"):
   - Key: GEMINI_API_KEY    Value: your_actual_key
   - Key: ENVIRONMENT       Value: production

7. Click Create Web Service

8. Wait 3-5 minutes → your API is live at:
   https://gmu-chatbot-api.onrender.com

NOTE: Render free tier sleeps after 15 mins of inactivity.
First request after sleep takes ~30 seconds. Upgrade to paid to avoid this.

NOTE: The scraping and vector database must be built before deploying.
Either:
  a) Run scraper.py and setup locally, then commit scraped_content/ and data/chroma_db/ to GitHub
     (remove those paths from .gitignore first)
  b) Or add a startup script that runs them on first deploy

Easiest approach: commit the scraped data to GitHub so Render has it on deploy.
In .gitignore, comment out these lines:
  # scraped_content/
  # data/chroma_db/

---

### Frontend → Deploy on Vercel.com

1. Create a new GitHub repository for the frontend:
```bash
cd frontend
git init
git add .
git commit -m "GMU Chatbot v2 - React Frontend"
git remote add origin https://github.com/YOUR_USERNAME/gmu-chatbot-frontend.git
git push -u origin main
```

2. Go to https://vercel.com → Sign up with GitHub

3. Click New Project → Import your frontend repository

4. Fill in settings:
   - Framework Preset: Vite
   - Root Directory:   ./   (leave as default)
   - Build Command:    npm run build
   - Output Directory: dist

5. Add Environment Variables:
   - Key: VITE_API_URL    Value: https://gmu-chatbot-api.onrender.com

6. Click Deploy

7. Wait 1-2 minutes → your frontend is live at:
   https://gmu-chatbot.vercel.app

---

## PART 3 — TEST EVERYTHING

### Test the API directly:

```bash
# Health check
curl https://gmu-chatbot-api.onrender.com/

# Send a message
curl -X POST https://gmu-chatbot-api.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "how do I apply for financial aid"}'

# Get stats
curl https://gmu-chatbot-api.onrender.com/stats
```

### Test the frontend:
Open https://gmu-chatbot.vercel.app and type questions.

---

## PART 4 — UPDATE AFTER CHANGES

Every git push auto-deploys:

```bash
# Backend update
git add .
git commit -m "your change description"
git push
# Render auto-deploys in 3-4 minutes

# Frontend update
cd frontend
git add .
git commit -m "your change description"
git push
# Vercel auto-deploys in 1-2 minutes
```

---

## PART 5 — YOUR RESUME URLS

Add these to your resume and LinkedIn:
- Live App:   https://gmu-chatbot.vercel.app
- API Docs:   https://gmu-chatbot-api.onrender.com/docs
- GitHub:     https://github.com/YOUR_USERNAME/gmu-chatbot-backend

---

## PART 6 — WHAT TO SAY IN INTERVIEWS

"I built a full-stack RAG-based AI chatbot for GMU students.
The backend is FastAPI with three endpoints — a health check,
a chat endpoint that runs fuzzy matching plus Gemini for generation,
and an analytics endpoint. I built a web scraping pipeline using
BeautifulSoup that visits all 26 GMU websites, extracts real content,
chunks it, and stores it as vectors in ChromaDB. When a student asks
a question, the system does semantic vector search to find the most
relevant scraped content, then passes that to Gemini as context to
generate a natural conversational answer grounded in real GMU data.
The React frontend has real-time chat bubbles, typing indicators,
source citations, and a live analytics dashboard. Both are deployed
with continuous deployment from GitHub — every push auto-deploys."
