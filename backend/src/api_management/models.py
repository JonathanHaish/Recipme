import httpx
import time
import logging
from mysite.settings import API_KEY 
from django.core.cache import cache
import unicodedata
import re
from typing import List, Dict, Optional, Union, Tuple

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Custom exception for API-related errors."""
    def __init__(self, message: str, error_code: str = None, original_exception: Exception = None):
        self.message = message
        self.error_code = error_code
        self.original_exception = original_exception
        super().__init__(self.message)


class ValidationError(APIException):
    """Exception for data validation errors."""
    pass


class NetworkError(APIException):
    """Exception for network-related errors."""
    pass


class CacheError(APIException):
    """Exception for cache-related errors."""
    pass


class ApiResult:
    """
    Structured result object for HTTP calls.
    
    Attributes:
        success (bool): True if request succeeded
        status (int): HTTP status code
        data (any): Parsed JSON or text response
        error (str): Error message if failed
        raw (httpx.Response): Raw HTTP response object
    """
    
    def __init__(self, success: bool, status: int = None, data: any = None, 
                 error: str = None, raw: any = None):
        try:
            self.success = bool(success)
            self.status = status
            self.data = data
            self.error = error
            self.raw = raw
        except Exception as e:
            logger.error(f"Error initializing ApiResult: {e}")
            self.success = False
            self.status = None
            self.data = None
            self.error = f"Initialization error: {str(e)}"
            self.raw = None

    def __bool__(self) -> bool:
        """Allow boolean evaluation: if result: ..."""
        try:
            return self.success
        except Exception as e:
            logger.error(f"Error in ApiResult.__bool__: {e}")
            return False

    def __repr__(self) -> str:
        """String representation of ApiResult."""
        try:
            return f"ApiResult(success={self.success}, status={self.status})"
        except Exception as e:
            logger.error(f"Error in ApiResult.__repr__: {e}")
            return "ApiResult(error=True)"
    
    def to_dict(self) -> Dict:
        """Convert ApiResult to dictionary."""
        try:
            return {
                'success': self.success,
                'status': self.status,
                'data': self.data,
                'error': self.error
            }
        except Exception as e:
            logger.error(f"Error converting ApiResult to dict: {e}")
            return {'success': False, 'error': f'Conversion error: {str(e)}'}


class HTTP2Client:
    """
    Synchronous HTTP/2 client with retries, backoff and JSON auto parsing.
    
    Features:
    - Automatic retry with exponential backoff
    - HTTP/2 support with HTTP/1.1 fallback
    - JSON response parsing
    - Connection pooling
    - Comprehensive error handling
    """

    def __init__(self, base_url: str = None, timeout: float = 8.0, 
                 retries: int = 3, backoff: float = 0.5):
        """
        Initialize HTTP2Client.
        
        Args:
            base_url (str, optional): Base URL for requests
            timeout (float): Request timeout in seconds
            retries (int): Maximum retry attempts
            backoff (float): Base backoff time for retries
            
        Raises:
            NetworkError: If client initialization fails
        """
        try:
            self.base_url = base_url.rstrip("/") if base_url else None
            self.timeout = float(timeout)
            self.retries = int(retries)
            self.backoff = float(backoff)
            
            # Validate parameters
            if self.timeout <= 0:
                logger.error("Timeout must be positive")
                return None
            if self.retries < 0:
                logger.error("Retries must be non-negative")
                return None
            if self.backoff < 0:
                logger.error("Backoff must be non-negative")
                return None

            # Initialize HTTP client with HTTP/2 support
            try:
                self.client = httpx.Client(http2=True, timeout=self.timeout)
                logger.info("HTTP/2 client initialized successfully")
            except ImportError as e:
                logger.warning(f"HTTP/2 not available, falling back to HTTP/1.1: {e}")
                self.client = httpx.Client(timeout=self.timeout)
            except Exception as e:
                logger.error(f"Failed to initialize HTTP client: {e}")
                return None
                
        except Exception:
            logger.error("HTTP2Client initialization failed")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in HTTP2Client.__init__: {e}")
            return None

    def close(self) -> None:
        """
        Close the underlying HTTP client and release resources.
        
        Raises:
            NetworkError: If closing fails
        """
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
                logger.debug("HTTP client closed successfully")
        except Exception as e:
            logger.error(f"Error closing HTTP client: {e}")
            return None

    def build_url(self, path: str) -> str:
        """
        Build full URL from base URL and path.
        
        Args:
            path (str): URL path or full URL
            
        Returns:
            str: Complete URL
            
        Raises:
            ValidationError: If path is invalid
        """
        try:
            if not isinstance(path, str):
                logger.error(f"Path must be string, got {type(path)}")
                return None
            
            if not path:
                logger.error("Path cannot be empty")
                return None
            
            # If path is already a full URL, return as-is
            if path.startswith(("http://", "https://")):
                return path
            
            # If no base URL, return path as-is
            if not self.base_url:
                return path
            
            # Combine base URL and path
            clean_path = path.lstrip('/')
            return f"{self.base_url}/{clean_path}"
            
        except Exception as e:
            logger.error(f"Error building URL: {e}")
            return None

    def _send_once(self, method: str, url: str, **kwargs) -> ApiResult:
        """
        Send a single HTTP request without retry logic.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): URL path or full URL
            **kwargs: Additional request parameters
            
        Returns:
            ApiResult: Result of the HTTP request
        """
        try:
            # Validate inputs
            if not isinstance(method, str) or not method:
                logger.error("Method must be non-empty string")
                return ApiResult(False, None, None, "Invalid method")
            
            if not isinstance(url, str) or not url:
                logger.error("URL must be non-empty string")
                return ApiResult(False, None, None, "Invalid URL")
            
            # Build full URL
            full_url = self.build_url(url)
            logger.debug(f"Sending {method} request to {full_url}")
            
            # Perform HTTP request
            resp = self.client.request(method, full_url, **kwargs)
            
            logger.debug(f"Request completed with status {resp.status_code}")
            return ApiResult(True, resp.status_code, resp.text, raw=resp)

        except ValidationError:
            return ApiResult(False, None, None, "Validation failed")
        except httpx.TimeoutException as e:
            error_msg = f"Request timeout: {str(e)}"
            logger.warning(error_msg)
            return ApiResult(False, None, None, error_msg)
        except httpx.NetworkError as e:
            error_msg = f"Network error: {str(e)}"
            logger.warning(error_msg)
            return ApiResult(False, None, None, error_msg)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {str(e)}"
            logger.warning(error_msg)
            return ApiResult(False, e.response.status_code, None, error_msg, raw=e.response)
        except Exception as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            return ApiResult(False, None, None, error_msg)

    def _parse_json_if_possible(self, result: ApiResult) -> ApiResult:
        """
        Try to parse JSON if response content-type indicates JSON.
        
        Args:
            result (ApiResult): Original API result
            
        Returns:
            ApiResult: Result with parsed JSON data if applicable
        """
        try:
            # Return failed results as-is
            if not result.success:
                return result

            # Check if we have a raw response
            resp = result.raw
            if resp is None:
                logger.debug("No raw response available for JSON parsing")
                return result

            # Check content-type header for JSON
            content_type = resp.headers.get("content-type", "").lower()
            if "application/json" not in content_type:
                logger.debug(f"Content-type '{content_type}' is not JSON, keeping as text")
                return result

            # Attempt JSON parsing
            try:
                data = resp.json()
                logger.debug("Successfully parsed JSON response")
                return ApiResult(True, resp.status_code, data, raw=resp)
            except (ValueError, TypeError) as e:
                error_msg = f"Invalid JSON response: {str(e)}"
                logger.warning(error_msg)
                return ApiResult(False, resp.status_code, None, error_msg, raw=resp)
            except Exception as e:
                error_msg = f"JSON parsing error: {str(e)}"
                logger.error(error_msg)
                return ApiResult(False, resp.status_code, None, error_msg, raw=resp)

        except Exception as e:
            logger.error(f"Unexpected error in JSON parsing: {e}")
            return ApiResult(False, None, None, f"JSON parsing failed: {str(e)}")

    def _send_with_retry(self, method: str, url: str, expected_status: Tuple[int, ...] = (200,), 
                        **kwargs) -> ApiResult:
        """
        Send HTTP request with retry logic, exponential backoff, and status validation.
        
        Args:
            method (str): HTTP method
            url (str): URL path or full URL
            expected_status (tuple): Tuple of acceptable status codes
            **kwargs: Additional request parameters
            
        Returns:
            ApiResult: Final result after retries
        """
        last_result = None
        
        try:
            # Validate expected_status
            if expected_status and not isinstance(expected_status, (tuple, list)):
                expected_status = (expected_status,)
            
            for attempt in range(self.retries + 1):
                try:
                    # Send request once
                    result = self._send_once(method, url, **kwargs)
                    last_result = result

                    # Try to parse JSON if applicable
                    result = self._parse_json_if_possible(result)

                    # If network-level failure and we have retries left → retry
                    if not result.success and attempt < self.retries:
                        delay = self.backoff * (2 ** attempt)
                        logger.warning(
                            f"HTTP2 request failed (attempt {attempt+1}): {result.error}, "
                            f"retrying in {delay} seconds"
                        )
                        time.sleep(delay)
                        continue

                    # If network-level failure and no retries left → return failure
                    if not result.success:
                        logger.error(f"Request failed after {self.retries + 1} attempts")
                        return result

                    # Check status code if specified
                    if expected_status and result.status not in expected_status:
                        error_msg = f"Unexpected status {result.status}, expected one of {expected_status}"
                        logger.warning(error_msg)
                        return ApiResult(False, result.status, None, error_msg, raw=result.raw)

                    # Success - valid response with expected status
                    logger.debug(f"Request successful on attempt {attempt + 1}")
                    return result

                except ValidationError:
                    # Don't retry validation errors
                    return ApiResult(False, None, None, "Validation error")
                except Exception as e:
                    logger.error(f"Unexpected error in retry attempt {attempt + 1}: {e}")
                    if attempt == self.retries:
                        return ApiResult(False, None, None, f"Retry failed: {str(e)}")
                    continue

            # Should not reach here, but just in case
            return ApiResult(False, None, None, "Failed after retries")
            
        except Exception as e:
            logger.error(f"Unexpected error in _send_with_retry: {e}")
            return ApiResult(False, None, None, f"Retry logic failed: {str(e)}")

    def request(self, method: str, url: str, *, expected_status: Tuple[int, ...] = (200,), 
               **kwargs) -> ApiResult:
        """
        Public synchronous request method with comprehensive error handling.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            url (str): URL path or complete URL
            expected_status (tuple): Acceptable HTTP status codes
            **kwargs: Additional parameters (headers, params, json, data, etc.)
            
        Returns:
            ApiResult: Result object with success, status, data, and error information
            
        Raises:
            ValidationError: If input parameters are invalid
            NetworkError: If network configuration is invalid
            
        Example:
            >>> client = HTTP2Client("https://api.example.com")
            >>> result = client.request("GET", "/users/123")
            >>> if result.success:
            ...     print(f"User data: {result.data}")
            >>> else:
            ...     print(f"Error: {result.error}")
        """
        try:
            # Validate method
            if not isinstance(method, str) or not method:
                logger.error("HTTP method must be non-empty string")
                return ApiResult(False, None, None, "Invalid HTTP method")
            
            method = method.upper()
            valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
            if method not in valid_methods:
                logger.error(f"Invalid HTTP method '{method}'. Valid methods: {valid_methods}")
                return ApiResult(False, None, None, f"Invalid HTTP method: {method}")
            
            # Validate URL
            if not isinstance(url, str) or not url:
                logger.error("URL must be non-empty string")
                return ApiResult(False, None, None, "Invalid URL")
            
            logger.info(f"Making {method} request to {url}")
            return self._send_with_retry(method, url, expected_status, **kwargs)
            
        except Exception as e:
            logger.error(f"Unexpected error in request method: {e}")
            return ApiResult(False, None, None, f"Request failed: {str(e)}")





class FoodDataCentralAPI:
    """
    API client for USDA FoodData Central with caching and custom food management.
    
    Features:
    - USDA FoodData Central API integration
    - Custom food storage and retrieval
    - Nutrition calculation for recipes
    - Intelligent caching with TTL
    - Comprehensive error handling
    - Unicode food name support
    """
    
    CACHE_TTL = 60 * 60  # 1 hour cache TTL
    MAX_CACHE_KEY_LENGTH = 250  # Maximum cache key length
    
    def __init__(self, http_client: HTTP2Client, api_key: str):
        """
        Initialize FoodDataCentralAPI.
        
        Args:
            http_client (HTTP2Client): HTTP client for API requests
            api_key (str): USDA FoodData Central API key
            
        Raises:
            ValidationError: If parameters are invalid
        """
        try:
            if not http_client:
                logger.error("HTTP client is required")
                return None
            
            if not isinstance(api_key, str) or not api_key.strip():
                logger.error("API key must be non-empty string")
                return None
            
            self.client = http_client
            self.api_key = api_key.strip()
            
            logger.info("FoodDataCentralAPI initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing FoodDataCentralAPI: {e}")
            return None

    # -------------------------------------------------------
    # Name sanitation / Key generation
    # -------------------------------------------------------
    def sanitize_name(self, name: str) -> str:
        """
        Sanitize food name for use as cache key.
        
        Process:
        1. Unicode normalization (NFKD)
        2. Convert to lowercase and strip whitespace
        3. Replace multiple spaces with single dashes
        4. Remove non-allowed characters (keep: a-z, 0-9, Hebrew, _, -)
        
        Args:
            name (str): Original food name
            
        Returns:
            str: Sanitized name suitable for cache key
            
        Raises:
            ValidationError: If name is invalid
            
        Example:
            >>> api.sanitize_name("Apple Pie & Ice Cream")
            'apple-pie--ice-cream'
        """
        try:
            if not isinstance(name, str):
                logger.error(f"Name must be string, got {type(name)}")
                return ""
            
            if not name.strip():
                return ""
            
            # Unicode normalization
            normalized = unicodedata.normalize("NFKD", name)
            
            # Convert to lowercase and strip
            normalized = normalized.lower().strip()
            
            # Replace multiple whitespace with single dash
            normalized = re.sub(r"\s+", "-", normalized)
            
            # Remove non-allowed characters (keep: a-z, 0-9, Hebrew letters, _, -)
            normalized = re.sub(r"[^a-z0-9א-ת_-]", "", normalized)
            
            # Truncate if too long for cache key
            if len(normalized) > self.MAX_CACHE_KEY_LENGTH - 10:  # Leave room for prefix
                normalized = normalized[:self.MAX_CACHE_KEY_LENGTH - 10]
                logger.warning(f"Truncated long food name to {len(normalized)} characters")
            
            logger.debug(f"Sanitized '{name}' to '{normalized}'")
            return normalized
            
        except Exception as e:
            logger.error(f"Error sanitizing name '{name}': {e}")
            return ""

    def generate_custom_key(self, name: str) -> str:
        """
        Generate unique cache key for custom food.
        
        If base key exists, appends incrementing number until unique key found.
        
        Args:
            name (str): Food name
            
        Returns:
            str: Unique cache key
            
        Raises:
            ValidationError: If name is invalid
            CacheError: If cache operations fail
            
        Example:
            >>> api.generate_custom_key("Apple Pie")
            'food:apple-pie'
            >>> api.generate_custom_key("Apple Pie")  # If first exists
            'food:apple-pie-2'
        """
        try:
            sanitized = self.sanitize_name(name)
            if not sanitized:
                logger.error("Sanitized name cannot be empty")
                return None
            
            base = f"food:{sanitized}"
            
            # Check if base key is available
            try:
                if cache.get(base) is None:
                    logger.debug(f"Generated unique key: {base}")
                    return base
            except Exception as e:
                logger.error(f"Cache check failed for key '{base}': {e}")
                return None
            
            # Find next available key with counter
            counter = 2
            max_attempts = 1000  # Prevent infinite loop
            
            while counter <= max_attempts:
                try:
                    key = f"{base}-{counter}"
                    if cache.get(key) is None:
                        logger.debug(f"Generated unique key: {key}")
                        return key
                    counter += 1
                except Exception as e:
                    logger.error(f"Cache check failed for key '{key}': {e}")
                    return None
            
            # If we reach here, we couldn't find a unique key
            logger.error(f"Could not generate unique key after {max_attempts} attempts")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error generating key for '{name}': {e}")
            return None

    # -------------------------------------------------------
    # Custom foods
    # -------------------------------------------------------
    def save_custom_food(self, name: str, data: Dict) -> str:
        """
        Save custom food data to cache.
        
        Args:
            name (str): Food name
            data (Dict): Food nutrition data
            
        Returns:
            str: Cache key used for storage
            
        Raises:
            ValidationError: If inputs are invalid
            CacheError: If cache operations fail
            
        Example:
            >>> food_data = {
            ...     "foodNutrients": [
            ...         {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 20.0}
            ...     ]
            ... }
            >>> key = api.save_custom_food("My Custom Food", food_data)
            >>> print(key)
            'food:my-custom-food'
        """
        try:
            # Validate inputs
            if not isinstance(name, str) or not name.strip():
                logger.error("Food name must be non-empty string")
                return None
            
            if not isinstance(data, dict):
                logger.error(f"Food data must be dictionary, got {type(data)}")
                return None
            
            if not data:
                logger.error("Food data cannot be empty")
                return None
            
            # Generate unique key
            key = self.generate_custom_key(name)
            
            # Save to cache (no timeout = permanent storage)
            try:
                cache.set(key, data, timeout=None)
                logger.info(f"Saved custom food '{name}' with key '{key}'")
                return key
            except Exception as e:
                logger.error(f"Failed to save custom food '{name}': {e}")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error saving custom food '{name}': {e}")
            return None

    def get_custom_food(self, name: str) -> Optional[Dict]:
        """
        Retrieve custom food by name.
        
        Searches for food using sanitized name, checking base key and numbered variants.
        
        Args:
            name (str): Food name to search for
            
        Returns:
            Optional[Dict]: Food data if found, None otherwise
            
        Raises:
            ValidationError: If name is invalid
            CacheError: If cache operations fail
            
        Example:
            >>> food_data = api.get_custom_food("My Custom Food")
            >>> if food_data:
            ...     print(f"Found food: {food_data}")
            >>> else:
            ...     print("Food not found")
        """
        try:
            # Validate input
            if not isinstance(name, str) or not name.strip():
                logger.error("Food name must be non-empty string")
                return None
            
            # Generate base key
            sanitized = self.sanitize_name(name)
            if not sanitized:
                logger.debug(f"Empty sanitized name for '{name}'")
                return None
            
            base_key = f"food:{sanitized}"
            
            # Try base key first
            try:
                item = cache.get(base_key)
                if item is not None:
                    logger.debug(f"Found custom food '{name}' with base key '{base_key}'")
                    return item
            except Exception as e:
                logger.error(f"Cache get failed for key '{base_key}': {e}")
                return None
            
            # Try numbered variants (food:name-2, food:name-3, etc.)
            counter = 2
            max_attempts = 100  # Reasonable limit to prevent infinite search
            
            while counter <= max_attempts:
                try:
                    key = f"{base_key}-{counter}"
                    item = cache.get(key)
                    
                    if item is not None:
                        logger.debug(f"Found custom food '{name}' with key '{key}'")
                        return item
                    
                    # If we get None, the key doesn't exist, so we can stop searching
                    # (assuming sequential numbering)
                    break
                    
                except Exception as e:
                    logger.error(f"Cache get failed for key '{key}': {e}")
                    # Continue searching despite error
                    pass
                
                counter += 1
            
            logger.debug(f"Custom food '{name}' not found in cache")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving custom food '{name}': {e}")
            return None

    # -------------------------------------------------------
    # USDA API Wrappers
    # -------------------------------------------------------
    def _with_key(self, params: Dict = None) -> Dict:
        """
        Add API key to request parameters.
        
        Args:
            params (Dict, optional): Existing parameters
            
        Returns:
            Dict: Parameters with API key added
            
        Raises:
            ValidationError: If API key is missing
        """
        try:
            if not self.api_key:
                logger.error("API key is not configured")
                return {}
            
            params = params or {}
            if not isinstance(params, dict):
                logger.error(f"Parameters must be dictionary, got {type(params)}")
                return {}
            
            # Create copy to avoid modifying original
            params_with_key = params.copy()
            params_with_key["api_key"] = self.api_key
            
            return params_with_key
            
        except Exception as e:
            logger.error(f"Error adding API key to parameters: {e}")
            return {}

    def api_get(self, url: str, params: Dict = None) -> ApiResult:
        """
        Make GET request to USDA API with automatic API key injection.
        
        Args:
            url (str): API endpoint URL
            params (Dict, optional): Request parameters
            
        Returns:
            ApiResult: API response result
            
        Raises:
            ValidationError: If inputs are invalid
            NetworkError: If request fails
        """
        try:
            if not isinstance(url, str) or not url:
                logger.error("URL must be non-empty string")
                return ApiResult(False, None, None, "Invalid URL")
            
            params = params or {}
            params_with_key = self._with_key(params)
            
            logger.debug(f"Making USDA API GET request to {url}")
            return self.client.request("GET", url, params=params_with_key)
            
        except Exception as e:
            logger.error(f"Error in USDA API GET request: {e}")
            return ApiResult(False, None, None, f"API request failed: {str(e)}")

    # -------------------------------------------------------
    # USDA: get food nutrition
    # -------------------------------------------------------
    def get_usda_food(self, fdc_id: int) -> Optional[Dict]:
        """
        Get food nutrition data from USDA FoodData Central API.
        
        Uses caching to avoid repeated API calls for the same food.
        
        Args:
            fdc_id (int): USDA Food Data Central ID
            
        Returns:
            Optional[Dict]: Food nutrition data if found, None otherwise
            
        Raises:
            ValidationError: If fdc_id is invalid
            NetworkError: If API request fails
            CacheError: If cache operations fail
            
        Example:
            >>> food_data = api.get_usda_food(123456)
            >>> if food_data:
            ...     print(f"Food: {food_data.get('description', 'Unknown')}")
        """
        try:
            # Validate input
            if not isinstance(fdc_id, int) or fdc_id <= 0:
                logger.error(f"FDC ID must be positive integer, got {fdc_id}")
                return None
            
            # Check cache first
            cache_key = f"fdc:{fdc_id}"
            try:
                cached = cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"Retrieved USDA food {fdc_id} from cache")
                    return cached
            except Exception as e:
                logger.warning(f"Cache get failed for USDA food {fdc_id}: {e}")
                # Continue with API request if cache fails
            
            # Make API request
            logger.debug(f"Fetching USDA food {fdc_id} from API")
            resp = self.api_get(f"food/{fdc_id}", {})
            
            if not resp.success:
                logger.warning(f"USDA API request failed for food {fdc_id}: {resp.error}")
                return None
            
            if not resp.data:
                logger.warning(f"USDA API returned empty data for food {fdc_id}")
                return None
            
            # Cache the result
            try:
                cache.set(cache_key, resp.data, self.CACHE_TTL)
                logger.debug(f"Cached USDA food {fdc_id} for {self.CACHE_TTL} seconds")
            except Exception as e:
                logger.warning(f"Failed to cache USDA food {fdc_id}: {e}")
                # Return data even if caching fails
            
            return resp.data
            
        except Exception as e:
            logger.error(f"Unexpected error getting USDA food {fdc_id}: {e}")
            return None

    # -------------------------------------------------------
    # Nutrient extraction
    # -------------------------------------------------------
    def extract_nutrients(self, food_data: Dict) -> Dict:
        """
        Extract standardized nutrients from food data.
        
        Supports both USDA API format and alternative formats.
        
        Args:
            food_data (Dict): Raw food data containing nutrients
            
        Returns:
            Dict: Standardized nutrient mapping with values and units
            
        Raises:
            ValidationError: If food_data is invalid
            
        Example:
            >>> nutrients = api.extract_nutrients(food_data)
            >>> print(f"Protein: {nutrients['protein']['value']}{nutrients['protein']['unit']}")
        """
        try:
            # Validate input
            if not isinstance(food_data, dict):
                logger.error(f"Food data must be dictionary, got {type(food_data)}")
                return {}
            
            # Nutrient name mapping (USDA names -> standardized keys)
            mapping = {
                "Protein": "protein",
                "Total lipid (fat)": "fat",
                "Carbohydrate, by difference": "carbohydrates",
                "Energy": "calories",
                "Fiber, total dietary": "fiber",
                "Sugars, total including NLEA": "sugars"
            }

            result = {}
            
            # Get nutrients list (handle missing key gracefully)
            nutrients_list = food_data.get("foodNutrients", [])
            if not isinstance(nutrients_list, list):
                logger.warning(f"foodNutrients is not a list: {type(nutrients_list)}")
                return result

            # Process each nutrient
            for n in nutrients_list:
                try:
                    if not isinstance(n, dict):
                        logger.warning(f"Skipping non-dict nutrient: {type(n)}")
                        continue
                    
                    # Extract nutrient name (support multiple formats)
                    name = None
                    if "nutrient" in n and isinstance(n["nutrient"], dict):
                        name = n["nutrient"].get("name")
                    if not name:
                        name = n.get("nutrientName")
                    
                    if not name or name not in mapping:
                        continue  # Skip unknown nutrients
                    
                    # Extract value (support multiple formats)
                    value = n.get("amount")
                    if value is None:
                        value = n.get("value", 0)
                    
                    # Ensure value is numeric
                    try:
                        value = float(value) if value is not None else 0.0
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid nutrient value for {name}: {value}")
                        value = 0.0
                    
                    # Extract unit (support multiple formats)
                    unit = ""
                    if "nutrient" in n and isinstance(n["nutrient"], dict):
                        unit = n["nutrient"].get("unitName", "")
                    if not unit:
                        unit = n.get("unitName", "")
                    
                    # Store standardized nutrient
                    key = mapping[name]
                    result[key] = {"value": value, "unit": unit}
                    
                except Exception as e:
                    logger.warning(f"Error processing nutrient {n}: {e}")
                    continue

            logger.debug(f"Extracted {len(result)} nutrients from food data")
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error extracting nutrients: {e}")
            return {}

    # -------------------------------------------------------
    # General food fetcher (USDA or custom)
    # -------------------------------------------------------
    def get_food(self, ingredient: Dict) -> Optional[Dict]:
        """
        Get food data from either USDA API or custom cache.
        
        Args:
            ingredient (Dict): Ingredient specification with either:
                - {"fdc_id": 12345, "amount_grams": 80}
                - {"custom_name": "My Food", "amount_grams": 80}
                
        Returns:
            Optional[Dict]: Food data if found, None otherwise
            
        Raises:
            ValidationError: If ingredient format is invalid
            
        Example:
            >>> # USDA ingredient
            >>> food = api.get_food({"fdc_id": 123456, "amount_grams": 100})
            >>> 
            >>> # Custom ingredient
            >>> food = api.get_food({"custom_name": "My Recipe", "amount_grams": 50})
        """
        try:
            # Validate input
            if not isinstance(ingredient, dict):
                logger.error(f"Ingredient must be dictionary, got {type(ingredient)}")
                return None
            
            if not ingredient:
                logger.error("Ingredient cannot be empty")
                return None
            
            # Try USDA food first
            if "fdc_id" in ingredient:
                fdc_id = ingredient["fdc_id"]
                if not isinstance(fdc_id, int) or fdc_id <= 0:
                    logger.error(f"FDC ID must be positive integer, got {fdc_id}")
                    return None
                
                logger.debug(f"Fetching USDA food {fdc_id}")
                return self.get_usda_food(fdc_id)
            
            # Try custom food
            elif "custom_name" in ingredient:
                custom_name = ingredient["custom_name"]
                if not isinstance(custom_name, str) or not custom_name.strip():
                    logger.error("Custom name must be non-empty string")
                    return None
                
                logger.debug(f"Fetching custom food '{custom_name}'")
                return self.get_custom_food(custom_name)
            
            else:
                logger.error("Ingredient must have 'fdc_id' or 'custom_name'")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error getting food for ingredient {ingredient}: {e}")
            return None

    # -------------------------------------------------------
    # Scaling nutrients by grams
    # -------------------------------------------------------
    def scale_nutrients(self, nutrients: Dict, grams: float) -> Dict:
        """
        Scale nutrient values by gram amount.
        
        Assumes nutrient values are per 100g and scales proportionally.
        
        Args:
            nutrients (Dict): Nutrient data with 'value' keys
            grams (float): Amount in grams to scale to
            
        Returns:
            Dict: Scaled nutrient values (key -> scaled_value)
            
        Raises:
            ValidationError: If inputs are invalid
            
        Example:
            >>> nutrients = {"protein": {"value": 20.0}, "calories": {"value": 100.0}}
            >>> scaled = api.scale_nutrients(nutrients, 150.0)
            >>> # Returns: {"protein": 30.0, "calories": 150.0}
        """
        try:
            # Validate inputs
            if not isinstance(nutrients, dict):
                logger.error(f"Nutrients must be dictionary, got {type(nutrients)}")
                return {}
            
            if not isinstance(grams, (int, float)):
                logger.error(f"Grams must be number, got {type(grams)}")
                return {}
            
            if grams < 0:
                logger.warning(f"Negative grams value: {grams}")
            
            scaled = {}
            
            for key, data in nutrients.items():
                try:
                    if not isinstance(data, dict) or "value" not in data:
                        logger.warning(f"Skipping invalid nutrient data for {key}: {data}")
                        continue
                    
                    value = data["value"]
                    if not isinstance(value, (int, float)):
                        logger.warning(f"Invalid nutrient value for {key}: {value}")
                        continue
                    
                    # Scale from per-100g to actual grams
                    scaled_value = (value * grams) / 100.0
                    scaled[key] = scaled_value
                    
                except Exception as e:
                    logger.warning(f"Error scaling nutrient {key}: {e}")
                    continue
            
            logger.debug(f"Scaled {len(scaled)} nutrients for {grams}g")
            return scaled
            
        except Exception as e:
            logger.error(f"Unexpected error scaling nutrients: {e}")
            return {}

    # -------------------------------------------------------
    # Modular recipe nutrition calculator
    # -------------------------------------------------------
    def calculate_recipe_nutrition(self, ingredients: List[Dict]) -> Dict:
        """
        Calculate total nutrition for a recipe with multiple ingredients.
        
        Process:
        1. Fetch food data for each ingredient (USDA or custom)
        2. Extract standardized nutrients
        3. Scale nutrients by ingredient amount
        4. Sum all nutrients for recipe total
        
        Args:
            ingredients (List[Dict]): List of ingredient specifications
            
        Returns:
            Dict: Total nutrition values for the recipe
            
        Raises:
            ValidationError: If ingredients format is invalid
            
        Example:
            >>> ingredients = [
            ...     {"fdc_id": 123456, "amount_grams": 100},
            ...     {"custom_name": "My Sauce", "amount_grams": 50}
            ... ]
            >>> nutrition = api.calculate_recipe_nutrition(ingredients)
            >>> print(f"Total calories: {nutrition['calories']}")
        """
        try:
            # Validate input
            if not isinstance(ingredients, list):
                logger.error(f"Ingredients must be list, got {type(ingredients)}")
                return {
                    "protein": 0.0,
                    "fat": 0.0,
                    "carbohydrates": 0.0,
                    "calories": 0.0,
                    "fiber": 0.0,
                    "sugars": 0.0
                }
            
            if not ingredients:
                logger.info("Empty ingredients list, returning zero nutrition")
                
            # Initialize totals
            totals = {
                "protein": 0.0,
                "fat": 0.0,
                "carbohydrates": 0.0,
                "calories": 0.0,
                "fiber": 0.0,
                "sugars": 0.0
            }

            processed_count = 0
            failed_count = 0

            for i, ing in enumerate(ingredients):
                try:
                    # Validate ingredient format
                    if not isinstance(ing, dict):
                        logger.warning(f"Skipping non-dict ingredient at index {i}: {type(ing)}")
                        failed_count += 1
                        continue
                    
                    # Get amount in grams
                    grams = ing.get("amount_grams", 0)
                    if not isinstance(grams, (int, float)):
                        logger.warning(f"Invalid amount_grams for ingredient {i}: {grams}")
                        failed_count += 1
                        continue
                    
                    if grams == 0:
                        logger.debug(f"Zero amount for ingredient {i}, skipping")
                        continue

                    # 1 - Fetch food data (USDA or custom)
                    food_data = self.get_food(ing)
                    if not food_data:
                        logger.warning(f"No food data found for ingredient {i}: {ing}")
                        failed_count += 1
                        continue

                    # 2 - Extract nutrients
                    nutrients = self.extract_nutrients(food_data)
                    if not nutrients:
                        logger.warning(f"No nutrients extracted for ingredient {i}")
                        failed_count += 1
                        continue

                    # 3 - Scale nutrients by grams
                    scaled = self.scale_nutrients(nutrients, grams)

                    # 4 - Accumulate totals
                    for key in totals:
                        if key in scaled:
                            totals[key] += scaled[key]
                    
                    processed_count += 1
                    logger.debug(f"Processed ingredient {i}: {grams}g")

                except Exception as e:
                    logger.warning(f"Validation error for ingredient {i}: {e}")
                    failed_count += 1
                    continue
                except Exception as e:
                    logger.warning(f"Error processing ingredient {i}: {e}")
                    failed_count += 1
                    continue

            # Log summary
            total_ingredients = len(ingredients)
            logger.info(f"Recipe calculation complete: {processed_count}/{total_ingredients} ingredients processed")
            
            if failed_count > 0:
                logger.warning(f"{failed_count} ingredients failed to process")
            
            if processed_count == 0 and total_ingredients > 0:
                logger.warning("No ingredients were successfully processed")

            return totals
            
        except Exception as e:
            logger.error(f"Unexpected error calculating recipe nutrition: {e}")
            return {
                "protein": 0.0,
                "fat": 0.0,
                "carbohydrates": 0.0,
                "calories": 0.0,
                "fiber": 0.0,
                "sugars": 0.0
            }

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
        try:
            if not isinstance(filter_criteria, dict):
                logger.error(f"Filter criteria must be dictionary, got {type(filter_criteria)}")
                return []
            
            logger.info(f"Searching foods with filter: {filter_criteria}")
            
            # Placeholder implementation
            # In a real implementation, this would:
            # 1. Query USDA search API with filters
            # 2. Search custom foods with matching criteria
            # 3. Return combined results
            
            logger.warning("search_food_according_filter is not fully implemented")
            return []
            
        except Exception as e:
            logger.error(f"Error in food filter search: {e}")
            return []

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
        try:
            if not isinstance(food, dict):
                logger.error(f"Food must be dictionary, got {type(food)}")
                return []
            
            if not isinstance(filter_criteria, dict):
                logger.error(f"Filter criteria must be dictionary, got {type(filter_criteria)}")
                return []
            
            logger.info(f"Searching substitutes for food with filter: {filter_criteria}")
            
            # Placeholder implementation
            # In a real implementation, this would:
            # 1. Analyze nutritional profile of original food
            # 2. Search for foods with similar nutrition
            # 3. Filter by dietary requirements
            # 4. Rank by nutritional similarity
            
            logger.warning("search_food_replace_filter is not fully implemented")
            return []
            
        except Exception as e:
            logger.error(f"Error in food replacement search: {e}")
            return []

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
        try:
            if not isinstance(substring, str):
                logger.error(f"Substring must be string, got {type(substring)}")
                return {}
            
            if not substring.strip():
                logger.error("Substring cannot be empty")
                return {}
            
            substring = substring.strip().lower()
            logger.info(f"Searching foods containing '{substring}'")
            
            # Placeholder implementation
            # In a real implementation, this would:
            # 1. Query USDA search API with substring
            # 2. Search custom foods with name matching
            # 3. Return combined results in specified format
            
            logger.warning("search_according_substring is not fully implemented")
            return {}
            
        except Exception as e:
            logger.error(f"Error in substring search: {e}")
            return {}




