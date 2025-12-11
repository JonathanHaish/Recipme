# API Endpoints Guide

## Overview

This guide provides detailed information about all available API endpoints in the API Management service. The service provides access to USDA FoodData Central nutrition data and custom food management capabilities.

## Base URL

All API endpoints are available under the `/api/` path:
- Local development: `http://localhost:8000/api/`
- Production: `https://yourdomain.com/api/`

## Authentication

Currently, the API uses server-side API key authentication for USDA FoodData Central. No client authentication is required for the endpoints.

## Response Format

All endpoints return JSON responses with a consistent structure:

### Success Response
```json
{
    "success": true,
    "data": {
        // Response data here
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message description"
}
```

## Endpoints

### 1. Get Food Nutrition

Get nutrition data for a USDA food by FDC ID.

**Endpoint:** `GET /api/food/{fdc_id}/`

**Parameters:**
- `fdc_id` (integer, required): USDA Food Data Central ID

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/food/123456/"
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "fdc_id": 123456,
        "description": "Apple, raw",
        "nutrients": {
            "protein": {"value": 0.26, "unit": "g"},
            "calories": {"value": 52, "unit": "kcal"},
            "carbohydrates": {"value": 13.81, "unit": "g"},
            "fat": {"value": 0.17, "unit": "g"},
            "fiber": {"value": 2.4, "unit": "g"},
            "sugars": {"value": 10.39, "unit": "g"}
        },
        "data_type": "Foundation",
        "publication_date": "2021-10-28"
    }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid FDC ID format
- `404 Not Found`: Food not found
- `503 Service Unavailable`: API service unavailable

### 2. Save Custom Food

Save custom food data to the system.

**Endpoint:** `POST /api/custom-food/`

**Content-Type:** `application/json`

**Request Body:**
```json
{
    "name": "Homemade Granola",
    "nutrients": [
        {
            "nutrient": {"name": "Protein", "unitName": "g"},
            "amount": 12.5
        },
        {
            "nutrient": {"name": "Energy", "unitName": "kcal"},
            "amount": 450.0
        },
        {
            "nutrient": {"name": "Total lipid (fat)", "unitName": "g"},
            "amount": 18.2
        },
        {
            "nutrient": {"name": "Carbohydrate, by difference", "unitName": "g"},
            "amount": 65.3
        },
        {
            "nutrient": {"name": "Fiber, total dietary", "unitName": "g"},
            "amount": 8.1
        }
    ]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/custom-food/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Homemade Granola",
    "nutrients": [
      {
        "nutrient": {"name": "Protein", "unitName": "g"},
        "amount": 12.5
      },
      {
        "nutrient": {"name": "Energy", "unitName": "kcal"},
        "amount": 450.0
      }
    ]
  }'
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "key": "food:homemade-granola",
        "name": "Homemade Granola",
        "message": "Custom food saved successfully"
    }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid request format or missing required fields
- `503 Service Unavailable`: API service unavailable

### 3. Calculate Recipe Nutrition

Calculate total nutrition for a recipe with multiple ingredients.

**Endpoint:** `POST /api/recipe/nutrition/`

**Content-Type:** `application/json`

**Request Body:**
```json
{
    "ingredients": [
        {"fdc_id": 123456, "amount_grams": 100},
        {"custom_name": "Homemade Granola", "amount_grams": 50},
        {"fdc_id": 789012, "amount_grams": 200}
    ]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/recipe/nutrition/" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"fdc_id": 123456, "amount_grams": 100},
      {"custom_name": "Homemade Granola", "amount_grams": 50}
    ]
  }'
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "nutrition": {
            "protein": 25.5,
            "calories": 350.0,
            "carbohydrates": 45.2,
            "fat": 12.1,
            "fiber": 8.3,
            "sugars": 15.7
        },
        "total_weight": 150.0,
        "ingredients_count": 2,
        "calculation_summary": "Successfully calculated nutrition for 2 ingredients",
        "has_nutrition_data": true
    }
}
```

**Ingredient Format:**
- **USDA Ingredient:** `{"fdc_id": 123456, "amount_grams": 100}`
- **Custom Ingredient:** `{"custom_name": "My Food", "amount_grams": 50}`

**Error Responses:**
- `400 Bad Request`: Invalid ingredients format or missing required fields
- `503 Service Unavailable`: API service unavailable

### 4. Health Check

Check API service health and status.

**Endpoint:** `GET /api/health/`

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/health/"
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "timestamp": "2024-12-11T10:30:00Z",
        "checks": {
            "api_client": true,
            "cache": true,
            "settings": true
        },
        "version": "1.0.0",
        "service": "API Management Service"
    }
}
```

**Status Values:**
- `healthy`: All systems operational
- `degraded`: Some systems have issues

### 5. Usage Examples

Get API usage examples and documentation.

