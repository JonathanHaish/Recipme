import { apiClient } from './auth';

const API_URL = typeof window !== 'undefined' 
  ? (window as any).ENV?.API_URL || 'http://localhost:8000'
  : 'http://localhost:8000';

interface Ingredient {
  id: number;
  name: string;
  category?: string;
  description?: string;
  fat_str?: string;
}

interface IngredientsResponse {
  status: number;
  res: Ingredient[];
}

interface NutritionValue {
  value: number;
  unit: string;
}

interface NutritionData {
  protein?: NutritionValue;
  calories?: NutritionValue;
  carbohydrates?: NutritionValue;
  fiber?: NutritionValue;
  fat?: NutritionValue;
  sugars?: NutritionValue;
}

interface NutritionResponse {
  status: number;
  res: NutritionData;
}

export const ingredientsAPI = {
  /**
   * Search for ingredients by food name
   * @param foodName - The name of the food to search for
   * @returns Array of ingredient options
   */
  searchIngredients: async (foodName: string): Promise<Ingredient[]> => {
    try {
      const response = await fetch(
        `${API_URL}/api/ingredients/?data=${encodeURIComponent(foodName)}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to search ingredients');
      }
      
      const data: IngredientsResponse = await response.json();
      return data.res || [];
    } catch (error) {
      console.error('Error searching ingredients:', error);
      throw error;
    }
  },

  /**
   * Get nutrition data for a specific ingredient by ID
   * @param foodId - The ID of the food item
   * @returns Nutrition data object
   */
  getNutritionData: async (foodId: number): Promise<NutritionData> => {
    try {
      const response = await fetch(
        `${API_URL}/api/ingredients/nutritions/?data=${foodId}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch nutrition data');
      }
      
      const data: NutritionResponse = await response.json();
      return data.res || {};
    } catch (error) {
      console.error('Error fetching nutrition data:', error);
      throw error;
    }
  },
};

interface RecipeIngredient {
  ingredient_name: string;
  quantity: string;
  unit?: string;
  note?: string;
}

interface BackendRecipe {
  id?: number;
  title: string;
  description: string;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  servings?: number;
  status: string;
  instructions: string;
  ingredients: RecipeIngredient[];
  created_at?: string;
  updated_at?: string;
  likes_count?: number;
  is_liked?: boolean;
  is_saved?: boolean;
}

interface FrontendRecipe {
  id?: string;
  name: string;
  type: string;
  instructions?: string;
  image?: string;
  ingredients: Array<{
    id: string;
    name: string;
    amount: string;
    fdc_id?: number;
  }>;
}

