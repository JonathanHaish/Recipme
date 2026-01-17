import { RecipeCard } from "@/app/recipe_configure/components/RecipeCard"

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

interface RecipeGridProps {
  recipes: Recipe[];
  onEdit: (recipe: Recipe) => void;
  onViewDetails: (recipe: Recipe) => void;
  onToggleLike: (recipeId: string) => void;
  onToggleSave: (recipeId: string) => void;
  isAdmin?: boolean;
  searchQuery?: string;
}

export function RecipeGrid({ 
  recipes, 
  onEdit, 
  onViewDetails,
  onToggleLike, 
  onToggleSave,
  isAdmin = false,
  searchQuery = ""
}: RecipeGridProps) {
  const filteredRecipes = recipes.filter(recipe =>
    recipe.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    recipe.type.toLowerCase().includes(searchQuery.toLowerCase())
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
      <h2 className="text-xl font-bold mb-6 text-black">
        My Recipes ({filteredRecipes.length})
      </h2>
      <div className="grid grid-cols-3 gap-4">
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
