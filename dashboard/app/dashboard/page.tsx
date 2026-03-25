import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#f8f8f6] font-sans">

      {/* Nav — dark like chat header */}
      <nav className="bg-gray-900 border-b border-gray-800 px-8 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="ArigatoAI" className="w-9 h-9 rounded-full object-cover"/>
          <div>
            <div className="text-white font-bold text-base">ArigatoAI</div>
            <div className="text-gray-500 text-xs">Tax & Compliance Assistant</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-gray-400 hover:text-white text-sm transition-colors">Admin</Link>
          <Link href="/chat" className="bg-[#0d9488] hover:bg-[#0f766e] text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition-colors">
            Try it free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center px-8 py-24 max-w-4xl mx-auto">
        <div className="inline-block bg-[#0d9488]/10 text-[#0d9488] text-xs font-semibold px-4 py-2 rounded-full border border-[#0d9488]/20 mb-6">
          AI-Powered Tax Assistant for CA Firms
        </div>
        <h1 className="text-5xl font-black text-gray-900 leading-tight mb-6 tracking-tight">
          Answer every client<br/>
          <span className="text-[#0d9488]">tax question</span> instantly
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          ArigatoAI answers GST, ITR, TDS and EPF questions 24/7 — automatically, accurately, and with sources cited. Built specifically for CA firms across India.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link href="/chat" className="bg-[#0d9488] hover:bg-[#0f766e] text-white font-semibold px-8 py-4 rounded-xl text-base transition-colors">
            Try it free
          </Link>
          <Link href="/login" className="border border-gray-200 text-gray-600 hover:border-gray-300 font-semibold px-8 py-4 rounded-xl text-base transition-colors bg-white">
            Admin login
          </Link>
        </div>
        <p className="text-xs text-gray-400 mt-4">No setup required · Works instantly · Free to try</p>
      </section>

      {/* Chat preview */}
      <section className="px-8 pb-20 max-w-3xl mx-auto">
        <div className="bg-gray-900 rounded-2xl overflow-hidden shadow-2xl border border-gray-800">
          <div className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="ArigatoAI" className="w-8 h-8 rounded-full object-cover"/>
              <div>
                <div className="text-white font-bold text-sm">ArigatoAI</div>
                <div className="text-gray-500 text-xs">Tax & Compliance Assistant</div>
              </div>
            </div>
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500 opacity-60"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500 opacity-60"></div>
              <div className="w-3 h-3 rounded-full bg-green-500 opacity-60"></div>
            </div>
          </div>
          <div className="p-6 flex flex-col gap-4">
            <div className="flex justify-end">
              <div className="bg-[#0d9488] text-white text-sm px-4 py-2.5 rounded-2xl rounded-br-sm max-w-xs">
                What is the TDS rate on rent payment?
              </div>
            </div>
            <div className="flex gap-3 items-start">
              <div className="w-7 h-7 rounded-full bg-[#0d9488]/20 flex items-center justify-center flex-shrink-0 mt-1">
                <div className="w-3 h-3 rounded-full bg-[#0d9488]"></div>
              </div>
              <div className="bg-gray-800 border border-gray-700 text-gray-200 text-sm px-4 py-3 rounded-2xl rounded-bl-sm max-w-sm leading-relaxed">
                The TDS rate on rent under Section 194I is:
                <ul className="mt-2 space-y-1 text-gray-300">
                  <li>• Land/Building — <span className="text-[#0d9488] font-semibold">10%</span></li>
                  <li>• Machinery/Equipment — <span className="text-[#0d9488] font-semibold">2%</span></li>
                  <li>• Threshold: ₹2.4 lakh/year</li>
                </ul>
                <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-[#0d9488]">
                  Source: incometax.gov.in · 71% confidence
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="bg-white py-20 px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-black text-gray-900 mb-3 tracking-tight">How it works</h2>
            <p className="text-gray-500">Three simple steps to get started</p>
          </div>
          <div className="grid grid-cols-3 gap-8">
            {[
              { step: "01", title: "Upload your documents", desc: "Upload tax circulars, rate charts, and firm-specific PDFs. Indexed in seconds." },
              { step: "02", title: "Share the chat link", desc: "Give your team and clients the chat link. No app download, works on any device." },
              { step: "03", title: "Get instant answers", desc: "ArigatoAI answers 24/7 with sources cited. Auto-updates every Monday." },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 rounded-full bg-[#0d9488]/10 border-2 border-[#0d9488]/20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-[#0d9488] font-black text-sm">{item.step}</span>
                </div>
                <h3 className="font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-8 bg-[#f8f8f6]">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-black text-gray-900 mb-3 tracking-tight">Everything your firm needs</h2>
            <p className="text-gray-500">Built specifically for Indian CA firms</p>
          </div>
          <div className="grid grid-cols-3 gap-6">
            {[
              { title: "RAG Pipeline", desc: "Answers come from real sources — incometax.gov.in, gst.gov.in, epfindia.gov.in", icon: "🔍" },
              { title: "PDF Upload", desc: "Upload any tax circular. Indexed and searchable in under a minute.", icon: "📄" },
              { title: "Auto Updates", desc: "Scrapes government portals every Monday. Always current.", icon: "🔄" },
              { title: "Embeddable Widget", desc: "One line of code adds the chat bubble to your existing website.", icon: "🔌" },
              { title: "Admin Dashboard", desc: "See what clients are asking, upload documents, manage everything.", icon: "📊" },
              { title: "Source Citations", desc: "Every answer includes the source URL so clients can verify.", icon: "✅" },
            ].map((f) => (
              <div key={f.title} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-2xl mb-3">{f.icon}</div>
                <h3 className="font-bold text-gray-900 mb-2 text-sm">{f.title}</h3>
                <p className="text-gray-500 text-xs leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gray-900 py-20 px-8 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-black text-white mb-4 tracking-tight">Ready to save hours every day?</h2>
          <p className="text-gray-400 mb-8">Join CA firms already using ArigatoAI to answer client questions instantly.</p>
          <Link href="/chat" className="bg-[#0d9488] hover:bg-[#0f766e] text-white font-bold px-10 py-4 rounded-xl text-base transition-colors inline-block">
            Try ArigatoAI free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-800 px-8 py-8 text-center">
        <div className="flex items-center justify-center gap-3 mb-3">
          <img src="/logo.png" alt="ArigatoAI" className="w-7 h-7 rounded-full object-cover"/>
          <div className="text-white font-bold">ArigatoAI</div>
        </div>
        <p className="text-gray-500 text-xs mb-4">AI Tax Assistant for CA Firms · Hyderabad, India</p>
        <div className="flex gap-6 justify-center text-xs text-gray-500">
          <Link href="/chat" className="hover:text-[#0d9488] transition-colors">Chat</Link>
          <Link href="/login" className="hover:text-[#0d9488] transition-colors">Admin</Link>
        </div>
        <p className="text-gray-600 text-xs mt-4">© 2024 ArigatoAI. Built for Arigato Consultancy Services Pvt. Ltd.</p>
      </footer>

    </div>
  );
}