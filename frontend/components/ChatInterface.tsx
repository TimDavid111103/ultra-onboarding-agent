'use client'

import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useRef, useState } from 'react'

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'

type Message = {
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
}


export default function ChatInterface({ sessionId }: { sessionId: string }) {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [isSynthesizing, setIsSynthesizing] = useState(false)
  const [coverage, setCoverage] = useState<Record<string, number>>({})
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const [initialized, setInitialized] = useState(false)
  useEffect(() => {
    if (!initialized) {
      setInitialized(true)
      sendMessage("Hello! I'm ready to get started.")
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isStreaming) return
      setInput('')

      const userMsg: Message = { role: 'user', content: text }
      setMessages((prev) => [...prev, userMsg])
      setIsStreaming(true)

      setMessages((prev) => [...prev, { role: 'assistant', content: '', streaming: true }])

      try {
        const res = await fetch(`${BACKEND}/api/session/${sessionId}/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: text }),
        })

        if (!res.ok || !res.body) {
          throw new Error('Failed to connect to server.')
        }

        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let partialJson = ''
        let finalMessage = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() ?? ''

          for (const line of lines) {
            if (line.startsWith('event: meta')) continue
            if (line.startsWith('event: done')) {
              setIsComplete(true)
              continue
            }

            if (line.startsWith('data: ')) {
              const raw = line.slice(6)

              try {
                const parsed = JSON.parse(raw)
                if (parsed.coverage) {
                  setCoverage(parsed.coverage)
                  finalMessage = parsed.message ?? finalMessage
                  if (parsed.is_complete) setIsComplete(true)
                } else if (parsed.type === 'token' && parsed.chunk !== undefined) {
                  partialJson += parsed.chunk
                  const msgMatch = partialJson.match(/"message"\s*:\s*"((?:[^"\\]|\\.)*)/)
                  if (msgMatch) {
                    const streamed = msgMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"').replace(/\\\\/g, '\\')
                    setMessages((prev) => {
                      const next = [...prev]
                      const last = next[next.length - 1]
                      if (last?.role === 'assistant') {
                        next[next.length - 1] = { ...last, content: streamed, streaming: true }
                      }
                      return next
                    })
                  }
                }
              } catch {
                // not JSON — ignore
              }
            }
          }
        }

        setMessages((prev) => {
          const next = [...prev]
          const last = next[next.length - 1]
          if (last?.role === 'assistant') {
            next[next.length - 1] = { ...last, content: finalMessage || last.content, streaming: false }
          }
          return next
        })
      } catch (e) {
        setMessages((prev) => {
          const next = [...prev]
          const last = next[next.length - 1]
          if (last?.role === 'assistant' && last.streaming) {
            next[next.length - 1] = {
              role: 'assistant',
              content: 'Something went wrong. Please try again.',
              streaming: false,
            }
          }
          return next
        })
      } finally {
        setIsStreaming(false)
      }
    },
    [isStreaming, sessionId],
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const handleGenerateProfile = async () => {
    setIsSynthesizing(true)
    try {
      const res = await fetch(`${BACKEND}/api/session/${sessionId}/synthesize`, {
        method: 'POST',
      })
      if (!res.ok) throw new Error('Synthesis failed.')
      router.push(`/profile/${sessionId}`)
    } catch {
      setIsSynthesizing(false)
      alert('Something went wrong generating your profile. Please try again.')
    }
  }

  return (
    <div className="flex h-screen bg-black">
      {/* Sidebar */}
      <div className="hidden md:flex w-64 flex-col bg-zinc-950 border-r border-zinc-800 p-5 gap-6">
        <div>
          <p className="text-xs font-semibold text-zinc-600 uppercase tracking-wider mb-1">Ultra</p>
          <p className="text-white font-semibold text-sm">Onboarding Interview</p>
        </div>

        {isComplete && (
          <button
            onClick={handleGenerateProfile}
            disabled={isSynthesizing}
            className="mt-auto w-full rounded-xl bg-zinc-700 hover:bg-zinc-600 disabled:opacity-60 disabled:cursor-wait px-4 py-3 text-white font-semibold text-sm transition-colors"
          >
            {isSynthesizing ? 'Building profile…' : 'Generate Profile →'}
          </button>
        )}
      </div>

      {/* Chat area */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Mobile header */}
        <div className="md:hidden flex items-center justify-between bg-zinc-950 border-b border-zinc-800 px-4 py-3">
          <p className="text-white font-semibold text-sm">Ultra Onboarding</p>
          {isComplete && (
            <button
              onClick={handleGenerateProfile}
              disabled={isSynthesizing}
              className="rounded-lg bg-zinc-700 hover:bg-zinc-600 disabled:opacity-60 px-3 py-1.5 text-white font-medium text-xs transition-colors"
            >
              {isSynthesizing ? 'Building…' : 'Generate Profile →'}
            </button>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-5">
          {messages
            .filter((m) => !(m.role === 'user' && m.content === "Hello! I'm ready to get started."))
            .map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="h-7 w-7 rounded-full bg-zinc-700 flex items-center justify-center mr-2 mt-1 shrink-0">
                    <span className="text-white text-xs font-bold">U</span>
                  </div>
                )}
                <div
                  className={[
                    'max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap',
                    msg.role === 'user'
                      ? 'bg-zinc-700 text-white rounded-br-sm'
                      : 'bg-zinc-900 text-zinc-100 rounded-bl-sm',
                  ].join(' ')}
                >
                  {msg.content}
                  {msg.streaming && (
                    <span className="inline-block w-0.5 h-3.5 bg-[#8b7aaa] ml-0.5 animate-pulse align-middle" />
                  )}
                </div>
              </div>
            ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        {!isComplete && (
          <div className="border-t border-zinc-800 bg-zinc-950 px-4 py-3">
            <form onSubmit={handleSubmit} className="flex items-end gap-2">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isStreaming}
                placeholder="Type your answer… (Enter to send, Shift+Enter for new line)"
                rows={1}
                className="flex-1 resize-none rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-100 placeholder-zinc-600 px-4 py-3 text-sm focus:outline-none focus:border-zinc-600 transition-colors disabled:opacity-50 min-h-[48px] max-h-36"
                style={{ height: 'auto' }}
                onInput={(e) => {
                  const el = e.currentTarget
                  el.style.height = 'auto'
                  el.style.height = `${el.scrollHeight}px`
                }}
              />
              <button
                type="submit"
                disabled={isStreaming || !input.trim()}
                className="h-12 w-12 rounded-xl bg-zinc-700 hover:bg-zinc-600 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-colors shrink-0"
              >
                <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </form>
          </div>
        )}

        {isComplete && (
          <div className="border-t border-zinc-800 bg-zinc-950 px-4 py-4 text-center">
            <p className="text-zinc-400 text-sm mb-3">
              The interview is complete! Click below to generate your profile.
            </p>
            <button
              onClick={handleGenerateProfile}
              disabled={isSynthesizing}
              className="rounded-xl bg-zinc-700 hover:bg-zinc-600 disabled:opacity-60 px-6 py-3 text-white font-semibold text-sm transition-colors"
            >
              {isSynthesizing ? 'Building your profile…' : 'Generate My Profile →'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
