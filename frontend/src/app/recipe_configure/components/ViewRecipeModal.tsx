interface Ingredient {
  id: string;
  name: string;
  amount: string;
}

interface Recipe {
  id?: string;
  name: string;
  type: string;
  instructions?: string;
  image?: string;
  ingredients: Ingredient[];
  dateCreated?: string;
  dateUpdated?: string;
}

interface ViewRecipeModalProps {
  isOpen: boolean;
  onClose: () => void;
  recipe: Recipe | null;
}

export function ViewRecipeModal({ isOpen, onClose, recipe }: ViewRecipeModalProps) {
  if (!isOpen || !recipe) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="relative z-[10000] w-full max-w-2xl rounded-xl border-2 border-black bg-white shadow-xl max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b-2 border-black px-5 py-4">
          <h2 className="text-xl font-bold text-black">Recipe Details</h2>
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
          {/* Recipe Name */}
          <div className="mb-4">
            <h3 className="text-2xl font-bold text-black">{recipe.name}</h3>
          </div>

          {/* Recipe Type */}
          <div className="mb-4">
            <span className="inline-block px-3 py-1 border border-black rounded text-sm text-black capitalize">
              {recipe.type}
            </span>
          </div>

          {/* Recipe Image */}
          {recipe.image && (
            <div className="mb-4 h-64 bg-white border-2 border-black rounded-lg overflow-hidden">
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
                    <span className="text-gray-700">{ingredient.amount}</span>
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
