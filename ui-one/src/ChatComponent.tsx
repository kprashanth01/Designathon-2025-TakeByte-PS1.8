import React, { useState } from 'react';
import axios from "axios"; // Make sure to install axios
import { MessageLoading } from "@/message-loading"; // Adjust the path as necessary

interface ChatComponentProps {
  setRecentSearches: React.Dispatch<React.SetStateAction<string[]>>; // Define the prop type
  recentSearches: string[]; // Add recent searches as a prop
}

export function ChatComponent({ setRecentSearches, recentSearches }: ChatComponentProps) {
  const [messages, setMessages] = useState<{ text: string; sender: 'user' | 'checker' }[]>([]);
  const [inputValue, setInputValue] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false); // State for loading

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (inputValue.trim()) {
      // Add user message to chat
      setMessages(prev => [...prev, { text: inputValue, sender: 'user' }]);
      setRecentSearches(prev => [...prev, inputValue]); // Update recent searches
      setInputValue(""); // Clear the input after submission
      setLoading(true); // Start loading

      try {
        // Send the input value to the backend
        const response = await axios.post('http://localhost:5000/api/analyze', { claim: inputValue });
        const checkerResponse = response.data.analysis; // Get the analysis from the response
        setMessages(prev => [...prev, { text: checkerResponse, sender: 'checker' }]); // Store raw response
      } catch (error) {
        console.error("Error sending message to backend:", error);
        setMessages(prev => [...prev, { text: "Sorry, I couldn't process your request.", sender: 'checker' }]);
      } finally {
        setLoading(false); // Stop loading
      }
    }
  };

  const formatResponse = (response: string) => {
    return response.split('\n').map((line, index) => (
      <div key={index} className="whitespace-pre-wrap">{line}</div>
    ));
  };

  return (
    <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-4 w-full">
      <h2 className="text-2xl font-bold text-white mb-4">Chat with the CHECKER</h2>
      <div className="mt-4 flex flex-col space-y-2 overflow-y-auto max-h-80">
        {messages.map((msg, index) => (
          <div key={index} className={`p-3 rounded-lg ${msg.sender === 'user' ? 'bg-blue-700 text-white self-end' : 'bg-white text-black self-start shadow-md'}`}>
            {msg.sender === 'checker' ? formatResponse(msg.text) : msg.text} {/* Format only checker responses */}
          </div>
        ))}
        {loading && (
          <div className="flex items-center justify-center p-3">
            <MessageLoading /> {/* Use the MessageLoading component */}
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="flex mt-4 w-full">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
        />
        <button type="submit" className="ml-2 bg-blue-600 text-white rounded-lg px-4 hover:bg-blue-700 transition duration-200">
          Send
        </button>
      </form>
    </div>
  );
}