**Endpoint:** `GET /api/examples/`

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/examples/"
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "service_info": {
            "name": "API Management Service",
            "version": "1.0.0",
            "description": "USDA FoodData Central API integration with custom food management"
        },
        "endpoints": {
            // Detailed endpoint information
        },
        "usage_patterns": {
            // Common usage patterns
        },
        "supported_nutrients": [
            "Protein (g)",
            "Total lipid (fat) (g)",
            "Carbohydrate, by difference (g)",
            "Energy (kcal)",
            "Fiber, total dietary (g)",
            "Sugars, total including NLEA (g)"
        ]
    }
}
```

## Usage Patterns

### Basic Workflow

1. **Check API Health**
   ```bash
   curl -X GET "http://localhost:8000/api/health/"
   ```

2. **Get Food Nutrition**
   ```bash
   curl -X GET "http://localhost:8000/api/food/123456/"
   ```

3. **Save Custom Food**
   ```bash
   curl -X POST "http://localhost:8000/api/custom-food/" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Food", "nutrients": [...]}'
   ```

4. **Calculate Recipe**
   ```bash
   curl -X POST "http://localhost:8000/api/recipe/nutrition/" \
     -H "Content-Type: application/json" \
     -d '{"ingredients": [...]}'
   ```

### Error Handling

Always check the `success` field in responses:

```javascript
fetch('/api/food/123456/')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Food data:', data.data);
    } else {
      console.error('Error:', data.error);
    }
  });
```

### Recipe Building Example

```javascript
// Build a recipe step by step
const recipe = {
  ingredients: []
};

// Add USDA ingredient
recipe.ingredients.push({
  fdc_id: 123456,
  amount_grams: 100
});

// Add custom ingredient
recipe.ingredients.push({
  custom_name: "Homemade Sauce",
  amount_grams: 50
});

// Calculate nutrition
fetch('/api/recipe/nutrition/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(recipe)
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Recipe nutrition:', data.data.nutrition);
    console.log('Total calories:', data.data.nutrition.calories);
  }
});
```

## Supported Nutrients

The API extracts and calculates the following nutrients:

| Nutrient | USDA Name | Unit | Key |
|----------|-----------|------|-----|
| Protein | Protein | g | `protein` |
| Fat | Total lipid (fat) | g | `fat` |
| Carbohydrates | Carbohydrate, by difference | g | `carbohydrates` |
| Calories | Energy | kcal | `calories` |
| Fiber | Fiber, total dietary | g | `fiber` |
| Sugars | Sugars, total including NLEA | g | `sugars` |

## Data Sources

### USDA FoodData Central
- **Source:** Official USDA nutrition database
- **Access:** Via FDC ID numbers
- **Coverage:** 300,000+ food items
- **Updates:** Regular USDA updates

### Custom Foods
- **Source:** User-defined foods
- **Storage:** Local cache system
- **Access:** Via custom names
- **Persistence:** Permanent storage

## Rate Limits

Currently, there are no explicit rate limits, but the USDA API has its own limits:
- **USDA API:** 1000 requests per hour per API key
- **Caching:** Reduces API calls through intelligent caching

## Error Codes

| HTTP Status | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |
| 503 | Service Unavailable - External API issues |

## Testing

### Using curl

```bash
# Test health check
curl -X GET "http://localhost:8000/api/health/"

# Test food lookup
curl -X GET "http://localhost:8000/api/food/123456/"

# Test custom food creation
curl -X POST "http://localhost:8000/api/custom-food/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Food", "nutrients": [{"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 10}]}'
```

### Using Python

```python
import requests

# Health check
response = requests.get('http://localhost:8000/api/health/')
print(response.json())

# Get food nutrition
response = requests.get('http://localhost:8000/api/food/123456/')
if response.json()['success']:
    nutrition = response.json()['data']['nutrients']
    print(f"Calories: {nutrition['calories']['value']} {nutrition['calories']['unit']}")
```

### Using JavaScript

```javascript
// Modern fetch API
async function getFoodNutrition(fdcId) {
  try {
    const response = await fetch(`/api/food/${fdcId}/`);
    const data = await response.json();
    
    if (data.success) {
      return data.data;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Error fetching food nutrition:', error);
    return null;
  }
}
```

## Troubleshooting

### Common Issues

1. **"API service unavailable"**
   - Check if API key is configured in Django settings
   - Verify USDA API connectivity
   - Check health endpoint for detailed status

2. **"Food not found"**
   - Verify FDC ID is correct
   - Check USDA database for food availability
   - Try alternative FDC IDs

3. **"Invalid JSON format"**
   - Ensure Content-Type header is set to application/json
   - Validate JSON syntax
   - Check for proper escaping of special characters

4. **Cache issues**
   - Check Redis/cache backend configuration
   - Verify cache connectivity in health check
   - Clear cache if needed

### Debug Mode

Enable Django debug mode for detailed error information:
```python
# In settings.py
DEBUG = True
```

---

**Version:** 1.0.0  
**Last Updated:** December 2024  
**Support:** Check logs for detailed error information