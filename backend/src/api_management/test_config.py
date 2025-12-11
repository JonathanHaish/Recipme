"""
Test Configuration for API Management Django App

This module contains configuration settings and utilities specifically for testing.
"""

import os
from django.conf import settings
from django.test.utils import override_settings

# Test-specific settings
TEST_SETTINGS = {
    # Use in-memory cache for faster tests
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
        }
    },
    
    # Use SQLite for faster test database
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    
    # Disable migrations for faster test setup
    'MIGRATION_MODULES': {
        'api_management': None,
    },
    
    # Test-specific logging
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',  # Reduce noise during tests
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
    
    # Disable debug mode for tests
    'DEBUG': False,
    
    # Use test API key
    'API_KEY': 'test_api_key_12345',
    
    # Disable CSRF for API tests
    'CSRF_COOKIE_SECURE': False,
    'SESSION_COOKIE_SECURE': False,
}


class TestConfig:
    """Configuration class for test utilities."""
    
    # Mock API responses
    MOCK_USDA_FOOD_RESPONSE = {
        "fdc_id": 12345,
        "description": "Apple, raw",
        "foodNutrients": [
            {
                "nutrient": {"name": "Protein", "unitName": "g"},
                "amount": 0.26
            },
            {
                "nutrient": {"name": "Total lipid (fat)", "unitName": "g"},
                "amount": 0.17
            },
            {
                "nutrient": {"name": "Carbohydrate, by difference", "unitName": "g"},
                "amount": 13.81
            },
            {
                "nutrient": {"name": "Energy", "unitName": "kcal"},
                "amount": 52
            },
            {
                "nutrient": {"name": "Fiber, total dietary", "unitName": "g"},
                "amount": 2.4
            },
            {
                "nutrient": {"name": "Sugars, total including NLEA", "unitName": "g"},
                "amount": 10.39
            }
        ]
    }
    
    MOCK_CUSTOM_FOOD_DATA = {
        "name": "Homemade Bread",
        "foodNutrients": [
            {
                "nutrient": {"name": "Protein", "unitName": "g"},
                "amount": 8.0
            },
            {
                "nutrient": {"name": "Total lipid (fat)", "unitName": "g"},
                "amount": 3.2
            },
            {
                "nutrient": {"name": "Carbohydrate, by difference", "unitName": "g"},
                "amount": 49.0
            },
            {
                "nutrient": {"name": "Energy", "unitName": "kcal"},
                "amount": 265
            }
        ]
    }
    
    # Test ingredient combinations
    SAMPLE_INGREDIENTS = [
        {"fdc_id": 12345, "amount_grams": 150},  # Apple
        {"custom_name": "homemade bread", "amount_grams": 100},
        {"fdc_id": 67890, "amount_grams": 50},   # Another USDA food
    ]
    
    # Expected nutrition values for sample ingredients
    EXPECTED_NUTRITION = {
        "protein": 12.39,    # (0.26*1.5) + 8.0 + (assumed 4.0*0.5)
        "calories": 423.0,   # (52*1.5) + 265 + (assumed 200*0.5)
        "carbohydrates": 69.715,  # (13.81*1.5) + 49 + (assumed 30*0.5)
        "fat": 3.455,        # (0.17*1.5) + 3.2 + (assumed 1*0.5)
        "fiber": 3.6,        # (2.4*1.5) + 0 + (assumed 0*0.5)
        "sugars": 15.585     # (10.39*1.5) + 0 + (assumed 0*0.5)
    }
    
    # Performance benchmarks
    PERFORMANCE_THRESHOLDS = {
        'single_food_lookup': 0.1,      # 100ms
        'recipe_calculation_10': 0.05,   # 50ms
        'recipe_calculation_100': 0.5,   # 500ms
        'cache_operation': 0.01,         # 10ms
    }
    
    # Test data sizes
    TEST_DATA_SIZES = {
        'small_recipe': 5,
        'medium_recipe': 25,
        'large_recipe': 100,
        'stress_test_recipe': 1000,
    }
    
    # Unicode test strings
    UNICODE_TEST_STRINGS = [
        "פיתה ביתית",           # Hebrew
        "café au lait",         # French with accents
        "naïve résumé",         # Multiple accents
        "北京烤鸭",              # Chinese
        "🍎 apple pie",         # Emoji
        "Ñoño niño",           # Spanish
        "Москва́",              # Russian
        "ελληνικά",            # Greek
        "العربية",             # Arabic
        "हिन्दी",               # Hindi
    ]
    
    # Error simulation scenarios
    ERROR_SCENARIOS = {
        'network_timeout': Exception("Request timeout"),
        'connection_error': Exception("Connection refused"),
        'json_decode_error': Exception("Invalid JSON"),
        'http_404': {'status_code': 404, 'text': 'Not Found'},
        'http_500': {'status_code': 500, 'text': 'Internal Server Error'},
        'empty_response': {'status_code': 200, 'text': ''},
    }


