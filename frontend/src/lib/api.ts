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

export type { Ingredient, NutritionData };

