import { Tag, RecipeNutrition } from "@/lib/api";
import { Edit, Trash2 } from "lucide-react";

interface Ingredient {
  id: string;
  name: string;
  amount: string;
  unit?: string;
}

interface Recipe {
  id?: string;
  authorId?: number;
  name: string;
  type: string;
  instructions?: string;
  image?: string;
  ingredients: Ingredient[];
  tags?: Tag[];
  dateCreated?: string;
  dateUpdated?: string;
  nutrition?: RecipeNutrition;
}

interface ViewRecipeModalProps {
  isOpen: boolean;
  onClose: () => void;
  recipe: Recipe | null;
  currentUserId?: number;
  isAdmin?: boolean;
  onEdit?: (recipe: Recipe) => void;
  onDelete?: (recipeId: string) => void;
}

export function ViewRecipeModal({
  isOpen,
  onClose,
  recipe,
  currentUserId,
  isAdmin = false,
  onEdit,
  onDelete
}: ViewRecipeModalProps) {
  if (!isOpen || !recipe) return null;

  // Check if current user can edit/delete (owner or admin)
  const canModify = isAdmin || (currentUserId && recipe.authorId === currentUserId);

  const handleEdit = () => {
    if (onEdit && recipe) {
      onEdit(recipe);
      onClose();
    }
  };

  const handleDelete = () => {
    if (onDelete && recipe.id && confirm('Are you sure you want to delete this recipe?')) {
      onDelete(recipe.id);
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="relative z-[10000] w-full max-w-full sm:max-w-2xl rounded-xl border-2 border-black bg-white shadow-xl max-h-[95vh] sm:max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b-2 border-black px-4 sm:px-5 py-3 sm:py-4">
          <h2 className="text-lg sm:text-xl font-bold text-black">Recipe Details</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-2xl font-bold text-black hover:text-gray-600"
          >
            ×
          </button>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-5 py-3 sm:py-4">
          {/* Recipe Name */}
          <div className="mb-4">
            <h3 className="text-2xl font-bold text-black">{recipe.name}</h3>
          </div>

          {/* Recipe Tags */}
          <div className="mb-4">
            {recipe.tags && recipe.tags.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {recipe.tags.map((tag) => (
                  <span
                    key={tag.id}
                    className="inline-block px-3 py-1 border border-black rounded text-sm text-black font-medium"
                  >
                    {tag.name}
                  </span>
                ))}
              </div>
            ) : (
              <span className="text-sm text-gray-400 italic">No tags</span>
            )}
          </div>

          {/* Recipe Image */}
          {recipe.image && (
            <div className="mb-4 h-48 sm:h-64 bg-white border-2 border-black rounded-lg overflow-hidden">
              <img
                src={recipe.image}
                alt={recipe.name}
                className="w-full h-full object-cover"
              />
            </div>
          )}

          {/* Recipe ID and Dates */}
          <div className="mb-4 text-sm text-gray-600 space-y-1">
            {recipe.id && <p><span className="font-medium">ID:</span> {recipe.id}</p>}
            {recipe.dateCreated && (
              <p><span className="font-medium">Created:</span> {new Date(recipe.dateCreated).toLocaleDateString()}</p>
            )}
            {recipe.dateUpdated && (
              <p><span className="font-medium">Updated:</span> {new Date(recipe.dateUpdated).toLocaleDateString()}</p>
            )}
          </div>

          {/* Nutrition Information */}
          {recipe.nutrition && (
            <div className="mb-4">
              <h4 className="text-lg font-bold text-black mb-2">Nutrition Information</h4>
              <div className="grid grid-cols-2 gap-3 p-3 border-2 border-black rounded-lg bg-gray-50">
                <div className="flex flex-col">
                  <span className="text-xs text-gray-600 font-medium">Calories</span>
                  <span className="text-lg font-bold text-black">
                    {recipe.nutrition.calories_kcal ? Math.round(Number(recipe.nutrition.calories_kcal)) : 0} kcal
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-600 font-medium">Protein</span>
                  <span className="text-lg font-bold text-black">
                    {recipe.nutrition.protein_g ? Number(recipe.nutrition.protein_g).toFixed(1) : '0.0'} g
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-600 font-medium">Fat</span>
                  <span className="text-lg font-bold text-black">
                    {recipe.nutrition.fat_g ? Number(recipe.nutrition.fat_g).toFixed(1) : '0.0'} g
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-600 font-medium">Carbohydrates</span>
                  <span className="text-lg font-bold text-black">
                    {recipe.nutrition.carbs_g ? Number(recipe.nutrition.carbs_g).toFixed(1) : '0.0'} g
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-600 font-medium">Fiber</span>
                  <span className="text-lg font-bold text-black">
                    {recipe.nutrition.fiber_g ? Number(recipe.nutrition.fiber_g).toFixed(1) : '0.0'} g
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-gray-600 font-medium">Sugars</span>
                  <span className="text-lg font-bold text-black">
                    {recipe.nutrition.sugars_g ? Number(recipe.nutrition.sugars_g).toFixed(1) : '0.0'} g
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Ingredients */}
          <div className="mb-4">
            <h4 className="text-lg font-bold text-black mb-2">Ingredients ({recipe.ingredients.length})</h4>
            {recipe.ingredients.length > 0 ? (
              <div className="space-y-2">
                {recipe.ingredients.map((ingredient, index) => (
                  <div
                    key={ingredient.id || index}
                    className="flex items-center justify-between py-2 px-3 border border-gray-300 rounded bg-gray-50"
                  >
                    <span className="text-black font-medium">{ingredient.name}</span>
                    <span className="text-gray-700 font-medium">
                      {ingredient.amount} g
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">No ingredients listed</p>
            )}
          </div>

          {/* Instructions */}
          {recipe.instructions && (
            <div className="mb-4">
              <h4 className="text-lg font-bold text-black mb-2">Instructions</h4>
              <div className="px-3 py-2 border border-gray-300 rounded bg-gray-50">
                <p className="text-black whitespace-pre-wrap">{recipe.instructions}</p>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex flex-col-reverse sm:flex-row justify-between gap-2 sm:gap-0 border-t-2 border-black px-4 sm:px-5 py-3">
          <div className="flex flex-col sm:flex-row gap-2">
            {canModify && onEdit && (
              <button
                type="button"
                onClick={handleEdit}
                className="flex items-center justify-center gap-2 rounded border-2 border-black bg-white px-4 py-2 text-black hover:bg-gray-100 font-medium min-h-[44px]"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
            )}
            {canModify && onDelete && (
              <button
                type="button"
                onClick={handleDelete}
                className="flex items-center justify-center gap-2 rounded border-2 border-red-600 bg-white px-4 py-2 text-red-600 hover:bg-red-50 font-medium min-h-[44px]"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded bg-black px-5 py-2 text-white hover:bg-gray-800 font-medium min-h-[44px]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
