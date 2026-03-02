export default function ChatWindow({ messages, loading }) {
  return (
    <div className="h-[65vh] overflow-y-auto rounded-xl border border-slate-700 bg-slate-900 p-4">
      {messages.map((m, idx) => (
        <div key={idx} className={`mb-3 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
          <span className={`inline-block rounded-lg px-3 py-2 ${m.role === 'user' ? 'bg-indigo-600' : 'bg-slate-700'}`}>
            {m.content}
          </span>
        </div>
      ))}
      {loading && <p className="text-sm text-slate-400">Assistant is typing...</p>}
    </div>
  )
}
