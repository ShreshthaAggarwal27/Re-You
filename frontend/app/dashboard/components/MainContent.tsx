"use client";

import {
  User as UserIcon,
  Send,
  Loader2,
  BookOpen,
  History,
  Plus,
  FolderOpen,
} from "lucide-react";
import MarkdownMessage from "@/components/MarkdownMessage";
import HistoryPanel from "./HistoryPanel";
import type { ChatSession } from "@/lib/chatApi";

type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
};

type Repository = {
  id: number;
  github_repo_id: number;
  name: string;
  full_name: string;
  indexed: boolean;
  last_indexed?: string;
  selected: boolean
};

type TabId = "chat" | "repos" | "history";

interface MainContentProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  messages: Message[];
  input: string;
  setInput: (v: string) => void;
  isSending: boolean;
  handleSend: () => void;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  inputRef: React.RefObject<HTMLInputElement>;
  formatTime: (d?: Date) => string;
  userRepositories: Repository[];
  toggleRepoSelection: (repo: Repository) => void;
  setShowRepoSetup: (show: boolean) => void;
  chatSessions: ChatSession[];
  onOpenSession: (id: number) => void;
}

export default function MainContent({
  activeTab,
  setActiveTab,
  messages,
  input,
  setInput,
  isSending,
  handleSend,
  messagesEndRef,
  inputRef,
  formatTime,
  userRepositories,
  toggleRepoSelection,
  setShowRepoSetup,
  chatSessions,
  onOpenSession,
}: MainContentProps) {
  const sendOnEnter = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 📌 Detect structured markdown messages — tables/code blocks/etc.
  const isRichMarkdown = (msg: string) => {
    return (
      msg.includes("```") ||
      msg.includes("|") ||
      msg.includes("###") ||
      msg.includes("**")
    );
  };

  return (
    <section className="flex-1 flex flex-col bg-gradient-to-b from-black to-slate-950/70">
      {/* Header */}
      <div className="px-8 py-5 border-b border-slate-800/60">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <img
              src="/brain-1.png"
              alt="DevMemory"
              width={36}
              height={36}
              className="rounded-md"
            />
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Your Developer Brain
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Ask questions about your code, across all indexed repositories.
              </p>
            </div>
          </div>

          <div className="flex-1"></div>

          <BookOpen className="w-5 h-5 text-slate-500" />
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        {activeTab === "chat" && (
          <div className="flex flex-col h-full">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
              {messages.length === 0 ? (
                // Empty chat screen
                <div className="h-full flex items-center justify-center text-center">
                  <div className="max-w-lg space-y-4">
                    <img
                      src="/brain-1.png"
                      alt="DevMemory"
                      width={120}
                      height={120}
                      className="mx-auto mb-2"
                    />
                    <h3 className="text-xl font-semibold">
                      Ask anything about your code
                    </h3>
                    <p className="text-slate-400 text-sm">For example:</p>

                    <div className="space-y-2 text-sm">
                      {[
                        "How does login work in my projects?",
                        "Show payment validation logic",
                        "Where do I handle JWT tokens?",
                      ].map((ex) => (
                        <button
                          key={ex}
                          onClick={() => setInput(ex)}
                          className="w-full text-left px-4 py-3 rounded-lg bg-slate-900/70 border border-slate-800 hover:border-cyan-500/40 transition"
                        >
                          "{ex}"
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, idx) => {
                    const rich = isRichMarkdown(msg.content);
                    const isUser = msg.role === "user";

                    return (
                      <div
                        key={idx}
                        className={`flex gap-3 ${
                          isUser ? "flex-row-reverse" : ""
                        }`}
                      >
                        {/* Avatar */}
                        <div
                          className={`w-9 h-9 rounded-full flex items-center justify-center ${
                            isUser
                              ? "bg-gradient-to-br from-cyan-600 to-blue-600"
                              : "bg-slate-900 border border-slate-800"
                          }`}
                        >
                          {isUser ? (
                            <UserIcon className="w-4 h-4" />
                          ) : (
                            <img
                              src="/brain-1.png"
                              width={18}
                              height={18}
                              className="rounded"
                              alt=""
                            />
                          )}
                        </div>

                        {/* Message bubble */}
                        <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} w-full`}>
  {!rich ? (
    // 🌑 Compact bubbles for normal messages
    <div
      className={`
        px-4 py-2 rounded-2xl text-sm leading-relaxed 
        max-w-[70%] w-auto inline-block 
        ${isUser
          ? "bg-gradient-to-r from-cyan-600/20 to-blue-600/20 border border-cyan-500/30 text-white"
          : "bg-slate-900/70 border border-slate-800 text-white"
        }
      `}
    >
      {msg.content}
    </div>
  ) : (
    // 🌕 Rich markdown → full-width centered card
    <div className="w-full flex justify-start">
      <MarkdownMessage content={msg.content} theme="light" />
    </div>
  )}

  {msg.timestamp && (
    <p className="text-[10px] text-slate-500 mt-1 px-1">
      {formatTime(msg.timestamp)}
    </p>
  )}
</div>

                      </div>
                    );
                  })}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Input box */}
            <div className="border-t border-slate-800/60 px-8 py-4 bg-black/90">
              <div className="max-w-3xl mx-auto flex gap-3">
                <input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={sendOnEnter}
                  placeholder='Ask something like: "How is authentication implemented?"'
                  className="flex-1 bg-slate-900/70 border border-slate-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40"
                  disabled={isSending}
                />

                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isSending}
                  className="px-5 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-xs font-medium flex items-center gap-2 hover:from-cyan-400 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {isSending ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Searching…
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Send
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === "repos" && (
          <div className="p-8 space-y-4">
            <h2 className="text-xl font-semibold mb-4">Your Repositories</h2>

            {userRepositories.length === 0 ? (
              <p className="text-slate-400 text-sm">No repositories connected.</p>
            ) : (
              <div className="grid gap-4">
                {userRepositories.map((repo) => (
                  <div
                    key={repo.id}
                    className={`p-4 rounded-xl border transition flex items-center justify-between
                      ${
                        repo.selected
                          ? "border-green-500/60 bg-green-500/5"
                          : "border-slate-800 bg-slate-900/60"
                      }
                    `}
                  >
                    {/* Repo info */}
                    <div>
                      <h3 className="font-medium">{repo.name}</h3>
                      <p className="text-xs text-slate-400">{repo.full_name}</p>

                      <div className="mt-2">
                        {repo.indexed ? (
                          <span className="text-xs text-green-400">Indexed ✅</span>
                        ) : (
                          <span className="text-xs text-yellow-400">
                            Not indexed / Indexing…
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Action button */}
                    <button
                      onClick={() => toggleRepoSelection(repo)}
                      className={`px-4 py-2 text-xs rounded-lg font-medium transition
                        ${
                          repo.selected
                            ? "bg-red-500/10 text-red-400 hover:bg-red-500/20"
                            : "bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20"
                        }
                      `}
                    >
                      {repo.selected ? "Remove" : "Add"}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}


        {activeTab === "history" && (
          <HistoryPanel sessions={chatSessions} onOpenSession={onOpenSession} />
        )}
      </div>
    </section>
  );
}