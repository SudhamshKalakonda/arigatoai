export default function ConversationsPage() {
  const conversations = [
    { question: "How do I file ITR-1 online?", answer: "To file ITR-1 online, log in to the e-Filing portal...", confidence: 70, time: "2 min ago", source: "incometax.gov.in" },
    { question: "What is the TDS rate on rent?", answer: "TDS rate on rent is 10% for land/building...", confidence: 43, time: "15 min ago", source: "pdf://tds_test.pdf" },
    { question: "Documents needed for GST registration?", answer: "You need PAN card, Aadhaar, business address proof...", confidence: 65, time: "1 hr ago", source: "gst.gov.in" },
    { question: "What is Section 80C deduction limit?", answer: "Section 80C allows deductions up to Rs 1.5 lakh...", confidence: 72, time: "2 hr ago", source: "incometax.gov.in" },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Conversations</h1>
        <p className="text-gray-400 text-sm mt-1">All client questions and answers</p>
      </div>

      <div className="flex flex-col gap-4">
        {conversations.map((c, i) => (
          <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="text-sm font-medium text-white">{c.question}</div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  c.confidence >= 65
                    ? "bg-green-900/50 text-green-400"
                    : "bg-yellow-900/50 text-yellow-400"
                }`}>
                  {c.confidence}%
                </span>
                <span className="text-xs text-gray-500">{c.time}</span>
              </div>
            </div>
            <div className="text-sm text-gray-400 mb-3 leading-relaxed">{c.answer}</div>
            <div className="text-xs text-[#00BFA5]">Source: {c.source}</div>
          </div>
        ))}
      </div>
    </div>
  );
}