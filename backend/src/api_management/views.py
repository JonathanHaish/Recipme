from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import logging

from .models import HTTP2Client, FoodDataCentralAPI

logger = logging.getLogger(__name__)

# Initialize API client (singleton pattern)
_api_client = None

def get_api_client():
    """Get or create API client instance."""
    global _api_client
    if _api_client is None:
        try:
            http_client = HTTP2Client(
                base_url="https://api.nal.usda.gov/fdc/v1",
                timeout=10.0,
                retries=3
            )
            if http_client is None:
                logger.error("Failed to initialize HTTP client")
                return None
                
            _api_client = FoodDataCentralAPI(http_client, settings.API_KEY)
            if _api_client is None:
                logger.error("Failed to initialize Food API client")
                return None
                
            logger.info("API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize API client: {e}")
            return None
    return _api_client


@require_http_methods(["GET"])
def get_food_nutrition(request, fdc_id):
    """
    Get nutrition data for a USDA food by FDC ID.
    
    URL: /api/food/<fdc_id>/
    Method: GET
    
    Parameters:
        fdc_id (int): USDA Food Data Central ID
    
    Response:
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
                }
            }
        }
    
    Error Response:
        {
            "success": false,
            "error": "Error message"
        }
    """
    try:
        # Validate FDC ID
        try:
            fdc_id = int(fdc_id)
            if fdc_id <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'FDC ID must be a positive integer'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid FDC ID format. Must be a number.'
            }, status=400)
        
        # Get API client
        api = get_api_client()
        if api is None:
            return JsonResponse({
                'success': False,
                'error': 'API service unavailable'
            }, status=503)
        
        # Fetch food data
        logger.info(f"Fetching nutrition data for FDC ID: {fdc_id}")
        food_data = api.get_usda_food(fdc_id)
        
        if food_data is None:
            return JsonResponse({
                'success': False,
                'error': f'Food with FDC ID {fdc_id} not found'
            }, status=404)
        
        # Extract nutrients
        nutrients = api.extract_nutrients(food_data)
        
        response_data = {
            'success': True,
            'data': {
                'fdc_id': fdc_id,
                'description': food_data.get('description', 'Unknown Food'),
                'nutrients': nutrients,
                'data_type': food_data.get('dataType', 'Unknown'),
                'publication_date': food_data.get('publicationDate', 'Unknown')
            }
        }
        
        logger.info(f"Successfully retrieved nutrition data for FDC ID: {fdc_id}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in get_food_nutrition for FDC ID {fdc_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error occurred'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def save_custom_food(request):
    """
    Save custom food data to the system.
    
    URL: /api/custom-food/
    Method: POST
    Content-Type: application/json
    
    Request Body:
        {
            "name": "My Custom Food",
            "nutrients": [
                {
                    "nutrient": {"name": "Protein", "unitName": "g"},
                    "amount": 20.0
                },
                {
                    "nutrient": {"name": "Energy", "unitName": "kcal"},
                    "amount": 250.0
                }
            ]
        }
    
    Response:
        {
            "success": true,
            "data": {
                "key": "food:my-custom-food",
                "name": "My Custom Food",
                "message": "Custom food saved successfully"
            }
        }
    
    Error Response:
        {
            "success": false,
            "error": "Error message"
        }
    """
    try:
        # Parse JSON request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON format: {str(e)}'
            }, status=400)
        
        # Validate required fields
        if not isinstance(data, dict):
            return JsonResponse({
                'success': False,
                'error': 'Request body must be a JSON object'
            }, status=400)
        
        if 'name' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Food name is required'
            }, status=400)
        
        if not isinstance(data['name'], str) or not data['name'].strip():
            return JsonResponse({
                'success': False,
                'error': 'Food name must be a non-empty string'
            }, status=400)
        
        if 'nutrients' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Nutrients data is required'
            }, status=400)
        
        if not isinstance(data['nutrients'], list):
            return JsonResponse({
                'success': False,
                'error': 'Nutrients must be a list'
            }, status=400)
        
        if not data['nutrients']:
            return JsonResponse({
                'success': False,
                'error': 'Nutrients list cannot be empty'
            }, status=400)
        
        # Validate nutrients format
        for i, nutrient in enumerate(data['nutrients']):
            if not isinstance(nutrient, dict):
                return JsonResponse({
                    'success': False,
                    'error': f'Nutrient at index {i} must be an object'
                }, status=400)
            
            if 'amount' not in nutrient and 'value' not in nutrient:
                return JsonResponse({
                    'success': False,
                    'error': f'Nutrient at index {i} must have "amount" or "value" field'
                }, status=400)
        
        # Prepare food data in expected format
        food_data = {
            'description': data['name'],
            'foodNutrients': data['nutrients']
        }
        
        # Get API client and save food
        api = get_api_client()
        if api is None:
            return JsonResponse({
                'success': False,
                'error': 'API service unavailable'
            }, status=503)
        
        logger.info(f"Saving custom food: {data['name']}")
        key = api.save_custom_food(data['name'], food_data)
        
        if key is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to save custom food'
            }, status=500)
        
        response_data = {
            'success': True,
            'data': {
                'key': key,
                'name': data['name'],
                'message': 'Custom food saved successfully'
            }
        }
        
        logger.info(f"Successfully saved custom food: {data['name']} with key: {key}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in save_custom_food: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error occurred'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def calculate_recipe_nutrition(request):
    """
    Calculate total nutrition for a recipe with multiple ingredients.
    
    URL: /api/recipe/nutrition/
    Method: POST
    Content-Type: application/json
    
    Request Body:
        {
            "ingredients": [
                {"fdc_id": 123456, "amount_grams": 100},
                {"custom_name": "My Custom Food", "amount_grams": 50}
            ]
        }
    
    Response:
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
                "calculation_summary": "Successfully calculated nutrition for 2 ingredients"
            }
        }
    
    Error Response:
        {
            "success": false,
            "error": "Error message"
        }
    """
    try:
        # Parse JSON request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON format: {str(e)}'
            }, status=400)
        
        # Validate request structure
        if not isinstance(data, dict):
            return JsonResponse({
                'success': False,
                'error': 'Request body must be a JSON object'
            }, status=400)
        
        if 'ingredients' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Ingredients list is required'
            }, status=400)
        
        ingredients = data['ingredients']
        if not isinstance(ingredients, list):
            return JsonResponse({
                'success': False,
                'error': 'Ingredients must be a list'
            }, status=400)
        
        if not ingredients:
            return JsonResponse({
                'success': False,
                'error': 'Ingredients list cannot be empty'
            }, status=400)
        
        # Validate ingredients format
        total_weight = 0
        for i, ingredient in enumerate(ingredients):
            if not isinstance(ingredient, dict):
                return JsonResponse({
                    'success': False,
                    'error': f'Ingredient at index {i} must be an object'
                }, status=400)
            
            # Check for required identifier
            has_fdc_id = 'fdc_id' in ingredient
            has_custom_name = 'custom_name' in ingredient
            
            if not has_fdc_id and not has_custom_name:
                return JsonResponse({
                    'success': False,
                    'error': f'Ingredient at index {i} must have either "fdc_id" or "custom_name"'
                }, status=400)
            
            # Validate amount
            if 'amount_grams' not in ingredient:
                return JsonResponse({
                    'success': False,
                    'error': f'Ingredient at index {i} must have "amount_grams"'
                }, status=400)
            
            try:
                amount = float(ingredient['amount_grams'])
                if amount < 0:
                    return JsonResponse({
                        'success': False,
                        'error': f'Ingredient at index {i} amount cannot be negative'
                    }, status=400)
                total_weight += amount
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': f'Ingredient at index {i} amount must be a number'
                }, status=400)
            
            # Validate FDC ID if present
            if has_fdc_id:
                try:
                    fdc_id = int(ingredient['fdc_id'])
                    if fdc_id <= 0:
                        return JsonResponse({
                            'success': False,
                            'error': f'Ingredient at index {i} FDC ID must be positive'
                        }, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'error': f'Ingredient at index {i} FDC ID must be a number'
                    }, status=400)
            
            # Validate custom name if present
            if has_custom_name:
                if not isinstance(ingredient['custom_name'], str) or not ingredient['custom_name'].strip():
                    return JsonResponse({
                        'success': False,
                        'error': f'Ingredient at index {i} custom_name must be a non-empty string'
                    }, status=400)
        
        # Get API client and calculate nutrition
        api = get_api_client()
        if api is None:
            return JsonResponse({
                'success': False,
                'error': 'API service unavailable'
            }, status=503)
        
        logger.info(f"Calculating nutrition for recipe with {len(ingredients)} ingredients")
        nutrition = api.calculate_recipe_nutrition(ingredients)
        
        if nutrition is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to calculate recipe nutrition'
            }, status=500)
        
        # Calculate summary statistics
        total_calories = nutrition.get('calories', 0)
        has_nutrition_data = any(nutrition.get(key, 0) > 0 for key in nutrition.keys())
        
        response_data = {
            'success': True,
            'data': {
                'nutrition': nutrition,
                'total_weight': round(total_weight, 2),
                'ingredients_count': len(ingredients),
                'calculation_summary': f'Successfully calculated nutrition for {len(ingredients)} ingredients',
                'has_nutrition_data': has_nutrition_data
            }
        }
        
        logger.info(f"Successfully calculated recipe nutrition: {total_calories} calories from {len(ingredients)} ingredients")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in calculate_recipe_nutrition: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error occurred'
        }, status=500)


