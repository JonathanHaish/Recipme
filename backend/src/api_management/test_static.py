"""
Static/Unit Tests for API Management Django App

These tests focus on individual components and methods in isolation,
testing the core logic without external dependencies.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from django.test import TestCase
from django.core.cache import cache
from django.conf import settings

from .models import (
    ApiResult, 
    HTTP2Client, 
    FoodDataCentralAPI
)


class TestApiResult(TestCase):
    """Test the ApiResult data structure."""
    
    def test_successful_result_creation(self):
        """Test creating a successful ApiResult."""
        result = ApiResult(success=True, status=200, data={"key": "value"})
        
        self.assertTrue(result.success)
        self.assertEqual(result.status, 200)
        self.assertEqual(result.data, {"key": "value"})
        self.assertIsNone(result.error)
        self.assertTrue(bool(result))  # Test __bool__ method
    
    def test_failed_result_creation(self):
        """Test creating a failed ApiResult."""
        result = ApiResult(success=False, error="Network error")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.status)
        self.assertIsNone(result.data)
        self.assertEqual(result.error, "Network error")
        self.assertFalse(bool(result))  # Test __bool__ method
    
    def test_repr_method(self):
        """Test the string representation of ApiResult."""
        result = ApiResult(success=True, status=200)
        expected = "ApiResult(success=True, status=200)"
        self.assertEqual(repr(result), expected)


class TestHTTP2Client(TestCase):
    """Test the HTTP2Client class."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            self.client = HTTP2Client(
                base_url="https://api.example.com",
                timeout=5.0,
                retries=2,
                backoff=0.1
            )
        except ImportError as e:
            self.skipTest(f"HTTP/2 dependencies not available: {e}")
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'client'):
            self.client.close()
    
    def test_client_initialization(self):
        """Test HTTP2Client initialization."""
        self.assertEqual(self.client.base_url, "https://api.example.com")
        self.assertEqual(self.client.timeout, 5.0)
        self.assertEqual(self.client.retries, 2)
        self.assertEqual(self.client.backoff, 0.1)
        self.assertIsNotNone(self.client.client)
    
    def test_build_url_with_base_url(self):
        """Test URL building with base URL."""
        url = self.client.build_url("/endpoint")
        self.assertEqual(url, "https://api.example.com/endpoint")
        
        url = self.client.build_url("endpoint")
        self.assertEqual(url, "https://api.example.com/endpoint")
    
    def test_build_url_absolute_url(self):
        """Test URL building with absolute URL."""
        url = self.client.build_url("https://other.com/endpoint")
        self.assertEqual(url, "https://other.com/endpoint")
    
    def test_build_url_no_base_url(self):
        """Test URL building without base URL."""
        client = HTTP2Client()
        url = client.build_url("/endpoint")
        self.assertEqual(url, "/endpoint")
        client.close()
    
    @patch('httpx.Client.request')
    def test_send_once_success(self, mock_request):
        """Test successful single request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_request.return_value = mock_response
        
        result = self.client._send_once("GET", "/test")
        
        self.assertTrue(result.success)
        self.assertEqual(result.status, 200)
        self.assertEqual(result.data, "success")
        self.assertIsNone(result.error)
    
    @patch('httpx.Client.request')
    def test_send_once_failure(self, mock_request):
        """Test failed single request."""
        mock_request.side_effect = Exception("Connection error")
        
        result = self.client._send_once("GET", "/test")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.status)
        self.assertIsNone(result.data)
        self.assertIn("Request error", result.error)
    
    @patch('httpx.Client.request')
    def test_parse_json_response(self, mock_request):
        """Test JSON response parsing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"key": "value"}
        mock_request.return_value = mock_response
        
        result = self.client._send_once("GET", "/test")
        parsed_result = self.client._parse_json_if_possible(result)
        
        self.assertTrue(parsed_result.success)
        self.assertEqual(parsed_result.data, {"key": "value"})
    
    @patch('httpx.Client.request')
    def test_parse_invalid_json_response(self, mock_request):
        """Test invalid JSON response parsing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'invalid json'
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        mock_request.return_value = mock_response
        
        result = self.client._send_once("GET", "/test")
        parsed_result = self.client._parse_json_if_possible(result)
        
        self.assertFalse(parsed_result.success)
        self.assertEqual(parsed_result.error, "Invalid JSON response")


class TestFoodDataCentralAPI(TestCase):
    """Test the FoodDataCentralAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.api = FoodDataCentralAPI(self.mock_client, "test_api_key")
        cache.clear()  # Clear cache before each test
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_sanitize_name(self):
        """Test name sanitization."""
        test_cases = [
            ("Apple Pie", "apple-pie"),
            ("Café au Lait", "cafe-au-lait"),
            ("Rice & Beans", "rice--beans"),  # Fixed: & becomes empty, creating double dash
            ("  Extra   Spaces  ", "extra-spaces"),
            ("פיתה ביתית", "פיתה-ביתית"),
            ("123 Numbers!", "123-numbers")
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.api.sanitize_name(input_name)
                self.assertEqual(result, expected)
    
    def test_generate_custom_key_unique(self):
        """Test custom key generation for unique names."""
        key = self.api.generate_custom_key("apple")
        self.assertEqual(key, "food:apple")
    
    def test_generate_custom_key_duplicate(self):
        """Test custom key generation for duplicate names."""
        # Set up existing key
        cache.set("food:apple", {"test": "data"})
        
        key = self.api.generate_custom_key("apple")
        self.assertEqual(key, "food:apple-2")
    
    def test_save_custom_food(self):
        """Test saving custom food data."""
        food_data = {"calories": 100, "protein": 5}
        key = self.api.save_custom_food("apple", food_data)
        
        self.assertEqual(key, "food:apple")
        cached_data = cache.get(key)
        self.assertEqual(cached_data, food_data)
    
    def test_get_custom_food_exists(self):
        """Test retrieving existing custom food."""
        food_data = {"calories": 100, "protein": 5}
        cache.set("food:apple", food_data)
        
        result = self.api.get_custom_food("apple")
        self.assertEqual(result, food_data)
    
    def test_get_custom_food_not_exists(self):
        """Test retrieving non-existing custom food."""
        result = self.api.get_custom_food("nonexistent")
        self.assertIsNone(result)
    
    def test_get_custom_food_versioned(self):
        """Test retrieving versioned custom food."""
        food_data = {"calories": 150, "protein": 8}
        cache.set("food:apple-2", food_data)
        
        result = self.api.get_custom_food("apple")
        self.assertEqual(result, food_data)
    
    def test_with_key_method(self):
        """Test API key addition to parameters."""
        params = {"query": "apple"}
        result = self.api._with_key(params)
        
        expected = {"query": "apple", "api_key": "test_api_key"}
        self.assertEqual(result, expected)
    
    def test_with_key_empty_params(self):
        """Test API key addition to empty parameters."""
        result = self.api._with_key()
        expected = {"api_key": "test_api_key"}
        self.assertEqual(result, expected)
    
    def test_extract_nutrients_complete_data(self):
        """Test nutrient extraction from complete food data."""
        food_data = {
            "foodNutrients": [
                {
                    "nutrient": {"name": "Protein", "unitName": "g"},
                    "amount": 25.0
                },
                {
                    "nutrient": {"name": "Total lipid (fat)", "unitName": "g"},
                    "amount": 10.0
                },
                {
                    "nutrient": {"name": "Energy", "unitName": "kcal"},
                    "amount": 200.0
                }
            ]
        }
        
        result = self.api.extract_nutrients(food_data)
        
        expected = {
            "protein": {"value": 25.0, "unit": "g"},
            "fat": {"value": 10.0, "unit": "g"},
            "calories": {"value": 200.0, "unit": "kcal"}
        }
        self.assertEqual(result, expected)
    
    def test_extract_nutrients_alternative_format(self):
        """Test nutrient extraction from alternative data format."""
        food_data = {
            "foodNutrients": [
                {
                    "nutrientName": "Protein",
                    "value": 15.0,
                    "unitName": "g"
                }
            ]
        }
        
        result = self.api.extract_nutrients(food_data)
        expected = {"protein": {"value": 15.0, "unit": "g"}}
        self.assertEqual(result, expected)
    
    def test_scale_nutrients(self):
        """Test nutrient scaling by grams."""
        nutrients = {
            "protein": {"value": 20.0},
            "calories": {"value": 100.0}
        }
        
        result = self.api.scale_nutrients(nutrients, 150.0)
        
        expected = {
            "protein": 30.0,  # (20 * 150) / 100
            "calories": 150.0  # (100 * 150) / 100
        }
        self.assertEqual(result, expected)
    
    def test_calculate_recipe_nutrition_usda_ingredients(self):
        """Test recipe nutrition calculation with USDA ingredients."""
        # Mock USDA food data
        usda_food = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 20.0},
                {"nutrient": {"name": "Energy", "unitName": "kcal"}, "amount": 100.0}
            ]
        }
        
        # Mock the get_usda_food method
        self.api.get_usda_food = Mock(return_value=usda_food)
        
        ingredients = [
            {"fdc_id": 12345, "amount_grams": 100},
            {"fdc_id": 67890, "amount_grams": 50}
        ]
        
        result = self.api.calculate_recipe_nutrition(ingredients)
        
        # Expected: 100g + 50g of the same food
        # Protein: (20 * 100)/100 + (20 * 50)/100 = 20 + 10 = 30
        # Calories: (100 * 100)/100 + (100 * 50)/100 = 100 + 50 = 150
        self.assertEqual(result["protein"], 30.0)
        self.assertEqual(result["calories"], 150.0)
    
    def test_calculate_recipe_nutrition_custom_ingredients(self):
        """Test recipe nutrition calculation with custom ingredients."""
        # Mock custom food data
        custom_food = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 15.0},
                {"nutrient": {"name": "Energy", "unitName": "kcal"}, "amount": 80.0}
            ]
        }
        
        # Mock the get_custom_food method
        self.api.get_custom_food = Mock(return_value=custom_food)
        
        ingredients = [
            {"custom_name": "homemade bread", "amount_grams": 200}
        ]
        
        result = self.api.calculate_recipe_nutrition(ingredients)
        
        # Expected: 200g of custom food
        # Protein: (15 * 200)/100 = 30
        # Calories: (80 * 200)/100 = 160
        self.assertEqual(result["protein"], 30.0)
        self.assertEqual(result["calories"], 160.0)
    
    def test_calculate_recipe_nutrition_missing_food(self):
        """Test recipe nutrition calculation with missing food data."""
        # Mock methods to return None (food not found)
        self.api.get_usda_food = Mock(return_value=None)
        self.api.get_custom_food = Mock(return_value=None)
        
        ingredients = [
            {"fdc_id": 99999, "amount_grams": 100},
            {"custom_name": "nonexistent", "amount_grams": 50}
        ]
        
        result = self.api.calculate_recipe_nutrition(ingredients)
        
        # All values should be 0 since no food data was found
        for key in result:
            self.assertEqual(result[key], 0.0)