def get_test_settings():
    """Get test-specific Django settings."""
    return TEST_SETTINGS


def apply_test_settings():
    """Apply test settings as Django override."""
    return override_settings(**TEST_SETTINGS)


class MockHTTPResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, status_code=200, data=None, text=None, 
                 headers=None, success=True):
        self.status_code = status_code
        self.data = data
        self.text = text or (str(data) if data else "")
        self.headers = headers or {}
        self.success = success
    
    def json(self):
        """Mock JSON parsing."""
        if self.data:
            return self.data
        import json
        return json.loads(self.text)


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_food_nutrient(name, amount, unit="g"):
        """Create a food nutrient entry."""
        return {
            "nutrient": {"name": name, "unitName": unit},
            "amount": amount
        }
    
    @staticmethod
    def create_food_data(fdc_id, description, nutrients):
        """Create complete food data structure."""
        return {
            "fdc_id": fdc_id,
            "description": description,
            "foodNutrients": nutrients
        }
    
    @staticmethod
    def create_ingredient(fdc_id=None, custom_name=None, amount_grams=100):
        """Create an ingredient entry."""
        if fdc_id:
            return {"fdc_id": fdc_id, "amount_grams": amount_grams}
        elif custom_name:
            return {"custom_name": custom_name, "amount_grams": amount_grams}
        else:
            raise ValueError("Either fdc_id or custom_name must be provided")
    
    @staticmethod
    def create_recipe(num_ingredients=5, mix_types=True):
        """Create a recipe with specified number of ingredients."""
        ingredients = []
        for i in range(num_ingredients):
            if mix_types and i % 2 == 0:
                # Custom ingredient
                ingredients.append(
                    TestDataFactory.create_ingredient(
                        custom_name=f"custom_food_{i}",
                        amount_grams=50 + i * 10
                    )
                )
            else:
                # USDA ingredient
                ingredients.append(
                    TestDataFactory.create_ingredient(
                        fdc_id=10000 + i,
                        amount_grams=100 + i * 5
                    )
                )
        return ingredients


class TestAssertions:
    """Custom assertions for testing."""
    
    @staticmethod
    def assert_nutrition_values(test_case, actual, expected, tolerance=0.01):
        """Assert nutrition values are within tolerance."""
        for key in expected:
            test_case.assertIn(key, actual, f"Missing nutrition key: {key}")
            test_case.assertAlmostEqual(
                actual[key], expected[key], delta=tolerance,
                msg=f"Nutrition value mismatch for {key}"
            )
    
    @staticmethod
    def assert_api_result_success(test_case, result):
        """Assert API result indicates success."""
        test_case.assertTrue(result.success, f"API call failed: {result.error}")
        test_case.assertIsNotNone(result.status)
        test_case.assertIsNone(result.error)
    
    @staticmethod
    def assert_api_result_failure(test_case, result):
        """Assert API result indicates failure."""
        test_case.assertFalse(result.success)
        test_case.assertIsNotNone(result.error)
    
    @staticmethod
    def assert_performance_threshold(test_case, execution_time, threshold_key):
        """Assert execution time is within performance threshold."""
        threshold = TestConfig.PERFORMANCE_THRESHOLDS.get(threshold_key)
        if threshold:
            test_case.assertLess(
                execution_time, threshold,
                f"Performance threshold exceeded for {threshold_key}: "
                f"{execution_time:.3f}s > {threshold}s"
            )


# Environment setup for tests
def setup_test_environment():
    """Set up test environment variables."""
    test_env = {
        'DJANGO_SETTINGS_MODULE': 'mysite.settings',
        'API_KEY': 'test_api_key_12345',
        'POSTGRES_DB': 'test_recipme',
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_password',
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'REDIS_HOST': 'localhost',
    }
    
    for key, value in test_env.items():
        os.environ.setdefault(key, value)


# Initialize test environment when module is imported
setup_test_environment()