import { useState } from "react";
import { Trash2 } from "lucide-react";

interface Recipe {
  id?: string;
  authorId?: number;
  name: string;
  type: string;
  instructions?: string;
  image?: string;
  ingredients: Array<{ id: string; name: string; amount: string }>;
  dateCreated?: string;
  dateUpdated?: string;
}

interface EditRecipeModalProps {
  isOpen: boolean;
  onClose: () => void;
  recipes: Recipe[];
  currentUserId?: number;
  isAdmin?: boolean;
  onSelectRecipe: (recipe: Recipe) => void;
  onDeleteRecipes: (recipeIds: string[]) => void;
}

export function EditRecipeModal({
  isOpen,
  onClose,
  recipes,
  currentUserId,
  isAdmin = false,
  onSelectRecipe,
  onDeleteRecipes
}: EditRecipeModalProps) {
  const [selectedRecipeIds, setSelectedRecipeIds] = useState<Set<string>>(new Set());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  if (!isOpen) return null;

  // Filter recipes to only show user's own recipes (unless admin)
  const userRecipes = isAdmin
    ? recipes
    : recipes.filter(recipe => recipe.authorId === currentUserId);

  const handleRowClick = (recipe: Recipe, event?: React.MouseEvent) => {
    // Don't select when clicking checkbox
    const target = event?.target as HTMLElement;
    if (target instanceof HTMLInputElement && target.type === 'checkbox') {
      return;
    }
    if (target?.closest('input[type="checkbox"]')) {
      return;
    }
    onSelectRecipe(recipe);
    onClose();
  };

  const handleToggleSelect = (recipeId: string) => {
    setSelectedRecipeIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(recipeId)) {
        newSet.delete(recipeId);
      } else {
        newSet.add(recipeId);
      }
      return newSet;
    });
  };

  const handleDeleteClick = () => {
    if (selectedRecipeIds.size > 0) {
      setShowDeleteConfirm(true);
    }
  };

  const handleConfirmDelete = () => {
    onDeleteRecipes(Array.from(selectedRecipeIds));
    setSelectedRecipeIds(new Set());
    setShowDeleteConfirm(false);
    onClose();
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="relative z-[10000] w-full max-w-4xl rounded-xl border-2 border-black bg-white shadow-xl max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b-2 border-black px-5 py-4">
          <h2 className="text-xl font-bold text-black">
            {isAdmin ? 'Edit Recipe (Admin)' : 'Edit Your Recipe'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-2xl font-bold text-black hover:text-gray-600"
          >
            ×
          </button>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {userRecipes.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-lg text-gray-600 mb-2">No recipes to edit</p>
              <p className="text-sm text-gray-500">
                {isAdmin ? 'No recipes found' : 'You haven\'t created any recipes yet'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-black">
                    <th className="text-left px-4 py-3 text-sm font-bold text-black w-12">
                      <input
                        type="checkbox"
                        checked={selectedRecipeIds.size === userRecipes.length && userRecipes.length > 0}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedRecipeIds(new Set(userRecipes.map(r => r.id!)));
                          } else {
                            setSelectedRecipeIds(new Set());
                          }
                        }}
                        onClick={(e) => e.stopPropagation()}
                        className="cursor-pointer"
                      />
                    </th>
                    <th className="text-left px-4 py-3 text-sm font-bold text-black">ID</th>
                    <th className="text-left px-4 py-3 text-sm font-bold text-black">Name</th>
                    <th className="text-left px-4 py-3 text-sm font-bold text-black">Type</th>
                    <th className="text-left px-4 py-3 text-sm font-bold text-black">Ingredients</th>
                    <th className="text-left px-4 py-3 text-sm font-bold text-black">Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {userRecipes.map((recipe) => (
                    <tr
                      key={recipe.id}
                      onClick={(e) => handleRowClick(recipe, e)}
                      className={`border-b border-gray-300 hover:bg-gray-100 cursor-pointer transition-colors ${
                        selectedRecipeIds.has(recipe.id || '') ? 'bg-gray-200' : ''
                      }`}
                    >
                      <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={selectedRecipeIds.has(recipe.id || '')}
                          onChange={() => handleToggleSelect(recipe.id!)}
                          onClick={(e) => e.stopPropagation()}
                          className="cursor-pointer"
                        />
                      </td>
                      <td className="px-4 py-3 text-sm text-black">{recipe.id}</td>
                      <td className="px-4 py-3 text-sm font-medium text-black">{recipe.name}</td>
                      <td className="px-4 py-3 text-sm text-black capitalize">{recipe.type}</td>
                      <td className="px-4 py-3 text-sm text-black">{recipe.ingredients.length}</td>
                      <td className="px-4 py-3 text-sm text-black">{recipe.dateUpdated || "N/A"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex justify-between items-center border-t-2 border-black px-5 py-3">
          <button
            type="button"
            onClick={handleDeleteClick}
            disabled={selectedRecipeIds.size === 0}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <Trash2 className="w-4 h-4" />
            Delete ({selectedRecipeIds.size})
          </button>
          <button
            type="button"
            onClick={onClose}
            className="rounded bg-black px-5 py-2 text-white hover:bg-gray-800 font-medium"
          >
            Close
          </button>
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div
            className="fixed inset-0 z-[10001] flex items-center justify-center bg-black/50 p-4"
            onClick={handleCancelDelete}
          >
            <div
              className="relative z-[10002] w-full max-w-md rounded-xl border-2 border-black bg-white shadow-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="px-5 py-4 border-b-2 border-black">
                <h3 className="text-lg font-bold text-black">Confirm Delete</h3>
              </div>
              <div className="px-5 py-4">
                <p className="text-black mb-2">
                  Are you sure you want to delete {selectedRecipeIds.size} recipe{selectedRecipeIds.size > 1 ? 's' : ''}?
                </p>
                <p className="text-sm text-gray-600">This action cannot be undone.</p>
              </div>
              <div className="flex justify-end gap-2 px-5 py-3 border-t-2 border-black">
                <button
                  type="button"
                  onClick={handleCancelDelete}
                  className="px-4 py-2 border border-black rounded hover:bg-gray-100 text-black font-medium"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleConfirmDelete}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-medium"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
