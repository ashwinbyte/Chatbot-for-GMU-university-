import { useState, useRef }  from "react"
import { useChat }           from "./hooks/useChat"
import { getStats }          from "./services/api"
import Header                from "./components/Header"
import ChatBubble            from "./components/ChatBubble"
import ChatInput             from "./components/ChatInput"
import TypingDots            from "./components/TypingDots"

const CHIPS = [
    "📄 How do I get my transcript?",
    "💰 How do I apply for financial aid?",
    "🏠 How do I apply for campus housing?",
    "💼 Where is the career center?",
    "📚 What are the library hours?",
    "🧠 I need mental health support",
]

export default function App() {
    const {
        messages, input, typing, ragEnabled,
        charCount, bottomRef,
        doSend, handleInput, handleKey
    } = useChat()

    const [showStats, setShowStats] = useState(false)
    const [stats,     setStats]     = useState([])

    const handleStats = async () => {
        try {
            const data = await getStats()
            setStats(data.top_topics || [])
        } catch { setStats([]) }
        setShowStats(true)
    }

    return (
        <div style={{
            display: "flex", flexDirection: "column",
            height: "100dvh", maxWidth: 860,
            margin: "0 auto", width: "100%"
        }}>
            <Header ragEnabled={ragEnabled} onStats={handleStats} />

            <div style={{
                flex: 1, overflowY: "auto",
                padding: "24px 20px", display: "flex",
                flexDirection: "column", gap: 16
            }}>
                {messages.length === 0 && (
                    <div style={{
                        display: "flex", flexDirection: "column",
                        alignItems: "center", textAlign: "center",
                        gap: 20, padding: "40px 20px", flex: 1
                    }}>
                        <div style={{
                            width: 72, height: 72,
                            background: "linear-gradient(135deg,#006633,#004d26)",
                            borderRadius: 20, display: "flex",
                            alignItems: "center", justifyContent: "center", fontSize: 32
                        }}>🏛️</div>
                        <h2 style={{ fontSize: 22, fontWeight: 600 }}>How can I help you today?</h2>
                        <p style={{ fontSize: 14, color: "var(--muted)", maxWidth: 400 }}>
                            Ask me anything about GMU resources in plain English.
                        </p>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
                            {CHIPS.map(chip => (
                                <button key={chip}
                                    style={{
                                        padding: "8px 16px",
                                        background: "var(--surface2)",
                                        border: "1px solid var(--border)",
                                        borderRadius: 20, fontSize: 13,
                                        color: "var(--muted)", cursor: "pointer",
                                        fontFamily: "inherit"
                                    }}
                                    onClick={() => doSend(chip.replace(/^[^\w]+/, "").trim())}
                                >{chip}</button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <ChatBubble key={i} message={msg} />
                ))}

                {typing && <TypingDots />}
                <div ref={bottomRef} />
            </div>

            <ChatInput
                input={input}
                onChange={handleInput}
                onSend={doSend}
                onKey={handleKey}
                charCount={charCount}
            />

            {showStats && (
                <div
                    style={{
                        position: "fixed", inset: 0,
                        background: "rgba(0,0,0,0.7)",
                        backdropFilter: "blur(4px)", zIndex: 100,
                        display: "flex", alignItems: "center", justifyContent: "center"
                    }}
                    onClick={() => setShowStats(false)}
                >
                    <div
                        style={{
                            background: "var(--surface)",
                            border: "1px solid var(--border)",
                            borderRadius: 16, padding: 28,
                            width: 380, maxWidth: "90vw"
                        }}
                        onClick={e => e.stopPropagation()}
                    >
                        <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 20 }}>
                            📊 Most Queried Topics
                        </div>
                        {stats.length === 0 ? (
                            <p style={{ color: "var(--muted)", fontSize: 13 }}>
                                No queries recorded yet.
                            </p>
                        ) : stats.map((s, i) => (
                            <div key={i} style={{
                                display: "flex", alignItems: "center",
                                gap: 10, marginBottom: 12
                            }}>
                                <span style={{
                                    fontSize: 12, color: "var(--muted)",
                                    width: 150, flexShrink: 0, textTransform: "capitalize"
                                }}>{s.intent}</span>
                                <div style={{
                                    flex: 1, background: "var(--bg)",
                                    borderRadius: 4, height: 6, overflow: "hidden"
                                }}>
                                    <div style={{
                                        height: "100%", background: "#006633",
                                        borderRadius: 4,
                                        width: `${(s.count / stats[0].count) * 100}%`
                                    }}/>
                                </div>
                                <span style={{
                                    fontSize: 11, color: "var(--muted)",
                                    width: 24, textAlign: "right"
                                }}>{s.count}</span>
                            </div>
                        ))}
                        <button
                            style={{
                                marginTop: 20, width: "100%",
                                background: "var(--surface2)",
                                border: "1px solid var(--border)",
                                color: "var(--text)", padding: 10,
                                borderRadius: 8, cursor: "pointer",
                                fontSize: 13, fontFamily: "inherit"
                            }}
                            onClick={() => setShowStats(false)}
                        >Close</button>
                    </div>
                </div>
            )}
        </div>
    )
}