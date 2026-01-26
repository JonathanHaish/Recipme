import { RecipeCard } from "@/app/recipe_configure/components/RecipeCard"
import { RecipeCardSkeleton } from "@/app/recipe_configure/components/RecipeCardSkeleton"

interface Recipe {
  id?: string;
  title: string;  // Changed from 'name' to match backend
  description: string;  // Changed from 'type' to match backend
  dateCreated?: string;
  dateUpdated?: string;
  image?: string;
  ingredients: Array<{ id: string; name: string; amount: string }>;
  isLiked?: boolean;
  isSaved?: boolean;
}

interface RecipeGridProps {
  recipes: Recipe[];
  onEdit: (recipe: Recipe) => void;
  onViewDetails: (recipe: Recipe) => void;
  onToggleLike: (recipeId: string) => void;
  onToggleSave: (recipeId: string) => void;
  isAdmin?: boolean;
  searchQuery?: string;
  isLoading?: boolean;
}

export function RecipeGrid({
  recipes,
  onEdit,
  onViewDetails,
  onToggleLike,
  onToggleSave,
  isAdmin = false,
  searchQuery = "",
  isLoading = false
}: RecipeGridProps) {
  // Show skeleton loaders while loading
  if (isLoading) {
    return (
      <div>
        <div className="h-7 bg-gray-300 rounded w-32 mb-4 sm:mb-6 animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {[...Array(6)].map((_, i) => (
            <RecipeCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  const filteredRecipes = recipes.filter(recipe =>
    recipe.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    recipe.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (recipes.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-gray-600 mb-2">No recipes yet</p>
        <p className="text-sm text-gray-500">Create your first recipe to get started</p>
      </div>
    );
  }

  if (filteredRecipes.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-gray-600 mb-2">No recipes found for "{searchQuery}"</p>
        <p className="text-sm text-gray-500">Try searching for something else</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg sm:text-xl font-bold mb-4 sm:mb-6 text-black">
        All Recipes ({filteredRecipes.length})
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        {filteredRecipes.map((recipe) => (
          <RecipeCard
            key={recipe.id}
            recipe={recipe}
            onEdit={onEdit}
            onViewDetails={onViewDetails}
            onToggleLike={onToggleLike}
            onToggleSave={onToggleSave}
            isAdmin={isAdmin}
          />
        ))}
      </div>
    </div>
  );
}
