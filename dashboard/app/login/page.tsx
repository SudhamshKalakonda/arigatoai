"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (password === "arigato2024") {
      localStorage.setItem("admin_auth", "true");
      router.push("/dashboard");
    } else {
      setError("Wrong password. Please try again.");
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="text-2xl font-bold text-[#00BFA5] mb-1">ArigatoAI</div>
          <div className="text-gray-400 text-sm">Admin Dashboard</div>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter admin password"
              className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-3 text-white text-sm outline-none focus:border-[#00BFA5]"
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm">{error}</div>
          )}

          <button
            type="submit"
            className="bg-[#00BFA5] hover:bg-[#00897B] text-white font-semibold py-3 rounded-lg text-sm transition-colors"
          >
            Login
          </button>
        </form>

        <div className="text-center text-gray-600 text-xs mt-6">
          Arigato Consultancy Services Pvt. Ltd.
        </div>
      </div>
    </div>
  );
}