export default function Header({ ragEnabled, onStats }) {
    return (
        <header style={{
            padding: "16px 20px",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            background: "rgba(10,14,26,0.95)",
        }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <div style={{
                    width: 44, height: 44,
                    background: "linear-gradient(135deg,#006633,#004d26)",
                    borderRadius: 12, display: "flex",
                    alignItems: "center", justifyContent: "center", fontSize: 22
                }}>🎓</div>
                <div>
                    <div style={{ fontWeight: 600, fontSize: 15 }}>GMU Resource Assistant</div>
                    <div style={{ fontSize: 11, color: "var(--muted)" }}>George Mason University · AI Chatbot</div>
                </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                {ragEnabled && (
                    <span style={{
                        fontSize: 10, padding: "3px 9px", borderRadius: 20,
                        background: "rgba(0,102,51,0.15)",
                        border: "1px solid rgba(0,102,51,0.4)", color: "#4ade80"
                    }}>RAG ✦</span>
                )}
                <button onClick={onStats} style={{
                    background: "var(--surface2)", border: "1px solid var(--border)",
                    color: "var(--muted)", padding: "7px 14px",
                    borderRadius: 8, fontSize: 12, cursor: "pointer"
                }}>📊 Stats</button>
            </div>
        </header>
    )
}