import { useMemo, useState } from 'react'
import ChatWindow from './components/ChatWindow'
import Composer from './components/Composer'
import { streamChat } from './lib/api'

export default function App() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dark, setDark] = useState(true)
  const sessionId = useMemo(() => crypto.randomUUID(), [])

  const handleSend = async (text) => {
    setError('')
    setLoading(true)
    setMessages((prev) => [...prev, { role: 'user', content: text }, { role: 'assistant', content: '' }])

    try {
      await streamChat(sessionId, text, (chunk) => {
        setMessages((prev) => {
          const next = [...prev]
          next[next.length - 1] = {
            ...next[next.length - 1],
            content: next[next.length - 1].content + chunk
          }
          return next
        })
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={dark ? 'dark' : ''}>
      <main className="min-h-screen bg-slate-100 p-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
        <div className="mx-auto max-w-3xl">
          <div className="mb-4 flex items-center justify-between">
            <h1 className="text-2xl font-bold">AI Customer Support Assistant</h1>
            <button onClick={() => setDark((d) => !d)} className="rounded-lg border px-3 py-1">
              {dark ? 'Light' : 'Dark'} Mode
            </button>
          </div>
          <ChatWindow messages={messages} loading={loading} />
          <Composer onSend={handleSend} disabled={loading} />
          {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
        </div>
      </main>
    </div>
  )
}
