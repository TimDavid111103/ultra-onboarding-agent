import ResumeUpload from '@/components/ResumeUpload'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-black flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-2xl text-center mb-10">
        <div className="inline-flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-full px-4 py-1.5 mb-6">
          <span className="h-1.5 w-1.5 rounded-full bg-[#8b7aaa] animate-pulse" />
          <span className="text-[#8b7aaa] text-xs font-medium tracking-wide uppercase">Ultra Onboarding</span>
        </div>

        <h1 className="font-serif text-4xl sm:text-5xl font-bold text-white leading-tight">
          Tell us who you are,<br />
          <span className="text-[#9d8fc0]">beyond the résumé.</span>
        </h1>

        <p className="mt-4 text-zinc-400 text-lg max-w-lg mx-auto">
          Upload your resume and our AI counselor will ask a few deeper questions to build
          a profile that actually gets you the right opportunities.
        </p>

      </div>

      <ResumeUpload />

      <p className="mt-8 text-zinc-700 text-xs">
        Your data is used only to generate your profile and is never shared.
      </p>
    </main>
  )
}
