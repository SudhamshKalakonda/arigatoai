"use client";
import { useState } from "react";

export default function DocumentsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title || file.name);
    formData.append("firm_id", "arigato");

    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setMessage(`Successfully uploaded! ${data.chunks_added} chunks added. Total vectors: ${data.total_vectors}`);
      setFile(null);
      setTitle("");
    } catch {
      setMessage("Upload failed. Make sure the backend is running.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Documents</h1>
        <p className="text-gray-400 text-sm mt-1">Upload PDFs to expand the knowledge base</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 max-w-lg">
        <div className="text-sm font-semibold text-white mb-4">Upload PDF</div>

        <form onSubmit={handleUpload} className="flex flex-col gap-4">
          <div
            className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center cursor-pointer hover:border-[#00BFA5] transition-colors"
            onClick={() => document.getElementById("file-input")?.click()}
          >
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#00BFA5" strokeWidth="1.5" className="mx-auto mb-3">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <div className="text-sm text-gray-400">
              {file ? file.name : "Click to select a PDF file"}
            </div>
            <div className="text-xs text-gray-600 mt-1">Max 10MB</div>
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>

          <div>
            <label className="text-sm text-gray-400 mb-1 block">Document title (optional)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. GST Circular 2024"
              className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-3 text-white text-sm outline-none focus:border-[#00BFA5]"
            />
          </div>

          <button
            type="submit"
            disabled={!file || uploading}
            className="bg-[#00BFA5] hover:bg-[#00897B] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg text-sm transition-colors"
          >
            {uploading ? "Uploading..." : "Upload & Index"}
          </button>
        </form>

        {message && (
          <div className={`mt-4 p-3 rounded-lg text-sm ${
            message.includes("failed")
              ? "bg-red-900/30 text-red-400 border border-red-800"
              : "bg-green-900/30 text-green-400 border border-green-800"
          }`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
}