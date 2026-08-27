import { useRef } from "react"

export default function ChatInput({ input, onChange, onSend, onKey, charCount }) {
    const inputRef = useRef(null)
    return (
        <div style={{
            padding: "14px 20px 20px",
            borderTop: "1px solid var(--border)",
            background: "rgba(10,14,26,0.95)",
            flexShrink: 0
        }}>
            <div style={{
                display: "flex", gap: 10, alignItems: "flex-end",
                background: "var(--surface)",
                border: "1px solid var(--border)",
                borderRadius: 14, padding: "10px 10px 10px 16px"
            }}>
                <textarea
                    ref={inputRef}
                    style={{
                        flex: 1, background: "transparent",
                        border: "none", outline: "none",
                        color: "var(--text)", fontSize: 14,
                        resize: "none", maxHeight: 120,
                        minHeight: 24, lineHeight: 1.5,
                        fontFamily: "inherit"
                    }}
                    value={input}
                    rows={1}
                    maxLength={300}
                    placeholder="Ask about any GMU resource…"
                    onChange={onChange}
                    onKeyDown={onKey}
                />
                <button
                    style={{
                        width: 36, height: 36,
                        background: "var(--accent)",
                        border: "none", borderRadius: 10,
                        cursor: "pointer", color: "white",
                        fontSize: 16, display: "flex",
                        alignItems: "center", justifyContent: "center",
                        flexShrink: 0
                    }}
                    onClick={onSend}
                >➤</button>
            </div>
            <div style={{
                fontSize: 11, marginTop: 6, textAlign: "right",
                fontFamily: "monospace",
                color: charCount > 250 ? "#EF9F27" : "var(--muted)"
            }}>
                {charCount} / 300
            </div>
        </div>
    )
}