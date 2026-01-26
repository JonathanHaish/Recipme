import { useState } from "react";
import { RecipeModal } from "./components/RecipeModal";
import { RecipeGrid } from "./components/RecipeGrid";
import { CreateRecipeButton } from "./components/CreateRecipeButton";
import { Tag } from "@/lib/api";

interface Ingredient {
  id: string;
  name: string;
  amount: string;
  unit?: string;
  fdc_id?: number;
}

interface Recipe {
  id?: string;
  title: string;
  description: string;
  instructions?: string;
  image?: string;
  ingredients: Ingredient[];
  tags?: Tag[];
  youtube_url?: string;
}

export  function RecipeConfig() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  const handleCreateNew = () => {
    setModalMode("create");
    setSelectedRecipe(null);
    setIsModalOpen(true);
  };

  // const handleEdit = (recipe: Recipe) => {
  //   setModalMode("edit");
  //   setSelectedRecipe(recipe);
  //   setIsModalOpen(true);
  // };

  // const handleToggleLike = (recipeId: string) => {
  //   setRecipes(
  //     recipes.map((recipe) =>
  //       recipe.id === recipeId ? { ...recipe, isLiked: !recipe.isLiked } : recipe
  //     )
  //   );
  // };

  // const handleToggleSave = (recipeId: string) => {
  //   setRecipes(
  //     recipes.map((recipe) =>
  //       recipe.id === recipeId ? { ...recipe, isSaved: !recipe.isSaved } : recipe
  //     )
  //   );
  // };

  const handleSaveRecipe = (recipe: Recipe) => {
    if (modalMode === "create") {
      const newRecipe = {
        ...recipe,
        id: Date.now().toString(),
      };
      setRecipes([...recipes, newRecipe]);
    } else {
      setRecipes(
        recipes.map((r) => (r.id === selectedRecipe?.id ? { ...recipe, id: r.id } : r))
      );
    }
  };

  

  return (
    <div>
      <div>
        
          
        <CreateRecipeButton onClick={handleCreateNew} />
        {/* Recipe Grid */}
        {/* <RecipeGrid
          recipes={recipes}
          onEdit={handleEdit}
          onToggleLike={handleToggleLike}
          onToggleSave={handleToggleSave}
        /> */}

        {/* Recipe Modal */}
        <RecipeModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSave={handleSaveRecipe}
          recipe={selectedRecipe}
          mode={modalMode}
        />
      </div>
    </div>
  );
}


