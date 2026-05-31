"""
scraper.py — Web scraping pipeline for GMU Chatbot v2

Run this ONCE to build the knowledge base:
    python scraper.py

What it does:
  1. Reads all 26 URLs from data/gmu_resources.json
  2. Visits each GMU website
  3. Extracts readable text (removes nav, footer, scripts)
  4. Splits text into chunks of ~300 words
  5. Saves each website as a JSON file in scraped_content/

Re-run monthly to refresh content when GMU updates their sites.
Do NOT run this on every user request — only when updating the knowledge base.
"""

import json
import time
import re
from pathlib import Path

# Try importing scraping libraries
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("Install scraping libraries: pip install requests beautifulsoup4")

CHUNK_SIZE   = 300   # words per chunk
DELAY        = 1.5   # seconds between requests — be polite to GMU servers
OUTPUT_DIR   = Path("scraped_content")
DB_PATH      = Path("data/gmu_resources.json")

# Navigation text to remove — appears on most GMU pages but adds no value
NAV_PHRASES = [
    "skip to main content", "skip to content", "back to top",
    "search this site", "toggle navigation", "main navigation",
    "breadcrumb", "you are here", "share this page",
    "last modified", "george mason university", "©",
    "all rights reserved", "privacy statement", "accessibility",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_page(url: str) -> str:
    """Fetch a URL and return raw HTML. Returns empty string on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"    ⚠️  Failed to fetch {url}: {e}")
        return ""


def extract_text(html: str) -> str:
    """
    Extract readable text from HTML.
    Removes scripts, styles, navigation, and other non-content elements.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "noscript", "iframe", "form",
                     "button", "input", "select"]):
        tag.decompose()

    # Get text
    text = soup.get_text(separator=" ", strip=True)

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    # Remove navigation phrases (case-insensitive)
    for phrase in NAV_PHRASES:
        text = re.sub(re.escape(phrase), " ", text, flags=re.IGNORECASE)

    # Remove very short lines (usually nav items)
    lines = [line.strip() for line in text.split(".") if len(line.strip()) > 40]
    text  = ". ".join(lines)

    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    """
    Split text into chunks of ~chunk_size words.
    Each chunk is one searchable unit in the vector database.
    """
    if not text:
        return []

    words  = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 50:   # skip very short chunks
            chunks.append(chunk.strip())

    return chunks


def scrape_site(intent: str, url: str) -> dict:
    """Scrape one GMU website and return structured data."""
    print(f"  Scraping: {intent} ({url})")

    html   = fetch_page(url)
    text   = extract_text(html)
    chunks = chunk_text(text)

    print(f"    → {len(chunks)} chunks extracted")

    return {
        "intent":  intent,
        "url":     url,
        "chunks":  chunks,
        "chunk_count": len(chunks),
    }


def scrape_all():
    """Main function — scrape all 26 GMU websites."""
    if not SCRAPING_AVAILABLE:
        print("Cannot scrape — missing libraries.")
        print("Run: pip install requests beautifulsoup4")
        return

    # Load database
    with open(DB_PATH, "r", encoding="utf-8") as f:
        database = json.load(f)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Filter entries that have URLs
    entries = [
        e for e in database
        if e.get("link", "").startswith("http")
        and e.get("intent", "").lower() not in {"greeting", "goodby", "goodbye"}
    ]

    print(f"\n🔍 Starting scrape of {len(entries)} GMU websites...\n")

    success = 0
    failed  = []

    for entry in entries:
        intent = entry["intent"]
        url    = entry["link"]

        # Skip if already scraped (to allow resuming)
        output_file = OUTPUT_DIR / f"{intent.replace(' ', '_').replace('/', '_')}.json"
        if output_file.exists():
            print(f"  ✅ Already scraped: {intent} — skipping")
            success += 1
            continue

        result = scrape_site(intent, url)

        if result["chunk_count"] > 0:
            output_file.write_text(
                json.dumps(result, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            success += 1
        else:
            print(f"    ❌ No content extracted for {intent}")
            failed.append(intent)

        # Polite delay between requests
        time.sleep(DELAY)

    # Summary
    print(f"\n{'='*50}")
    print(f"✅ Successfully scraped: {success}/{len(entries)} sites")
    if failed:
        print(f"❌ Failed (possibly JavaScript-rendered): {', '.join(failed)}")
        print("   For failed sites, consider adding manual content to scraped_content/")
    print(f"📁 Output saved to: {OUTPUT_DIR}/")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    scrape_all()
