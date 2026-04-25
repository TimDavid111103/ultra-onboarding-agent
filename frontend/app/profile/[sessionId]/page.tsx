import { redirect } from 'next/navigation'
import ProfileDisplay from '@/components/ProfileDisplay'

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8000'

async function getProfile(sessionId: string) {
  const res = await fetch(`${BACKEND}/api/session/${sessionId}/profile`, {
    cache: 'no-store',
  })
  if (!res.ok) return null
  return res.json()
}

export default async function ProfilePage({
  params,
}: {
  params: Promise<{ sessionId: string }>
}) {
  const { sessionId } = await params

  const profile = await getProfile(sessionId)
  if (!profile) redirect('/')

  return <ProfileDisplay profile={profile} />
}
