import { apiClient } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

export const tagsAPI = {
  /**
   * Get all active tags
   * @returns Array of tags
   */
  getAllTags: async (): Promise<Tag[]> => {
    try {
      const response = await apiClient.request<PaginatedResponse<Tag>>(`${API_URL}/recipes/tags/`);
      return response.results;
    } catch (error) {
      console.error('Error fetching tags:', error);
      throw error;
    }
  },
};

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

export interface Tag {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface RecipeIngredient {
  ingredient_name: string;
  quantity: string;
  unit?: string;
  note?: string;
}

interface RecipeNutrition {
  calories_kcal?: number | string; // Django Decimal serializes as string
  protein_g?: number | string;
  fat_g?: number | string;
  carbs_g?: number | string;
  fiber_g?: number | string;
  sugars_g?: number | string;
  updated_at?: string;
}

interface BackendRecipe {
  id?: number;
  author?: number;  // User ID of the recipe creator
  title: string;
  description: string;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  servings?: number;
  status: string;
  instructions: string;
  ingredients: RecipeIngredient[];
  tags?: Tag[];
  created_at?: string;
  updated_at?: string;
  likes_count?: number;
  is_liked?: boolean;
  is_saved?: boolean;
  nutrition?: RecipeNutrition;
  image_url?: string;  // Primary image URL
  images?: Array<{id: number; image: string; image_url: string; is_primary: boolean}>;
  youtube_url?: string;
}

interface FrontendRecipe {
  id?: string;
  title: string;  // Changed from 'name' to match backend
  description: string;  // Changed from 'type' to match backend
  instructions?: string;
  image?: string;
  ingredients: Array<{
    id: string;
    name: string;
    amount: string;
    unit?: string;
    fdc_id?: number;
  }>;
  tags?: Tag[];
  nutrition?: RecipeNutrition;
  youtube_url?: string;
}

export const recipesAPI = {
  /**
   * Create a new recipe
   * @param recipe - Recipe data from frontend
   * @returns Created recipe data
   */
  createRecipe: async (recipe: FrontendRecipe): Promise<BackendRecipe> => {
    try {
      // No transformation needed - frontend now uses same field names as backend
      const backendRecipe: any = {
        title: recipe.title,
        description: recipe.description,
        status: 'draft',
        instructions: recipe.instructions || '', // Use instructions from form
        recipe_ingredients: recipe.ingredients.map((ing) => {
          const ingredientData: any = {
            ingredient: {
              name: ing.name,
              id: ing.fdc_id, // Include fdc_id in ingredient dict
            },
            quantity: ing.amount,
            unit: ing.unit || null,
            fdc_id: ing.fdc_id, // Also include as separate field for serializer
          };
          return ingredientData;
        }),
      };

      // Add tag_ids if tags are provided
      if (recipe.tags && recipe.tags.length > 0) {
        backendRecipe.tag_ids = recipe.tags.map(tag => tag.id);
      }

      // Add image if provided
      if (recipe.image) {
        backendRecipe.image = recipe.image;
      }

      // Add youtube_url if provided
      if (recipe.youtube_url) {
        backendRecipe.youtube_url = recipe.youtube_url;
      }

      // Debug: log what we're sending (excluding large image data)
      const logData = { ...backendRecipe };
      if (logData.image) {
        logData.image = `<base64 image data: ${logData.image.substring(0, 50)}...>`;
      }
      console.log('Sending recipe data:', JSON.stringify(logData, null, 2));

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
        title: recipe.title,
        description: recipe.description,
        status: 'draft',
        instructions: recipe.instructions || '',
        recipe_ingredients: recipe.ingredients.map((ing) => ({
          ingredient: {
            name: ing.name,
            id: ing.fdc_id,
          },
          quantity: ing.amount,
          unit: ing.unit || null,
          fdc_id: ing.fdc_id,
        })),
      };

      // Add tag_ids if tags are provided
      if (recipe.tags && recipe.tags.length > 0) {
        backendRecipe.tag_ids = recipe.tags.map(tag => tag.id);
      }

      // Add image if provided
      if (recipe.image) {
        backendRecipe.image = recipe.image;
      }

      // Add youtube_url if provided
      if (recipe.youtube_url) {
        backendRecipe.youtube_url = recipe.youtube_url;
      }

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
   * Get all recipes in the system
   * @param page - Page number (default: 1)
   * @returns Paginated response with recipes
   */
  getAllRecipes: async (page: number = 1): Promise<PaginatedResponse<BackendRecipe>> => {
    try {
      // Use apiClient for authenticated requests
      return await apiClient.request<PaginatedResponse<BackendRecipe>>(`${API_URL}/recipes/recipes/?page=${page}`);
    } catch (error) {
      console.error('Error fetching recipes:', error);
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
      const response = await apiClient.request<PaginatedResponse<BackendRecipe>>(`${API_URL}/recipes/recipes/my_recipes/`);
      return response.results;
    } catch (error) {
      console.error('Error fetching recipes:', error);
      throw error;
    }
  },

  /**
   * Search recipes by query
   * @param query - Search query string
   * @param page - Page number (default: 1)
   * @returns Paginated response with matching recipes
   */
  searchRecipes: async (query: string, page: number = 1): Promise<PaginatedResponse<BackendRecipe>> => {
    try {
      const encodedQuery = encodeURIComponent(query);
      return await apiClient.request<PaginatedResponse<BackendRecipe>>(`${API_URL}/recipes/recipes/search/?q=${encodedQuery}&page=${page}`);
    } catch (error) {
      console.error('Error searching recipes:', error);
      throw error;
    }
  },

  /**
   * Filter recipes by tags
   * @param tagIds - Array of tag IDs
   * @param matchMode - "any" (OR logic) or "all" (AND logic)
   * @returns Array of filtered recipes
   */
  filterByTags: async (tagIds: number[], matchMode: 'any' | 'all' = 'any'): Promise<BackendRecipe[]> => {
    try {
      if (tagIds.length === 0) {
        return [];
      }
      const tagIdsStr = tagIds.join(',');
      const response = await apiClient.request<PaginatedResponse<BackendRecipe>>(
        `${API_URL}/recipes/recipes/filter_by_tags/?tag_ids=${tagIdsStr}&match=${matchMode}`
      );
      return response.results;
    } catch (error) {
      console.error('Error filtering recipes by tags:', error);
      throw error;
    }
  },

  /**
   * Get user's saved recipes
   * @returns Array of saved recipes
   */
  getSavedRecipes: async (): Promise<BackendRecipe[]> => {
    try {
      const response = await apiClient.request<PaginatedResponse<BackendRecipe>>(`${API_URL}/recipes/recipes/saved/`);
      return response.results;
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

  /**
   * Get personalized recipes ordered by user's profile (goals and diet)
   * @param page - Page number (default: 1)
   * @returns Paginated response with personalized recipes
   */
  getPersonalizedRecipes: async (page: number = 1): Promise<PaginatedResponse<BackendRecipe>> => {
    try {
      return await apiClient.request<PaginatedResponse<BackendRecipe>>(`${API_URL}/recipes/recipes/personalized/?page=${page}`);
    } catch (error) {
      console.error('Error fetching personalized recipes:', error);
      throw error;
    }
  },
};

export type { Ingredient, NutritionData, FrontendRecipe, BackendRecipe, RecipeNutrition };

// Profile API
export interface UserProfile {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile_image: string | null;
  profile_image_url: string | null;
  goals: Goal[];
  diet: DietType | null;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  profile_image?: File | string | null;
  goal_ids?: number[];
  diet_id?: number | null;
  description?: string;
}

export interface Goal {
  id: number;
  code: string;
  name: string;
  description?: string;
  is_active: boolean;
  display_order: number;
}

export interface DietType {
  id: number;
  code: string;
  name: string;
  description?: string;
  is_active: boolean;
  display_order: number;
}

export const profileAPI = {
  /**
   * Get all active goals
   */
  getGoals: async (): Promise<Goal[]> => {
    try {
      return await apiClient.request<Goal[]>(`${API_URL}/api/profiles/goals/`);
    } catch (error) {
      console.error('Error fetching goals:', error);
      throw error;
    }
  },

  /**
   * Get all active diet types
   */
  getDietTypes: async (): Promise<DietType[]> => {
    try {
      return await apiClient.request<DietType[]>(`${API_URL}/api/profiles/diet-types/`);
    } catch (error) {
      console.error('Error fetching diet types:', error);
      throw error;
    }
  },

  /**
   * Get current user's profile
   * @returns User profile data
   */
  getProfile: async (): Promise<UserProfile> => {
    try {
      return await apiClient.request<UserProfile>(`${API_URL}/api/profiles/me`);
    } catch (error) {
      console.error('Error fetching profile:', error);
      throw error;
    }
  },

  /**
   * Update current user's profile
   * @param profileData - Profile data to update
   * @returns Updated profile data
   */
  updateProfile: async (profileData: UpdateProfileRequest): Promise<UserProfile> => {
    try {
      const formData = new FormData();

      // Handle profile image
      if (profileData.profile_image instanceof File) {
        formData.append('profile_image', profileData.profile_image);
      }

      // Handle goal_ids - always send, even if empty array
      if (profileData.goal_ids !== undefined) {
        // Send as JSON string for array
        formData.append('goal_ids', JSON.stringify(profileData.goal_ids));
      }

      // Handle diet_id - send if provided
      if (profileData.diet_id !== undefined) {
        formData.append('diet_id', profileData.diet_id !== null ? profileData.diet_id.toString() : '');
      }

      // Handle description - always send if provided
      if (profileData.description !== undefined) {
        formData.append('description', profileData.description);
      }

      return await apiClient.request<UserProfile>(`${API_URL}/api/profiles/me`, {
        method: 'PUT',
        body: formData,
        // Don't set Content-Type header, let browser set it with boundary for FormData
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  },
};

