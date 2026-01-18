"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ChefHat, Send, ArrowLeft, CheckCircle } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { contactAPI } from "@/lib/contact";

export default function ContactPage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, loading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    // Basic validation
    if (!subject.trim()) {
      setError("Please enter a subject.");
      return;
    }
    if (!message.trim()) {
      setError("Please enter a message.");
      return;
    }

    setIsSubmitting(true);
    try {
      await contactAPI.sendMessage({
        subject: subject.trim(),
        message: message.trim(),
      });
      setSuccess(true);
      setSubject("");
      setMessage("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show loading while checking auth
  if (loading) {
    return (
      <div className="flex-1 bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex-1 bg-gray-50 p-6">
      {/* Header */}
      <div className="max-w-2xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <ChefHat className="w-10 h-10 text-black" />
            <h1 className="text-3xl font-bold text-black">Contact Us</h1>
          </div>
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 px-4 py-2 border border-black rounded hover:bg-gray-100 text-black transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
        </div>
        <p className="text-gray-600">
          Have a question, feedback, or need help? Send us a message and our team will get back to you.
        </p>
      </div>

      {/* Contact Form */}
      <div className="max-w-2xl mx-auto">
        <div className="bg-white border-2 border-black rounded-lg p-6">
          {success ? (
            <div className="text-center py-8">
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-black mb-2">
                Message Sent!
              </h2>
              <p className="text-gray-600 mb-6">
                Thank you for reaching out. We&apos;ll get back to you as soon as possible.
              </p>
              <div className="flex gap-3 justify-center">
                <button
                  onClick={() => setSuccess(false)}
                  className="px-6 py-2 border border-black rounded hover:bg-gray-100 text-black transition-colors"
                >
                  Send Another Message
                </button>
                <button
                  onClick={() => router.push("/recipes")}
                  className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
                >
                  Back to Recipes
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Error Message */}
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                  {error}
                </div>
              )}

              {/* Subject Field */}
              <div>
                <label
                  htmlFor="subject"
                  className="block text-sm font-medium text-black mb-2"
                >
                  Subject
                </label>
                <input
                  type="text"
                  id="subject"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="What is your message about?"
                  className="w-full px-4 py-2 border border-black rounded text-black placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-1"
                  maxLength={200}
                  disabled={isSubmitting}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {subject.length}/200 characters
                </p>
              </div>

              {/* Message Field */}
              <div>
                <label
                  htmlFor="message"
                  className="block text-sm font-medium text-black mb-2"
                >
                  Message
                </label>
                <textarea
                  id="message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Write your message here..."
                  rows={6}
                  className="w-full px-4 py-2 border border-black rounded text-black placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-1 resize-none"
                  disabled={isSubmitting}
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-black text-white rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {isSubmitting ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send Message
                  </>
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
