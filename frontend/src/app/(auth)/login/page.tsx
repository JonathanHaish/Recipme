"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // כאן תוסיף את קריאת ה-API ל-backend
      console.log("Logging in with:", { email, password });

      // לדוגמה:
      // const response = await fetch("http://localhost:8000/api/login/", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ email, password }),
      // });

      // אם ההתחברות הצליחה, מעבר ל-recipes
      alert("התחברות הצליחה! מעבר לעמוד המתכונים");
      router.push("/recipes");
    } catch (err) {
      setError("שגיאה בהתחברות");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <div className="w-full max-w-md rounded-lg bg-white dark:bg-zinc-900 p-8 shadow-lg">
        <h1 className="mb-6 text-3xl font-bold text-center text-black dark:text-zinc-50">
          התחברות
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
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

          <div>
            <label className="block mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
              סיסמה
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-zinc-300 bg-white px-4 py-2 text-black focus:border-blue-500 focus:outline-none dark:border-zinc-600 dark:bg-zinc-800 dark:text-white"
              placeholder="••••••••"
            />
          </div>

          {/* קישור "שכחתי סיסמה" */}
          <div className="text-right">
            <Link
              href="/forgot-password"
              className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
            >
              שכחתי סיסמה
            </Link>
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
            {loading ? "מתחבר..." : "התחבר"}
          </button>
        </form>

        {/* כפתור הירשם */}
        <div className="mt-6 text-center">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            עדיין אין לך חשבון?{" "}
            <Link
              href="/register"
              className="font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
            >
              הירשם עכשיו
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

