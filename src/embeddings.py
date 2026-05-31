"""
embeddings.py — Vector database setup and search for GMU Chatbot v2

What this does:
  - Converts scraped GMU website text into vectors (lists of numbers)
  - Stores vectors in ChromaDB on disk
  - Searches for the most semantically similar chunks when a query arrives

Why vectors instead of keywords:
  Keywords: "I feel overwhelmed" → no keyword match → fails
  Vectors:  "I feel overwhelmed" → similar meaning to mental health content → matches ✅

Run setup_vector_database() once after scraping:
  python -c "from src.embeddings import setup_vector_database; setup_vector_database()"
"""

from __future__ import annotations
import json
from pathlib import Path

# Try importing vector DB libraries
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

SCRAPED_DIR  = Path("scraped_content")
CHROMA_DIR   = Path("data/chroma_db")
COLLECTION   = "gmu_resources"
MODEL_NAME   = "all-MiniLM-L6-v2"   # small, fast, free model
SIMILARITY_THRESHOLD = 0.35          # minimum similarity to return a result

# ── Lazy initialization — load model only when first needed ──────────────
_model      = None
_client     = None
_collection = None


def _get_model():
    global _model
    if _model is None and EMBEDDINGS_AVAILABLE:
        print("Loading embedding model (first time only)...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    global _client, _collection
    if _collection is None and EMBEDDINGS_AVAILABLE:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client     = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = _client.get_or_create_collection(
            name=COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def setup_vector_database() -> bool:
    """
    Load all scraped JSON files and store as vectors in ChromaDB.
    Only needs to run ONCE after scraping.
    Safe to re-run — skips already embedded chunks.
    """
    if not EMBEDDINGS_AVAILABLE:
        print("Missing libraries. Run: pip install chromadb sentence-transformers")
        return False

    if not SCRAPED_DIR.exists():
        print(f"No scraped content found at {SCRAPED_DIR}/")
        print("Run scraper.py first: python scraper.py")
        return False

    scraped_files = list(SCRAPED_DIR.glob("*.json"))
    if not scraped_files:
        print("No scraped JSON files found. Run scraper.py first.")
        return False

    model      = _get_model()
    collection = _get_collection()

    total_chunks = 0
    print(f"\n🔢 Building vector database from {len(scraped_files)} scraped files...\n")

    for file in scraped_files:
        try:
            data   = json.loads(file.read_text(encoding="utf-8"))
            intent = data.get("intent", file.stem)
            url    = data.get("url", "")
            chunks = data.get("chunks", [])

            if not chunks:
                print(f"  ⚠️  No chunks in {file.name} — skipping")
                continue

            for i, chunk in enumerate(chunks):
                chunk_id = f"{intent}_{i}"

                # Skip if already in the database
                existing = collection.get(ids=[chunk_id])
                if existing["ids"]:
                    continue

                # Convert chunk text to a 384-dimensional vector
                vector = model.encode(chunk).tolist()

                # Store in ChromaDB with metadata
                collection.add(
                    ids=[chunk_id],
                    embeddings=[vector],
                    documents=[chunk],
                    metadatas=[{
                        "intent": intent,
                        "url":    url,
                        "chunk":  i,
                    }]
                )
                total_chunks += 1

            print(f"  ✅ {intent}: {len(chunks)} chunks embedded")

        except Exception as e:
            print(f"  ❌ Error processing {file.name}: {e}")

    print(f"\n✅ Vector database ready — {total_chunks} new chunks added")
    print(f"📁 Stored at: {CHROMA_DIR}/\n")
    return True


def find_similar_chunks(query: str, n_results: int = 3) -> list:
    """
    Convert query to vector and find the most semantically similar chunks.

    Returns list of dicts:
      [{text, intent, url, similarity_score}, ...]

    Returns empty list if embeddings not available or no good matches.
    """
    if not EMBEDDINGS_AVAILABLE:
        return []

    collection = _get_collection()
    if collection is None or collection.count() == 0:
        return []

    model = _get_model()
    if model is None:
        return []

    try:
        query_vector = model.encode(query).tolist()

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(n_results, collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # Convert cosine distance to similarity score (0 to 1)
            similarity = 1.0 - (dist / 2.0)

            if similarity >= SIMILARITY_THRESHOLD:
                chunks.append({
                    "text":       doc,
                    "intent":     meta.get("intent", ""),
                    "url":        meta.get("url", ""),
                    "similarity": round(similarity, 3),
                })

        return chunks

    except Exception as e:
        print(f"Vector search error: {e}")
        return []


def is_vector_db_ready() -> bool:
    """Check if vector database has been set up and contains data."""
    if not EMBEDDINGS_AVAILABLE:
        return False
    try:
        collection = _get_collection()
        return collection is not None and collection.count() > 0
    except Exception:
        return False
