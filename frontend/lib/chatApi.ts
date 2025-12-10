// frontend/lib/chatApi.ts
const BASE_URL = "http://localhost:8000"

export type ChatSession = {
  id: number
  title: string
  created_at?: string
  updated_at?: string
  preview?: string
}

export type ChatMessageDTO = {
  id: number
  role: "user" | "assistant"
  content: string
  created_at?: string
}

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  }
}

export async function listChatSessions(token: string): Promise<ChatSession[]> {
  const res = await fetch(`${BASE_URL}/chat/sessions`, {
    headers: authHeaders(token),
  })
  if (!res.ok) return []
  return res.json()
}

export async function getChatSession(
  sessionId: number,
  token: string
): Promise<{ id: number; title: string; messages: ChatMessageDTO[] } | null> {
  const res = await fetch(`${BASE_URL}/chat/sessions/${sessionId}`, {
    headers: authHeaders(token),
  })
  if (!res.ok) return null
  return res.json()
}

export async function createChatSession(
  token: string,
  title?: string | null
): Promise<ChatSession | null> {
  const res = await fetch(`${BASE_URL}/chat/session`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ title: title ?? null }),
  })
  if (!res.ok) return null
  const data = await res.json()
  return { id: data.id, title: data.title }
}

export async function sendChatMessage(
  token: string,
  question: string,
  sessionId?: number | null
): Promise<{ answer: string; session_id: number } | null> {
  const res = await fetch(`${BASE_URL}/chat/query`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({
      question,
      session_id: sessionId ?? null,
    }),
  })
  if (!res.ok) return null
  return res.json()
}