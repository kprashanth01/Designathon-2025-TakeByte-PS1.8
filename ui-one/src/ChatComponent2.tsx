"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import axios from "axios"
import { Send, Sparkles, Clock, RefreshCw } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface ChatComponentProps {
  setRecentSearches: React.Dispatch<React.SetStateAction<string[]>>
  recentSearches: string[]
}

export function ChatComponent2({ setRecentSearches, recentSearches }: ChatComponentProps) {
  const [messages, setMessages] = useState<{ text: string; sender: "user" | "checker"; timestamp: Date }[]>([])
  const [inputValue, setInputValue] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (inputValue.trim()) {
      // Add user message to chat
      setMessages((prev) => [...prev, { text: inputValue, sender: "user", timestamp: new Date() }])
      setRecentSearches((prev) => [inputValue, ...prev.slice(0, 4)]) // Keep only 5 recent searches
      setInputValue("") // Clear the input after submission
      setLoading(true) // Start loading

      try {
        // Send the input value to the backend
        const response = await axios.post("http://localhost:5000/api/analyze", { claim: inputValue })
        const checkerResponse = response.data.analysis // Get the analysis from the response

        // Simulate a slight delay for a more natural conversation flow
        setTimeout(() => {
          setMessages((prev) => [...prev, { text: checkerResponse, sender: "checker", timestamp: new Date() }])
          setLoading(false)
        }, 500)
      } catch (error) {
        console.error("Error sending message to backend:", error)
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            {
              text: "Sorry, I couldn't process your request. Please try again later.",
              sender: "checker",
              timestamp: new Date(),
            },
          ])
          setLoading(false)
        }, 500)
      }
    }
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  const formatResponse = (response: string) => {
    return response.split("\n").map((line, index) => (
      <div key={index} className="whitespace-pre-wrap">
        {line}
      </div>
    ))
  }

  return (
    <div className="relative w-full max-w-4xl mx-auto rounded-xl overflow-hidden backdrop-blur-sm bg-gradient-to-br from-indigo-900/80 via-purple-900/80 to-violet-900/80 border border-indigo-500/30 shadow-[0_0_15px_rgba(139,92,246,0.5)]">
      {/* Chat header */}
      <div className="flex items-center justify-between p-4 border-b border-indigo-500/30 bg-black/20">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-full border-2 border-indigo-400 p-0.5 bg-indigo-900 flex items-center justify-center text-white overflow-hidden">
          <img 
  src="https://www.shutterstock.com/shutterstock/photos/2226702899/display_1500/stock-vector-fact-check-concept-of-thorough-fact-checking-or-easy-compare-evidence-vector-stock-illustration-2226702899.jpg" 
  alt="AI Assistant" 
  className="w-full h-full object-cover rounded-lg" 
/>
          </div>
          <div>
            <h2 className="text-xl font-bold bg-clip-text">
              FACT CHECK
            </h2>
            <div className="flex items-center space-x-2">
              <span className="flex items-center">
                <span className="relative flex h-2 w-2 mr-1">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-xs text-emerald-300">Online</span>
              </span>
              <span className="text-xs bg-indigo-800/40 text-indigo-200 border border-indigo-500/50 px-2 py-0.5 rounded-full flex items-center">
                <Sparkles className="h-3 w-3 mr-1" /> Advanced
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Chat messages */}
      <div className="p-4 h-[60vh] overflow-y-auto bg-gradient-to-b from-black/10 to-black/30 backdrop-blur-sm scrollbar-thin scrollbar-thumb-indigo-600 scrollbar-track-indigo-900/20">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full text-center"
            >
              <div className="w-20 h-20 mb-4 rounded-full bg-indigo-600/20 flex items-center justify-center">
                <Sparkles className="h-10 w-10 text-indigo-300" />
              </div>
              <h3 className="text-xl font-semibold text-indigo-200 mb-2">Welcome to CHECKER AI</h3>
              <p className="text-indigo-300/80 max-w-md">
                Ask me to verify any claim or information, and I'll analyze it for accuracy.
              </p>
            </motion.div>
          )}

          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} mb-4`}
            >
              <div className={`flex flex-col max-w-[80%] ${msg.sender === "user" ? "items-end" : "items-start"}`}>
                <div
                  className={`flex items-center mb-1 text-xs ${msg.sender === "user" ? "text-indigo-200" : "text-cyan-200"}`}
                >
                  {msg.sender === "user" ? "You" : "CHECKER AI"}
                  <Clock className="h-3 w-3 mx-1" />
                  {formatTimestamp(msg.timestamp)}
                </div>
                <div
                  className={`p-3 rounded-2xl ${
                    msg.sender === "user"
                      ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-tr-none shadow-[0_0_10px_rgba(139,92,246,0.3)]"
                      : "bg-gradient-to-r from-gray-900/90 to-indigo-900/90 text-gray-100 rounded-tl-none border border-indigo-500/30 shadow-[0_0_10px_rgba(99,102,241,0.2)]"
                  }`}
                >
                  {msg.sender === "checker" ? formatResponse(msg.text) : msg.text}
                </div>
              </div>
            </motion.div>
          ))}

          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start mb-4"
            >
              <div className="flex flex-col max-w-[80%] items-start">
                <div className="flex items-center mb-1 text-xs text-cyan-200">
                  CHECKER AI <Clock className="h-3 w-3 mx-1" /> now
                </div>
                <div className="p-3 rounded-2xl bg-gradient-to-r from-gray-900/90 to-indigo-900/90 text-gray-100 rounded-tl-none border border-indigo-500/30">
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="h-4 w-4 animate-spin text-indigo-300" />
                    <span>Analyzing your request...</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </AnimatePresence>
      </div>

      {/* Chat input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-indigo-500/30 bg-black/20">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me to verify something..."
            className="flex-1 bg-indigo-950/50 border border-indigo-500/50 rounded-md px-3 py-2 text-white placeholder-indigo-300/50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !inputValue.trim()}
            className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white px-4 py-2 rounded-md flex items-center transition-all duration-300 shadow-[0_0_15px_rgba(99,102,241,0.5)] hover:shadow-[0_0_20px_rgba(139,92,246,0.6)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4 mr-1" />
            Send
          </button>
        </div>

        {recentSearches.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-xs text-indigo-300/70">Recent:</span>
            {recentSearches.slice(0, 3).map((search, index) => (
              <button
                key={index}
                className="text-xs py-0 h-6 px-2 bg-indigo-900/30 text-indigo-300 hover:bg-indigo-800/50 hover:text-indigo-200 rounded-md"
                onClick={() => setInputValue(search)}
              >
                {search.length > 20 ? `${search.substring(0, 20)}...` : search}
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  )
}

