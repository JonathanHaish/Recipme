import { Heart, Bookmark, Edit } from "lucide-react";
import { Tag, RecipeNutrition } from "@/lib/api";

interface Recipe {
  id?: string;
  name: string;
  type: string;
  dateCreated?: string;
  dateUpdated?: string;
  image?: string;
  ingredients: Array<{ id: string; name: string; amount: string }>;
  tags?: Tag[];
  isLiked?: boolean;
  isSaved?: boolean;
  likesCount?: number;
  nutrition?: RecipeNutrition;
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
              className="flex items-center gap-1 p-1.5 hover:bg-gray-100 rounded"
            >
              <Heart
                className={`w-4 h-4 sm:w-3.5 sm:h-3.5 text-black stroke-black ${
                  recipe.isLiked ? "fill-black" : ""
                }`}
              />
            </button>
            {recipe.likesCount !== undefined && (
              <span className="text-xs text-black">{recipe.likesCount}</span>
            )}
          </div>
          <button onClick={() => onToggleSave(recipe.id!)} className="p-1.5 hover:bg-gray-100 rounded">
            <Bookmark
              className={`w-4 h-4 sm:w-3.5 sm:h-3.5 text-black stroke-black ${
                recipe.isSaved ? "fill-black" : ""
              }`}
            />
          </button>
          {isAdmin && (
            <button
              onClick={() => onEdit(recipe)}
              className="ml-1 p-1.5 hover:bg-gray-100 rounded"
            >
              <Edit className="w-4 h-4 sm:w-3.5 sm:h-3.5 text-black stroke-black" />
            </button>
          )}
        </div>
      </div>

      {/* Image */}
      {recipe.image ? (
        <div className="h-32 sm:h-24 bg-white border-b border-black">
          <img
            src={recipe.image}
            alt={recipe.name}
            className="w-full h-full object-cover"
          />
        </div>
      ) : (
        <div className="h-32 sm:h-24 bg-white border-b border-black"></div>
      )}

      {/* Tags */}
      <div className="px-2 py-1.5 border-b border-black min-h-[32px]">
        {recipe.tags && recipe.tags.length > 0 ? (
          <div className="flex flex-wrap gap-1">
            {recipe.tags.map((tag) => (
              <span
                key={tag.id}
                className="inline-block px-1.5 py-0.5 border border-black rounded text-xs text-black"
              >
                {tag.name}
              </span>
            ))}
          </div>
        ) : (
          <span className="text-xs text-gray-400 italic">No tags</span>
        )}
      </div>

      {/* Name/Title */}
      <div className="px-2 py-2 border-b border-black">
        <h3 className="text-base font-bold text-black">{recipe.name}</h3>
        <p className="text-xs text-gray-600 mt-1">
          <span className="font-medium">Ingredients:</span> {recipe.ingredients.length}
        </p>
        {recipe.nutrition && (
          <p className="text-xs text-gray-600 mt-0.5">
            <span className="font-medium">Calories:</span> {recipe.nutrition.calories_kcal ? Math.round(Number(recipe.nutrition.calories_kcal)) : 0} kcal
            <span className="ml-2"><span className="font-medium">Protein:</span> {recipe.nutrition.protein_g ? Number(recipe.nutrition.protein_g).toFixed(1) : '0.0'}g</span>
            <span className="ml-2"><span className="font-medium">Fat:</span> {recipe.nutrition.fat_g ? Number(recipe.nutrition.fat_g).toFixed(1) : '0.0'}g</span>
          </p>
        )}
        <p className="text-xs text-gray-600 mt-0.5">
          <span className="font-medium">Updated:</span> {recipe.dateUpdated || "N/A"}
        </p>
      </div>

      {/* Actions */}
      <div className="p-2">
        <button
          type="button"
          onClick={() => onViewDetails(recipe)}
          className="w-full py-2 text-sm border border-black rounded hover:bg-gray-100 font-medium text-black min-h-[44px]"
        >
          View Details
        </button>
      </div>
    </div>
  );
}
