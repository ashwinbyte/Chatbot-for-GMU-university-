export default function TypingDots() {
    return (
        <div style={{ display: "flex", gap: 10 }}>
            <div style={{
                width: 32, height: 32, borderRadius: 10,
                display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: 14,
                background: "linear-gradient(135deg,#006633,#004d26)"
            }}>🤖</div>
            <div style={{
                background: "var(--surface)",
                border: "1px solid var(--border)",
                borderRadius: 14, borderTopLeftRadius: 4,
                padding: "14px 18px",
                display: "flex", gap: 5, alignItems: "center"
            }}>
                {[0, 0.2, 0.4].map((delay, i) => (
                    <span key={i} style={{
                        width: 6, height: 6,
                        background: "var(--muted)",
                        borderRadius: "50%",
                        animation: `bounce 1.2s infinite ${delay}s`
                    }}/>
                ))}
            </div>
        </div>
    )
}