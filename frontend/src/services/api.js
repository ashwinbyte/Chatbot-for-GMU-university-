/**
 * api.js — Centralized API layer
 *
 * All communication with the FastAPI backend goes through here.
 * If the backend URL changes, you only change it in one place.
 *
 * During development: Vite proxy forwards /chat and /stats to localhost:8000
 * In production:      Set VITE_API_URL in your Vercel environment variables
 */

const BASE_URL = import.meta.env.VITE_API_URL || "";

/**
 * Send a message to the chatbot.
 * Returns { response, intent, confidence, link, rag_used }
 */
export async function sendMessage(message) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ message }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${res.status}`);
  }

  return res.json();
}

/**
 * Get the top queried topics for the analytics dashboard.
 * Returns { top_topics: [{intent, count}] }
 */
export async function getStats() {
  const res = await fetch(`${BASE_URL}/stats`);
  if (!res.ok) throw new Error("Failed to load stats");
  return res.json();
}

/**
 * Check if the backend is running.
 * Returns { status, version, rag_enabled, vector_db, resources }
 */
export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/`);
  if (!res.ok) throw new Error("Backend offline");
  return res.json();
}
