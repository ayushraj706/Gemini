'use client'
import { useChat } from 'ai/react'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat()
  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      {messages.map(m => (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} 
          key={m.id} className={`mb-4 p-4 rounded-lg ${m.role === 'user' ? 'bg-blue-600' : 'bg-gray-800'}`}>
          <ReactMarkdown>{m.content}</ReactMarkdown>
        </motion.div>
      ))}
      <form onSubmit={handleSubmit} className="fixed bottom-0 w-full max-w-md mb-8">
        <input className="w-full p-2 text-black rounded shadow-xl" value={input}
          placeholder="Gemini se kuch pucho..." onChange={handleInputChange} />
      </form>
    </div>
  )
}
