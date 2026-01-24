"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        // If logged in, go to recipes
        router.push("/recipes");
      } else {
        // If not logged in, go to login
        router.push("/login");
      }
    }
  }, [isAuthenticated, loading, router]);

  return (
    <div className="flex flex-1 items-center justify-center bg-zinc-50 dark:bg-black">
      <div className="text-center">
        <p className="text-zinc-600 dark:text-zinc-400">
          {loading ? "Loading..." : "Redirecting..."}
        </p>
      </div>
    </div>
  );
}
