'use client'

import { useRouter } from 'next/navigation'
import { useCallback, useRef, useState } from 'react'

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'

export default function ResumeUpload() {
  const router = useRouter()
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [status, setStatus] = useState<'idle' | 'parsing' | 'error'>('idle')
  const [errorMsg, setErrorMsg] = useState('')

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.name.match(/\.(pdf|docx|doc)$/i)) {
        setErrorMsg('Please upload a PDF or DOCX file.')
        setStatus('error')
        return
      }

      setStatus('parsing')
      setErrorMsg('')

      const form = new FormData()
      form.append('file', file)

      try {
        const res = await fetch(`${BACKEND}/api/upload-resume`, {
          method: 'POST',
          body: form,
        })

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Upload failed.' }))
          throw new Error(err.detail ?? 'Upload failed.')
        }

        const data = await res.json()
        router.push(`/onboarding?session=${data.session_id}`)
      } catch (e: unknown) {
        setErrorMsg(e instanceof Error ? e.message : 'Something went wrong.')
        setStatus('error')
      }
    },
    [router],
  )

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div className="w-full max-w-lg mx-auto">
      <div
        onDrop={onDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onClick={() => inputRef.current?.click()}
        className={[
          'relative cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition-all',
          isDragging
            ? 'border-[#8b7aaa] bg-zinc-900'
            : 'border-zinc-700 bg-zinc-900/50 hover:border-zinc-600 hover:bg-zinc-900',
          status === 'parsing' ? 'pointer-events-none opacity-60' : '',
        ].join(' ')}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.doc"
          className="hidden"
          onChange={onInputChange}
        />

        {status === 'parsing' ? (
          <div className="flex flex-col items-center gap-3">
            <div className="h-10 w-10 rounded-full border-2 border-[#8b7aaa] border-t-transparent animate-spin" />
            <p className="text-zinc-300 text-sm">Parsing your resume&hellip;</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="h-14 w-14 rounded-full bg-zinc-800 flex items-center justify-center">
              <svg className="h-7 w-7 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <p className="text-zinc-200 font-medium">Drop your resume here</p>
              <p className="text-zinc-500 text-sm mt-1">or click to browse &mdash; PDF or DOCX</p>
            </div>
          </div>
        )}
      </div>

      {status === 'error' && (
        <p className="mt-3 text-center text-sm text-red-400">{errorMsg}</p>
      )}
    </div>
  )
}
