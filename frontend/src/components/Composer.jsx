import { useState } from 'react'

export default function Composer({ onSend, disabled }) {
  const [value, setValue] = useState('')

  const submit = (e) => {
    e.preventDefault()
    if (!value.trim()) return
    onSend(value)
    setValue('')
  }

  return (
    <form onSubmit={submit} className="mt-4 flex gap-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ask about order status, returns, shipping..."
        className="flex-1 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2"
      />
      <button disabled={disabled} className="rounded-lg bg-indigo-600 px-4 py-2 disabled:opacity-60">Send</button>
    </form>
  )
}
