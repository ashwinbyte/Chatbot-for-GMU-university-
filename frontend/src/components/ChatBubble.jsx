export default function ChatBubble({ message }) {
    const isUser = message.role === "user"
    return (
        <div style={{
            display: "flex",
            flexDirection: isUser ? "row-reverse" : "row",
            gap: 10,
            animation: "fadeIn 0.25s ease"
        }}>
            <div style={{
                width: 32, height: 32, borderRadius: 10,
                display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: 14,
                background: isUser ? "var(--surface2)" : "linear-gradient(135deg,#006633,#004d26)",
                border: isUser ? "1px solid var(--border)" : "none",
                flexShrink: 0, marginTop: 2
            }}>
                {isUser ? "👤" : "🤖"}
            </div>
            <div style={{ maxWidth: "78%" }}>
                <div style={{
                    padding: "12px 16px", borderRadius: 14, fontSize: 14, lineHeight: 1.65,
                    background: isUser ? "var(--accent)" : "var(--surface)",
                    border: isUser ? "none" : "1px solid var(--border)",
                    color: isUser ? "#fff" : "var(--text)",
                    borderTopRightRadius: isUser ? 4 : 14,
                    borderTopLeftRadius:  isUser ? 14 : 4,
                }}>
                    <span dangerouslySetInnerHTML={{
                        __html: message.text
                            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                            .replace(/\n/g, "<br/>")
                    }}/>
                    {message.link && (
                        <a href={message.link} target="_blank" rel="noopener noreferrer" style={{
                            display: "flex", alignItems: "center", gap: 6,
                            marginTop: 10, padding: "8px 14px",
                            background: "rgba(0,102,51,0.15)",
                            border: "1px solid rgba(0,102,51,0.4)",
                            borderRadius: 8, color: "#4ade80",
                            textDecoration: "none", fontSize: 13
                        }}>
                            🔗 {message.link}
                        </a>
                    )}
                    {message.ragUsed && (
                        <span style={{
                            display: "inline-block", marginTop: 6,
                            fontSize: 10, padding: "2px 8px",
                            background: "rgba(0,102,51,0.1)",
                            border: "1px solid rgba(0,102,51,0.3)",
                            borderRadius: 20, color: "#4ade80"
                        }}>✦ RAG</span>
                    )}
                </div>
                <div style={{
                    fontSize: 10, color: "var(--muted)", marginTop: 4,
                    padding: "0 4px",
                    textAlign: isUser ? "right" : "left"
                }}>
                    {message.time}
                </div>
            </div>
        </div>
    )
}