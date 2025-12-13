"""
Dynamic Tests for API Management Django Application
Tests runtime behavior, API interactions, and dynamic functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from django.test import TestCase, RequestFactory, Client
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.urls import reverse
import json
import time
import httpx
from concurrent.futures import ThreadPoolExecutor
import threading

from .models import ApiResult, HTTP2Client, FoodDataCentralAPI
from .views import get_food_nutrition, get_multiple_foods, calculate_recipe_nutrition


class HTTP2ClientDynamicTests(TestCase):
    """Test HTTP2Client dynamic behavior and interactions"""

    def setUp(self):
        self.client = HTTP2Client(
            base_url="https://api.test.com",
            timeout=5.0,
            retries=2,
            backoff=0.1
        )

    def tearDown(self):
        if hasattr(self, 'client'):
            self.client.close()

    @patch('httpx.Client')
    def test_send_once_successful_request(self, mock_client_class):
        """Test _send_once with successful request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HTTP2Client()
        result = client._send_once("GET", "test")
        
        self.assertTrue(result.success)
        self.assertEqual(result.status, 200)
        self.assertEqual(result.data, "success")

    @patch('httpx.Client')
    def test_send_once_request_exception(self, mock_client_class):
        """Test _send_once with request exception"""
        mock_client = Mock()
        mock_client.request.side_effect = httpx.RequestError("Connection failed")
        mock_client_class.return_value = mock_client
        
        client = HTTP2Client()
        result = client._send_once("GET", "test")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.status)
        self.assertIn("Request error", result.error)

    @patch('httpx.Client')
    def test_parse_json_if_possible_valid_json(self, mock_client_class):
        """Test JSON parsing with valid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"key": "value"}
        
        mock_client_class.return_value = Mock()
        
        client = HTTP2Client()
        result = ApiResult(True, 200, "raw_text", None, mock_response)
        parsed_result = client._parse_json_if_possible(result)
        
        self.assertTrue(parsed_result.success)
        self.assertEqual(parsed_result.data, {"key": "value"})

    @patch('httpx.Client')
    def test_parse_json_if_possible_invalid_json(self, mock_client_class):
        """Test JSON parsing with invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        mock_client_class.return_value = Mock()
        
        client = HTTP2Client()
        result = ApiResult(True, 200, "invalid json", None, mock_response)
        parsed_result = client._parse_json_if_possible(result)
        
        self.assertFalse(parsed_result.success)
        self.assertEqual(parsed_result.error, "Invalid JSON response")

    @patch('httpx.Client')
    def test_parse_json_if_possible_non_json_content(self, mock_client_class):
        """Test JSON parsing with non-JSON content type"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "plain text"
        
        mock_client_class.return_value = Mock()
        
        client = HTTP2Client()
        result = ApiResult(True, 200, "plain text", None, mock_response)
        parsed_result = client._parse_json_if_possible(result)
        
        self.assertTrue(parsed_result.success)
        self.assertEqual(parsed_result.data, "plain text")

    @patch('httpx.Client')
    @patch('time.sleep')
    def test_send_with_retry_success_after_retry(self, mock_sleep, mock_client_class):
        """Test retry mechanism with success after retry"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_response.headers = {"content-type": "text/plain"}
        
        # First call fails, second succeeds
        mock_client.request.side_effect = [
            httpx.RequestError("Connection failed"),
            mock_response
        ]
        mock_client_class.return_value = mock_client
        
        client = HTTP2Client(retries=2, backoff=0.1)
        result = client._send_with_retry("GET", "test")
        
        self.assertTrue(result.success)
        self.assertEqual(result.status, 200)
        mock_sleep.assert_called_once_with(0.1)

    @patch('httpx.Client')
    @patch('time.sleep')
    def test_send_with_retry_exhausted_retries(self, mock_sleep, mock_client_class):
        """Test retry mechanism with exhausted retries"""
        mock_client = Mock()
        mock_client.request.side_effect = httpx.RequestError("Connection failed")
        mock_client_class.return_value = mock_client
        
        client = HTTP2Client(retries=1, backoff=0.1)
        result = client._send_with_retry("GET", "test")
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Failed after retries")
        self.assertEqual(mock_sleep.call_count, 2)  # Called for each retry

    @patch('httpx.Client')
    def test_send_with_retry_unexpected_status_code(self, mock_client_class):
        """Test retry mechanism with unexpected status code"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.headers = {"content-type": "text/plain"}
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HTTP2Client()
        result = client._send_with_retry("GET", "test", expected_status=(200,))
        
        self.assertFalse(result.success)
        self.assertEqual(result.status, 404)
        self.assertIn("Unexpected status", result.error)

    @patch('httpx.Client')
    def test_request_method_delegates_to_send_with_retry(self, mock_client_class):
        """Test that request method delegates to _send_with_retry"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_response.headers = {"content-type": "text/plain"}
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HTTP2Client()
        result = client.request("GET", "test", expected_status=(200,))
        
        self.assertTrue(result.success)
        self.assertEqual(result.status, 200)

    def test_concurrent_requests(self):
        """Test concurrent requests handling"""
        with patch('httpx.Client') as mock_client_class:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "success"
            mock_response.headers = {"content-type": "text/plain"}
            
            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            client = HTTP2Client()
            
            def make_request():
                return client.request("GET", "test")
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [future.result() for future in futures]
            
            # All requests should succeed
            for result in results:
                self.assertTrue(result.success)
                self.assertEqual(result.status, 200)


