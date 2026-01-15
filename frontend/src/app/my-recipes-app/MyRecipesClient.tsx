// "use client";

// import { useMemo, useState } from "react";
// import { Search } from "lucide-react";
// import type { MyRecipeRow } from "@/types/my_recipes";
// import { MyRecipesTable } from "@/app/my-recipes-app/MyRecipesTable";

// export function MyRecipesClient({ rows }: { rows: MyRecipeRow[] }) {
//   const [query, setQuery] = useState("");

//   const filteredRows = useMemo(() => {
//     const q = query.trim().toLowerCase();
//     if (!q) return rows;

//     return rows.filter((r) => r.name.toLowerCase().includes(q));
//   }, [rows, query]);

//   return (
//     <div className="space-y-4">
//       {/* Search bar */}
//       <div className="relative">
//         <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-black" />
//         <input
//           value={query}
//           onChange={(e) => setQuery(e.target.value)}
//           placeholder="Search my recipes..."
//           className="w-full pl-10 pr-3 py-2 border border-black rounded text-black bg-white"
//         />
//       </div>

//       {/* Table */}
//       <MyRecipesTable rows={filteredRows} />
//     </div>
//   );
// }

"use client";

import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import type { MyRecipeRow } from "@/types/my_recipes";
import { MyRecipesTable } from "@/app/my-recipes-app/MyRecipesTable";

export function MyRecipesClient({ rows }: { rows: MyRecipeRow[] }) {
  const [query, setQuery] = useState("");

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState<MyRecipeRow | null>(null);

  const filteredRows = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => r.name.toLowerCase().includes(q));
  }, [rows, query]);

  const openRecipeModal = (recipe: MyRecipeRow) => {
    setSelectedRecipe(recipe);
    setIsModalOpen(true);

    // Placeholder: can fetch full recipe + notes here later
    // e.g. fetchRecipeDetails(recipeId) then set state
  };

  const closeRecipeModal = () => {
    setIsModalOpen(false);
    setSelectedRecipe(null);
  };

  return (
    <div className="space-y-4">
      {/* Search bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-black" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search my recipes..."
          className="w-full pl-10 pr-3 py-2 border border-black rounded text-black bg-white"
        />
      </div>

      {/* Table (name click opens modal) */}
      <MyRecipesTable rows={filteredRows} onNameClick={openRecipeModal} />

      {/* Modal placeholder */}
      {isModalOpen && (
        <div
          className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
          onClick={closeRecipeModal}
        >
          <div
            className="relative z-[10000] w-full max-w-2xl rounded-xl border-2 border-black bg-white shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b-2 border-black px-5 py-4">
              <h2 className="text-xl font-bold text-black">
                {selectedRecipe?.name ?? "Recipe"}
              </h2>
              <button
                type="button"
                onClick={closeRecipeModal}
                className="text-2xl font-bold text-black hover:text-gray-600"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            {/* Body (empty placeholder) */}
            <div className="px-5 py-6">
              {/* Intentionally empty — partner will attach recipe details + notes here */}
              <div className="rounded-lg border border-dashed border-gray-400 p-6 text-center text-gray-600">
                Placeholder modal body (empty for now)
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end border-t-2 border-black px-5 py-3">
              <button
                type="button"
                onClick={closeRecipeModal}
                className="rounded bg-black px-5 py-2 text-white hover:bg-gray-800 font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}