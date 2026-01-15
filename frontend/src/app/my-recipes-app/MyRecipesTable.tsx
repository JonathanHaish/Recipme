// import type { MyRecipeRow } from "@/types/my_recipes";

// function formatDate(iso: string) {
//   const d = new Date(iso);
//   if (Number.isNaN(d.getTime())) return iso;
//   return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "2-digit" });
// }

// export function MyRecipesTable({ rows }: { rows: MyRecipeRow[] }) {
//   return (
//     <div className="bg-white border-2 border-black rounded-lg overflow-hidden">
//       {/* Section header */}
//       <div className="flex items-center justify-between px-4 py-3 border-b-2 border-black">
//         <h2 className="text-xl font-bold text-black">My Recipes</h2>
//         <span className="text-sm text-gray-600">{rows.length} total</span>
//       </div>

//       {/* Table */}
//       <div className="overflow-x-auto">
//         <table className="w-full border-collapse">
//           <thead>
//             <tr className="border-b border-black">
//               <th className="text-left px-4 py-3 text-sm font-semibold text-black">Name</th>
//               <th className="text-left px-4 py-3 text-sm font-semibold text-black">Created</th>
//               <th className="text-left px-4 py-3 text-sm font-semibold text-black">Updated</th>
//             </tr>
//           </thead>

//           <tbody>
//             {rows.map((r, idx) => (
//               <tr key={`${r.name}-${r.createdAt}-${idx}`} className="border-b border-gray-200">
//                 <td className="px-4 py-3 text-black font-medium">{r.name}</td>
//                 <td className="px-4 py-3 text-gray-600">{formatDate(r.createdAt)}</td>
//                 <td className="px-4 py-3 text-gray-600">{formatDate(r.updatedAt)}</td>
//               </tr>
//             ))}

//             {rows.length === 0 && (
//               <tr>
//                 <td colSpan={3} className="px-4 py-10 text-center text-gray-600">
//                   No recipes yet. Click <span className="font-medium text-black">Add Recipe</span> to create one.
//                 </td>
//               </tr>
//             )}
//           </tbody>
//         </table>
//       </div>
//     </div>
//   );
// }


import type { MyRecipeRow } from "@/types/my_recipes";

function formatDate(iso: string) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
  });
}

export function MyRecipesTable({
  rows,
  onNameClick,
}: {
  rows: MyRecipeRow[];
  onNameClick?: (recipe: MyRecipeRow) => void;
}) {
  return (
    <div className="bg-white border-2 border-black rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b-2 border-black">
        <h2 className="text-xl font-bold text-black">My Recipes</h2>
        <span className="text-sm text-gray-600">{rows.length} total</span>
      </div>

      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-black">
            <th className="px-4 py-3 text-left text-sm font-semibold text-black">
              Name
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-black">
              Created
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-black">
              Updated
            </th>
          </tr>
        </thead>

        <tbody>
          {rows.map((r, i) => (
            <tr key={`${r.name}-${i}`} className="border-b border-gray-200">
              <td className="px-4 py-3">
                {onNameClick ? (
                  <button
                    type="button"
                    onClick={() => onNameClick(r)}
                    className="text-black font-medium underline underline-offset-2 hover:text-gray-700"
                  >
                    {r.name}
                  </button>
                ) : (
                  <span className="text-black">{r.name}</span>
                )}
              </td>

              <td className="px-4 py-3 text-gray-600">
                {formatDate(r.createdAt)}
              </td>

              <td className="px-4 py-3 text-gray-600">
                {formatDate(r.updatedAt)}
              </td>
            </tr>
          ))}

          {rows.length === 0 && (
            <tr>
              <td colSpan={3} className="px-4 py-10 text-center text-gray-600">
                No recipes yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}