@require_http_methods(["GET"])
def api_health_check(request):
    """
    Health check endpoint for API status monitoring.
    
    URL: /api/health/
    Method: GET
    
    Response:
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
                "version": "1.0.0"
            }
        }
    
    Error Response:
        {
            "success": false,
            "error": "Health check failed"
        }
    """
    try:
        import datetime
        
        checks = {}
        
        # Check API client initialization
        try:
            api = get_api_client()
            checks['api_client'] = api is not None
            if api is None:
                logger.warning("API client initialization failed during health check")
        except Exception as e:
            logger.error(f"API client health check failed: {e}")
            checks['api_client'] = False
        
        # Check cache functionality
        try:
            from django.core.cache import cache
            test_key = 'health_check_test'
            test_value = 'health_check_value'
            
            cache.set(test_key, test_value, 10)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)
            
            checks['cache'] = retrieved_value == test_value
            if not checks['cache']:
                logger.warning("Cache health check failed: value mismatch")
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            checks['cache'] = False
        
        # Check Django settings
        try:
            api_key_configured = bool(getattr(settings, 'API_KEY', None))
            checks['settings'] = api_key_configured
            if not api_key_configured:
                logger.warning("API key not configured in settings")
        except Exception as e:
            logger.error(f"Settings health check failed: {e}")
            checks['settings'] = False
        
        # Determine overall status
        all_healthy = all(checks.values())
        status = "healthy" if all_healthy else "degraded"
        
        if not all_healthy:
            logger.warning(f"Health check shows degraded status: {checks}")
        
        response_data = {
            'success': True,
            'data': {
                'status': status,
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                'checks': checks,
                'version': '1.0.0',
                'service': 'API Management Service'
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Health check endpoint failed: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Health check failed',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
        }, status=500)


