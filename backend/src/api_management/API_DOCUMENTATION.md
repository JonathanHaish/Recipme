# API Management Documentation

## Overview

The API Management module provides a comprehensive interface for interacting with the USDA FoodData Central API and managing custom food data. It includes robust error handling, caching, and nutrition calculation capabilities.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Classes Overview](#classes-overview)
3. [Error Handling](#error-handling)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Setup

```python
from api_management.models import HTTP2Client, FoodDataCentralAPI
from django.conf import settings

# Initialize HTTP client
http_client = HTTP2Client(
    base_url="https://api.nal.usda.gov/fdc/v1",
    timeout=10.0,
    retries=3
)

# Initialize Food API
food_api = FoodDataCentralAPI(http_client, settings.API_KEY)
```

### Simple Usage

```python
# Get USDA food data
food_data = food_api.get_usda_food(123456)
if food_data:
    print(f"Food: {food_data['description']}")

# Save custom food
custom_food = {
    "foodNutrients": [
        {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 20.0}
    ]
}
key = food_api.save_custom_food("My Recipe", custom_food)

# Calculate recipe nutrition
ingredients = [
    {"fdc_id": 123456, "amount_grams": 100},
    {"custom_name": "My Recipe", "amount_grams": 50}
]
nutrition = food_api.calculate_recipe_nutrition(ingredients)
print(f"Total protein: {nutrition['protein']}g")
```

## Classes Overview

### ApiResult

A structured result object for HTTP operations.

**Attributes:**
- `success` (bool): Whether the operation succeeded
- `status` (int): HTTP status code
- `data` (any): Response data (parsed JSON or text)
- `error` (str): Error message if failed
- `raw` (httpx.Response): Raw HTTP response object

### HTTP2Client

HTTP/2 client with retry logic and automatic JSON parsing.

**Features:**
- HTTP/2 support with HTTP/1.1 fallback
- Exponential backoff retry mechanism
- Automatic JSON response parsing
- Connection pooling
- Comprehensive error handling

### FoodDataCentralAPI

Main API client for food data operations.

**Features:**
- USDA FoodData Central integration
- Custom food storage and retrieval
- Recipe nutrition calculation
- Intelligent caching
- Unicode food name support

## Error Handling

The API uses a comprehensive error handling system with custom exceptions:

### Exception Hierarchy

```
APIException (base)
├── ValidationError (input validation)
├── NetworkError (network/HTTP issues)
└── CacheError (cache operations)
```

### Error Handling Patterns

```python
from api_management.models import ValidationError, NetworkError, CacheError

try:
    result = food_api.get_usda_food(123456)
except ValidationError as e:
    print(f"Invalid input: {e.message}")
except NetworkError as e:
    print(f"Network issue: {e.message}")
except CacheError as e:
    print(f"Cache problem: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Reference

### HTTP2Client

#### Constructor

```python
HTTP2Client(base_url=None, timeout=8.0, retries=3, backoff=0.5)
```

**Parameters:**
- `base_url` (str, optional): Base URL for requests
- `timeout` (float): Request timeout in seconds (default: 8.0)
- `retries` (int): Maximum retry attempts (default: 3)
- `backoff` (float): Base backoff time for retries (default: 0.5)

#### Methods

##### request(method, url, *, expected_status=(200,), **kwargs)

Make HTTP request with retry logic.

**Parameters:**
- `method` (str): HTTP method (GET, POST, etc.)
- `url` (str): URL path or complete URL
- `expected_status` (tuple): Acceptable status codes
- `**kwargs`: Additional request parameters

**Returns:** `ApiResult`

**Example:**
```python
client = HTTP2Client("https://api.example.com")
result = client.request("GET", "/users/123")
if result.success:
    print(f"User: {result.data}")
```

##### build_url(path)

Build complete URL from base URL and path.

**Parameters:**
- `path` (str): URL path

**Returns:** `str` - Complete URL

##### close()

Close HTTP client and release resources.

### FoodDataCentralAPI

#### Constructor

```python
FoodDataCentralAPI(http_client, api_key)
```

**Parameters:**
- `http_client` (HTTP2Client): HTTP client instance
- `api_key` (str): USDA FoodData Central API key

#### Core Methods

##### get_usda_food(fdc_id)

Get food data from USDA API.

**Parameters:**
- `fdc_id` (int): USDA Food Data Central ID

**Returns:** `Optional[Dict]` - Food data or None if not found

**Example:**
```python
food = food_api.get_usda_food(123456)
if food:
    print(f"Description: {food['description']}")
    nutrients = food.get('foodNutrients', [])
```

##### save_custom_food(name, data)

Save custom food to cache.

**Parameters:**
- `name` (str): Food name
- `data` (Dict): Food nutrition data

**Returns:** `str` - Cache key used for storage

**Example:**
```python
food_data = {
    "foodNutrients": [
        {
            "nutrient": {"name": "Protein", "unitName": "g"},
            "amount": 25.0
        },
        {
            "nutrient": {"name": "Energy", "unitName": "kcal"},
            "amount": 200.0
        }
    ]
}
key = food_api.save_custom_food("Homemade Bread", food_data)
```

##### get_custom_food(name)

Retrieve custom food by name.

**Parameters:**
- `name` (str): Food name to search for

**Returns:** `Optional[Dict]` - Food data or None if not found

**Example:**
```python
food = food_api.get_custom_food("Homemade Bread")
if food:
    nutrients = food.get('foodNutrients', [])
```

##### calculate_recipe_nutrition(ingredients)

Calculate total nutrition for recipe ingredients.

**Parameters:**
- `ingredients` (List[Dict]): List of ingredient specifications

**Ingredient Format:**
```python
# USDA ingredient
{"fdc_id": 123456, "amount_grams": 100}

# Custom ingredient
{"custom_name": "My Food", "amount_grams": 50}
```

**Returns:** `Dict` - Nutrition totals

**Example:**
```python
ingredients = [
    {"fdc_id": 123456, "amount_grams": 150},
    {"custom_name": "Homemade Bread", "amount_grams": 100}
]
nutrition = food_api.calculate_recipe_nutrition(ingredients)

print(f"Protein: {nutrition['protein']}g")
print(f"Calories: {nutrition['calories']} kcal")
print(f"Carbs: {nutrition['carbohydrates']}g")
print(f"Fat: {nutrition['fat']}g")
print(f"Fiber: {nutrition['fiber']}g")
print(f"Sugars: {nutrition['sugars']}g")
```

#### Utility Methods

##### sanitize_name(name)

Sanitize food name for cache key usage.

**Parameters:**
- `name` (str): Original food name

**Returns:** `str` - Sanitized name

**Example:**
```python
sanitized = food_api.sanitize_name("Apple Pie & Ice Cream")
# Returns: "apple-pie--ice-cream"
```

##### extract_nutrients(food_data)

Extract standardized nutrients from food data.

**Parameters:**
- `food_data` (Dict): Raw food data with nutrients

**Returns:** `Dict` - Standardized nutrient mapping

**Example:**
```python
nutrients = food_api.extract_nutrients(food_data)
# Returns: {"protein": {"value": 20.0, "unit": "g"}, ...}
```

##### scale_nutrients(nutrients, grams)

Scale nutrient values by gram amount.

**Parameters:**
- `nutrients` (Dict): Nutrient data
- `grams` (float): Amount in grams

**Returns:** `Dict` - Scaled nutrient values

## Usage Examples

### Complete Recipe Management

```python
from api_management.models import HTTP2Client, FoodDataCentralAPI
from django.conf import settings

# Setup
client = HTTP2Client("https://api.nal.usda.gov/fdc/v1")
api = FoodDataCentralAPI(client, settings.API_KEY)

# Create custom ingredient
homemade_sauce = {
    "foodNutrients": [
        {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 3.0},
        {"nutrient": {"name": "Energy", "unitName": "kcal"}, "amount": 45},
        {"nutrient": {"name": "Total lipid (fat)", "unitName": "g"}, "amount": 2.0}
    ]
}
sauce_key = api.save_custom_food("Homemade Tomato Sauce", homemade_sauce)

# Define recipe
pasta_recipe = [
    {"fdc_id": 123456, "amount_grams": 100},  # Pasta
    {"fdc_id": 789012, "amount_grams": 50},   # Cheese
    {"custom_name": "Homemade Tomato Sauce", "amount_grams": 75}
]

# Calculate nutrition
nutrition = api.calculate_recipe_nutrition(pasta_recipe)

print("Recipe Nutrition (per serving):")
print(f"  Calories: {nutrition['calories']:.1f} kcal")
print(f"  Protein: {nutrition['protein']:.1f}g")
print(f"  Carbohydrates: {nutrition['carbohydrates']:.1f}g")
print(f"  Fat: {nutrition['fat']:.1f}g")
print(f"  Fiber: {nutrition['fiber']:.1f}g")
```

### Batch Food Processing

```python
# Process multiple foods
food_ids = [123456, 789012, 345678]
foods = {}

for fdc_id in food_ids:
    try:
        food_data = api.get_usda_food(fdc_id)
        if food_data:
            foods[fdc_id] = {
                'name': food_data.get('description', 'Unknown'),
                'nutrients': api.extract_nutrients(food_data)
            }
    except Exception as e:
        print(f"Failed to process food {fdc_id}: {e}")

# Display results
for fdc_id, food_info in foods.items():
    print(f"{food_info['name']} (ID: {fdc_id})")
    nutrients = food_info['nutrients']
    if 'protein' in nutrients:
        print(f"  Protein: {nutrients['protein']['value']}{nutrients['protein']['unit']}")
```

### Error Handling Example

```python
from api_management.models import ValidationError, NetworkError, CacheError

def safe_get_food(api, fdc_id):
    """Safely get food with comprehensive error handling."""
    try:
        # Validate input
        if not isinstance(fdc_id, int) or fdc_id <= 0:
            raise ValidationError(f"Invalid FDC ID: {fdc_id}")
        
        # Get food data
        food_data = api.get_usda_food(fdc_id)
        
        if not food_data:
            print(f"Food {fdc_id} not found")
            return None
        
        return food_data
        
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return None
    except NetworkError as e:
        print(f"Network error: {e.message}")
        # Could implement retry logic here
        return None
    except CacheError as e:
        print(f"Cache error: {e.message}")
        # Cache errors shouldn't prevent API calls
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
food = safe_get_food(api, 123456)
if food:
    print(f"Successfully retrieved: {food['description']}")
```

## Best Practices

### 1. Resource Management

Always close HTTP clients when done:

```python
client = HTTP2Client()
try:
    # Use client
    api = FoodDataCentralAPI(client, api_key)
    # ... operations ...
finally:
    client.close()
```

Or use context manager pattern:

```python
class ManagedFoodAPI:
    def __init__(self, api_key):
        self.client = HTTP2Client("https://api.nal.usda.gov/fdc/v1")
        self.api = FoodDataCentralAPI(self.client, api_key)
    
    def __enter__(self):
        return self.api
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

# Usage
with ManagedFoodAPI(settings.API_KEY) as api:
    food = api.get_usda_food(123456)
```

### 2. Error Handling

Always handle specific exceptions:

```python
try:
    result = api.get_usda_food(fdc_id)
except ValidationError:
    # Handle input validation errors
    pass
except NetworkError:
    # Handle network/API errors
    pass
except CacheError:
    # Handle cache errors
    pass
```

### 3. Caching Strategy

- USDA foods are cached automatically with TTL
- Custom foods are cached permanently
- Consider cache warming for frequently used foods

```python
# Pre-load frequently used foods
common_foods = [123456, 789012, 345678]
for fdc_id in common_foods:
    api.get_usda_food(fdc_id)  # Loads into cache
```

### 4. Input Validation

Always validate inputs before API calls:

```python
def validate_ingredient(ingredient):
    """Validate ingredient format."""
    if not isinstance(ingredient, dict):
        raise ValidationError("Ingredient must be dictionary")
    
    if 'fdc_id' in ingredient:
        if not isinstance(ingredient['fdc_id'], int) or ingredient['fdc_id'] <= 0:
            raise ValidationError("FDC ID must be positive integer")
    elif 'custom_name' in ingredient:
        if not isinstance(ingredient['custom_name'], str) or not ingredient['custom_name'].strip():
            raise ValidationError("Custom name must be non-empty string")
    else:
        raise ValidationError("Ingredient must have 'fdc_id' or 'custom_name'")
    
    if 'amount_grams' not in ingredient:
        raise ValidationError("Ingredient must have 'amount_grams'")
    
    if not isinstance(ingredient['amount_grams'], (int, float)) or ingredient['amount_grams'] < 0:
        raise ValidationError("Amount must be non-negative number")
```

### 5. Performance Optimization

- Use batch operations when possible
- Implement request rate limiting for API calls
- Monitor cache hit rates

```python
import time
from collections import defaultdict

class RateLimitedAPI:
    def __init__(self, api, requests_per_second=10):
        self.api = api
        self.min_interval = 1.0 / requests_per_second
        self.last_request = 0
        self.stats = defaultdict(int)
    
    def get_usda_food(self, fdc_id):
        # Rate limiting
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_request = time.time()
        
        # Track statistics
        self.stats['requests'] += 1
        
        result = self.api.get_usda_food(fdc_id)
        if result:
            self.stats['cache_hits'] += 1
        
        return result
```

## Troubleshooting

### Common Issues

#### 1. API Key Issues

**Problem:** `ValidationError: API key is not configured`

**Solution:**
```python
# Check API key configuration
from django.conf import settings
print(f"API Key configured: {bool(settings.API_KEY)}")

# Set API key if missing
import os
os.environ['API_KEY'] = 'your-api-key-here'
```

#### 2. Network Connectivity

**Problem:** `NetworkError: Request timeout`

**Solution:**
```python
# Increase timeout and retries
client = HTTP2Client(
    base_url="https://api.nal.usda.gov/fdc/v1",
    timeout=30.0,  # Increased timeout
    retries=5,     # More retries
    backoff=1.0    # Longer backoff
)
```

#### 3. Cache Issues

**Problem:** `CacheError: Cache access failed`

**Solution:**
```python
# Check cache configuration
from django.core.cache import cache
try:
    cache.set('test', 'value', 10)
    result = cache.get('test')
    print(f"Cache working: {result == 'value'}")
except Exception as e:
    print(f"Cache error: {e}")
```

#### 4. HTTP/2 Support

**Problem:** `ImportError: h2 package not installed`

**Solution:**
```bash
# Install HTTP/2 support
pip install httpx[http2]

# Or install h2 separately
pip install h2
```

#### 5. Unicode Issues

**Problem:** Unicode characters in food names causing errors

**Solution:**
```python
# The API handles Unicode automatically, but you can test:
test_names = ["café", "naïve", "北京烤鸭", "🍎"]
for name in test_names:
    try:
        sanitized = api.sanitize_name(name)
        print(f"'{name}' -> '{sanitized}'")
    except Exception as e:
        print(f"Error with '{name}': {e}")
```

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('api_management.models')
logger.setLevel(logging.DEBUG)

# Now API calls will show detailed logs
food = api.get_usda_food(123456)
```

### Health Check

Create a health check function:

```python
def health_check(api):
    """Perform comprehensive health check."""
    checks = {}
    
    # Test API connectivity
    try:
        # Use a known good FDC ID for testing
        test_food = api.get_usda_food(123456)
        checks['api_connectivity'] = bool(test_food)
    except Exception as e:
        checks['api_connectivity'] = f"Error: {e}"
    
    # Test cache functionality
    try:
        test_data = {"test": "data"}
        key = api.save_custom_food("health_check_food", test_data)
        retrieved = api.get_custom_food("health_check_food")
        checks['cache_functionality'] = retrieved == test_data
    except Exception as e:
        checks['cache_functionality'] = f"Error: {e}"
    
    # Test nutrition calculation
    try:
        ingredients = [{"fdc_id": 123456, "amount_grams": 100}]
        nutrition = api.calculate_recipe_nutrition(ingredients)
        checks['nutrition_calculation'] = isinstance(nutrition, dict)
    except Exception as e:
        checks['nutrition_calculation'] = f"Error: {e}"
    
    return checks

# Usage
health = health_check(api)
for check, result in health.items():
    status = "✅" if result is True else "❌"
    print(f"{status} {check}: {result}")
```

---

## Support

For additional support:

1. Check the [test documentation](TEST_DOCUMENTATION.md) for examples
2. Review the [installation guide](INSTALLATION_GUIDE.md) for setup issues
3. Run the [environment validator](validate_test_environment.py) for system checks
4. Examine the comprehensive test suite for usage patterns

**Version:** 2.0  
**Last Updated:** December 2024