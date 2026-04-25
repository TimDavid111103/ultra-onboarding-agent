import { redirect } from 'next/navigation'
import ChatInterface from '@/components/ChatInterface'

export default async function OnboardingPage({
  searchParams,
}: {
  searchParams: Promise<{ session?: string | string[] }>
}) {
  const { session } = await searchParams
  const sessionId = Array.isArray(session) ? session[0] : session

  if (!sessionId) {
    redirect('/')
  }

  return <ChatInterface sessionId={sessionId} />
}