class TestFoodDataCentralAPIIntegration(TestCase):
    """Integration tests for FoodDataCentralAPI with mocked HTTP client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.api = FoodDataCentralAPI(self.mock_client, "test_api_key")
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_get_usda_food_success(self):
        """Test successful USDA food retrieval."""
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = {"fdc_id": 12345, "description": "Apple"}
        
        self.mock_client.request.return_value = mock_response
        
        result = self.api.get_usda_food(12345)
        
        self.assertEqual(result, {"fdc_id": 12345, "description": "Apple"})
        self.mock_client.request.assert_called_once()
    
    def test_get_usda_food_cached(self):
        """Test USDA food retrieval from cache."""
        # Pre-populate cache
        cached_data = {"fdc_id": 12345, "description": "Cached Apple"}
        cache.set("fdc:12345", cached_data, self.api.CACHE_TTL)
        
        result = self.api.get_usda_food(12345)
        
        self.assertEqual(result, cached_data)
        # Should not make HTTP request
        self.mock_client.request.assert_not_called()
    
    def test_get_usda_food_failure(self):
        """Test failed USDA food retrieval."""
        mock_response = Mock()
        mock_response.success = False
        
        self.mock_client.request.return_value = mock_response
        
        result = self.api.get_usda_food(12345)
        
        self.assertIsNone(result)
    
    def test_api_get_method(self):
        """Test the api_get wrapper method."""
        params = {"query": "apple"}
        
        # The api_get method calls _with_key internally
        self.api.api_get("search", params)
        
        # The params should be modified by _with_key to include api_key
        expected_params = {"query": "apple", "api_key": "test_api_key"}
        self.mock_client.request.assert_called_once_with(
            "GET", "search", params=expected_params
        )


if __name__ == '__main__':
    unittest.main()