class FoodDataCentralAPIDynamicTests(TestCase):
    """Test FoodDataCentralAPI dynamic behavior"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch.object(FoodDataCentralAPI, 'request')
    def test_search_ingredient_cache_miss_and_hit(self, mock_request):
        """Test search_ingredient caching behavior"""
        mock_response_data = {
            "foods": [
                {"fdcId": 123, "description": "Apple"},
                {"fdcId": 124, "description": "Apple juice"}
            ]
        }
        mock_result = ApiResult(True, 200, mock_response_data)
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        # First call - cache miss
        result1 = api.search_ingredient("apple")
        self.assertEqual(len(result1), 2)
        self.assertEqual(mock_request.call_count, 1)
        
        # Second call - cache hit
        result2 = api.search_ingredient("apple")
        self.assertEqual(len(result2), 2)
        self.assertEqual(mock_request.call_count, 1)  # No additional call
        
        # Results should be identical
        self.assertEqual(result1, result2)

    @patch.object(FoodDataCentralAPI, 'request')
    def test_search_ingredient_api_failure(self, mock_request):
        """Test search_ingredient with API failure"""
        mock_result = ApiResult(False, 500, None, "Server error")
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="test_key")
        result = api.search_ingredient("apple")
        
        self.assertEqual(result, [])

    @patch.object(FoodDataCentralAPI, 'request')
    def test_search_ingredient_different_parameters(self, mock_request):
        """Test search_ingredient with different parameters creates different cache keys"""
        mock_result = ApiResult(True, 200, {"foods": []})
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        # Different queries
        api.search_ingredient("apple")
        api.search_ingredient("banana")
        
        # Different page sizes
        api.search_ingredient("apple", page_size=5)
        api.search_ingredient("apple", page_size=15)
        
        # Should make 4 different API calls
        self.assertEqual(mock_request.call_count, 4)

    @patch.object(FoodDataCentralAPI, 'request')
    def test_get_food_nutrition_cache_behavior(self, mock_request):
        """Test get_food_nutrition caching behavior"""
        mock_food_data = {
            "fdcId": 123,
            "description": "Apple",
            "foodNutrients": []
        }
        mock_result = ApiResult(True, 200, mock_food_data)
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        # First call
        result1 = api.get_food_nutrition(123)
        self.assertEqual(result1["fdcId"], 123)
        
        # Second call should use cache
        result2 = api.get_food_nutrition(123)
        self.assertEqual(result2["fdcId"], 123)
        
        # Only one API call should be made
        self.assertEqual(mock_request.call_count, 1)

    @patch.object(FoodDataCentralAPI, 'request')
    def test_get_food_nutrition_api_failure(self, mock_request):
        """Test get_food_nutrition with API failure"""
        mock_result = ApiResult(False, 404, None, "Not found")
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="test_key")
        result = api.get_food_nutrition(999)
        
        self.assertIsNone(result)

    @patch.object(FoodDataCentralAPI, 'request')
    def test_get_multiple_foods_cache_behavior(self, mock_request):
        """Test get_multiple_foods caching behavior"""
        mock_foods_data = [
            {"fdcId": 123, "description": "Apple"},
            {"fdcId": 124, "description": "Banana"}
        ]
        mock_result = ApiResult(True, 200, mock_foods_data)
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        # First call
        result1 = api.get_multiple_foods([123, 124])
        self.assertEqual(len(result1), 2)
        
        # Second call with same IDs should use cache
        result2 = api.get_multiple_foods([123, 124])
        self.assertEqual(len(result2), 2)
        
        # Only one API call should be made
        self.assertEqual(mock_request.call_count, 1)

    @patch.object(FoodDataCentralAPI, 'request')
    def test_get_multiple_foods_different_order_same_cache(self, mock_request):
        """Test get_multiple_foods with different order uses same cache"""
        mock_foods_data = [
            {"fdcId": 123, "description": "Apple"},
            {"fdcId": 124, "description": "Banana"}
        ]
        mock_result = ApiResult(True, 200, mock_foods_data)
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        # First call
        result1 = api.get_multiple_foods([123, 124])
        
        # Second call with different order should use same cache
        result2 = api.get_multiple_foods([124, 123])
        
        # Only one API call should be made
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(result1, result2)

    def test_extract_key_nutrients_dynamic_processing(self):
        """Test extract_key_nutrients with various nutrient combinations"""
        api = FoodDataCentralAPI(api_key="test_key")
        
        # Test with all supported nutrients
        food_data = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 20.5},
                {"nutrient": {"name": "Total lipid (fat)", "unitName": "g"}, "amount": 10.2},
                {"nutrient": {"name": "Carbohydrate, by difference", "unitName": "g"}, "amount": 45.3},
                {"nutrient": {"name": "Energy", "unitName": "kcal"}, "amount": 250},
                {"nutrient": {"name": "Fiber, total dietary", "unitName": "g"}, "amount": 5.1},
                {"nutrient": {"name": "Sugars, total including NLEA", "unitName": "g"}, "amount": 12.8}
            ]
        }
        
        result = api.extract_key_nutrients(food_data)
        
        expected_keys = ["protein", "fat", "carbohydrates", "calories", "fiber", "sugars"]
        self.assertEqual(set(result.keys()), set(expected_keys))
        
        # Verify values
        self.assertEqual(result["protein"]["value"], 20.5)
        self.assertEqual(result["fat"]["value"], 10.2)
        self.assertEqual(result["carbohydrates"]["value"], 45.3)
        self.assertEqual(result["calories"]["value"], 250)
        self.assertEqual(result["fiber"]["value"], 5.1)
        self.assertEqual(result["sugars"]["value"], 12.8)

    def test_cache_ttl_behavior(self):
        """Test cache TTL behavior for different methods"""
        api = FoodDataCentralAPI(api_key="test_key")
        
        # Verify TTL constants
        self.assertEqual(api.SEARCH_TTL, 60 * 60)  # 1 hour
        self.assertEqual(api.FOOD_TTL, 24 * 60 * 60)  # 24 hours
        self.assertEqual(api.MULTI_TTL, 24 * 60 * 60)  # 24 hours

    @patch.object(FoodDataCentralAPI, 'request')
    def test_concurrent_api_calls(self, mock_request):
        """Test concurrent API calls behavior"""
        mock_result = ApiResult(True, 200, {"foods": [{"fdcId": 123}]})
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        def make_search():
            return api.search_ingredient("apple")
        
        # Make concurrent calls
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_search) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All should return the same result
        for result in results:
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["fdcId"], 123)

    @patch.object(FoodDataCentralAPI, 'request')
    def test_api_key_injection(self, mock_request):
        """Test API key is properly injected into requests"""
        mock_result = ApiResult(True, 200, {"foods": []})
        mock_request.return_value = mock_result
        
        api = FoodDataCentralAPI(api_key="secret_key")
        api.search_ingredient("apple")
        
        # Verify API key was included in params
        call_args = mock_request.call_args
        params = call_args[1]['params']
        self.assertEqual(params['api_key'], "secret_key")


class ViewsDynamicTests(TestCase):
    """Test views dynamic behavior and integration"""

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    @patch.object(FoodDataCentralAPI, 'get_food_nutrition')
    def test_get_food_nutrition_success_response(self, mock_get_nutrition):
        """Test get_food_nutrition with successful API response"""
        mock_nutrition = {
            "fdcId": 123,
            "description": "Apple",
            "foodNutrients": []
        }
        mock_get_nutrition.return_value = mock_nutrition
        
        request = self.factory.get('/food/', {'food': 'apple'})
        response = get_food_nutrition(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['succss'])  # Note: typo in original code
        self.assertEqual(response_data['nutrition'], mock_nutrition)

    @patch.object(FoodDataCentralAPI, 'get_food_nutrition')
    def test_get_food_nutrition_not_found_response(self, mock_get_nutrition):
        """Test get_food_nutrition with food not found"""
        mock_get_nutrition.return_value = None
        
        request = self.factory.get('/food/', {'food': 'nonexistent'})
        response = get_food_nutrition(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('not found', response_data['error'])

    @patch.object(FoodDataCentralAPI, 'get_multiple_foods')
    def test_get_multiple_foods_success(self, mock_get_multiple):
        """Test get_multiple_foods with successful response"""
        mock_foods = [
            {"fdcId": 123, "description": "Apple"},
            {"fdcId": 124, "description": "Banana"}
        ]
        mock_get_multiple.return_value = mock_foods
        
        # Note: The view has a bug - it expects list but gets string from GET
        # This test shows the current behavior
        request = self.factory.get('/foods/', {'foods': ['apple', 'banana']})
        response = get_multiple_foods(request)
        
        # This will actually return HttpResponseBadRequest due to the bug
        self.assertIsInstance(response, HttpResponseBadRequest)

    @patch.object(FoodDataCentralAPI, 'extract_key_nutrients')
    def test_calculate_recipe_nutrition_success(self, mock_extract):
        """Test calculate_recipe_nutrition with valid recipe"""
        mock_nutrients = {
            "protein": {"value": 20.5, "unit": "g"},
            "calories": {"value": 250, "unit": "kcal"}
        }
        mock_extract.return_value = mock_nutrients
        
        recipe = {
            'name': 'Test Recipe',
            'foodNutrients': ['apple', 'banana', 123]  # Mixed types
        }
        
        request = self.factory.get('/recipe/nutrition/', {'recipe': recipe})
        response = calculate_recipe_nutrition(request)
        
        # The view returns the result directly, not as JsonResponse
        self.assertEqual(response, mock_nutrients)

    def test_view_method_validation_comprehensive(self):
        """Test all views reject non-GET methods"""
        methods = ['POST', 'PUT', 'DELETE', 'PATCH']
        views = [get_food_nutrition, get_multiple_foods, calculate_recipe_nutrition]
        
        for view in views:
            for method in methods:
                request = getattr(self.factory, method.lower())('/')
                response = view(request)
                self.assertIsInstance(response, HttpResponseBadRequest)

    def test_parameter_validation_edge_cases(self):
        """Test parameter validation with edge cases"""
        # Test with None values
        request = self.factory.get('/food/', {'food': None})
        response = get_food_nutrition(request)
        self.assertIsInstance(response, HttpResponseBadRequest)
        
        # Test with empty string after strip
        request = self.factory.get('/food/', {'food': '   '})
        response = get_food_nutrition(request)
        self.assertIsInstance(response, HttpResponseBadRequest)

    @patch.object(FoodDataCentralAPI, 'get_food_nutrition')
    def test_get_food_nutrition_with_special_characters(self, mock_get_nutrition):
        """Test get_food_nutrition with special characters in food name"""
        mock_nutrition = {"fdcId": 123, "description": "Café au lait"}
        mock_get_nutrition.return_value = mock_nutrition
        
        request = self.factory.get('/food/', {'food': 'café au lait'})
        response = get_food_nutrition(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['succss'])

    def test_concurrent_view_requests(self):
        """Test concurrent requests to views"""
        def make_request():
            request = self.factory.get('/food/', {'food': 'apple'})
            return get_food_nutrition(request)
        
        with patch.object(FoodDataCentralAPI, 'get_food_nutrition') as mock_get:
            mock_get.return_value = {"fdcId": 123}
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in futures]
            
            # All responses should be JsonResponse
            for response in responses:
                self.assertIsInstance(response, JsonResponse)


class IntegrationDynamicTests(TestCase):
    """Test integration between components"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch('httpx.Client')
    def test_full_api_flow_integration(self, mock_client_class):
        """Test full API flow from HTTP client to view response"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "foods": [{"fdcId": 123, "description": "Apple"}]
        }
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Make request through view
        factory = RequestFactory()
        request = factory.get('/food/', {'food': 'apple'})
        
        with patch.object(FoodDataCentralAPI, 'get_food_nutrition') as mock_get:
            mock_get.return_value = {"fdcId": 123, "description": "Apple"}
            response = get_food_nutrition(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['succss'])

    def test_cache_integration_across_methods(self):
        """Test cache integration across different API methods"""
        with patch.object(FoodDataCentralAPI, 'request') as mock_request:
            mock_request.return_value = ApiResult(True, 200, {"foods": []})
            
            api = FoodDataCentralAPI(api_key="test_key")
            
            # Make multiple calls that should use different cache keys
            api.search_ingredient("apple")
            api.search_ingredient("apple", page_size=5)
            api.get_food_nutrition(123)
            api.get_multiple_foods([123, 124])
            
            # Each should make separate API calls due to different cache keys
            self.assertEqual(mock_request.call_count, 4)

    def test_error_propagation_through_stack(self):
        """Test error propagation from HTTP client through to view"""
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.request.side_effect = httpx.RequestError("Network error")
            mock_client_class.return_value = mock_client
            
            factory = RequestFactory()
            request = factory.get('/food/', {'food': 'apple'})
            response = get_food_nutrition(request)
            
            # Should return error response
            self.assertIsInstance(response, JsonResponse)
            response_data = json.loads(response.content)
            self.assertFalse(response_data['success'])

    @patch.object(FoodDataCentralAPI, 'request')
    def test_cache_performance_under_load(self, mock_request):
        """Test cache performance under concurrent load"""
        mock_request.return_value = ApiResult(True, 200, {"foods": []})
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        def make_cached_call():
            return api.search_ingredient("apple")
        
        # Make many concurrent calls
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_cached_call) for _ in range(50)]
            results = [future.result() for future in futures]
        
        # Should only make one API call due to caching
        self.assertEqual(mock_request.call_count, 1)
        
        # All results should be identical
        for result in results:
            self.assertEqual(result, [])

    def test_memory_usage_with_large_responses(self):
        """Test memory handling with large API responses"""
        with patch.object(FoodDataCentralAPI, 'request') as mock_request:
            # Create large response
            large_foods = [{"fdcId": i, "description": f"Food {i}"} for i in range(1000)]
            mock_request.return_value = ApiResult(True, 200, {"foods": large_foods})
            
            api = FoodDataCentralAPI(api_key="test_key")
            result = api.search_ingredient("test")
            
            self.assertEqual(len(result), 1000)
            self.assertEqual(result[0]["fdcId"], 0)
            self.assertEqual(result[999]["fdcId"], 999)


if __name__ == '__main__':
    unittest.main()