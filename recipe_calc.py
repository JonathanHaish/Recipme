
from POC_api import *

def calculate_recipe_nutrition(ingredients: List[Dict], fdc_api: FoodDataCentralAPI) -> Dict:
    """
    Calculate total nutrition for a recipe
    
    Args:
        ingredients: List of dicts with 'fdc_id' and 'amount_grams'
        fdc_api: FoodDataCentralAPI instance
        
    Returns:
        Total nutrition for the recipe
    """
    total_nutrition = {
        "protein": 0,
        "fat": 0,
        "carbohydrates": 0,
        "calories": 0
    }
    
    for ingredient in ingredients:
        food_data = fdc_api.get_food_nutrition(ingredient['fdc_id'])
        if food_data:
            nutrients = fdc_api.extract_key_nutrients(food_data)
            amount_grams = ingredient['amount_grams']
            
            # Calculate based on actual amount (nutrients are per 100g)
            for key in total_nutrition:
                if key in nutrients:
                    value = nutrients[key]['value']
                    total_nutrition[key] += (value * amount_grams) / 100
    
    return total_nutrition


if __name__ == '__main__':
    # Example usage
    ingredients = [
        {"fdc_id": 171477, "amount_grams": 200},  # 200g chicken breast
        {"fdc_id": 170379, "amount_grams": 150}   # 150g rice
    ]

    api_key = "OsxzJJV049cMYt2e1XU6lEQP7o864NKbxkvNAGWv"  # Replace with your actual API key or use "DEMO_KEY" for testing
    fdc_api = FoodDataCentralAPI(api_key)
    
    recipe_nutrition = calculate_recipe_nutrition(ingredients, fdc_api)
    print(f"Total Recipe Nutrition: {recipe_nutrition}")
