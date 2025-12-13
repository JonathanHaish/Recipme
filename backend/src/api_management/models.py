import httpx
import time
import logging
from typing import List, Dict, Optional
logger = logging.getLogger(__name__)
from django.core.cache import cache
import json
import hashlib
from mysite.settings import API_KEY

class ApiResult:
    """Structured result object for HTTP calls."""
    def __init__(self, success, status=None, data=None, error=None, raw=None):
        self.success = success      # True if request succeeded
        self.status = status        # HTTP status code
        self.data = data            # Parsed JSON or text
        self.error = error          # Error message string if failed
        self.raw = raw              # Raw httpx.Response

    def __bool__(self):
        # Allows: if result: ...
        return self.success

    def __repr__(self):
        return f"ApiResult(success={self.success}, status={self.status})"


class HTTP2Client:
    """Synchronous HTTP/2 client with retries, backoff and JSON auto parsing."""

    def __init__(self, base_url=None, timeout=8.0, retries=3, backoff=0.5):
        self.base_url = base_url.rstrip("/") if base_url else None   # Normalize base URL
        self.timeout = timeout                                       # Default timeout (seconds)
        self.retries = retries                                       # Max retry attempts
        self.backoff = backoff                                       # Backoff base for retries

        # Single HTTP/2 client with internal connection pooling and multiplexing
        self.client = httpx.Client(http2=True, timeout=self.timeout)

    def close(self):
        """Close the underlying HTTP/2 client."""
        self.client.close()

    def build_url(self, path):
        """Build full URL from base URL and path."""
        if self.base_url and not path.startswith("http"):
            return f"{self.base_url}/{path.lstrip('/')}"
        return path

    def _send_once(self, method, url, params,payload={}):
        """Send a single HTTP request without retry logic."""
        full_url = self.build_url(url)                  # Build full URL
        
        try:
            resp = self.client.request(method, full_url, params=params,json=payload)  # Perform HTTP/2 request
            
            return ApiResult(True, resp.status_code, resp.text, raw=resp)

        except Exception as e:
           #Any network/transport error is captured as failure
           return ApiResult(False, None, None, f"Request error: {e}")

    def _parse_json_if_possible(self, result):
        """Try to parse JSON if response is JSON."""
        if not result.success:
            return result

        resp = result.raw
        if resp is None:
            return result

        # Check content-type header
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            try:
              data = resp.json()                            # Parse JSON
              return ApiResult(True, resp.status_code, data, raw=resp)
            except Exception:
                # JSON was expected but invalid
                return ApiResult(False, resp.status_code, None, "Invalid JSON response", raw=resp)

        # Not JSON → keep text
        return ApiResult(True, resp.status_code, resp.text, raw=resp)

    def _send_with_retry(self, method, url, expected_status=(200,), params={},json={}):
        """Send HTTP request with retry + backoff and status code validation."""
        for attempt in range(self.retries + 1):
            # Send request once
            result = self._send_once(method, url, params,json)
            
            # Try to parse JSON if applicable
            result = self._parse_json_if_possible(result)

            # If network-level failure → retry
            if not result.success:
                delay = self.backoff * (2 ** attempt)
                logger.warning(
                    f"HTTP2 request failed (attempt {attempt+1}): {result.error}, "
                    f"retrying in {delay} seconds"
                )
                time.sleep(delay)
                continue
            
            # If response succeeded but status code unexpected → treat as error
            if expected_status and result.status not in expected_status:
                error_msg = f"Unexpected status {result.status}"
                logger.warning(error_msg)
                return ApiResult(False, result.status, None, error_msg, raw=result.raw)

            # Valid and expected response
            return result

        # Exhausted retries
        return ApiResult(False, None, None, "Failed after retries")

    def request(self, method, url, *, expected_status=(200,), params={},json={}):
        """
        Public synchronous request method.
        Returns ApiResult with .success, .status, .data, .error.
        """
        
        return self._send_with_retry(method, url, expected_status, params,json)




    



