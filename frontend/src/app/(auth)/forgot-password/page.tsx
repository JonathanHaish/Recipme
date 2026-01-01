"use client";

import { useState } from "react";
import Link from "next/link";
import { authAPI } from "@/lib/auth";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);

    try {
      await authAPI.forgotPassword(email);
      console.log("Password reset email sent to:", email);
      setSuccess(true);
    } catch (err: any) {
      console.error("Error sending email:", err);
      setError(err.message || "Error sending password reset email");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-lg border border-gray-200">
        <h1 className="mb-6 text-3xl font-bold text-center text-black">
          Forgot Password
        </h1>
        
        {success ? (
          <div className="space-y-4">
            <div className="rounded-lg bg-green-100 p-4 text-sm text-green-700">
              Password reset email sent to: {email}
            </div>
            <Link 
              href="/login"
              className="block w-full text-center rounded-lg bg-black px-4 py-2 font-medium text-white transition-colors hover:bg-gray-800"
            >
              Back to Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-sm text-gray-600 mb-4">
              Enter your email address and we'll send you a link to reset your password.
            </p>

            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-black focus:border-blue-500 focus:outline-none"
                placeholder="your@email.com"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-black px-4 py-2 font-medium text-white transition-colors hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Sending..." : "Send Reset Link"}
            </button>
          </form>
        )}

        <div className="mt-6 text-center">
          <Link 
            href="/login"
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
}

