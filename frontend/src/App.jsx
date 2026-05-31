import { useState, useEffect, useRef, useCallback } from "react";
import { sendMessage, getStats, checkHealth } from "./api.js";

/* ── Styles ────────────────────────────────────────────────────────────── */
const S = {
  app: {
    display: "flex", flexDirection: "column",
    height: "100dvh", maxWidth: 860, margin: "0 auto", width: "100%",
    position: "relative",
  },

  /* Header */
  header: {
    padding: "16px 20px", borderBottom: "1px solid var(--border)",
    display: "flex", alignItems: "center", justifyContent: "space-between",
    background: "rgba(10,14,26,0.95)", backdropFilter: "blur(12px)",
    flexShrink: 0,
  },
  headerLeft:  { display: "flex", alignItems: "center", gap: 14 },
  logo: {
    width: 44, height: 44,
    background: "linear-gradient(135deg,#006633,#004d26)",
    borderRadius: 12, display: "flex", alignItems: "center",
    justifyContent: "center", fontSize: 22,
    boxShadow: "0 0 20px rgba(0,102,51,0.4)",
  },
  headerTitle: { fontWeight: 600, fontSize: 15, letterSpacing: "0.01em" },
  headerSub:   { fontSize: 11, color: "var(--muted)", marginTop: 2 },
  headerRight: { display: "flex", alignItems: "center", gap: 12 },
  onlineDot: {
    width: 8, height: 8, borderRadius: "50%",
    background: "#22c55e", boxShadow: "0 0 8px #22c55e",
    animation: "pulse 2s infinite",
  },
  ragBadge: {
    fontSize: 10, padding: "3px 9px", borderRadius: 20,
    background: "rgba(0,102,51,0.15)", border: "1px solid rgba(0,102,51,0.4)",
    color: "#4ade80", fontFamily: "monospace",
  },
  statsBtn: {
    background: "var(--surface2)", border: "1px solid var(--border)",
    color: "var(--muted)", padding: "7px 14px", borderRadius: 8,
    fontSize: 12, cursor: "pointer", transition: "all 0.2s",
  },

  /* Chat area */
  chatArea: {
    flex: 1, overflowY: "auto", padding: "24px 20px",
    display: "flex", flexDirection: "column", gap: 16,
  },

  /* Welcome */
  welcome: {
    display: "flex", flexDirection: "column",
    alignItems: "center", textAlign: "center",
    gap: 20, padding: "40px 20px", flex: 1,
  },
  welcomeIcon: {
    width: 72, height: 72,
    background: "linear-gradient(135deg,#006633,#004d26)",
    borderRadius: 20, display: "flex", alignItems: "center",
    justifyContent: "center", fontSize: 32,
    boxShadow: "0 0 40px rgba(0,102,51,0.35)",
  },
  welcomeTitle: { fontSize: 22, fontWeight: 600, letterSpacing: "-0.01em" },
  welcomeSub:   { fontSize: 14, color: "var(--muted)", maxWidth: 400, lineHeight: 1.6 },
  chips:        { display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center", maxWidth: 520 },
  chip: {
    padding: "8px 16px", background: "var(--surface2)",
    border: "1px solid var(--border)", borderRadius: 20,
    fontSize: 13, color: "var(--muted)", cursor: "pointer",
    transition: "all 0.2s", fontFamily: "inherit",
  },

  /* Messages */
  message: { display: "flex", gap: 10, animation: "fadeIn 0.25s ease" },
  avatar: {
    width: 32, height: 32, borderRadius: 10, flexShrink: 0,
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: 14, marginTop: 2,
    background: "linear-gradient(135deg,#006633,#004d26)",
  },
  avatarUser: { background: "var(--surface2)", border: "1px solid var(--border)" },
  bubble: {
    maxWidth: "78%", padding: "12px 16px",
    borderRadius: "var(--radius)", fontSize: 14,
    lineHeight: 1.65, wordBreak: "break-word",
  },
  bubbleBot: {
    background: "var(--surface)", border: "1px solid var(--border)",
    borderTopLeftRadius: 4,
  },
  bubbleUser: {
    background: "var(--accent)", color: "#fff",
    borderTopRightRadius: 4,
  },
  linkCard: {
    display: "flex", alignItems: "center", gap: 6,
    marginTop: 10, padding: "8px 14px",
    background: "rgba(0,102,51,0.15)", border: "1px solid rgba(0,102,51,0.4)",
    borderRadius: 8, color: "#4ade80", textDecoration: "none",
    fontSize: 13, wordBreak: "break-all", transition: "all 0.2s",
  },
  ragLabel: {
    display: "inline-block", marginTop: 6,
    fontSize: 10, padding: "2px 8px",
    background: "rgba(0,102,51,0.1)", border: "1px solid rgba(0,102,51,0.3)",
    borderRadius: 20, color: "#4ade80", fontFamily: "monospace",
  },
  confBadge: {
    display: "inline-block", marginTop: 6, marginLeft: 6,
    fontSize: 10, padding: "2px 8px",
    background: "rgba(255,204,0,0.1)", border: "1px solid rgba(255,204,0,0.3)",
    borderRadius: 20, color: "var(--accent2)", fontFamily: "monospace",
  },
  timestamp: { fontSize: 10, color: "var(--muted)", marginTop: 4, padding: "0 4px" },

  /* Typing */
  typingDots: {
    background: "var(--surface)", border: "1px solid var(--border)",
    borderRadius: "var(--radius)", borderTopLeftRadius: 4,
    padding: "14px 18px", display: "flex", gap: 5, alignItems: "center",
  },
  dot: {
    width: 6, height: 6, background: "var(--muted)",
    borderRadius: "50%", animation: "bounce 1.2s infinite",
  },

  /* Input */
  inputArea: {
    padding: "14px 20px 20px", borderTop: "1px solid var(--border)",
    background: "rgba(10,14,26,0.95)", backdropFilter: "blur(12px)",
    flexShrink: 0,
  },
  inputRow: {
    display: "flex", gap: 10, alignItems: "flex-end",
    background: "var(--surface)", border: "1px solid var(--border)",
    borderRadius: "var(--radius)", padding: "10px 10px 10px 16px",
    transition: "border-color 0.2s",
  },
  textarea: {
    flex: 1, background: "transparent", border: "none",
    outline: "none", color: "var(--text)", fontSize: 14,
    resize: "none", maxHeight: 120, minHeight: 24,
    lineHeight: 1.5, fontFamily: "inherit",
  },
  sendBtn: {
    width: 36, height: 36, background: "var(--accent)", border: "none",
    borderRadius: 10, cursor: "pointer", color: "white", fontSize: 16,
    display: "flex", alignItems: "center", justifyContent: "center",
    transition: "all 0.2s", flexShrink: 0,
  },
  charCount: { fontSize: 11, color: "var(--muted)", marginTop: 6, textAlign: "right", fontFamily: "monospace" },

  /* Stats modal */
  overlay: {
    position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)",
    backdropFilter: "blur(4px)", zIndex: 100,
    display: "flex", alignItems: "center", justifyContent: "center",
  },
  modal: {
    background: "var(--surface)", border: "1px solid var(--border)",
    borderRadius: 16, padding: 28, width: 380, maxWidth: "90vw",
  },
  modalTitle: { fontSize: 15, fontWeight: 600, marginBottom: 20 },
  statRow:    { display: "flex", alignItems: "center", gap: 10, marginBottom: 12 },
  statLabel:  { fontSize: 12, color: "var(--muted)", width: 150, flexShrink: 0, textTransform: "capitalize" },
  barWrap:    { flex: 1, background: "var(--bg)", borderRadius: 4, height: 6, overflow: "hidden" },
  bar:        { height: "100%", background: "var(--accent)", borderRadius: 4, transition: "width 0.6s" },
  statCount:  { fontSize: 11, color: "var(--muted)", width: 24, textAlign: "right", fontFamily: "monospace" },
  closeBtn: {
    marginTop: 20, width: "100%", background: "var(--surface2)",
    border: "1px solid var(--border)", color: "var(--text)",
    padding: 10, borderRadius: 8, cursor: "pointer",
    fontSize: 13, fontFamily: "inherit",
  },
};

