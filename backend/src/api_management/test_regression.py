"""
Regression Tests for API Management Django Application
Tests for preventing regressions and ensuring backward compatibility
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory, Client, override_settings
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.urls import reverse, resolve
from django.conf import settings
import json
import time
import httpx
import threading
from concurrent.futures import ThreadPoolExecutor
import sys
import os

from .models import ApiResult, HTTP2Client, FoodDataCentralAPI
from .views import get_food_nutrition, get_multiple_foods, calculate_recipe_nutrition, render_response, api_data_view


class BackwardCompatibilityTests(TestCase):
    """Test backward compatibility of API responses and behavior"""

    def setUp(self):
        self.factory = RequestFactory()

    def test_api_result_backward_compatibility(self):
        """Test ApiResult maintains backward compatibility"""
        # Test original constructor signature
        result = ApiResult(True, 200, "data", "error", "raw")
        self.assertTrue(result.success)
        self.assertEqual(result.status, 200)
        self.assertEqual(result.data, "data")
        self.assertEqual(result.error, "error")
        self.assertEqual(result.raw, "raw")

    def test_api_result_boolean_behavior_regression(self):
        """Test ApiResult boolean behavior hasn't changed"""
        # Success case
        success_result = ApiResult(True)
        self.assertTrue(bool(success_result))
        self.assertTrue(success_result)
        
        # Failure case
        failure_result = ApiResult(False)
        self.assertFalse(bool(failure_result))
        self.assertFalse(failure_result)

    def test_api_result_repr_format_regression(self):
        """Test ApiResult repr format hasn't changed"""
        result = ApiResult(True, 200)
        expected_format = "ApiResult(success=True, status=200)"
        self.assertEqual(repr(result), expected_format)

    def test_http2_client_constructor_backward_compatibility(self):
        """Test HTTP2Client constructor maintains backward compatibility"""
        # Default constructor
        client1 = HTTP2Client()
        self.assertIsNone(client1.base_url)
        self.assertEqual(client1.timeout, 8.0)
        self.assertEqual(client1.retries, 3)
        self.assertEqual(client1.backoff, 0.5)
        
        # Full constructor
        client2 = HTTP2Client("https://api.nal.usda.gov/fdc/v1", 10.0, 5, 1.0)
        self.assertEqual(client2.base_url, "https://api.nal.usda.gov/fdc/v1")
        self.assertEqual(client2.timeout, 10.0)
        self.assertEqual(client2.retries, 5)
        self.assertEqual(client2.backoff, 1.0)

    def test_food_api_cache_ttl_constants_regression(self):
        """Test FoodDataCentralAPI cache TTL constants haven't changed"""
        self.assertEqual(FoodDataCentralAPI.SEARCH_TTL, 3600)  # 1 hour
        self.assertEqual(FoodDataCentralAPI.FOOD_TTL, 86400)   # 24 hours
        self.assertEqual(FoodDataCentralAPI.MULTI_TTL, 86400)  # 24 hours

    @patch.object(FoodDataCentralAPI, 'get_food_nutrition')
    def test_get_food_nutrition_response_format_regression(self, mock_get_nutrition):
        """Test get_food_nutrition response format hasn't changed"""
        mock_nutrition = {"fdcId": 123, "description": "Apple"}
        mock_get_nutrition.return_value = mock_nutrition
        
        request = self.factory.get('/food/', {'food': 'apple'})
        response = get_food_nutrition(request)
        
        self.assertIsInstance(response, dict)
        
        # Check response structure
        self.assertIn('nutrition', response)
        self.assertIn('succss', response)  # Note: original typo preserved
        self.assertTrue(response['succss'])
        self.assertEqual(response['nutrition'], mock_nutrition)

    @patch.object(FoodDataCentralAPI, 'get_food_nutrition')
    def test_get_food_nutrition_error_response_format_regression(self, mock_get_nutrition):
        """Test get_food_nutrition error response format hasn't changed"""
        mock_get_nutrition.return_value = None
        
        request = self.factory.get('/food/', {'food': 'nonexistent'})
        response = get_food_nutrition(request)
        
        self.assertIsInstance(response, dict)
        
        # Check error response structure
        self.assertIn('error', response)
        self.assertIn('success', response)
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], "The food not found in the system")

    def test_url_patterns_backward_compatibility(self):
        """Test URL patterns maintain backward compatibility"""
        from .urls import urlpatterns, app_name
        
        # Check app name
        self.assertEqual(app_name, 'api_management')
        
        # Check URL patterns exist
        self.assertIsInstance(urlpatterns, list)
        self.assertEqual(len(urlpatterns), 1)  # Now single dispatcher endpoint
        
        # Check dispatcher pattern
        pattern_names = [pattern.name for pattern in urlpatterns if hasattr(pattern, 'name')]
        self.assertIn('api_data_view', pattern_names)

    def test_view_parameter_validation_regression(self):
        """Test view parameter validation behavior hasn't changed"""
        # get_food_nutrition parameter validation
        request = self.factory.get('/food/')  # Missing 'food' parameter
        response = get_food_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))
        
        # get_multiple_foods parameter validation
        request = self.factory.get('/foods/')  # Missing 'foods' parameter
        response = get_multiple_foods(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))
        
        # calculate_recipe_nutrition parameter validation
        request = self.factory.get('/recipe/nutrition/')  # Missing 'recipe' parameter
        response = calculate_recipe_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_http_method_restrictions_regression(self):
        """Test HTTP method restrictions haven't changed"""
        views = [get_food_nutrition, get_multiple_foods, calculate_recipe_nutrition]
        methods = ['POST', 'PUT', 'DELETE', 'PATCH']
        
        for view in views:
            for method in methods:
                request = getattr(self.factory, method.lower())('/')
                response = view(request)
                self.assertIsInstance(response, dict)
                self.assertFalse(response.get('success'))

    @patch('api_management.views.settings')
    def test_dispatcher_response_format_regression(self, mock_settings):
        """Test dispatcher response format consistency"""
        mock_settings.INTERNAL_API_SECRET_KEY = "test_secret"
        
        request = self.factory.get('/api/food/', HTTP_X_MY_APP_SECRET_KEY="test_secret")
        request.path = "/api/food/"
        
        with patch('api_management.views.get_food_nutrition') as mock_get_food:
            mock_get_food.return_value = {"success": True, "data": "test"}
            response = api_data_view(request)
            
            self.assertIsInstance(response, JsonResponse)
            response_data = json.loads(response.content)
            self.assertIn('status', response_data)
            self.assertIn('res', response_data)
            self.assertEqual(response_data['status'], 200)

    def test_render_response_format_regression(self):
        """Test render_response format hasn't changed"""
        test_data = {"success": True, "data": "test"}
        response = render_response(200, test_data)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        
        # Check wrapper format
        self.assertIn('status', response_data)
        self.assertIn('res', response_data)
        self.assertEqual(response_data['status'], 200)
        self.assertEqual(response_data['res'], test_data)


