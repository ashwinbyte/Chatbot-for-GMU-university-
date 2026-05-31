# GMU Intelligent Resource Navigation AI Chatbot

A full-stack AI-powered chatbot that helps George Mason University students find campus resources instantly — by just asking in plain English. No more digging through 26 different GMU websites.

---

## The Problem

GMU has over 26 separate resource websites. Financial aid is one place, housing is another, transcripts somewhere else. Students waste time searching or give up entirely. I wanted to fix that with a single conversational interface that actually understands what you are asking — even with typos, informal phrasing, or vague questions.

---

## What It Does

You type something like *"how do I apply for financial aid"* or *"where is the RAC"* and the chatbot:

- Figures out exactly what you need using a custom matching engine
- Searches through real scraped content from the actual GMU websites
- Generates a natural conversational answer using Gemini AI
- Gives you the direct link to the right page

No keywords required. No exact phrasing needed. Just ask like you would ask a friend.

---

## How It Actually Works

The system has three layers working together:

**Layer 1 — Intent Matching**
A custom 4-tier fuzzy scoring engine reads your query, removes stop words, and scores all 26 resources simultaneously. The highest scorer above a 65% confidence threshold wins. This replaced a broken first-match approach that returned wrong results constantly.

**Layer 2 — Semantic Search (RAG)**
Scraped content from all 26 GMU websites is split into 62 text chunks, converted into 384-dimensional sentence embeddings using `all-MiniLM-L6-v2`, and stored in ChromaDB. When you ask a question, the 3 most semantically relevant chunks are retrieved — even if your words do not exactly match the content.

**Layer 3 — Response Generation**
The retrieved chunks plus your original question go to Gemini API as a grounded prompt. Gemini writes a natural 2-4 sentence answer using only the real GMU content — no hallucination, no guessing. If Gemini is unavailable, the system falls back to pre-written descriptions automatically.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | FastAPI, Python |
| AI / Generation | Gemini API (google-genai) |
| Vector Search | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Web Scraping | requests, BeautifulSoup4 |
| Fuzzy Matching | rapidfuzz |
| Deployment | Render (backend), Vercel (frontend) |

---

## Project Structure

```
├── main.py                  # FastAPI server — 3 endpoints
├── scraper.py               # Scrapes 26 GMU websites
├── data/
│   ├── gmu_resources.json   # 26 GMU resources with keywords and links
│   └── analytics.json       # Persisted query popularity counts
├── scraped_content/         # Real text extracted from GMU websites
├── src/
│   ├── matcher.py           # 4-tier fuzzy scoring engine
│   ├── responder.py         # Response formatting with RAG fallback
│   ├── embeddings.py        # ChromaDB vector setup and search
│   ├── rag.py               # Gemini API integration
│   └── analytics.py        # Persistent query tracking
└── frontend/
    └── src/
        ├── App.jsx          # Chat UI with typing indicators and stats
        └── api.js           # Centralized API layer
```

---

## Running Locally

**Prerequisites:** Python 3.10+, Node.js 18+

**Step 1 — Clone and install**
```bash
git clone https://github.com/your-username/gmu-chatbot.git
cd gmu-chatbot
pip install -r requirements.txt
```

**Step 2 — Add your Gemini API key**
```bash
cp .env.example .env
# Open .env and add your key from aistudio.google.com
```

**Step 3 — Scrape GMU websites and build vector database**
```bash
python scraper.py
python -c "from src.embeddings import setup_vector_database; setup_vector_database()"
```

**Step 4 — Start the backend**
```bash
python main.py
# API docs available at http://localhost:8000/docs
```

**Step 5 — Start the frontend**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check — confirms server status and RAG availability |
| POST | `/chat` | Send a message, receive a response with intent, confidence, and link |
| GET | `/stats` | Returns top 10 most queried topics for the analytics dashboard |

Interactive docs available at `http://localhost:8000/docs` when running locally.

---

## What I Fixed Along the Way

The original version of this chatbot had a critical bug — it returned the **first** keyword match found, not the best one. Typing "campus wifi issue" would return "campus map" because "campus" matched first. I rebuilt the entire matching engine to score every resource and return the highest scorer.

A few other things I fixed and improved:

- **False positive fuzzy matches** — "hi" was matching inside "scholarships" through a sliding window search. Fixed with word boundary regex.
- **Canvas vs Blackboard disambiguation** — they had identical keywords and constantly returned each other's results.
- **Analytics reset on restart** — the original popularity counter lived only in memory. Rebuilt with disk persistence so data survives indefinitely.
- **Scraped content quality** — many GMU pages use JavaScript rendering so the scraper got navigation menus instead of real content. Addressed with manual knowledge base entries for thin pages.

---

## Key Design Decisions

**Why fuzzy matching AND vector search?**
Fuzzy matching is fast, explainable, and handles typos well for known keywords. Vector search handles semantic meaning — "I feel overwhelmed" matching mental health resources with zero keyword overlap. Using both together (hybrid retrieval) gives better coverage than either alone.

**Why confidence thresholding?**
Below 65% confidence the chatbot says "I couldn't find a match" rather than guessing confidently. A wrong answer delivered confidently is worse than admitting uncertainty.

**Why graceful RAG fallback?**
If Gemini is unavailable, the system returns pre-written descriptions instead of crashing. The chatbot is never down because of an external API failure.

---

## Metrics

- **26** GMU campus resources covered
- **62** vector-embedded knowledge chunks in ChromaDB
- **95%+** intent recognition accuracy across test queries
- **58** automated tests — unit, integration, and edge cases
- **4** critical matching bugs identified and resolved
- **3** API endpoints with auto-generated interactive documentation
- **Sub-second** response times for fuzzy matching (RAG adds ~1-2s for Gemini)

---

## Future Improvements

- **Playwright scraping** — replace requests with a real browser automation tool to handle JavaScript-rendered GMU pages and get complete content
- **Conversation memory** — remember context across messages so follow-up questions like "how do I apply?" work after a housing match
- **Voice input** — Web Speech API integration for hands-free queries
- **GMU NetID authentication** — personalize responses based on student vs faculty vs staff
- **Automated re-scraping** — scheduled monthly refresh of GMU website content so the knowledge base stays current

---

## License

MIT License — feel free to adapt this for your own university or organization.

---

*Built for George Mason University students. Not an official GMU product.*
