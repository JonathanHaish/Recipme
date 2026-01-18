"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { ChefHat, CheckCircle, AlertCircle } from "lucide-react";
import { authAPI } from "@/lib/auth";

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const uid = searchParams.get("uid");
  const token = searchParams.get("token");

  const isInvalidLink = !uid || !token;

  useEffect(() => {
    if (isInvalidLink) {
      setError("Invalid or missing reset link. Please request a new password reset.");
    }
  }, [isInvalidLink]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isInvalidLink) {
      setError("Invalid reset link");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords don't match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await authAPI.resetPassword({
        uid,
        token,
        password,
        password2: confirmPassword,
      });
      setSuccess(true);

      // Redirect to login after 2 seconds
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to reset password. The link may have expired.";
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
          Reset Password
        </h2>

        {success ? (
          <div className="space-y-4">
            <div className="flex flex-col items-center py-4">
              <CheckCircle className="w-16 h-16 text-green-600 mb-4" />
              <p className="text-lg font-medium text-black text-center">
                Password Reset Successful!
              </p>
              <p className="text-sm text-gray-600 text-center mt-2">
                Redirecting to login...
              </p>
            </div>
            <Link
              href="/login"
              className="block w-full text-center rounded-lg bg-black px-4 py-2 font-medium text-white transition-colors hover:bg-gray-800"
            >
              Go to Login
            </Link>
          </div>
        ) : isInvalidLink ? (
          <div className="space-y-4">
            <div className="flex flex-col items-center py-4">
              <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
              <p className="text-lg font-medium text-black text-center">
                Invalid Reset Link
              </p>
              <p className="text-sm text-gray-600 text-center mt-2">
                This password reset link is invalid or has expired.
              </p>
            </div>
            <Link
              href="/forgot-password"
              className="block w-full text-center rounded-lg bg-black px-4 py-2 font-medium text-white transition-colors hover:bg-gray-800"
            >
              Request New Reset Link
            </Link>
            <Link
              href="/login"
              className="block w-full text-center rounded-lg border-2 border-black px-4 py-2 font-medium text-black transition-colors hover:bg-gray-100"
            >
              Back to Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-sm text-gray-600 mb-4">
              Enter your new password below.
            </p>

            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700">
                New Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-black focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-black focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
                placeholder="••••••••"
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
              {loading ? "Resetting..." : "Reset Password"}
            </button>
          </form>
        )}

        {!success && !isInvalidLink && (
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
