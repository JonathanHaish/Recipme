import httpx
import time
import logging
from mysite.settings import API_KEY 
from django.core.cache import cache
import unicodedata
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


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

    def _send_once(self, method, url, **kwargs):
        """Send a single HTTP request without retry logic."""
        full_url = self.build_url(url)                  # Build full URL

        try:
            resp = self.client.request(method, full_url, **kwargs)  # Perform HTTP/2 request
            return ApiResult(True, resp.status_code, resp.text, raw=resp)

        except Exception as e:
            # Any network/transport error is captured as failure
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

    def _send_with_retry(self, method, url, expected_status=(200,), **kwargs):
        """Send HTTP request with retry + backoff and status code validation."""
        for attempt in range(self.retries + 1):
            # Send request once
            result = self._send_once(method, url, **kwargs)

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

    def request(self, method, url, *, expected_status=(200,), **kwargs):
        """
        Public synchronous request method.
        Returns ApiResult with .success, .status, .data, .error.
        """
        return self._send_with_retry(method, url, expected_status, **kwargs)





class FoodDataCentralAPI:
    CACHE_TTL = 60 * 60

    def __init__(self, http_client, api_key: str):
        self.client = http_client
        self.api_key = api_key

    # -------------------------------------------------------
    # Name sanitation / Key generation
    # -------------------------------------------------------
    def sanitize_name(self, name: str) -> str:
        normalized = unicodedata.normalize("NFKD", name)
        normalized = normalized.lower().strip()
        normalized = re.sub(r"\s+", "-", normalized)
        normalized = re.sub(r"[^a-z0-9א-ת_-]", "", normalized)
        return normalized

    def generate_custom_key(self, name: str) -> str:
        base = f"food:{self.sanitize_name(name)}"

        if cache.get(base) is None:
            return base

        counter = 2
        while True:
            key = f"{base}-{counter}"
            if cache.get(key) is None:
                return key
            counter += 1

    # -------------------------------------------------------
    # Custom foods
    # -------------------------------------------------------
    def save_custom_food(self, name: str, data: Dict) -> str:
        key = self.generate_custom_key(name)
        cache.set(key, data, timeout=None)
        return key

    def get_custom_food(self, name: str) -> Optional[Dict]:
        """Retrieve custom food by name (not by key)."""
        # user provides name, we map to the sanitized key
        base_key = f"food:{self.sanitize_name(name)}"

        # existing key?
        if cache.get(base_key):
            return cache.get(base_key)

        # check additional versions (food:name-2, food:name-3...)
        counter = 2
        while True:
            key = f"{base_key}-{counter}"
            item = cache.get(key)
            if item:
                return item
            if not item:
                break
            counter += 1

        return None

    # -------------------------------------------------------
    # USDA API Wrappers
    # -------------------------------------------------------
    def _with_key(self, params=None):
        params = params or {}
        params["api_key"] = self.api_key
        return params

    def api_get(self, url: str, params: dict):
        return self.client.request("GET", url, params=params)

    # -------------------------------------------------------
    # USDA: get food nutrition
    # -------------------------------------------------------
    def get_usda_food(self, fdc_id: int) -> Optional[Dict]:
        cache_key = f"fdc:{fdc_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        params = self._with_key({})
        resp = self.api_get(f"food/{fdc_id}", params)

        if not resp.success:
            return None

        cache.set(cache_key, resp.data, self.CACHE_TTL)
        return resp.data

    # -------------------------------------------------------
    # Nutrient extraction
    # -------------------------------------------------------
    def extract_nutrients(self, food_data: Dict) -> Dict:
        mapping = {
            "Protein": "protein",
            "Total lipid (fat)": "fat",
            "Carbohydrate, by difference": "carbohydrates",
            "Energy": "calories",
            "Fiber, total dietary": "fiber",
            "Sugars, total including NLEA": "sugars"
        }

        result = {}

        for n in food_data.get("foodNutrients", []):
            name = n.get("nutrient", {}).get("name") or n.get("nutrientName")
            if name in mapping:
                key = mapping[name]
                value = n.get("amount") or n.get("value", 0)
                unit = n.get("nutrient", {}).get("unitName") or n.get("unitName", "")
                result[key] = {"value": value, "unit": unit}

        return result

    # -------------------------------------------------------
    # General food fetcher (USDA or custom)
    # -------------------------------------------------------
    def get_food(self, ingredient: Dict) -> Optional[Dict]:
        """
        ingredient dict may include:
        - {"fdc_id": 12345, "amount_grams": 80}
        - {"custom_name": "פיתה ביתית", "amount_grams": 80}
        """
        if "fdc_id" in ingredient:
            return self.get_usda_food(ingredient["fdc_id"])

        if "custom_name" in ingredient:
            return self.get_custom_food(ingredient["custom_name"])

        return None

    # -------------------------------------------------------
    # Scaling nutrients by grams
    # -------------------------------------------------------
    def scale_nutrients(self, nutrients: Dict, grams: float) -> Dict:
        scaled = {}
        for key, data in nutrients.items():
            scaled[key] = (data["value"] * grams) / 100.0
        return scaled

    # -------------------------------------------------------
    # Modular recipe nutrition calculator
    # -------------------------------------------------------
    def calculate_recipe_nutrition(self, ingredients: List[Dict]) -> Dict:
        totals = {
            "protein": 0.0,
            "fat": 0.0,
            "carbohydrates": 0.0,
            "calories": 0.0,
            "fiber": 0.0,
            "sugars": 0.0
        }

        for ing in ingredients:
            grams = ing.get("amount_grams", 0)

            # 1 - fetch USDA or custom food
            food_data = self.get_food(ing)
            if not food_data:
                continue

            # 2 - extract nutrients
            nutrients = self.extract_nutrients(food_data)

            # 3 - scale per user grams
            scaled = self.scale_nutrients(nutrients, grams)

            # 4 - accumulate totals
            for key in totals:
                totals[key] += scaled.get(key, 0.0)

        return totals





