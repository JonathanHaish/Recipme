import httpx
import time
import logging
import asyncio
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


class HTTP2Client:
    """Synchronous HTTP/2 client with retries, backoff and JSON auto parsing."""

    def __init__(self, base_url=None, timeout=8.0, retries=3, backoff=0.5):
        self.base_url = base_url.rstrip("/") if base_url else None   # Normalize base URL
        self.timeout = timeout                                       # Default timeout (seconds)
        self.retries = retries                                       # Max retry attempts
        self.backoff = backoff                                       # Backoff base for retries

        # Single HTTP/2 client with internal connection pooling and multiplexing
        self.client = httpx.Client(http2=True, timeout=self.timeout)
        self._async_client = None  # Lazy-initialized async client

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

    async def _get_async_client(self):
        """Lazy initialization of async client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(http2=True, timeout=self.timeout)
        return self._async_client

    async def _async_send_once(self, method, url, params, payload={}):
        """Send a single async HTTP request without retry logic."""
        full_url = self.build_url(url)

        try:
            client = await self._get_async_client()
            resp = await client.request(method, full_url, params=params, json=payload)
            return ApiResult(True, resp.status_code, resp.text, raw=resp)
        except Exception as e:
            return ApiResult(False, None, None, f"Request error: {e}")

    async def _async_send_with_retry(self, method, url, expected_status=(200,), params={}, json={}):
        """Send async HTTP request with retry + backoff and status code validation."""
        for attempt in range(self.retries + 1):
            result = await self._async_send_once(method, url, params, json)
            result = self._parse_json_if_possible(result)

            if not result.success:
                delay = self.backoff * (2 ** attempt)
                logger.warning(
                    f"Async HTTP2 request failed (attempt {attempt+1}): {result.error}, "
                    f"retrying in {delay} seconds"
                )
                await asyncio.sleep(delay)
                continue

            if expected_status and result.status not in expected_status:
                error_msg = f"Unexpected status {result.status}"
                logger.warning(error_msg)
                return ApiResult(False, result.status, None, error_msg, raw=result.raw)

            return result

        return ApiResult(False, None, None, "Failed after retries")

    async def async_request(self, method, url, *, expected_status=(200,), params={}, json={}):
        """
        Public asynchronous request method.
        Returns ApiResult with .success, .status, .data, .error.
        """
        return await self._async_send_with_retry(method, url, expected_status, params, json)

    async def close_async(self):
        """Close the async client."""
        if self._async_client:
            await self._async_client.aclose()




    



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

    async def _async_fetch_single_nutrition(self, food_id: str):
        """
        Async helper to fetch nutrition for a single food_id.
        Checks cache first, then makes API request if needed.
        """
        cache_key = f"fdc_sys:food:nutritions:{food_id}"
        cached = cache.get(cache_key)
        if cached is not None and cached != '':
            return food_id, cached

        params = self._with_key({"query": food_id})

        try:
            result = await self.async_request("GET", f"food/{food_id}", params=params)
            if not result or result.data is None:
                return food_id, {}

            nutritions = self.extract_key_nutrients(result.data)
            cache.set(cache_key, nutritions, self.FOOD_TTL)
            return food_id, nutritions
        except Exception as e:
            logger.error(f"Error fetching nutrition for food_id {food_id}: {e}")
            return food_id, {}

    async def _fetch_nutritions_batch_async(self, food_ids: List[str]):
        """
        Async helper to fetch nutrition data for multiple food_ids concurrently.
        Returns dict mapping food_id -> nutrition_data.
        """
        tasks = [self._async_fetch_single_nutrition(food_id) for food_id in food_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        nutrition_map = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Exception in batch nutrition fetch: {result}")
                continue
            food_id, nutrition_data = result
            nutrition_map[food_id] = nutrition_data

        return nutrition_map

    def search_food_nutritions_batch(self, food_ids: List[str]) -> Dict[str, Dict]:
        """
        Fetch nutrition data for multiple food_ids concurrently.
        This is the synchronous wrapper that can be called from Django views/serializers.

        :param food_ids: List of fdc_ids to fetch
        :return: Dictionary mapping food_id -> nutrition data
        """
        if not food_ids:
            return {}

        try:
            # Run the async batch fetch in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self._fetch_nutritions_batch_async(food_ids))
                return result
            finally:
                # Clean up async client if it was created
                if self._async_client:
                    loop.run_until_complete(self.close_async())
                    self._async_client = None
                loop.close()
        except Exception as e:
            logger.error(f"Error in batch nutrition fetch: {e}")
            return {}



    




