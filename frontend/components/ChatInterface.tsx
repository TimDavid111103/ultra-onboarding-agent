'use client'

import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useRef, useState } from 'react'

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'

type Message = {
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
}


function cleanContent(text: string): string {
  return text
    .replace(/\*/g, '')
    .replace(/\s*—\s*/g, ' ')
    .replace(/ {2,}/g, ' ')
}

export default function ChatInterface({ sessionId }: { sessionId: string }) {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [isSynthesizing, setIsSynthesizing] = useState(false)
  const [isProfileReady, setIsProfileReady] = useState(false)
  const [coverage, setCoverage] = useState<Record<string, number>>({})
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const streamingLock = useRef(false)

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
      if (!text.trim() || streamingLock.current) return
      streamingLock.current = true
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
        streamingLock.current = false
        setIsStreaming(false)
      }
    },
    [sessionId],
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
      setIsProfileReady(true)
    } catch {
      setIsSynthesizing(false)
      alert('Something went wrong generating your profile. Please try again.')
    }
  }

  return (
    <div className="flex h-screen flex-col bg-[#111111] items-center">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto w-full">
        <div className="max-w-[840px] mx-auto px-6 pt-10 pb-4">
          {(() => {
            const visible = messages.filter(
              (m) => !(m.role === 'user' && m.content === "Hello! I'm ready to get started.")
            )
            const lastStreamingIdx = visible.reduce((idx, m, i) => (m.streaming ? i : idx), -1)
            return visible.map((msg, i) => (
              <div key={i} className={`mb-8 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'user' ? (
                  <div className="max-w-[80%] rounded-3xl bg-zinc-800 px-5 py-3.5 text-[16px] leading-relaxed text-zinc-100 font-[var(--font-sans)]">
                    {msg.content}
                  </div>
                ) : (
                  <div className="w-full text-[19px] leading-[1.35] text-zinc-100 whitespace-pre-wrap" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                    {cleanContent(msg.content)}
                    {i === lastStreamingIdx && (
                      <span className="inline-block w-0.5 h-4 bg-zinc-400 ml-0.5 animate-pulse align-middle" />
                    )}
                  </div>
                )}
              </div>
            ))
          })()}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <div className="w-full max-w-[840px] mx-auto px-6 pb-8 pt-2">
        {isComplete ? (
          <div className="text-center py-4">
            {isProfileReady ? (
              <button
                onClick={() => router.push(`/profile/${sessionId}`)}
                className="rounded-2xl bg-zinc-800 hover:bg-zinc-700 px-7 py-3 text-white font-medium text-sm transition-colors"
              >
                View Profile →
              </button>
            ) : isSynthesizing ? (
              <p className="text-zinc-500 text-sm">Building your profile…</p>
            ) : (
              <>
                <p className="text-zinc-500 text-sm mb-4">
                  The interview is complete. Ready to generate your profile.
                </p>
                <button
                  onClick={handleGenerateProfile}
                  className="rounded-2xl bg-zinc-800 hover:bg-zinc-700 px-7 py-3 text-white font-medium text-sm transition-colors"
                >
                  Generate My Profile →
                </button>
              </>
            )}
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="rounded-2xl bg-zinc-900 border border-zinc-800 overflow-hidden">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isStreaming}
                placeholder="Reply…"
                rows={1}
                className="w-full resize-none bg-transparent text-zinc-100 placeholder-zinc-600 px-4 pt-4 pb-2 text-[15px] focus:outline-none disabled:opacity-50 h-12 overflow-y-auto font-[var(--font-sans)]"
              />
              <div className="flex items-center justify-between px-3 pb-3 pt-1">
                <div className="flex items-center gap-1">
                  {/* + button */}
                  <button
                    type="button"
                    className="h-8 w-8 rounded-full flex items-center justify-center text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 transition-colors"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>
                <button
                  type="submit"
                  disabled={isStreaming || !input.trim()}
                  className="h-8 w-8 rounded-full bg-zinc-700 hover:bg-zinc-600 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
                >
                  <svg className="h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18" />
                  </svg>
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
