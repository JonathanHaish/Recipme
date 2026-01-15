"use client";

import type { MyRecipeRow } from "@/types/my_recipes";
import { MyRecipesClient } from "@/app/my-recipes-app/MyRecipesClient";

export function MyRecipesModal({
  isOpen,
  onClose,
  rows,
}: {
  isOpen: boolean;
  onClose: () => void;
  rows: MyRecipeRow[];
}) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="relative z-[10000] w-full max-w-5xl rounded-xl border-2 border-black bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b-2 border-black px-5 py-4">
          <h2 className="text-xl font-bold text-black">My Recipes</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-2xl font-bold text-black hover:text-gray-600"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Body */}
        <div className="px-5 py-5">
          <MyRecipesClient rows={rows} />
        </div>

        {/* Footer */}
        <div className="flex justify-end border-t-2 border-black px-5 py-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded bg-black px-5 py-2 text-white hover:bg-gray-800 font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}