class DataFormatRegressionTests(TestCase):
    """Test data format consistency and regression prevention"""

    def test_extract_key_nutrients_output_format_regression(self):
        """Test extract_key_nutrients output format hasn't changed"""
        api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
        
        food_data = {
            "foodNutrients": [
                {
                    "nutrient": {"name": "Protein", "unitName": "g"},
                    "amount": 20.5
                }
            ]
        }
        
        result = api.extract_key_nutrients(food_data)
        
        # Check output format
        self.assertIsInstance(result, dict)
        self.assertIn("protein", result)
        self.assertIsInstance(result["protein"], dict)
        self.assertIn("value", result["protein"])
        self.assertIn("unit", result["protein"])
        self.assertEqual(result["protein"]["value"], 20.5)
        self.assertEqual(result["protein"]["unit"], "g")

    def test_nutrient_mapping_regression(self):
        """Test nutrient name mapping hasn't changed"""
        api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
        
        # Test all mapped nutrients
        nutrient_tests = [
            ("Protein", "protein"),
            ("Total lipid (fat)", "fat"),
            ("Carbohydrate, by difference", "carbohydrates"),
            ("Energy", "calories"),
            ("Fiber, total dietary", "fiber"),
            ("Sugars, total including NLEA", "sugars")
        ]
        
        for nutrient_name, expected_key in nutrient_tests:
            food_data = {
                "foodNutrients": [
                    {
                        "nutrient": {"name": nutrient_name, "unitName": "g"},
                        "amount": 10.0
                    }
                ]
            }
            
            result = api.extract_key_nutrients(food_data)
            self.assertIn(expected_key, result)

    def test_cache_key_format_regression(self):
        """Test cache key format hasn't changed"""
        api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
        
        payload = {"query": "apple", "pageSize": 10}
        cache_key = api._cache_key("search", payload)
        
        # Check format: "fdc:prefix:hash"
        parts = cache_key.split(":")
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], "fdc")
        self.assertEqual(parts[1], "search")
        self.assertEqual(len(parts[2]), 64)  # SHA256 hash length

    def test_api_key_injection_format_regression(self):
        """Test API key injection format hasn't changed"""
        api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
        api.api_key = "test_key"
        
        # Test with empty params
        result = api._with_key()
        self.assertEqual(result, {"api_key": "test_key"})
        
        # Test with existing params
        result = api._with_key({"query": "apple"})
        expected = {"query": "apple", "api_key": "test_key"}
        self.assertEqual(result, expected)


