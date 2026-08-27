

const BASE_URL = import.meta.env.VITE_API_URL || "";


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


export async function getStats() {
  const res = await fetch(`${BASE_URL}/stats`);
  if (!res.ok) throw new Error("Failed to load stats");
  return res.json();
}


export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/`);
  if (!res.ok) throw new Error("Backend offline");
  return res.json();
}
