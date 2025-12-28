"use client";

import { useState } from "react";
import Link from "next/link";

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
      console.log("Sending reset password to:", email);
      // כאן תוסיף את קריאת ה-API ל-backend
      // const response = await fetch("http://localhost:8000/api/forgot-password/", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ email }),
      // });
      
      setSuccess(true);
    } catch (err) {
      setError("שגיאה בשליחת אימייל");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <div className="w-full max-w-md rounded-lg bg-white dark:bg-zinc-900 p-8 shadow-lg">
        <h1 className="mb-6 text-3xl font-bold text-center text-black dark:text-zinc-50">
          שכחתי סיסמה
        </h1>
        
        {success ? (
          <div className="space-y-4">
            <div className="rounded-lg bg-green-100 p-4 text-sm text-green-700 dark:bg-green-900 dark:text-green-300">
              נשלח אימייל לאיפוס סיסמה לכתובת: {email}
            </div>
            <Link 
              href="/login"
              className="block w-full text-center rounded-lg bg-black px-4 py-2 font-medium text-white transition-colors hover:bg-zinc-800 dark:bg-white dark:text-black dark:hover:bg-zinc-200"
            >
              חזרה להתחברות
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
              הזן את כתובת האימייל שלך ונשלח לך קישור לאיפוס הסיסמה.
            </p>

            <div>
              <label className="block mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                אימייל
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-lg border border-zinc-300 bg-white px-4 py-2 text-black focus:border-blue-500 focus:outline-none dark:border-zinc-600 dark:bg-zinc-800 dark:text-white"
                placeholder="your@email.com"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700 dark:bg-red-900 dark:text-red-300">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-black px-4 py-2 font-medium text-white transition-colors hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black dark:hover:bg-zinc-200"
            >
              {loading ? "שולח..." : "שלח קישור איפוס"}
            </button>
          </form>
        )}

        <div className="mt-6 text-center">
          <Link 
            href="/login"
            className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
          >
            חזרה להתחברות
          </Link>
        </div>
      </div>
    </div>
  );
}