export const recipesAPI = {
  /**
   * Create a new recipe
   * @param recipe - Recipe data from frontend
   * @returns Created recipe data
   */
  createRecipe: async (recipe: FrontendRecipe): Promise<BackendRecipe> => {
    try {
      // Transform frontend format to backend format
      const backendRecipe: any = {
        title: recipe.name,
        description: recipe.type || recipe.name, // Use type or name as description
        status: 'draft',
        instructions: recipe.instructions || '', // Use instructions from form
        recipe_ingredients: recipe.ingredients.map((ing) => {
          const ingredientData: any = {
            ingredient: {
              name: ing.name,
              id: ing.fdc_id, // Include fdc_id in ingredient dict
            },
            quantity: ing.amount,
            fdc_id: ing.fdc_id, // Also include as separate field for serializer
          };
          return ingredientData;
        }),
      };

      // Debug: log what we're sending
      console.log('Sending recipe data:', JSON.stringify(backendRecipe, null, 2));

      // Use apiClient for authenticated requests with automatic token refresh
      return await apiClient.request<BackendRecipe>(`${API_URL}/recipes/recipes/`, {
        method: 'POST',
        body: JSON.stringify(backendRecipe),
      });
    } catch (error: any) {
      console.error('Error creating recipe:', error);
      // If it's an error with a message, throw it; otherwise throw a generic error
      if (error && error.message) {
        throw error;
      }
      throw new Error('Failed to create recipe. Please check the console for details.');
    }
  },

  /**
   * Update an existing recipe
   * @param recipeId - ID of the recipe to update
   * @param recipe - Updated recipe data
   * @returns Updated recipe data
   */
  updateRecipe: async (recipeId: string, recipe: FrontendRecipe): Promise<BackendRecipe> => {
    try {
      const backendRecipe: any = {
        title: recipe.name,
        description: recipe.type || recipe.name,
        status: 'draft',
        instructions: recipe.instructions || '',
        recipe_ingredients: recipe.ingredients.map((ing) => ({
          ingredient: {
            name: ing.name,
            id: ing.fdc_id,
          },
          quantity: ing.amount,
          fdc_id: ing.fdc_id,
        })),
      };

      // Use apiClient for authenticated requests
      return await apiClient.request<BackendRecipe>(`${API_URL}/recipes/recipes/${recipeId}/`, {
        method: 'PUT',
        body: JSON.stringify(backendRecipe),
      });
    } catch (error) {
      console.error('Error updating recipe:', error);
      throw error;
    }
  },

  /**
   * Get user's recipes
   * @returns Array of user's recipes
   */
  getMyRecipes: async (): Promise<BackendRecipe[]> => {
    try {
      // Use apiClient for authenticated requests
      return await apiClient.request<BackendRecipe[]>(`${API_URL}/recipes/recipes/my_recipes/`);
    } catch (error) {
      console.error('Error fetching recipes:', error);
      throw error;
    }
  },

  /**
   * Search recipes by query
   * @param query - Search query string
   * @returns Array of matching recipes
   */
  searchRecipes: async (query: string): Promise<BackendRecipe[]> => {
    try {
      const encodedQuery = encodeURIComponent(query);
      return await apiClient.request<BackendRecipe[]>(`${API_URL}/recipes/recipes/search/?q=${encodedQuery}`);
    } catch (error) {
      console.error('Error searching recipes:', error);
      throw error;
    }
  },

  /**
   * Filter recipes by type
   * @param type - Recipe type/description
   * @returns Array of filtered recipes
   */
  filterByType: async (type: string): Promise<BackendRecipe[]> => {
    try {
      const encodedType = encodeURIComponent(type);
      return await apiClient.request<BackendRecipe[]>(`${API_URL}/recipes/recipes/filter_by_type/?type=${encodedType}`);
    } catch (error) {
      console.error('Error filtering recipes by type:', error);
      throw error;
    }
  },

  /**
   * Get top 10 liked recipes
   * @returns Array of top liked recipes
   */
  getTopLiked: async (): Promise<BackendRecipe[]> => {
    try {
      return await apiClient.request<BackendRecipe[]>(`${API_URL}/recipes/recipes/top_liked/`);
    } catch (error) {
      console.error('Error fetching top liked recipes:', error);
      throw error;
    }
  },

  /**
   * Get user's saved recipes
   * @returns Array of saved recipes
   */
  getSavedRecipes: async (): Promise<BackendRecipe[]> => {
    try {
      return await apiClient.request<BackendRecipe[]>(`${API_URL}/recipes/recipes/saved/`);
    } catch (error) {
      console.error('Error fetching saved recipes:', error);
      throw error;
    }
  },

  /**
   * Toggle like on a recipe
   * @param recipeId - Recipe ID
   * @returns Object with liked status and likes_count
   */
  toggleLike: async (recipeId: string): Promise<{ liked: boolean; likes_count: number }> => {
    try {
      return await apiClient.request<{ liked: boolean; likes_count: number }>(
        `${API_URL}/recipes/recipes/${recipeId}/toggle_like/`,
        { method: 'POST' }
      );
    } catch (error) {
      console.error('Error toggling like:', error);
      throw error;
    }
  },

  /**
   * Toggle save on a recipe
   * @param recipeId - Recipe ID
   * @returns Object with saved status
   */
  toggleSave: async (recipeId: string): Promise<{ saved: boolean }> => {
    try {
      return await apiClient.request<{ saved: boolean }>(
        `${API_URL}/recipes/recipes/${recipeId}/toggle_save/`,
        { method: 'POST' }
      );
    } catch (error) {
      console.error('Error toggling save:', error);
      throw error;
    }
  },

  /**
   * Delete a recipe
   * @param recipeId - Recipe ID to delete
   * @returns void
   */
  deleteRecipe: async (recipeId: string): Promise<void> => {
    try {
      await apiClient.request<void>(
        `${API_URL}/recipes/recipes/${recipeId}/`,
        { method: 'DELETE' }
      );
    } catch (error) {
      console.error('Error deleting recipe:', error);
      throw error;
    }
  },
};

export type { Ingredient, NutritionData, FrontendRecipe, BackendRecipe };

