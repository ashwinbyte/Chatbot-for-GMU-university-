import { useState, useRef, useCallback, useEffect } from "react"
import { sendMessage, checkHealth } from "../services/api"

export function useChat() {
    const [messages,   setMessages]   = useState([])
    const [input,      setInput]      = useState("")
    const [typing,     setTyping]     = useState(false)
    const [ragEnabled, setRagEnabled] = useState(false)
    const [charCount,  setCharCount]  = useState(0)
    const bottomRef     = useRef(null)
    const greetingShown = useRef(false)

    const addMessage = useCallback((role, data) => {
        setMessages(prev => [...prev, {
            role,
            text:     typeof data === "string" ? data : data.response,
            link:     typeof data === "object"  ? data.link     : null,
            ragUsed:  typeof data === "object"  ? data.rag_used : false,
            time:     new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }])
    }, [])

    const doSend = useCallback(async (text) => {
        const msg = (text || input).trim()
        if (!msg || typing) return
        if (!text) {
            addMessage("user", msg)
            setInput("")
            setCharCount(0)
        }
        setTyping(true)
        try {
            const data = await sendMessage(msg)
            addMessage("bot", data)
        } catch (err) {
            addMessage("bot", "Connection error. Please try again.")
        }
        setTyping(false)
    }, [input, typing, addMessage])

    const handleInput = useCallback((e) => {
        const val = e.target.value
        setInput(val)
        setCharCount(val.length)
        e.target.style.height = "auto"
        e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px"
    }, [])

    const handleKey = useCallback((e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            doSend()
        }
    }, [doSend])

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, typing])

    useEffect(() => {
        if (greetingShown.current) return
        greetingShown.current = true
        checkHealth().then(h => setRagEnabled(h.rag_enabled)).catch(() => {})
        addMessage("bot", {
            response: "Hi there! 👋 I am the GMU Resource Assistant. Ask me anything about campus resources — financial aid, housing, health services, careers, transcripts, and more!",
            link: null, rag_used: false
        })
    }, [addMessage])

    return {
        messages, input, typing, ragEnabled,
        charCount, bottomRef,
        doSend, handleInput, handleKey
    }
}