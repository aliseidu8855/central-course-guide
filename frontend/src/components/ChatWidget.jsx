/**
 * ChatWidget.jsx — Floating Course Q&A Chatbot
 *
 * A polished chat assistant grounded in the actual course data.
 * Floating button bottom-right; expands into a premium chat panel.
 * Powered by Llama 3.1 8B via NVIDIA NIM.
 */

import { useEffect, useRef, useState } from "react";
import api from "../services/api";
import {
  ChatBubbleIcon,
  SendIcon,
  XMarkIcon,
  SparklesIcon,
  GraduationCapIcon,
} from "./Icons";

// ---- Markdown-ish formatter (bold, code, lists, paragraphs) ----
const formatText = (text) => {
  // Split into paragraphs (double newline)
  const paragraphs = text.split(/\n\n+/);
  return paragraphs.map((para, pi) => {
    // Check if it's a list — lines starting with -, *, or 1. 2. etc.
    const lines = para.split("\n");
    const isBulletList = lines.every((l) => /^\s*[-*]\s/.test(l.trim()));
    const isNumberedList = lines.every((l) => /^\s*\d+[.)]\s/.test(l.trim()));

    if (isBulletList || isNumberedList) {
      return (
        <ul key={pi} className="mt-1.5 space-y-1 list-none">
          {lines.map((line, li) => {
            const cleaned = line.replace(/^\s*[-*\d]+[.)]\s*/, "");
            return (
              <li key={li} className="flex gap-2 text-xs sm:text-sm leading-relaxed">
                <span className="text-maroon/60 shrink-0 mt-0.5 select-none">
                  {isNumberedList ? `${li + 1}.` : "•"}
                </span>
                <span>{inlineFormat(cleaned)}</span>
              </li>
            );
          })}
        </ul>
      );
    }

    // Plain paragraph with inline formatting + line breaks
    return (
      <p key={pi} className="text-xs sm:text-sm leading-relaxed min-h-[1em]">
        {lines.map((line, li) => (
          <span key={li}>
            {li > 0 && <br />}
            {inlineFormat(line)}
          </span>
        ))}
      </p>
    );
  });
};

