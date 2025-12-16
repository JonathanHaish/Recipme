"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // מעבר אוטומטי לעמוד ההתחברות
    router.push("/login");
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <div className="text-center">
        <p className="text-zinc-600 dark:text-zinc-400">מעבר לעמוד ההתחברות...</p>
      </div>
    </div>
  );
}
