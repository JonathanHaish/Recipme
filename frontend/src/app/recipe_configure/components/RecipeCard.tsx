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
  likesCount?: number;
  authorUsername?: string;
  authorFirstName?: string;
  authorLastName?: string;
}

interface RecipeCardProps {
  recipe: Recipe;
  onEdit: (recipe: Recipe) => void;
  onViewDetails: (recipe: Recipe) => void;
  onToggleLike: (recipeId: string) => void;
  onToggleSave: (recipeId: string) => void;
  isAdmin?: boolean;
}

export function RecipeCard({ recipe, onEdit, onViewDetails, onToggleLike, onToggleSave, isAdmin = false }: RecipeCardProps) {
  return (
    <div className="bg-white border-2 border-black rounded-lg overflow-hidden">
      {/* Header with ID and icons */}
      <div className="flex items-center justify-between px-2 py-1.5 border-b border-black">
        <span className="text-xs text-black">ID: {recipe.id}</span>
        <div className="flex items-center gap-1.5">
          <div className="flex items-center gap-0.5">
            <button
              onClick={() => onToggleLike(recipe.id!)}
              className="flex items-center gap-1"
            >
              <Heart
                className={`w-3.5 h-3.5 text-black stroke-black ${
                  recipe.isLiked ? "fill-black" : ""
                }`}
              />
            </button>
            {recipe.likesCount !== undefined && (
              <span className="text-xs text-black">{recipe.likesCount}</span>
            )}
          </div>
          <button onClick={() => onToggleSave(recipe.id!)}>
            <Bookmark
              className={`w-3.5 h-3.5 text-black stroke-black ${
                recipe.isSaved ? "fill-black" : ""
              }`}
            />
          </button>
          {isAdmin && (
            <button
              onClick={() => onEdit(recipe)}
              className="ml-1"
            >
              <Edit className="w-3.5 h-3.5 text-black stroke-black" />
            </button>
          )}
        </div>
      </div>

      {/* Image */}
      {recipe.image ? (
        <div className="h-24 bg-white border-b border-black">
          <img
            src={recipe.image}
            alt={recipe.name}
            className="w-full h-full object-cover"
          />
        </div>
      ) : (
        <div className="h-24 bg-white border-b border-black"></div>
      )}

      {/* Category Tag */}
      <div className="px-2 py-1.5 border-b border-black">
        <span className="inline-block px-1.5 py-0.5 border border-black rounded text-xs text-black capitalize">
          {recipe.type}
        </span>
      </div>

      {/* Name/Title */}
      <div className="px-2 py-2 border-b border-black">
        <h3 className="text-base font-bold text-black">{recipe.name}</h3>
        {recipe.authorUsername && (
          <p className="text-xs text-gray-600 mt-1">
            <span className="font-medium">By:</span> {
              recipe.authorFirstName && recipe.authorLastName
                ? `${recipe.authorFirstName} ${recipe.authorLastName}`
                : recipe.authorUsername
            }
          </p>
        )}
        <p className="text-xs text-gray-600 mt-0.5">
          <span className="font-medium">Ingredients:</span> {recipe.ingredients.length}
        </p>
        <p className="text-xs text-gray-600 mt-0.5">
          <span className="font-medium">Updated:</span> {recipe.dateUpdated || "N/A"}
        </p>
      </div>

      {/* Actions */}
      <div className="p-2">
        <button
          type="button"
          onClick={() => onViewDetails(recipe)}
          className="w-full py-1.5 text-xs border border-black rounded hover:bg-gray-100 font-medium text-black"
        >
          View Details
        </button>
      </div>
    </div>
  );
}