const inlineFormat = (text) => {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-text-primary">
          {part.slice(2, -2)}
        </strong>
      );
    }
    const codeSplit = part.split(/(`[^`]+`)/g);
    return codeSplit.map((seg, j) => {
      if (seg.startsWith("`") && seg.endsWith("`")) {
        return (
          <code key={`${i}-${j}`} className="text-[11px] bg-maroon/8 text-maroon px-1 py-0.5 rounded font-medium">
            {seg.slice(1, -1)}
          </code>
        );
      }
      return seg;
    });
  });
};

// ---- Quick-start suggestions ----
const SUGGESTIONS = [
  { label: "Coding courses", icon: "technology", query: "Which courses involve coding or computers?" },
  { label: "Nursing careers", icon: "health", query: "What can I do with a nursing degree?" },
  { label: "Entry requirements", icon: "leadership", query: "What are the entry requirements like?" },
  { label: "Practical work", icon: "building", query: "Which programme has the most hands-on practical work?" },
];

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [configured, setConfigured] = useState(true);

  const listRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 200);
  }, [open]);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTo({
        top: listRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  const send = async (textOverride) => {
    const text = (textOverride || input).trim();
    if (!text || loading) return;

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    if (!textOverride) setInput("");
    setLoading(true);
    setConfigured(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await api.post("/chat", { message: text, history });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.reply },
      ]);
    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail || "Something went wrong.";
      if (status === 503) {
        setConfigured(false);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: detail, isError: true },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <>
      {/* ---- Floating button ---- */}
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={`fixed bottom-5 right-5 sm:bottom-6 sm:right-6 z-50 flex items-center gap-2.5 pl-4 pr-5 h-14 rounded-full bg-linear-to-br from-maroon to-maroon-dark text-white shadow-lg shadow-maroon/25 hover:shadow-xl hover:shadow-maroon/35 hover:-translate-y-0.5 transition-all duration-300 cursor-pointer ${
          open ? "scale-0 opacity-0 pointer-events-none" : "scale-100 opacity-100"
        }`}
        aria-label="Open course advisor chat"
      >
        <span className="flex items-center justify-center h-8 w-8 rounded-full bg-white/20 shrink-0">
          <ChatBubbleIcon className="h-4.5 w-4.5" />
        </span>
        <span className="text-sm font-semibold hidden sm:inline">Chat with Biggie</span>
      </button>

      {/* ---- Chat panel ---- */}
      <div
        className={`fixed bottom-5 right-5 sm:bottom-6 sm:right-6 z-50 w-[calc(100vw-2.5rem)] sm:w-[400px] max-h-[36rem] sm:max-h-[40rem] bg-surface rounded-2xl shadow-2xl shadow-black/15 border border-surface-alt/80 flex flex-col overflow-hidden transition-all duration-300 origin-bottom-right ${
          open ? "scale-100 opacity-100" : "scale-95 opacity-0 pointer-events-none"
        }`}
      >
        {/* ---- Header ---- */}
        <div className="relative shrink-0 bg-linear-to-br from-maroon via-maroon-dark to-maroon px-5 py-4">
          {/* Decorative blobs */}
          <div className="absolute top-0 right-0 h-20 w-20 rounded-bl-full bg-white/10 -mr-4 -mt-4" />
          <div className="absolute bottom-0 right-12 h-14 w-14 rounded-tl-full bg-white/5" />
          <div className="relative flex items-center gap-3">
            <span className="flex items-center justify-center h-10 w-10 rounded-xl bg-white/20 text-white backdrop-blur-sm shrink-0 shadow-inner">
              <GraduationCapIcon className="h-5 w-5" />
            </span>
            <div>
              <p className="text-xl font-extrabold text-white leading-tight tracking-tight">
                Biggie
              </p>
              <p className="text-[10px] text-white/70 flex items-center gap-1.5">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.6)]" />
                Knows every course. Just ask.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="ml-auto p-2 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              aria-label="Close chat"
            >
              <XMarkIcon className="h-4.5 w-4.5" />
            </button>
          </div>
        </div>

        {/* ---- Body ---- */}
        <div
          ref={listRef}
          className="flex-1 overflow-y-auto min-h-0 bg-linear-to-b from-surface to-background/60"
        >
          {!configured ? (
            <div className="flex flex-col items-center justify-center text-center px-6 py-12">
              <div className="h-14 w-14 rounded-2xl bg-maroon/10 flex items-center justify-center mb-4">
                <SparklesIcon className="h-7 w-7 text-maroon" />
              </div>
              <p className="text-sm font-bold text-text-primary">Chatbot not configured</p>
              <p className="mt-1.5 text-xs text-text-secondary leading-relaxed max-w-[260px]">
                Add <code className="text-[11px] bg-surface-alt px-1 py-0.5 rounded">NVIDIA_API_KEY</code> to{" "}
                <code className="text-[11px] bg-surface-alt px-1 py-0.5 rounded">backend/.env</code> and restart.
              </p>
              <a
                href="https://build.nvidia.com/explore/discover"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 text-xs font-medium text-maroon hover:underline"
              >
                Get a free key →
              </a>
            </div>
          ) : !hasMessages ? (
            /* ---- Welcome ---- */
            <div className="flex flex-col items-center px-5 py-8">
              <div className="h-16 w-16 rounded-2xl bg-linear-to-br from-maroon/15 to-accent/20 flex items-center justify-center mb-4 ring-1 ring-maroon/10">
                <SparklesIcon className="h-8 w-8 text-maroon" />
              </div>
              <h3 className="text-base font-bold text-text-primary">Hey, my name is Biggie</h3>
              <p className="mt-1.5 text-xs text-text-secondary text-center leading-relaxed max-w-[260px]">
                I know every programme at Central University inside out — subjects, careers, entry requirements, what you'll actually study day to day. Just ask.
              </p>
              <div className="mt-5 grid grid-cols-2 gap-2 w-full">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s.label}
                    type="button"
                    onClick={() => send(s.query)}
                    className="group flex flex-col items-start gap-1.5 p-3 rounded-xl bg-surface border border-surface-alt hover:border-maroon/30 hover:bg-maroon/3 text-left transition-all cursor-pointer"
                  >
                    <span className="inline-flex items-center justify-center h-7 w-7 rounded-lg bg-maroon/8 text-maroon group-hover:bg-maroon group-hover:text-white transition-colors">
                      <SparklesIcon className="h-3.5 w-3.5" />
                    </span>
                    <span className="text-xs font-semibold text-text-secondary group-hover:text-maroon transition-colors leading-tight">
                      {s.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* ---- Messages ---- */
            <div className="px-4 py-4 space-y-4">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex gap-2.5 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  {/* Assistant avatar */}
                  {msg.role === "assistant" && !msg.isError && (
                    <span className="flex items-start shrink-0 mt-0.5">
                      <span className="flex items-center justify-center h-7 w-7 rounded-full bg-maroon/10 text-maroon">
                        <SparklesIcon className="h-3.5 w-3.5" />
                      </span>
                    </span>
                  )}

                  <div
                    className={`max-w-[82%] px-3.5 py-2.5 text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "rounded-2xl rounded-br-md bg-linear-to-br from-maroon to-maroon-dark text-white shadow-sm"
                        : msg.isError
                          ? "rounded-2xl rounded-bl-md bg-red-50 text-red-700 border border-red-100"
                          : "rounded-2xl rounded-bl-md bg-white border border-surface-alt/80 text-text-secondary shadow-sm"
                    }`}
                  >
                    {typeof msg.content === "string" && msg.role === "assistant" && !msg.isError
                      ? formatText(msg.content)
                      : msg.content}
                  </div>

                  {/* User avatar */}
                  {msg.role === "user" && (
                    <span className="flex items-start shrink-0 mt-0.5">
                      <span className="flex items-center justify-center h-7 w-7 rounded-full bg-accent/20 text-accent-dark text-xs font-bold">
                        U
                      </span>
                    </span>
                  )}
                </div>
              ))}

              {/* Typing indicator */}
              {loading && (
                <div className="flex gap-2.5 justify-start">
                  <span className="flex items-start shrink-0 mt-1">
                    <span className="flex items-center justify-center h-7 w-7 rounded-full bg-maroon/10 text-maroon">
                      <SparklesIcon className="h-3.5 w-3.5" />
                    </span>
                  </span>
                  <div className="bg-white border border-surface-alt/80 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                    <span className="flex gap-1.5">
                      {[0, 1, 2].map((d) => (
                        <span
                          key={d}
                          className="thinking-dot h-2 w-2 rounded-full bg-maroon/50"
                          style={{ animationDelay: `${d * 0.15}s` }}
                        />
                      ))}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ---- Input ---- */}
        {configured && (
          <div className="shrink-0 px-4 py-3 border-t border-surface-alt/80 bg-white/80 backdrop-blur-sm">
            <div className="flex items-center gap-2 bg-background rounded-xl border border-surface-alt focus-within:border-maroon/40 focus-within:ring-2 focus-within:ring-maroon/10 transition-all">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={hasMessages ? "Ask a follow-up…" : "Ask about any course…"}
                disabled={loading}
                className="flex-1 bg-transparent text-sm px-4 py-2.5 text-text-primary placeholder:text-text-muted focus:outline-none disabled:opacity-40"
              />
              <button
                type="button"
                onClick={() => send()}
                disabled={!input.trim() || loading}
                className="flex items-center justify-center h-8 w-8 rounded-lg bg-maroon text-white hover:bg-maroon-dark transition-colors shrink-0 mr-1.5 cursor-pointer disabled:opacity-20 disabled:cursor-not-allowed disabled:hover:bg-maroon"
                aria-label="Send message"
              >
                <SendIcon className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
