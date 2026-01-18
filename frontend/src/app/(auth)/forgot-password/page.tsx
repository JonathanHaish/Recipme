"use client";

import { useState } from "react";
import Link from "next/link";
import { ChefHat, Mail, CheckCircle } from "lucide-react";
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
      setSuccess(true);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Error sending password reset email";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-1 items-center justify-center bg-white">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-lg border border-gray-200">
        {/* Logo Header */}
        <div className="mb-6 flex items-center justify-center gap-3">
          <ChefHat className="w-10 h-10 text-black" />
          <h1 className="text-3xl font-bold text-black">Recipme</h1>
        </div>

        <h2 className="mb-6 text-2xl font-semibold text-center text-gray-700">
          Forgot Password
        </h2>
        
        {success ? (
          <div className="space-y-4">
            <div className="flex flex-col items-center py-4">
              <CheckCircle className="w-16 h-16 text-green-600 mb-4" />
              <p className="text-lg font-medium text-black text-center">
                Check Your Email
              </p>
              <p className="text-sm text-gray-600 text-center mt-2">
                We&apos;ve sent a password reset link to:
              </p>
              <p className="text-sm font-medium text-black mt-1">
                {email}
              </p>
            </div>
            <div className="rounded-lg bg-gray-50 p-4 border border-gray-200">
              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-gray-500 mt-0.5" />
                <p className="text-sm text-gray-600">
                  The link will expire in 24 hours. If you don&apos;t see the email, check your spam folder.
                </p>
              </div>
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
              Enter your email address and we&apos;ll send you a link to reset your password.
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
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-black focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
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

        {!success && (
          <div className="mt-6 text-center">
            <Link 
              href="/login"
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Back to Login
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
