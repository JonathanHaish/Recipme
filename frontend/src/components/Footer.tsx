"use client";

import Link from "next/link";
import { Mail } from "lucide-react";

export default function Footer() {
  return (
    <footer className="w-full border-t border-gray-200 bg-white mt-auto">
      <div className="max-w-5xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            © {new Date().getFullYear()} Recipme. All rights reserved.
          </p>
          <Link
            href="/contact"
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-black transition-colors"
          >
            <Mail className="w-4 h-4" />
            Contact Us
          </Link>
        </div>
      </div>
    </footer>
  );
}
