"use client";

import { useEffect, useState, useRef } from "react";
import Sidebar from "./components/Sidebar";
import MainContent from "./components/MainContent";
import SetupModal from "./components/SetupModal";
import {
  listChatSessions,
  createChatSession,
  sendChatMessage,
  getChatSession,
  type ChatSession,
} from "@/lib/chatApi";

type User = {
  id: number;
  username: string;
  avatar: string;
  needs_setup: boolean;
};

type Repository = {
  id: number;
  github_repo_id: number;
  name: string;
  full_name: string;
  indexed: boolean;
  last_indexed?: string;
  selected: boolean;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
};

type TabId = "chat" | "repos" | "history";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [userRepositories, setUserRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRepoSetup, setShowRepoSetup] = useState(false);

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const [activeTab, setActiveTab] = useState<TabId>("chat");
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // ---- Fetch /me on mount ----
  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("devmemory_token")
        : null;

    if (!token) {
      setError("No session found. Please login again.");
      setLoading(false);
      return;
    }

    (async () => {
      try {
        const res = await fetch("http://localhost:8000/me", {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (res.status === 401) {
          localStorage.removeItem("devmemory_token");
          window.location.href = "/";
          return;
        }

        if (!res.ok) {
          throw new Error(`Failed to load user: HTTP ${res.status}`);
        }

        const data = await res.json();
        setUser(data);
        setError(null);

        if (data.repositories) {
          setUserRepositories(data.repositories);
        }

        if (data.needs_setup) {
          setShowRepoSetup(true);
        }

        // Load chat sessions
        const sessions = await listChatSessions(token);
        setChatSessions(sessions);

        setMessages([
          {
            role: "assistant",
            content: `Welcome, ${data.username}! I'm your DevMemory assistant. Ask me anything about your code.`,
            timestamp: new Date(),
          },
        ]);
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const refreshUserData = async () => {
    const token = localStorage.getItem("devmemory_token");
    if (!token) return;

    try {
      const res = await fetch("http://localhost:8000/me", {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (res.ok) {
        const data = await res.json();
        setUser(data);
        if (data.repositories) {
          setUserRepositories(data.repositories);
        }
      }
    } catch (err) {
      console.error("Failed to refresh user data:", err);
    }
  };

  const hasIndexingInProgress = userRepositories.some(
    (r) => r.selected && !r.indexed
  );

  useEffect(() => {
    if (!hasIndexingInProgress) return;

    const interval = setInterval(() => {
      refreshUserData();
    }, 5000);

    return () => clearInterval(interval);
  }, [hasIndexingInProgress]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Focus input
  useEffect(() => {
    if (!loading && !error) {
      inputRef.current?.focus();
    }
  }, [loading, error]);

  // ---- Send Message ----
  const handleSend = async () => {
    if (!input.trim() || isSending) return;

    const text = input.trim();

    const userMessage: Message = {
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    setInput("");
    setIsSending(true);

    const token = localStorage.getItem("devmemory_token");
    if (!token) {
      setIsSending(false);
      return;
    }

    try {
      const data = await sendChatMessage(token, text, currentSessionId);

      if (!data) throw new Error("Empty backend response");

      if (!currentSessionId && data.session_id) {
        setCurrentSessionId(data.session_id);

        const sessions = await listChatSessions(token);
        setChatSessions(sessions);
      }

      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer || "No answer returned from backend.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);

      const errorMessage: Message = {
        role: "assistant",
        content: "⚠️ Unable to reach backend.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    }

    setIsSending(false);
  };

  // ---- Start New Chat ----
  const startNewChat = () => {
    if (!user) return;

    const token = localStorage.getItem("devmemory_token");
    if (!token) return;

    (async () => {
      try {
        const session = await createChatSession(
          token,
          `Chat with ${user.username}`
        );

        if (session) {
          setCurrentSessionId(session.id);

          const sessions = await listChatSessions(token);
          setChatSessions(sessions);
        }

        setMessages([
          {
            role: "assistant",
            content: `New chat started. What do you want to explore in your code today, ${user.username}?`,
            timestamp: new Date(),
          },
        ]);
      } catch (err) {
        console.error("Failed to create chat session", err);
      }
    })();
  };

  // ---- Open a Chat Session ----
  const openSession = async (sessionId: number) => {
    const token = localStorage.getItem("devmemory_token");
    if (!token) return;

    try {
      const data = await getChatSession(sessionId, token);
      if (!data) return;

      setCurrentSessionId(data.id);

      setMessages(
        data.messages.map((m) => ({
          role: m.role,
          content: m.content,
          timestamp: m.created_at ? new Date(m.created_at) : undefined,
        }))
      );

      setActiveTab("chat");
    } catch (err) {
      console.error("Failed to open session", err);
    }
  };

  const logout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("devmemory_token");
      window.location.href = "/";
    }
  };

  const formatTime = (date?: Date) =>
    date
      ? date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      : "";

  const toggleRepoSelection = async (repo: Repository) => {
    const token = localStorage.getItem("devmemory_token");
    if (!token) return;

    try {
      setUserRepositories((prev) =>
        prev.map((r) =>
          r.id === repo.id ? { ...r, selected: !r.selected } : r
        )
      );

      await fetch("http://localhost:8000/repos/toggle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          repository_id: repo.id,
          selected: !repo.selected,
        }),
      });
    } catch (err) {
      console.error("Failed to toggle repo", err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="relative">
            <div className="absolute w-40 h-40 bg-gradient-to-br from-cyan-400/20 to-blue-500/20 blur-2xl rounded-full" />
            <div className="relative z-10 flex flex-col items-center gap-2">
              <img
                src="/brain-1.png"
                alt="DevMemory"
                width={60}
                height={60}
                className="animate-pulse"
              />
              <p className="text-slate-300 font-medium">
                Loading your dashboard…
              </p>
            </div>
          </div>
          <div className="w-6 h-6 animate-spin text-cyan-400 mx-auto border-2 border-cyan-400 border-t-transparent rounded-full" />
        </div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="max-w-md p-8 rounded-xl border border-slate-800 bg-black text-center">
          <div className="w-10 h-10 text-red-500 mx-auto mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-slate-100 mb-2">
            Couldn&apos;t load dashboard
          </h2>
          <p className="text-slate-400 mb-6 text-sm">
            {error || "Unknown error"}
          </p>
          <button
            onClick={() => (window.location.href = "/")}
            className="px-5 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg text-sm font-medium hover:from-cyan-400 hover:to-blue-400 transition"
          >
            Go back to home
          </button>
        </div>
      </div>
    );
  }
  return (
    <main className="min-h-screen bg-black text-slate-100">
      <SetupModal
        isOpen={showRepoSetup}
        onClose={() => setShowRepoSetup(false)}
        onSuccess={refreshUserData}
      />
      <div className="flex h-screen">
        <Sidebar
          user={user}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          startNewChat={startNewChat}
          logout={logout}
          openRepoManagement={() => setShowRepoSetup(true)}
        />

        <MainContent
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          messages={messages}
          input={input}
          setInput={setInput}
          isSending={isSending}
          handleSend={handleSend}
          messagesEndRef={messagesEndRef}
          inputRef={inputRef}
          formatTime={formatTime}
          userRepositories={userRepositories}
          setShowRepoSetup={setShowRepoSetup}
          toggleRepoSelection={toggleRepoSelection}
          chatSessions={chatSessions}          // ⬅ NEW
          onOpenSession={openSession}
        />
      </div>
    </main>
  );
}
