"use client";
import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "ai";
  text: string;
  sources?: string[];
  confidence?: number;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "ai",
      text: "Hi! I am ArigatoAI. Ask me anything about income tax, GST, TDS, EPF, or any other tax and compliance questions.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setLoading(true);

    try {
      const res = await fetch("https://arigatoai-backend.onrender.com/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, firm_id: "arigato" }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: data.answer,
          sources: data.sources,
          confidence: data.confidence,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "Sorry, could not connect. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function formatText(text: string) {
    const lines = text.split(/\n|(?=\d+\.\s)/);
    const elements: React.ReactNode[] = [];
    let olItems: string[] = [];

    lines.forEach((line, i) => {
      line = line.trim();
      if (!line) return;
      const olMatch = line.match(/^(\d+)\.\s+(.+)/);
      if (olMatch) {
        olItems.push(olMatch[2]);
      } else {
        if (olItems.length > 0) {
          elements.push(
            <ol key={`ol-${i}`} className="list-decimal pl-5 my-2 flex flex-col gap-1">
              {olItems.map((item, j) => (
                <li key={j} className="text-sm leading-relaxed">{item}</li>
              ))}
            </ol>
          );
          olItems = [];
        }
        elements.push(
          <p key={i} className="text-sm leading-relaxed mb-1">{line}</p>
        );
      }
    });

    if (olItems.length > 0) {
      elements.push(
        <ol key="ol-last" className="list-decimal pl-5 my-2 flex flex-col gap-1">
          {olItems.map((item, j) => (
            <li key={j} className="text-sm leading-relaxed">{item}</li>
          ))}
        </ol>
      );
    }

    return elements;
  }

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">

      <div className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="ArigatoAI" className="w-9 h-9 rounded-full object-cover"/>
          <div>
            <div className="text-white font-bold text-base">ArigatoAI</div>
            <div className="text-gray-500 text-xs">Tax & Compliance Assistant</div>
          </div>
        </div>
        <div className="text-xs text-gray-600">Arigato Consultancy Services Pvt. Ltd.</div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-4 max-w-3xl mx-auto w-full">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "ai" && (
              <img src="/logo.png" alt="AI" className="w-8 h-8 rounded-full object-cover mr-3 flex-shrink-0 mt-1"/>
            )}
            <div className={`max-w-xl rounded-2xl px-4 py-3 ${
              msg.role === "user"
                ? "bg-[#0d9488] text-white rounded-br-sm"
                : "bg-gray-900 border border-gray-800 text-gray-200 rounded-bl-sm"
            }`}>
              {msg.role === "ai" ? (
                <div>{formatText(msg.text)}</div>
              ) : (
                <p className="text-sm">{msg.text}</p>
              )}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-700">
                  <div className="text-xs text-[#0d9488]">
                    Source: {msg.sources.map(u => {
                      try { return new URL(u).hostname; }
                      catch { return u; }
                    }).join(", ")}
                  </div>
                  {msg.confidence && (
                    <div className="text-xs text-gray-500 mt-0.5">
                      Confidence: {Math.round(msg.confidence * 100)}%
                    </div>
                  )}
                </div>
              )}
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-white text-xs font-bold ml-3 flex-shrink-0 mt-1">
                You
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <img src="/logo.png" alt="AI" className="w-8 h-8 rounded-full object-cover mr-3 flex-shrink-0"/>
            <div className="bg-gray-900 border border-gray-800 rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex gap-1 items-center h-5">
                <div className="w-2 h-2 bg-[#0d9488] rounded-full animate-bounce" style={{animationDelay: "0ms"}}></div>
                <div className="w-2 h-2 bg-[#0d9488] rounded-full animate-bounce" style={{animationDelay: "150ms"}}></div>
                <div className="w-2 h-2 bg-[#0d9488] rounded-full animate-bounce" style={{animationDelay: "300ms"}}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-gray-800 bg-gray-900 px-4 py-4 flex-shrink-0">
        <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about income tax, GST, TDS, EPF..."
            className="flex-1 bg-gray-950 border border-gray-800 rounded-xl px-4 py-3 text-white text-sm outline-none focus:border-[#0d9488] placeholder-gray-600"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-[#0d9488] hover:bg-[#0f766e] disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl text-sm font-semibold transition-colors"
          >
            Send
          </button>
        </form>
        <div className="text-center text-gray-700 text-xs mt-2">
          Powered by ArigatoAI — For internal use only
        </div>
      </div>
    </div>
  );
}