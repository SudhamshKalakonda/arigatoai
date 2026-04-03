import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#f8f8f6] font-sans">

      {/* Nav */}
      <nav className="bg-black px-8 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="ArigatoAI" className="w-9 h-9 rounded-full object-cover"/>
          <div>
            <div className="text-white font-bold text-base">ArigatoAI</div>
            <div className="text-gray-500 text-xs">Tax & Compliance Assistant</div>
          </div>
        </div>
        <Link href="/chat" className="bg-[#0d9488] hover:bg-[#0f766e] text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition-colors">
          Try it free
        </Link>
      </nav>

      {/* Hero */}
      <section className="text-center px-8 py-28 max-w-4xl mx-auto">
        <div className="inline-block bg-[#0d9488]/10 text-[#0d9488] text-xs font-semibold px-4 py-2 rounded-full border border-[#0d9488]/20 mb-8">
          Built for CA firms across India
        </div>
        <h1 className="text-5xl font-black text-gray-900 leading-tight mb-6 tracking-tight">
          Your clients deserve<br/>
          <span className="text-[#0d9488]">instant tax answers</span>
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          ArigatoAI answers GST, ITR, TDS and EPF questions 24/7 — instantly, accurately, with sources cited. No more waiting for callbacks.
        </p>
        <Link href="/chat" className="bg-[#0d9488] hover:bg-[#0f766e] text-white font-bold px-10 py-4 rounded-xl text-base transition-colors inline-block shadow-lg shadow-[#0d9488]/20">
          Start chatting free
        </Link>
        <p className="text-xs text-gray-400 mt-4">No signup required · Works instantly</p>
      </section>

      {/* Chat preview */}
      <section className="px-8 pb-24 max-w-2xl mx-auto">
        <div className="bg-black rounded-2xl overflow-hidden shadow-2xl border border-[#1a1a1a]">
          <div className="bg-[#0a0a0a] border-b border-[#1a1a1a] px-5 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="ArigatoAI" className="w-7 h-7 rounded-full object-cover"/>
              <div className="text-white font-bold text-sm">ArigatoAI</div>
            </div>
            <div className="flex gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500 opacity-60"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-500 opacity-60"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 opacity-60"></div>
            </div>
          </div>
          <div className="p-5 flex flex-col gap-4">
            <div className="flex justify-end">
              <div className="bg-[#0d9488] text-white text-sm px-4 py-2.5 rounded-2xl rounded-br-sm max-w-xs">
                What is the TDS rate on rent?
              </div>
            </div>
            <div className="flex gap-3 items-start">
              <img src="/logo.png" alt="AI" className="w-7 h-7 rounded-full object-cover flex-shrink-0 mt-1"/>
              <div className="bg-[#111] border border-[#1f1f1f] text-gray-200 text-sm px-4 py-3 rounded-2xl rounded-bl-sm leading-relaxed">
                TDS on rent under Section 194I:
                <ul className="mt-2 space-y-1 text-gray-300 text-xs">
                  <li>• Land/Building — <span className="text-[#0d9488] font-semibold">10%</span></li>
                  <li>• Machinery — <span className="text-[#0d9488] font-semibold">2%</span></li>
                  <li>• Threshold: ₹2.4 lakh/year</li>
                </ul>
                <div className="mt-2 text-xs text-[#0d9488]">Source: incometax.gov.in</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-white py-20 px-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-gray-900 mb-12 text-center tracking-tight">Why CA firms love ArigatoAI</h2>
          <div className="grid grid-cols-3 gap-6">
            {[
              { icon: "⚡", title: "Instant answers", desc: "Clients get answers in seconds. No more waiting for callbacks on basic tax queries." },
              { icon: "📄", title: "Upload any PDF", desc: "Upload circulars, rate charts, or firm documents. Searchable in under a minute." },
              { icon: "🔄", title: "Always updated", desc: "Automatically scrapes government portals every Monday. Always current." },
              { icon: "🔍", title: "Cited sources", desc: "Every answer includes the source URL. Clients can verify themselves." },
              { icon: "🔌", title: "Embed anywhere", desc: "One line of code adds the chat bubble to your existing website." },
              { icon: "🇮🇳", title: "Built for India", desc: "Trained on incometax.gov.in, gst.gov.in, epfindia.gov.in and more." },
            ].map((f) => (
              <div key={f.title} className="bg-[#f8f8f6] border border-gray-100 rounded-2xl p-6 hover:shadow-md transition-shadow">
                <div className="text-2xl mb-3">{f.icon}</div>
                <h3 className="font-bold text-gray-900 mb-2 text-sm">{f.title}</h3>
                <p className="text-gray-500 text-xs leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-black py-20 px-8 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-black text-white mb-4 tracking-tight">
            Ready to try it?
          </h2>
          <p className="text-gray-400 mb-8">Ask any tax question right now. No signup needed.</p>
          <Link href="/chat" className="bg-[#0d9488] hover:bg-[#0f766e] text-white font-bold px-10 py-4 rounded-xl text-base transition-colors inline-block">
            Start chatting free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black border-t border-[#1a1a1a] px-8 py-8 text-center">
        <div className="flex items-center justify-center gap-3 mb-3">
          <img src="/logo.png" alt="ArigatoAI" className="w-7 h-7 rounded-full object-cover"/>
          <div className="text-white font-bold">ArigatoAI</div>
        </div>
        <p className="text-gray-600 text-xs">Built for Arigato Consultancy Services Pvt. Ltd. · Hyderabad, India</p>
      </footer>

    </div>
  );
}