/* ── Quick suggestion chips ─────────────────────────────────────────────── */
const CHIPS = [
  "📄 How do I get my transcript?",
  "💰 How do I apply for financial aid?",
  "🏠 How do I apply for campus housing?",
  "💼 Where is the career center?",
  "📚 What are the library hours?",
  "🧠 I need mental health support",
  "🅿️ How do I get a parking permit?",
  "📅 When does the semester end?",
];

/* ── Helper: format message text (basic markdown-like) ──────────────────── */
function MessageText({ text }) {
  const formatted = text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>");
  return <span dangerouslySetInnerHTML={{ __html: formatted }} />;
}

/* ── Main App ────────────────────────────────────────────────────────────── */
export default function App() {
  const [messages,    setMessages]    = useState([]);
  const [input,       setInput]       = useState("");
  const [typing,      setTyping]      = useState(false);
  const [showStats,   setShowStats]   = useState(false);
  const [stats,       setStats]       = useState([]);
  const [ragEnabled,  setRagEnabled]  = useState(false);
  const [charCount,   setCharCount]   = useState(0);
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  /* Auto-scroll to bottom when messages change */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  /* Check server health and send greeting on load */
  useEffect(() => {
    checkHealth()
      .then(h => setRagEnabled(h.rag_enabled))
      .catch(() => {});
    doSend("hello");
  }, []);

  /* Add a message bubble to the chat */
  const addMessage = useCallback((role, data) => {
    setMessages(prev => [...prev, {
      role,
      text:       typeof data === "string" ? data : data.response,
      link:       typeof data === "object" ? data.link       : null,
      confidence: typeof data === "object" ? data.confidence : null,
      ragUsed:    typeof data === "object" ? data.rag_used   : false,
      time:       new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }]);
  }, []);

  /* Core send function */
  const doSend = useCallback(async (text) => {
    const msg = (text || input).trim();
    if (!msg || typing) return;

    if (!text) {
      addMessage("user", msg);
      setInput("");
      setCharCount(0);
    }

    setTyping(true);

    try {
      const data = await sendMessage(msg);
      addMessage("bot", data);
    } catch (err) {
      addMessage("bot", `⚠️ ${err.message || "Connection error. Is the server running?"}`);
    }

    setTyping(false);
    inputRef.current?.focus();
  }, [input, typing, addMessage]);

  /* Handle keyboard in textarea */
  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      doSend();
    }
  };

  /* Handle input change */
  const handleInput = (e) => {
    const val = e.target.value;
    setInput(val);
    setCharCount(val.length);
    // Auto-resize
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  /* Send a chip suggestion */
  const sendChip = (chip) => {
    const text = chip.replace(/^[^\w]+/, "").trim();
    doSend(text);
  };

  /* Load and show stats */
  const handleStats = async () => {
    try {
      const data = await getStats();
      setStats(data.top_topics || []);
    } catch {
      setStats([]);
    }
    setShowStats(true);
  };

  const hasMessages = messages.length > 0;

  return (
    <div style={S.app}>

      {/* ── Header ── */}
      <header style={S.header}>
        <div style={S.headerLeft}>
          <div style={S.logo}>🎓</div>
          <div>
            <div style={S.headerTitle}>GMU Resource Assistant</div>
            <div style={S.headerSub}>George Mason University · AI Chatbot</div>
          </div>
        </div>
        <div style={S.headerRight}>
          {ragEnabled && <span style={S.ragBadge}>RAG ✦</span>}
          <button style={S.statsBtn} onClick={handleStats}>📊 Stats</button>
          <div style={S.onlineDot} title="Online" />
        </div>
      </header>

      {/* ── Chat area ── */}
      <div style={S.chatArea}>

        {/* Welcome screen — shown before first message */}
        {!hasMessages && (
          <div style={S.welcome}>
            <div style={S.welcomeIcon}>🏛️</div>
            <h2 style={S.welcomeTitle}>How can I help you today?</h2>
            <p style={S.welcomeSub}>
              Ask me anything about GMU resources — transcripts, financial aid,
              housing, health services, career support, and more.
              {ragEnabled && " Powered by RAG with real GMU website content."}
            </p>
            <div style={S.chips}>
              {CHIPS.map(chip => (
                <button
                  key={chip}
                  style={S.chip}
                  onClick={() => sendChip(chip)}
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message bubbles */}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...S.message,
              flexDirection: msg.role === "user" ? "row-reverse" : "row",
            }}
          >
            {/* Avatar */}
            <div style={{
              ...S.avatar,
              ...(msg.role === "user" ? S.avatarUser : {}),
            }}>
              {msg.role === "bot" ? "🤖" : "👤"}
            </div>

            {/* Bubble + metadata */}
            <div style={{ maxWidth: "78%" }}>
              <div style={{
                ...S.bubble,
                ...(msg.role === "bot" ? S.bubbleBot : S.bubbleUser),
              }}>
                <MessageText text={msg.text} />

                {/* Clickable link card */}
                {msg.link && (
                  <a
                    href={msg.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={S.linkCard}
                  >
                    🔗 {msg.link}
                  </a>
                )}

                {/* RAG badge */}
                {msg.ragUsed && (
                  <span style={S.ragLabel}>✦ RAG</span>
                )}

                {/* Low confidence warning */}
                {msg.confidence !== null && msg.confidence < 80 && msg.confidence > 0 && (
                  <span style={S.confBadge}>
                    {msg.confidence}% confident
                  </span>
                )}
              </div>

              {/* Timestamp */}
              <div style={{
                ...S.timestamp,
                textAlign: msg.role === "user" ? "right" : "left",
              }}>
                {msg.time}
              </div>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {typing && (
          <div style={{ ...S.message, flexDirection: "row" }}>
            <div style={S.avatar}>🤖</div>
            <div style={S.typingDots}>
              <span style={S.dot} />
              <span style={{ ...S.dot, animationDelay: "0.2s" }} />
              <span style={{ ...S.dot, animationDelay: "0.4s" }} />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── Input area ── */}
      <div style={S.inputArea}>
        <div style={S.inputRow}>
          <textarea
            ref={inputRef}
            style={S.textarea}
            value={input}
            rows={1}
            maxLength={300}
            placeholder="Ask about any GMU resource…"
            onChange={handleInput}
            onKeyDown={handleKey}
          />
          <button
            style={{
              ...S.sendBtn,
              ...(typing ? { background: "var(--surface2)", cursor: "not-allowed" } : {}),
            }}
            onClick={() => doSend()}
            disabled={typing}
            title="Send"
          >
            ➤
          </button>
        </div>
        <div style={{
          ...S.charCount,
          color: charCount > 250 ? "var(--accent2)" : "var(--muted)",
        }}>
          {charCount} / 300
        </div>
      </div>

      {/* ── Stats modal ── */}
      {showStats && (
        <div style={S.overlay} onClick={() => setShowStats(false)}>
          <div style={S.modal} onClick={e => e.stopPropagation()}>
            <div style={S.modalTitle}>📊 Most Queried Topics</div>

            {stats.length === 0 ? (
              <p style={{ color: "var(--muted)", fontSize: 13 }}>
                No queries recorded yet — start chatting!
              </p>
            ) : (
              stats.map((s, i) => (
                <div key={i} style={S.statRow}>
                  <span style={S.statLabel}>{s.intent}</span>
                  <div style={S.barWrap}>
                    <div style={{
                      ...S.bar,
                      width: `${(s.count / stats[0].count) * 100}%`,
                    }} />
                  </div>
                  <span style={S.statCount}>{s.count}</span>
                </div>
              ))
            )}

            <button style={S.closeBtn} onClick={() => setShowStats(false)}>
              Close
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
