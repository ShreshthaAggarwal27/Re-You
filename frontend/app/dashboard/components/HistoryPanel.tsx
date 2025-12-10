"use client"

import { History } from "lucide-react"
import type { ChatSession } from "@/lib/chatApi"

type Props = {
  sessions: ChatSession[]
  onOpenSession: (id: number) => void
}

export default function HistoryPanel({ sessions, onOpenSession }: Props) {
  return (
    <div className="h-full p-8 text-sm text-slate-200">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <History className="w-5 h-5 text-slate-400" />
        Recent conversations
      </h2>

      {sessions.length === 0 ? (
        <div className="h-full flex items-center justify-center text-center text-slate-400">
          <div>
            <p className="font-medium mb-2">No conversations yet</p>
            <p className="text-slate-500 mb-4">
              Start a new chat and your conversations will show up here.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map((s) => (
            <button
              key={s.id}
              onClick={() => onOpenSession(s.id)}
              className="w-full text-left px-4 py-3 rounded-lg bg-slate-900/70 border border-slate-800 hover:border-cyan-500/40 hover:bg-slate-900 transition"
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium">{s.title || `Chat #${s.id}`}</span>
                {s.updated_at && (
                  <span className="text-[11px] text-slate-500">
                    {new Date(s.updated_at).toLocaleString()}
                  </span>
                )}
              </div>
              {s.preview && (
                <p className="text-xs text-slate-400 line-clamp-1">{s.preview}</p>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}