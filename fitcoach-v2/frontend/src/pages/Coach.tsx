import { useState } from 'react'
import { askAgent } from '../services/api'
import { Send } from 'lucide-react'

interface Message {
  role: 'user' | 'coach'
  content: string
  tips?: string[]
}

export default function Coach() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'coach', content: 'Salut ! Je suis ton coach IA. Pose-moi tes questions sur l\'entraînement, la nutrition, ou demande-moi des conseils. 💪', tips: [] },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const result = await askAgent(userMsg, 'user1', { agent: 'coach' })
      const response = result.response
      setMessages(prev => [...prev, {
        role: 'coach',
        content: response.message || 'Je suis là pour t\'aider !',
        tips: response.tips || [],
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'coach',
        content: 'Désolé, je rencontre un problème technique. Réessaie dans un instant.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="pb-20 md:pb-0 flex flex-col h-[calc(100vh-140px)]">
      <h1 className="text-2xl font-bold mb-4">🤖 Coach IA</h1>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-xl px-4 py-3 ${
              msg.role === 'user'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-800 border border-gray-700'
            }`}>
              <p className="text-sm">{msg.content}</p>
              {msg.tips && msg.tips.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {msg.tips.map((tip, j) => (
                    <li key={j} className="text-xs text-gray-300 flex items-start space-x-1">
                      <span>💡</span><span>{tip}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-3">
              <span className="text-sm text-gray-400 animate-pulse">Le coach réfléchit...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Posez votre question au coach..."
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="px-4 py-2.5 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 rounded-lg transition-colors"
          aria-label="Envoyer"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}