class PerformanceRegressionTests(TestCase):
    """Test performance characteristics haven't regressed"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch.object(FoodDataCentralAPI, 'request')
    def test_cache_hit_performance_regression(self, mock_request):
        """Test cache hit performance hasn't regressed"""
        mock_request.return_value = ApiResult(True, 200, {"foods": []})
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        # First call - cache miss
        start_time = time.time()
        api.search_ingredient("apple")
        first_call_time = time.time() - start_time
        
        # Second call - cache hit (should be much faster)
        start_time = time.time()
        api.search_ingredient("apple")
        second_call_time = time.time() - start_time
        
        # Cache hit should be significantly faster
        self.assertLess(second_call_time, first_call_time * 0.1)  # At least 10x faster

    @patch.object(FoodDataCentralAPI, 'request')
    def test_concurrent_request_performance_regression(self, mock_request):
        """Test concurrent request performance hasn't regressed"""
        mock_request.return_value = ApiResult(True, 200, {"foods": []})
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        def make_request():
            return api.search_ingredient("apple")
        
        # Measure concurrent performance
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in futures]
        concurrent_time = time.time() - start_time
        
        # Should complete reasonably quickly
        self.assertLess(concurrent_time, 1.0)  # Less than 1 second
        
        # Should only make one API call due to caching
        self.assertEqual(mock_request.call_count, 1)

    def test_memory_usage_regression(self):
        """Test memory usage patterns haven't regressed"""
        import gc
        
        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Create and use API objects
        for i in range(100):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            result = ApiResult(True, 200, f"data_{i}")
            client = HTTP2Client()
            client.close()
        
        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory usage shouldn't grow excessively
        object_growth = final_objects - initial_objects
        self.assertLess(object_growth, 1000)  # Reasonable growth limit


class ErrorHandlingRegressionTests(TestCase):
    """Test error handling behavior hasn't regressed"""

    def setUp(self):
        self.factory = RequestFactory()

    def test_http_client_error_handling_regression(self):
        """Test HTTP client error handling hasn't changed"""
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.request.side_effect = httpx.RequestError("Connection failed")
            mock_client_class.return_value = mock_client
            
            client = HTTP2Client()
            result = client._send_once("GET", "test")
            
            self.assertFalse(result.success)
            self.assertIsNone(result.status)
            self.assertIn("Request error", result.error)

    def test_json_parsing_error_handling_regression(self):
        """Test JSON parsing error handling hasn't changed"""
        with patch('httpx.Client') as mock_client_class:
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

    def test_view_error_responses_regression(self):
        """Test view error responses haven't changed"""
        # Test method validation
        request = self.factory.post('/food/')
        response = get_food_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))
        
        # Test parameter validation
        request = self.factory.get('/food/')
        response = get_food_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    @patch.object(FoodDataCentralAPI, 'request')
    def test_api_failure_handling_regression(self, mock_request):
        """Test API failure handling hasn't changed"""
        mock_request.return_value = ApiResult(False, 500, None, "Server error")
        
        api = FoodDataCentralAPI(api_key="test_key")
        
        # Test search failure
        result = api.search_ingredient("apple")
        self.assertEqual(result, [])
        
        # Test nutrition failure
        result = api.get_food_nutrition(123)
        self.assertIsNone(result)
        
        # Test multiple foods failure
        result = api.get_multiple_foods([123, 124])
        self.assertEqual(result, [])