class FoodDataCentralAPI(HTTP2Client):
    """USDA FoodData Central API client using HTTP/2 with Django Cache."""

    SEARCH_TTL = 60 * 60          # 1 hour
    FOOD_TTL = 24 * 60 * 60       # 24 hours
    MULTI_TTL = 24 * 60 * 60

    def __init__(self, api_key: str=API_KEY, timeout: float = 8.0):
        super().__init__(
            base_url="https://api.nal.usda.gov/fdc/v1",
            timeout=timeout,
            retries=3,
            backoff=0.5
        )
        self.api_key = api_key
       
    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def _with_key(self, params: Optional[Dict] = None) -> Dict:
        """Attach API key to query parameters."""
        params = params or {}
        params["api_key"] = self.api_key
        return params

    def _cache_key(self, prefix: str, payload: Dict) -> str:
        """
        Create a stable cache key from request payload.
        """
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"fdc:{prefix}:{digest}"
    

    
    
    # --------------------------------------------------
    # Search ingredient (CACHED)
    # --------------------------------------------------
    def search_ingredient(self, ingredient_name: str, page_size: int = 10):
        params = self._with_key({
            "query": ingredient_name,
            "pageSize": page_size,
        })
        cache_key = f"fdc:food:name:{ingredient_name}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        # 2. Call USDA API
        result = self.request("GET", "foods/search", params=params)
        if not result:
            return []

        foods = result.data.get("foods", [])
        cache.set(cache_key, foods, self.FOOD_TTL)
        return foods


    # --------------------------------------------------
    # Get single food nutrition (CACHED)
    # --------------------------------------------------
    def get_food_nutrition(self, fdc_id: int) -> Optional[Dict]:
        cache_key = f"fdc:food:{fdc_id}"

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        params = self._with_key({})
        result = self.request("GET", f"food/{fdc_id}", params=params)
        if not result:
            return None

        cache.set(cache_key, result.data, self.FOOD_TTL)
        return result.data
    



    # --------------------------------------------------
    # Get multiple foods (CACHED)
    # --------------------------------------------------
    def get_multiple_foods(self, fdc_ids: List[int]) -> List[Dict]:
        payload = {"fdcIds": sorted(fdc_ids)}
        cache_key = self._cache_key("multi", payload)

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        params = self._with_key()

        result = self.request("POST", "foods", params=params, json={"fdcIds": fdc_ids})

        if not result:
            return []

        cache.set(cache_key, result.data, self.MULTI_TTL)
        return result.data

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
    

    def calculate_recipe_nutrition(self,ingredients: List[Dict]) -> Dict:
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
            food_data = self.get_food_nutrition(ingredient['fdc_id'])
            if food_data:
                nutrients = self.extract_key_nutrients(food_data)
                amount_grams = ingredient['amount_grams']
                
                # Calculate based on actual amount (nutrients are per 100g)
                for key in total_nutrition:
                    if key in nutrients:
                        value = nutrients[key]['value']
                        total_nutrition[key] += (value * amount_grams) / 100
        
        return total_nutrition


    def search_food_according_filter(self, filter_criteria: Dict) -> List[Dict]:
        """
        Search for foods matching specific dietary filters.
        
        Args:
            filter_criteria (Dict): Filter specifications like:
                - {"lactose_free": True}
                - {"gluten_free": True}
                - {"vegan": True}
                - {"max_calories": 100}
                
        Returns:
            List[Dict]: List of matching foods
            
        Note: This is a placeholder implementation. Full implementation would
              require integration with USDA food search API or custom database.
        """
        

    def search_food_replace_filter(self, food: Dict, filter_criteria: Dict) -> List[Dict]:
        """
        Search for substitute foods matching dietary filters.
        
        Args:
            food (Dict): Original food to replace
            filter_criteria (Dict): Dietary requirements for substitute
            
        Returns:
            List[Dict]: List of suitable substitute foods
            
        Note: This is a placeholder implementation. Full implementation would
              require nutritional similarity analysis and dietary compatibility.
        """
        

    def search_according_substring(self, substring: str) -> Dict[str, Dict]:
        """
        Search for foods by partial name matching.
        
        Args:
            substring (str): Partial food name to search for
            
        Returns:
            Dict[str, Dict]: Dictionary mapping food names to their data
            
        Example:
            >>> results = api.search_according_substring("rice")
            >>> # Returns: {"Brown Rice": {...}, "White Rice": {...}, "Wild Rice": {...}}
            
        Note: This is a placeholder implementation. Full implementation would
              require integration with USDA food search API.
        """
        




