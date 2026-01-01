import requests
from typing import List, Dict, Optional
from urllib.parse import quote

class FoodDataCentralAPI:
    """Client for USDA FoodData Central API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
    
    def search_ingredient(self, ingredient_name: str, page_size: int = 10) -> List[Dict]:
        """
        Search for an ingredient by name
        
        Args:
            ingredient_name: Name of the ingredient to search
            page_size: Number of results to return (default 10)
            
        Returns:
            List of matching foods with basic info
        """
        url = f"{self.base_url}/foods/search"
        params = {
            "query": ingredient_name,
            "api_key": self.api_key,
            "pageSize": page_size
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("foods", [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching for ingredient: {e}")
            return []
    
    def get_food_nutrition(self, fdc_id: int) -> Optional[Dict]:
        """
        Get detailed nutrition information for a specific food
        
        Args:
            fdc_id: FoodData Central ID
            
        Returns:
            Dictionary with detailed food and nutrient data
        """
        url = f"{self.base_url}/food/{fdc_id}"
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting food nutrition: {e}")
            return None
    
    def get_multiple_foods(self, fdc_ids: List[int]) -> List[Dict]:
        """
        Get nutrition info for multiple foods at once
        
        Args:
            fdc_ids: List of FoodData Central IDs
            
        Returns:
            List of food data dictionaries
        """
        url = f"{self.base_url}/foods"
        params = {"api_key": self.api_key}
        payload = {"fdcIds": fdc_ids}
        
        try:
            response = requests.post(url, params=params, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting multiple foods: {e}")
            return []
    
    def extract_key_nutrients(self, food_data: Dict) -> Dict[str, float]:
        """
        Extract key nutrients from food data
        
        Args:
            food_data: Full food data from API
            
        Returns:
            Dictionary with key nutrients (protein, fat, carbs, calories)
        """
        nutrients = {}
        nutrient_mapping = {
            "Protein": "protein",
            "Total lipid (fat)": "fat",
            "Carbohydrate, by difference": "carbohydrates",
            "Energy": "calories",
            "Fiber, total dietary": "fiber",
            "Sugars, total including NLEA": "sugars"
        }
        
        for nutrient in food_data.get("foodNutrients", []):
            nutrient_name = nutrient.get("nutrient", {}).get("name") or nutrient.get("nutrientName")
            if nutrient_name in nutrient_mapping:
                key = nutrient_mapping[nutrient_name]
                value = nutrient.get("amount") or nutrient.get("value", 0)
                unit = nutrient.get("nutrient", {}).get("unitName") or nutrient.get("unitName", "")
                nutrients[key] = {
                    "value": value,
                    "unit": unit
                }
        
        return nutrients





# Example usage
def main():
    # Initialize the API client
    api_key = "OsxzJJV049cMYt2e1XU6lEQP7o864NKbxkvNAGWv"  # Replace with your actual API key or use "DEMO_KEY" for testing
    fdc_api = FoodDataCentralAPI(api_key)
    
    # Search for an ingredient
    print("Searching for 'chicken breast'...")
    results = fdc_api.search_ingredient("chicken breast")
    
    if results:
        print(f"\nFound {len(results)} results:")
        for i, food in enumerate(results[:3], 1):  # Show first 3 results
            print(f"\n{i}. {food.get('description')}")
            print(f"   FDC ID: {food.get('fdcId')}")
            print(f"   Data Type: {food.get('dataType')}")
        
        # Get detailed nutrition for the first result
        first_food_id = results[0].get('fdcId')
        print(f"\n\nGetting detailed nutrition for FDC ID {first_food_id}...")
        
        nutrition_data = fdc_api.get_food_nutrition(first_food_id)
        
        if nutrition_data:
            print(f"\nFood: {nutrition_data.get('description')}")
            
            # Extract key nutrients
            key_nutrients = fdc_api.extract_key_nutrients(nutrition_data)
            print("\nKey Nutrients (per 100g):")
            for nutrient, data in key_nutrients.items():
                print(f"  {nutrient.capitalize()}: {data['value']} {data['unit']}")
    else:
        print("No results found")


if __name__ == "__main__":
    main()