class ConfigurationRegressionTests(TestCase):
    """Test configuration and settings regression"""

    def test_django_settings_regression(self):
        """Test Django settings haven't changed unexpectedly"""
        # Test API_KEY setting exists
        self.assertTrue(hasattr(settings, 'API_KEY'))
        
        # Test INTERNAL_API_SECRET_KEY setting exists
        self.assertTrue(hasattr(settings, 'INTERNAL_API_SECRET_KEY'))
        
        # Test app is in INSTALLED_APPS
        self.assertIn('api_management', settings.INSTALLED_APPS)
        
        # Test cache configuration
        self.assertIn('default', settings.CACHES)

    def test_url_configuration_regression(self):
        """Test URL configuration hasn't changed"""
        from django.urls import reverse
        
        # Test URL reversal works for dispatcher
        try:
            url = reverse('api_management:api_data_view')
            self.assertTrue(url.endswith('/'))
        except:
            self.fail("URL reversal failed")

    def test_middleware_configuration_regression(self):
        """Test middleware configuration is compatible"""
        # Test CORS middleware is present
        self.assertIn('corsheaders.middleware.CorsMiddleware', settings.MIDDLEWARE)
        
        # Test CORS settings
        self.assertTrue(hasattr(settings, 'CORS_ALLOWED_ORIGINS'))
        self.assertTrue(hasattr(settings, 'CORS_ALLOW_CREDENTIALS'))


class DatabaseRegressionTests(TestCase):
    """Test database-related regression issues"""

    def test_cache_backend_regression(self):
        """Test cache backend configuration hasn't regressed"""
        from django.core.cache import cache
        
        # Test cache is accessible
        self.assertIsNotNone(cache)
        
        # Test basic cache operations
        cache.set('test_key', 'test_value', 60)
        self.assertEqual(cache.get('test_key'), 'test_value')
        cache.delete('test_key')
        self.assertIsNone(cache.get('test_key'))

    def test_database_configuration_regression(self):
        """Test database configuration is valid"""
        from django.db import connection
        
        # Test database connection is configured
        self.assertIsNotNone(connection.settings_dict)
        self.assertEqual(connection.settings_dict['ENGINE'], 'django.db.backends.postgresql')


class SecurityRegressionTests(TestCase):
    """Test security-related regression issues"""

    def test_api_key_handling_regression(self):
        """Test API key handling security hasn't regressed"""
        api = FoodDataCentralAPI(api_key="secret_key")
        
        # API key should be stored securely
        self.assertEqual(api.api_key, "secret_key")
        
        # API key should be included in requests
        params = api._with_key({"query": "test"})
        self.assertEqual(params["api_key"], "secret_key")

    def test_input_validation_regression(self):
        """Test input validation security hasn't regressed"""
        # Test SQL injection prevention (basic check)
        request = self.factory.get('/food/', {'food': "'; DROP TABLE users; --"})
        response = get_food_nutrition(request)
        # Should not crash and should handle safely
        self.assertIsInstance(response, (JsonResponse, HttpResponseBadRequest))

    def test_xss_prevention_regression(self):
        """Test XSS prevention hasn't regressed"""
        # Test script injection in parameters
        request = self.factory.get('/food/', {'food': '<script>alert("xss")</script>'})
        response = get_food_nutrition(request)
        # Should handle safely without executing script
        self.assertIsInstance(response, (JsonResponse, HttpResponseBadRequest))


class IntegrationRegressionTests(TestCase):
    """Test integration points haven't regressed"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch('httpx.Client')
    @patch('api_management.views.settings')
    def test_end_to_end_flow_regression(self, mock_settings, mock_client_class):
        """Test end-to-end flow hasn't regressed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "test_secret"
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"foods": [{"fdcId": 123}]}
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Test full flow through dispatcher
        factory = RequestFactory()
        request = factory.get('/api/food/', {'food': 'apple'}, HTTP_X_MY_APP_SECRET_KEY="test_secret")
        request.path = "/api/food/"
        
        with patch.object(FoodDataCentralAPI, 'get_food_nutrition') as mock_get:
            mock_get.return_value = {"fdcId": 123, "description": "Apple"}
            response = api_data_view(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 200)

    def test_cache_integration_regression(self):
        """Test cache integration hasn't regressed"""
        with patch.object(FoodDataCentralAPI, 'request') as mock_request:
            mock_request.return_value = ApiResult(True, 200, {"foods": []})
            
            api = FoodDataCentralAPI(api_key="test_key")
            
            # First call
            result1 = api.search_ingredient("apple")
            
            # Second call should use cache
            result2 = api.search_ingredient("apple")
            
            # Should only make one API call
            self.assertEqual(mock_request.call_count, 1)
            self.assertEqual(result1, result2)

    def test_concurrent_access_regression(self):
        """Test concurrent access patterns haven't regressed"""
        with patch.object(FoodDataCentralAPI, 'request') as mock_request:
            mock_request.return_value = ApiResult(True, 200, {"foods": []})
            
            api = FoodDataCentralAPI(api_key="test_key")
            
            def make_call():
                return api.search_ingredient("apple")
            
            # Make concurrent calls
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_call) for _ in range(10)]
                results = [future.result() for future in futures]
            
            # All should succeed
            for result in results:
                self.assertEqual(result, [])
            
            # Should use cache effectively
            self.assertEqual(mock_request.call_count, 1)