@require_http_methods(["GET"])
def api_usage_examples(request):
    """
    Display API usage examples and documentation.
    
    URL: /api/examples/
    Method: GET
    
    Response:
        {
            "success": true,
            "data": {
                "service_info": {...},
                "endpoints": {...},
                "examples": {...}
            }
        }
    """
    try:
        examples_data = {
            'success': True,
            'data': {
                'service_info': {
                    'name': 'API Management Service',
                    'version': '1.0.0',
                    'description': 'USDA FoodData Central API integration with custom food management',
                    'documentation': '/api/docs/',
                    'health_check': '/api/health/'
                },
                'endpoints': {
                    'get_food_nutrition': {
                        'url': '/api/food/{fdc_id}/',
                        'method': 'GET',
                        'description': 'Get nutrition data for USDA food by FDC ID',
                        'parameters': {
                            'fdc_id': 'integer - USDA Food Data Central ID'
                        },
                        'example_url': '/api/food/123456/'
                    },
                    'save_custom_food': {
                        'url': '/api/custom-food/',
                        'method': 'POST',
                        'description': 'Save custom food data to the system',
                        'content_type': 'application/json',
                        'example_body': {
                            'name': 'Homemade Granola',
                            'nutrients': [
                                {
                                    'nutrient': {'name': 'Protein', 'unitName': 'g'},
                                    'amount': 12.5
                                },
                                {
                                    'nutrient': {'name': 'Energy', 'unitName': 'kcal'},
                                    'amount': 450.0
                                },
                                {
                                    'nutrient': {'name': 'Total lipid (fat)', 'unitName': 'g'},
                                    'amount': 18.2
                                }
                            ]
                        }
                    },
                    'calculate_recipe_nutrition': {
                        'url': '/api/recipe/nutrition/',
                        'method': 'POST',
                        'description': 'Calculate total nutrition for a recipe',
                        'content_type': 'application/json',
                        'example_body': {
                            'ingredients': [
                                {'fdc_id': 123456, 'amount_grams': 100},
                                {'custom_name': 'Homemade Granola', 'amount_grams': 50},
                                {'fdc_id': 789012, 'amount_grams': 200}
                            ]
                        }
                    },
                    'health_check': {
                        'url': '/api/health/',
                        'method': 'GET',
                        'description': 'Check API service health and status'
                    },
                    'usage_examples': {
                        'url': '/api/examples/',
                        'method': 'GET',
                        'description': 'Get API usage examples and documentation'
                    }
                },
                'usage_patterns': {
                    'basic_workflow': [
                        '1. Check API health: GET /api/health/',
                        '2. Get food nutrition: GET /api/food/{fdc_id}/',
                        '3. Save custom foods: POST /api/custom-food/',
                        '4. Calculate recipe: POST /api/recipe/nutrition/'
                    ],
                    'error_handling': {
                        'check_success_field': 'Always check the "success" field in responses',
                        'handle_404': 'Food not found returns 404 status',
                        'handle_400': 'Invalid input returns 400 with error details',
                        'handle_500': 'Server errors return 500 status'
                    }
                },
                'supported_nutrients': [
                    'Protein (g)',
                    'Total lipid (fat) (g)',
                    'Carbohydrate, by difference (g)',
                    'Energy (kcal)',
                    'Fiber, total dietary (g)',
                    'Sugars, total including NLEA (g)'
                ],
                'data_sources': {
                    'usda_fdc': 'USDA FoodData Central API',
                    'custom_foods': 'User-defined custom food database'
                }
            }
        }
        
        logger.info("API usage examples requested")
        return JsonResponse(examples_data)
        
    except Exception as e:
        logger.error(f"Error in api_usage_examples: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to generate usage examples'
        }, status=500)