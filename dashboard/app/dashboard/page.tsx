"use client";
import { useEffect, useState } from "react";

interface Stats {
  total_vectors: number;
  index_fullness: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetch("https://arigatoai-backend.onrender.com/api/stats")
      .then((r) => r.json())
      .then(setStats)
      .catch(console.error);
  }, []);

  const conversations = [
    { question: "How do I file ITR-1 online?", confidence: 70, time: "2 min ago" },
    { question: "What is the TDS rate on rent?", confidence: 43, time: "15 min ago" },
    { question: "Documents needed for GST registration?", confidence: 65, time: "1 hr ago" },
    { question: "What is Section 80C deduction limit?", confidence: 72, time: "2 hr ago" },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 text-sm mt-1">Arigato Consultancy Services</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Total vectors</div>
          <div className="text-3xl font-bold text-white">{stats?.total_vectors ?? "..."}</div>
          <div className="text-xs text-[#00BFA5] mt-1">Knowledge base size</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Sources scraped</div>
          <div className="text-3xl font-bold text-white">3</div>
          <div className="text-xs text-[#00BFA5] mt-1">incometax, gst, epf</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Next update</div>
          <div className="text-xl font-bold text-white">Every Monday</div>
          <div className="text-xs text-[#00BFA5] mt-1">Auto scrape at 9am</div>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <div className="text-sm font-semibold text-white mb-4">Recent conversations</div>
        <div className="flex flex-col gap-3">
          {conversations.map((c, i) => (
            <div key={i} className="bg-gray-950 rounded-lg p-3 border border-gray-800">
              <div className="text-sm text-gray-200">{c.question}</div>
              <div className="flex items-center gap-3 mt-2">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  c.confidence >= 65
                    ? "bg-green-900/50 text-green-400"
                    : "bg-yellow-900/50 text-yellow-400"
                }`}>
                  {c.confidence}% confidence
                </span>
                <span className="text-xs text-gray-500">{c.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}