class VersionCompatibilityTests(TestCase):
    """Test version compatibility and upgrade paths"""

    def test_python_version_compatibility(self):
        """Test Python version compatibility"""
        # Test that code works with current Python version
        self.assertGreaterEqual(sys.version_info, (3, 8))

    def test_django_version_compatibility(self):
        """Test Django version compatibility"""
        import django
        # Test that Django version is compatible
        self.assertGreaterEqual(django.VERSION, (4, 0))

    def test_httpx_version_compatibility(self):
        """Test httpx version compatibility"""
        # Test that httpx features are available
        self.assertTrue(hasattr(httpx, 'Client'))
        self.assertTrue(hasattr(httpx, 'RequestError'))

    def test_dependency_imports_regression(self):
        """Test all required dependencies can be imported"""
        try:
            import httpx
            import json
            import hashlib
            import time
            import logging
            from django.core.cache import cache
            from django.http import JsonResponse, HttpResponseForbidden
            from django.test import TestCase, RequestFactory
        except ImportError as e:
            self.fail(f"Required dependency import failed: {e}")


class DispatcherRegressionTests(TestCase):
    """Test dispatcher functionality regression"""

    def setUp(self):
        self.factory = RequestFactory()

    @patch('api_management.views.settings')
    def test_dispatcher_authentication_regression(self, mock_settings):
        """Test dispatcher authentication hasn't regressed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "test_secret_key"
        
        # Test valid authentication
        request = self.factory.get('/api/food/', HTTP_X_MY_APP_SECRET_KEY="test_secret_key")
        request.path = "/api/food/"
        
        with patch('api_management.views.get_food_nutrition') as mock_get_food:
            mock_get_food.return_value = {"success": True}
            response = api_data_view(request)
            self.assertIsInstance(response, JsonResponse)

    @patch('api_management.views.settings')
    def test_dispatcher_forbidden_response_regression(self, mock_settings):
        """Test dispatcher forbidden response format hasn't changed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "correct_secret"
        
        request = self.factory.get('/api/food/', HTTP_X_MY_APP_SECRET_KEY="wrong_secret")
        response = api_data_view(request)
        
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertIn("Access denied", response.content.decode())

    @patch('api_management.views.settings')
    def test_dispatcher_path_routing_regression(self, mock_settings):
        """Test dispatcher path routing hasn't changed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "test_secret"
        
        routing_tests = [
            ("/api/food/", "get_food_nutrition"),
            ("/api/foods/", "get_multiple_foods"),
            ("/api/recipe/nutrition/", "calculate_recipe_nutrition")
        ]
        
        for path, expected_function in routing_tests:
            with patch(f'api_management.views.{expected_function}') as mock_func:
                mock_func.return_value = {"success": True}
                
                request = self.factory.get(path, HTTP_X_MY_APP_SECRET_KEY="test_secret")
                request.path = path
                response = api_data_view(request)
                
                self.assertIsInstance(response, JsonResponse)
                mock_func.assert_called_once()

    @patch('api_management.views.settings')
    def test_dispatcher_unknown_path_regression(self, mock_settings):
        """Test dispatcher unknown path handling hasn't changed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "test_secret"
        
        request = self.factory.get('/api/unknown/', HTTP_X_MY_APP_SECRET_KEY="test_secret")
        request.path = "/api/unknown/"
        response = api_data_view(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 404)
        self.assertFalse(response_data['res']['success'])


