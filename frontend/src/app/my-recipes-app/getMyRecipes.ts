import { MyRecipeRow, MOCK_DJANGO_RECIPES } from "../../types/my_recipes";

/**
 * Fetches "My Recipes" rows.
 * For now this simulates pulling from Django DB.
 * Later this function can call Django + Food Central API.
 */
export async function getMyRecipes(): Promise<MyRecipeRow[]> {
  // simulate async DB / API delay
  await new Promise((resolve) => setTimeout(resolve, 150));

  // return a copy to mimic real fetch behavior
  return MOCK_DJANGO_RECIPES.map((recipe) => ({
    id: recipe.id,
    name: recipe.name,
    createdAt: recipe.createdAt,
    updatedAt: recipe.updatedAt,
  }));
}