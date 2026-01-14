import { Heart, Bookmark, Edit } from "lucide-react";

interface Recipe {
  id?: string;
  name: string;
  type: string;
  dateCreated?: string;
  dateUpdated?: string;
  image?: string;
  ingredients: Array<{ id: string; name: string; amount: string }>;
  isLiked?: boolean;
  isSaved?: boolean;
}

interface RecipeCardProps {
  recipe: Recipe;
  onEdit: (recipe: Recipe) => void;
  onToggleLike: (recipeId: string) => void;
  onToggleSave: (recipeId: string) => void;
}

export function RecipeCard({ recipe, onEdit, onToggleLike, onToggleSave }: RecipeCardProps) {
  return (
    <div className="bg-white border-2 border-black rounded-lg overflow-hidden">
      {/* Header with ID and icons */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-black">
        <span className="text-sm text-black">ID: {recipe.id}</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onToggleLike(recipe.id!)}
            className="flex items-center gap-1"
          >
            <Heart
              className={`w-4 h-4 text-black stroke-black ${
                recipe.isLiked ? "fill-black" : ""
              }`}
            />
          </button>
          <button onClick={() => onToggleSave(recipe.id!)}>
            <Bookmark
              className={`w-4 h-4 text-black stroke-black ${
                recipe.isSaved ? "fill-black" : ""
              }`}
            />
          </button>
        </div>
      </div>

      {/* Image */}
      {recipe.image ? (
        <div className="h-40 bg-white border-b border-black">
          <img
            src={recipe.image}
            alt={recipe.name}
            className="w-full h-full object-cover"
          />
        </div>
      ) : (
        <div className="h-40 bg-white border-b border-black"></div>
      )}

      {/* Category Tag */}
      <div className="px-3 py-2 border-b border-black">
        <span className="inline-block px-2 py-1 border border-black rounded text-sm text-black capitalize">
          {recipe.type}
        </span>
      </div>

      {/* Name/Title */}
      <div className="px-3 py-3 border-b border-black">
        <h3 className="text-xl font-bold text-black">{recipe.name}</h3>
        <p className="text-sm text-gray-600 mt-2">
          <span className="font-medium">Ingredients:</span> {recipe.ingredients.length}
        </p>
        <p className="text-sm text-gray-600 mt-1">
          <span className="font-medium">Updated:</span> {recipe.dateUpdated || "N/A"}
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-2 p-3">
        <button
          type="button"
          onClick={() => onEdit(recipe)}
          className="p-2 border border-black rounded hover:bg-gray-100"
        >
          <Edit className="w-5 h-5 text-black stroke-black" />
        </button>
        <button
          type="button"
          onClick={() => onEdit(recipe)}
          className="flex-1 py-2 border border-black rounded hover:bg-gray-100 font-medium text-black"
        >
          View Details
        </button>
      </div>
    </div>
  );
}
