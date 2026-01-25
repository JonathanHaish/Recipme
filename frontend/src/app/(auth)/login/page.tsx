"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ChefHat } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { authAPI } from "@/lib/auth";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sessionExpiredMessage, setSessionExpiredMessage] = useState("");
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, loading: authLoading } = useAuth();

  // Check for session expiration message
  useEffect(() => {
    const sessionExpired = searchParams.get('session_expired');
    if (sessionExpired === 'true' && !sessionExpiredMessage) {
      setSessionExpiredMessage("Your session has expired. Please log in again.");
    }
  }, [searchParams, sessionExpiredMessage]);

  // Redirect if already logged in
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/recipes");
    }
  }, [isAuthenticated, authLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSessionExpiredMessage(""); // Clear session expired message on submit

    try {
      const response = await authAPI.login({ email, password });
      console.log("Login successful:", response);

      // Redirect to recipes page on success
      router.push("/recipes");
    } catch (err: any) {
      console.error("Login error:", err);
      setError(err.message || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };
  const handleGuestLogin = () => {
    router.push("/recipes");
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="flex flex-1 items-center justify-center bg-white">
        <div className="text-center">
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render login form if already authenticated
  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="flex flex-1 items-center justify-center bg-white">
      <div className="w-full max-w-md rounded-lg bg-white p-6 sm:p-8 shadow-lg border border-gray-200">
        <div className="mb-6 flex items-center justify-center gap-3">
          <ChefHat className="w-10 h-10 text-black" />
          <h1 className="text-3xl font-bold text-black">
            Recipes
          </h1>
        </div>
        <h2 className="mb-6 text-2xl font-semibold text-center text-gray-700">
          Login
        </h2>

        <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
          <div>
            <label className="block mb-2 text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-black text-base focus:border-blue-500 focus:outline-none min-h-[44px]"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label className="block mb-2 text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-black text-base focus:border-blue-500 focus:outline-none min-h-[44px]"
              placeholder="••••••••"
            />
          </div>

          {/* Forgot password link */}
          <div className="text-right">
            <Link
              href="/forgot-password"
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Forgot password?
            </Link>
          </div>

          {sessionExpiredMessage && (
            <div className="rounded-lg bg-yellow-100 border border-yellow-300 p-3 text-sm text-yellow-800">
              {sessionExpiredMessage}
            </div>
          )}

          {error && (
            <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-black px-4 py-2 font-medium text-white transition-colors hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px]"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        {/* Guest login button */}
        <div className="mt-4">
          <button
            type="button"
            onClick={handleGuestLogin}
            className="w-full rounded-lg border-2 border-black px-4 py-2 font-medium text-black transition-colors hover:bg-gray-100 min-h-[44px]"
          >
            Continue as Guest
          </button>
        </div>

        {/* Register button */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{" "}
            <Link
              href="/register"
              className="font-medium text-blue-600 hover:text-blue-800"
            >
              Register now
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}





