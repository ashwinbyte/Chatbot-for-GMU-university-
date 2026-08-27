# GMU Chatbot — Architecture

## Stack
- Frontend: React + Vite
- Backend: FastAPI + Python
- AI: Groq LLaMA 3.3
- Vector DB: ChromaDB
- Embeddings: sentence-transformers

## Flow
Student → React → FastAPI → ChromaDB → Groq → Response

## Endpoints
- GET  /       Health check
- POST /chat   Process question
- GET  /stats  Analytics data