class SecurityRegressionEnhancedTests(TestCase):
    """Enhanced security regression tests for new architecture"""

    def setUp(self):
        self.factory = RequestFactory()

    @patch('api_management.views.settings')
    def test_secret_key_validation_regression(self, mock_settings):
        """Test secret key validation security hasn't regressed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "secure_secret_123"
        
        # Test various invalid keys
        invalid_keys = [
            None,
            "",
            "wrong_key",
            "secure_secret_12",  # Partial match
            "secure_secret_1234",  # Extended
            "SECURE_SECRET_123",  # Case variation
        ]
        
        for invalid_key in invalid_keys:
            headers = {}
            if invalid_key is not None:
                headers['HTTP_X_MY_APP_SECRET_KEY'] = invalid_key
            
            request = self.factory.get('/api/food/', **headers)
            response = api_data_view(request)
            
            self.assertIsInstance(response, HttpResponseForbidden)

    @patch('api_management.views.settings')
    def test_header_injection_security_regression(self, mock_settings):
        """Test header injection security hasn't regressed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "test_secret"
        
        # Test various header injection attempts
        injection_attempts = [
            "test_secret\r\nX-Injected: malicious",
            "test_secret\nX-Injected: malicious",
            "test_secret; X-Injected: malicious",
        ]
        
        for malicious_key in injection_attempts:
            request = self.factory.get('/api/food/', HTTP_X_MY_APP_SECRET_KEY=malicious_key)
            response = api_data_view(request)
            
            # Should be forbidden due to key mismatch
            self.assertIsInstance(response, HttpResponseForbidden)

    @patch('api_management.views.settings')
    def test_path_traversal_security_regression(self, mock_settings):
        """Test path traversal security hasn't regressed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "test_secret"
        
        # Test various path traversal attempts
        malicious_paths = [
            "/api/../admin/",
            "/api/food/../../../etc/passwd",
            "/api/food/..%2F..%2Fadmin",
        ]
        
        for malicious_path in malicious_paths:
            request = self.factory.get(malicious_path, HTTP_X_MY_APP_SECRET_KEY="test_secret")
            request.path = malicious_path
            response = api_data_view(request)
            
            # Should return 404 for unknown paths
            if isinstance(response, JsonResponse):
                response_data = json.loads(response.content)
                self.assertEqual(response_data['status'], 404)


class ResponseFormatRegressionTests(TestCase):
    """Test response format consistency regression"""

    def setUp(self):
        self.factory = RequestFactory()

    def test_render_response_structure_regression(self):
        """Test render_response structure hasn't changed"""
        test_cases = [
            (200, {"success": True, "data": "test"}),
            (404, {"success": False, "error": "Not found"}),
            (500, {"success": False, "error": "Server error"}),
        ]
        
        for status, data in test_cases:
            response = render_response(status, data)
            
            self.assertIsInstance(response, JsonResponse)
            response_data = json.loads(response.content)
            
            # Check wrapper structure
            self.assertIn('status', response_data)
            self.assertIn('res', response_data)
            self.assertEqual(response_data['status'], status)
            self.assertEqual(response_data['res'], data)

    def test_json_serialization_regression(self):
        """Test JSON serialization hasn't regressed"""
        complex_data = {
            "foods": [
                {"fdcId": 123, "nutrients": {"protein": 20.5}},
                {"fdcId": 124, "nutrients": {"fat": 10.2}}
            ],
            "metadata": {"total": 2, "timestamp": "2023-01-01T00:00:00Z"},
            "success": True
        }
        
        response = render_response(200, complex_data)
        self.assertIsInstance(response, JsonResponse)
        
        # Verify it can be parsed back
        response_data = json.loads(response.content)
        self.assertEqual(response_data['res'], complex_data)

    @patch('api_management.views.settings')
    def test_dispatcher_response_consistency_regression(self, mock_settings):
        """Test dispatcher response consistency hasn't regressed"""
        mock_settings.INTERNAL_API_SECRET_KEY = "test_secret"
        
        # Test all endpoints return consistent format
        endpoints = ["/api/food/", "/api/foods/", "/api/recipe/nutrition/"]
        
        for endpoint in endpoints:
            with patch('api_management.views.get_food_nutrition') as mock_food, \
                 patch('api_management.views.get_multiple_foods') as mock_foods, \
                 patch('api_management.views.calculate_recipe_nutrition') as mock_recipe:
                
                mock_food.return_value = {"success": True}
                mock_foods.return_value = {"success": True}
                mock_recipe.return_value = {"success": True}
                
                request = self.factory.get(endpoint, HTTP_X_MY_APP_SECRET_KEY="test_secret")
                request.path = endpoint
                response = api_data_view(request)
                
                self.assertIsInstance(response, JsonResponse)
                response_data = json.loads(response.content)
                
                # Check consistent wrapper format
                self.assertIn('status', response_data)
                self.assertIn('res', response_data)
                self.assertEqual(response_data['status'], 200)


if __name__ == '__main__':
    unittest.main()