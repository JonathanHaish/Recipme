import requests
import time
import logging
from typing import List, Dict, Optional
logger = logging.getLogger(__name__)
from django.core.cache import cache
import json
import hashlib
from mysite.settings import API_KEY
import datetime
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


class SimpleHTTPClient:
    """Simple synchronous HTTP client with retries and proper cleanup."""

    def __init__(self, base_url=None, timeout=8.0, retries=3, backoff=0.5):
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        # Use a session for connection pooling - requests handles this properly
        self.session = requests.Session()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit."""
        self.session.close()

    def close(self):
        """Explicitly close the session."""
        self.session.close()

    def build_url(self, path):
        """Build full URL from base URL and path."""
        if self.base_url and not path.startswith("http"):
            return f"{self.base_url}/{path.lstrip('/')}"
        return path

    def _send_once(self, method, url, params, payload=None):
        """Send a single HTTP request without retry logic."""
        full_url = self.build_url(url)

        try:
            if payload:
                resp = self.session.request(method, full_url, params=params, json=payload, timeout=self.timeout)
            else:
                resp = self.session.request(method, full_url, params=params, timeout=self.timeout)

            return ApiResult(True, resp.status_code, resp.text, raw=resp)

        except Exception as e:
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

    def request(self, method, url, *, expected_status=(200,), params={}, json=None):
        """
        Public synchronous request method.
        Returns ApiResult with .success, .status, .data, .error.
        """
        return self._send_with_retry(method, url, expected_status, params, json)




    



class FoodDataCentralAPI(SimpleHTTPClient):
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
    

    def generate_product_tagline(self,food_json: dict):
        """
        The function generate the tag product
        """
        #1. Product Type and Category
        description = food_json.get('description', 'None')
        category = food_json.get('foodCategory', 'None')
        
        #2. Extracting fat percentage (from the nutrient list)
        fat_value = 0
        nutrients = food_json.get('foodNutrients', [])
        for n in nutrients:
            # Searches for the exact name of a fat in an FDC
            if n.get('nutrientName') == 'Total lipid (fat)':
                fat_value = n.get('value', 0)
                break
        
        # 3. Company name extraction (only available in branded products)
        brand = food_json.get('brandOwner') or food_json.get('brandName')
        if not brand:
            # If it's Survey Food, there is no specific company
            if food_json.get('dataType') == 'Survey (FNDDS)':
                brand = "Ganery product"
            else:
                brand = "Unknown product"

        # 4. Constructing the sentence in the desired structure
        # Rounding the fat percentage to one gram or leaving one decimal point
        fat_str = f"{fat_value}% fat" if fat_value > 0 else "none fat"
        fdc_id = food_json.get('fdcId',0)
        
        tagline = {"id":fdc_id,"name":description,"category":category,"description":brand,"fat_str":fat_str}
        return tagline



    def search_ingredients(self,ingredient_name: str):
        """
        Docstring for search_ingredients
        The function search ingredient and return list of options 
     
        :param ingredient_name: name of the ingredient
        :type ingredient_name: str
        """
       
        params = self._with_key({
            "query": ingredient_name
        })
        
        cache_key = f"fdc_sys:food:name:{ingredient_name}"
        cached = cache.get(cache_key)
        
        if cached is not None and cached != '' and cached != []:
           return cached
        
        result = self.request("GET", "foods/search", params=params)
        if not result or result.data == []:
            return []
        
        
        options=[]
        foods = result.data.get("foods", [])
        for food in foods:
            options.append(self.generate_product_tagline(food))
        
        
        if options != []:
            cache.set(cache_key,options,self.FOOD_TTL)
        return options
    
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
            "Total Sugars": "sugars"
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
        
    

    def search_food_nutritions(self,food_id):
        """
        Docstring for search_food_nutritions
        The function get the food nutritions
        :param food_id: fdc_id
        """
        params = self._with_key({
            "query": food_id
        })

        cache_key = f"fdc_sys:food:nutritions:{food_id}"
        cached = cache.get(cache_key)
        if cached is not None and cached != '':
           return cached

        result = self.request("GET", f"food/{food_id}", params=params)
        if not result or result.data == None:
            return {}

        nutritions = self.extract_key_nutrients(result.data)
        cache.set(cache_key,nutritions,self.FOOD_TTL)
        return nutritions

    def search_food_nutritions_batch(self, food_ids: List[str]) -> Dict[str, Dict]:
        """
        Fetch nutrition data for multiple food_ids.
        Simple synchronous approach - reliable and doesn't leak connections.

        :param food_ids: List of fdc_ids to fetch
        :return: Dictionary mapping food_id -> nutrition data
        """
        if not food_ids:
            return {}

        nutrition_map = {}

        # Simple loop - just fetch one by one
        for food_id in food_ids:
            try:
                # Use the existing search_food_nutritions method
                # It already handles caching and proper requests
                nutrition_data = self.search_food_nutritions(food_id)
                if nutrition_data:
                    nutrition_map[food_id] = nutrition_data
            except Exception as e:
                logger.error(f"Error fetching nutrition for food_id {food_id}: {e}")
                # Continue with other ingredients even if one fails
                continue

        return nutrition_map



    




