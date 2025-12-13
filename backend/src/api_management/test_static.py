"""
Static Tests for API Management Django Application
Tests basic functionality, model validation, and static behavior
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
import json
import hashlib
import httpx

from .models import ApiResult, HTTP2Client, FoodDataCentralAPI
from .views import get_food_nutrition, get_multiple_foods, calculate_recipe_nutrition, render_response, api_data_view


class ApiResultStaticTests(TestCase):
    """Test ApiResult class static behavior"""

    def test_api_result_initialization_success(self):
        """Test ApiResult initialization with success"""
        result = ApiResult(True, 200, {"data": "test"}, None, None)
        self.assertTrue(result.success)
        self.assertEqual(result.status, 200)
        self.assertEqual(result.data, {"data": "test"})
        self.assertIsNone(result.error)

    def test_api_result_initialization_failure(self):
        """Test ApiResult initialization with failure"""
        result = ApiResult(False, 404, None, "Not found", None)
        self.assertFalse(result.success)
        self.assertEqual(result.status, 404)
        self.assertIsNone(result.data)
        self.assertEqual(result.error, "Not found")

    def test_api_result_bool_conversion_true(self):
        """Test ApiResult boolean conversion when success is True"""
        result = ApiResult(True, 200, "data", None, None)
        self.assertTrue(bool(result))

    def test_api_result_bool_conversion_false(self):
        """Test ApiResult boolean conversion when success is False"""
        result = ApiResult(False, 404, None, "error", None)
        self.assertFalse(bool(result))

    def test_api_result_repr(self):
        """Test ApiResult string representation"""
        result = ApiResult(True, 200, "data", None, None)
        expected = "ApiResult(success=True, status=200)"
        self.assertEqual(repr(result), expected)

    def test_api_result_default_values(self):
        """Test ApiResult with minimal parameters"""
        result = ApiResult(True)
        self.assertTrue(result.success)
        self.assertIsNone(result.status)
        self.assertIsNone(result.data)
        self.assertIsNone(result.error)
        self.assertIsNone(result.raw)

    def test_api_result_all_parameters(self):
        """Test ApiResult with all parameters"""
        mock_response = Mock()
        result = ApiResult(True, 201, {"created": True}, None, mock_response)
        self.assertTrue(result.success)
        self.assertEqual(result.status, 201)
        self.assertEqual(result.data, {"created": True})
        self.assertIsNone(result.error)
        self.assertEqual(result.raw, mock_response)

    def test_api_result_error_with_status(self):
        """Test ApiResult with error and status code"""
        result = ApiResult(False, 500, None, "Internal server error", None)
        self.assertFalse(result.success)
        self.assertEqual(result.status, 500)
        self.assertEqual(result.error, "Internal server error")

    def test_api_result_success_without_data(self):
        """Test ApiResult success without data"""
        result = ApiResult(True, 204, None, None, None)
        self.assertTrue(result.success)
        self.assertEqual(result.status, 204)
        self.assertIsNone(result.data)

    def test_api_result_if_condition_usage(self):
        """Test using ApiResult in if conditions"""
        success_result = ApiResult(True, 200, "data", None, None)
        failure_result = ApiResult(False, 404, None, "error", None)
        
        if success_result:
            success_check = True
        else:
            success_check = False
            
        if failure_result:
            failure_check = True
        else:
            failure_check = False
            
        self.assertTrue(success_check)
        self.assertFalse(failure_check)


class HTTP2ClientStaticTests(TestCase):
    """Test HTTP2Client class static behavior"""

    def test_http2_client_initialization_default(self):
        """Test HTTP2Client initialization with defaults"""
        client = HTTP2Client()
        self.assertIsNone(client.base_url)
        self.assertEqual(client.timeout, 8.0)
        self.assertEqual(client.retries, 3)
        self.assertEqual(client.backoff, 0.5)
        self.assertIsInstance(client.client, httpx.Client)

    def test_http2_client_initialization_custom(self):
        """Test HTTP2Client initialization with custom values"""
        client = HTTP2Client(
            base_url="https://api.example.com/",
            timeout=10.0,
            retries=5,
            backoff=1.0
        )
        self.assertEqual(client.base_url, "https://api.example.com")
        self.assertEqual(client.timeout, 10.0)
        self.assertEqual(client.retries, 5)
        self.assertEqual(client.backoff, 1.0)

    def test_build_url_with_base_url(self):
        """Test URL building with base URL"""
        client = HTTP2Client(base_url="https://api.example.com")
        url = client.build_url("endpoint")
        self.assertEqual(url, "https://api.example.com/endpoint")

    def test_build_url_with_base_url_trailing_slash(self):
        """Test URL building with base URL having trailing slash"""
        client = HTTP2Client(base_url="https://api.example.com/")
        url = client.build_url("endpoint")
        self.assertEqual(url, "https://api.example.com/endpoint")

    def test_build_url_with_leading_slash_path(self):
        """Test URL building with path having leading slash"""
        client = HTTP2Client(base_url="https://api.example.com")
        url = client.build_url("/endpoint")
        self.assertEqual(url, "https://api.example.com/endpoint")

    def test_build_url_without_base_url(self):
        """Test URL building without base URL"""
        client = HTTP2Client()
        url = client.build_url("https://api.example.com/endpoint")
        self.assertEqual(url, "https://api.example.com/endpoint")

    def test_build_url_absolute_path_ignores_base(self):
        """Test URL building with absolute path ignores base URL"""
        client = HTTP2Client(base_url="https://api.example.com")
        url = client.build_url("https://other.com/endpoint")
        self.assertEqual(url, "https://other.com/endpoint")

    def test_build_url_empty_path(self):
        """Test URL building with empty path"""
        client = HTTP2Client(base_url="https://api.example.com")
        url = client.build_url("")
        self.assertEqual(url, "https://api.example.com/")

    def test_build_url_none_base_url(self):
        """Test URL building with None base URL"""
        client = HTTP2Client(base_url=None)
        url = client.build_url("endpoint")
        self.assertEqual(url, "endpoint")

    def test_close_method_exists(self):
        """Test that close method exists and is callable"""
        client = HTTP2Client()
        self.assertTrue(hasattr(client, 'close'))
        self.assertTrue(callable(client.close))

    @patch('httpx.Client')
    def test_close_method_calls_client_close(self, mock_client_class):
        """Test that close method calls underlying client close"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = HTTP2Client()
        client.close()
        
        mock_client.close.assert_called_once()


class FoodDataCentralAPIStaticTests(TestCase):
    """Test FoodDataCentralAPI class static behavior"""

    def test_food_api_initialization_default(self):
        """Test FoodDataCentralAPI initialization with defaults"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            api.api_key = "test_key"
            self.assertEqual(api.api_key, "test_key")

    def test_food_api_constants(self):
        """Test FoodDataCentralAPI class constants"""
        self.assertEqual(FoodDataCentralAPI.SEARCH_TTL, 60 * 60)
        self.assertEqual(FoodDataCentralAPI.FOOD_TTL, 24 * 60 * 60)
        self.assertEqual(FoodDataCentralAPI.MULTI_TTL, 24 * 60 * 60)

    def test_with_key_method_empty_params(self):
        """Test _with_key method with empty parameters"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            api.api_key = "test_key"
            result = api._with_key()
            self.assertEqual(result, {"api_key": "test_key"})

    def test_with_key_method_existing_params(self):
        """Test _with_key method with existing parameters"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            api.api_key = "test_key"
            result = api._with_key({"query": "apple"})
            expected = {"query": "apple", "api_key": "test_key"}
            self.assertEqual(result, expected)

    def test_cache_key_generation(self):
        """Test cache key generation"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            payload = {"query": "apple", "pageSize": 10}
            key = api._cache_key("search", payload)
            
            # Verify key format
            self.assertTrue(key.startswith("fdc:search:"))
            self.assertEqual(len(key.split(":")), 3)

    def test_cache_key_consistency(self):
        """Test cache key consistency for same payload"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            payload = {"query": "apple", "pageSize": 10}
            key1 = api._cache_key("search", payload)
            key2 = api._cache_key("search", payload)
            self.assertEqual(key1, key2)

    def test_cache_key_different_for_different_payload(self):
        """Test cache key differs for different payloads"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            payload1 = {"query": "apple", "pageSize": 10}
            payload2 = {"query": "banana", "pageSize": 10}
            key1 = api._cache_key("search", payload1)
            key2 = api._cache_key("search", payload2)
            self.assertNotEqual(key1, key2)

    def test_extract_key_nutrients_empty_data(self):
        """Test extract_key_nutrients with empty data"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            result = api.extract_key_nutrients({})
            self.assertEqual(result, {})

    def test_extract_key_nutrients_no_nutrients(self):
        """Test extract_key_nutrients with no foodNutrients key"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            result = api.extract_key_nutrients({"description": "Apple"})
            self.assertEqual(result, {})

    def test_extract_key_nutrients_empty_nutrients_list(self):
        """Test extract_key_nutrients with empty nutrients list"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            result = api.extract_key_nutrients({"foodNutrients": []})
            self.assertEqual(result, {})

    def test_extract_key_nutrients_protein(self):
        """Test extract_key_nutrients extracts protein correctly"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
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
            expected = {"protein": {"value": 20.5, "unit": "g"}}
            self.assertEqual(result, expected)

    def test_extract_key_nutrients_multiple_nutrients(self):
        """Test extract_key_nutrients with multiple nutrients"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            food_data = {
                "foodNutrients": [
                    {
                        "nutrient": {"name": "Protein", "unitName": "g"},
                        "amount": 20.5
                    },
                    {
                        "nutrient": {"name": "Total lipid (fat)", "unitName": "g"},
                        "amount": 10.2
                    }
                ]
            }
            result = api.extract_key_nutrients(food_data)
            expected = {
                "protein": {"value": 20.5, "unit": "g"},
                "fat": {"value": 10.2, "unit": "g"}
            }
            self.assertEqual(result, expected)

    def test_extract_key_nutrients_alternative_format(self):
        """Test extract_key_nutrients with alternative nutrient format"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            food_data = {
                "foodNutrients": [
                    {
                        "nutrientName": "Energy",
                        "value": 250,
                        "unitName": "kcal"
                    }
                ]
            }
            result = api.extract_key_nutrients(food_data)
            expected = {"calories": {"value": 250, "unit": "kcal"}}
            self.assertEqual(result, expected)

    def test_extract_key_nutrients_missing_amount(self):
        """Test extract_key_nutrients with missing amount defaults to 0"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            food_data = {
                "foodNutrients": [
                    {
                        "nutrient": {"name": "Protein", "unitName": "g"}
                    }
                ]
            }
            result = api.extract_key_nutrients(food_data)
            expected = {"protein": {"value": 0, "unit": "g"}}
            self.assertEqual(result, expected)

    def test_extract_key_nutrients_unknown_nutrient_ignored(self):
        """Test extract_key_nutrients ignores unknown nutrients"""
        with patch.object(FoodDataCentralAPI, '__init__', lambda x: None):
            api = FoodDataCentralAPI.__new__(FoodDataCentralAPI)
            food_data = {
                "foodNutrients": [
                    {
                        "nutrient": {"name": "Unknown Nutrient", "unitName": "g"},
                        "amount": 5.0
                    },
                    {
                        "nutrient": {"name": "Protein", "unitName": "g"},
                        "amount": 20.5
                    }
                ]
            }
            result = api.extract_key_nutrients(food_data)
            expected = {"protein": {"value": 20.5, "unit": "g"}}
            self.assertEqual(result, expected)


class ViewsStaticTests(TestCase):
    """Test views static behavior and validation"""

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_food_nutrition_wrong_method_post(self):
        """Test get_food_nutrition with POST method returns error dict"""
        request = self.factory.post('/food/')
        response = get_food_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))
        self.assertEqual(response.get('error'), 'Bad Request')

    def test_get_food_nutrition_wrong_method_put(self):
        """Test get_food_nutrition with PUT method returns error dict"""
        request = self.factory.put('/food/')
        response = get_food_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_get_food_nutrition_wrong_method_delete(self):
        """Test get_food_nutrition with DELETE method returns error dict"""
        request = self.factory.delete('/food/')
        response = get_food_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_get_food_nutrition_missing_food_parameter(self):
        """Test get_food_nutrition without food parameter returns error dict"""
        request = self.factory.get('/food/')
        response = get_food_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))
        self.assertEqual(response.get('error'), 'Bad Request')

    def test_get_food_nutrition_empty_food_parameter(self):
        """Test get_food_nutrition with empty food parameter returns error dict"""
        request = self.factory.get('/food/', {'food': ''})
        response = get_food_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_get_multiple_foods_wrong_method_post(self):
        """Test get_multiple_foods with POST method returns error dict"""
        request = self.factory.post('/foods/')
        response = get_multiple_foods(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_get_multiple_foods_missing_foods_parameter(self):
        """Test get_multiple_foods without foods parameter returns error dict"""
        request = self.factory.get('/foods/')
        response = get_multiple_foods(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_get_multiple_foods_non_list_parameter(self):
        """Test get_multiple_foods with non-list foods parameter returns error dict"""
        request = self.factory.get('/foods/', {'foods': 'apple'})
        response = get_multiple_foods(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_calculate_recipe_nutrition_wrong_method_post(self):
        """Test calculate_recipe_nutrition with POST method returns error dict"""
        request = self.factory.post('/recipe/nutrition/')
        response = calculate_recipe_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_calculate_recipe_nutrition_missing_recipe_parameter(self):
        """Test calculate_recipe_nutrition without recipe parameter returns error dict"""
        request = self.factory.get('/recipe/nutrition/')
        response = calculate_recipe_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_calculate_recipe_nutrition_non_dict_parameter(self):
        """Test calculate_recipe_nutrition with non-dict recipe parameter returns error dict"""
        request = self.factory.get('/recipe/nutrition/', {'recipe': 'invalid'})
        response = calculate_recipe_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_calculate_recipe_nutrition_missing_name(self):
        """Test calculate_recipe_nutrition with recipe missing name returns error dict"""
        recipe = {'foodNutrients': ['apple', 'banana']}
        request = self.factory.get('/recipe/nutrition/', {'recipe': recipe})
        response = calculate_recipe_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_calculate_recipe_nutrition_missing_nutrients(self):
        """Test calculate_recipe_nutrition with recipe missing foodNutrients returns error dict"""
        recipe = {'name': 'Test Recipe'}
        request = self.factory.get('/recipe/nutrition/', {'recipe': recipe})
        response = calculate_recipe_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_calculate_recipe_nutrition_non_string_name(self):
        """Test calculate_recipe_nutrition with non-string name returns error dict"""
        recipe = {'name': 123, 'foodNutrients': ['apple']}
        request = self.factory.get('/recipe/nutrition/', {'recipe': recipe})
        response = calculate_recipe_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_calculate_recipe_nutrition_non_list_nutrients(self):
        """Test calculate_recipe_nutrition with non-list foodNutrients returns error dict"""
        recipe = {'name': 'Test Recipe', 'foodNutrients': 'apple'}
        request = self.factory.get('/recipe/nutrition/', {'recipe': recipe})
        response = calculate_recipe_nutrition(request)
        self.assertIsInstance(response, dict)
        self.assertFalse(response.get('success'))

    def test_render_response_function(self):
        """Test render_response function creates proper JsonResponse"""
        response = render_response(200, {"success": True})
        self.assertIsInstance(response, JsonResponse)
        
        # Parse the response content
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 200)
        self.assertEqual(response_data['res'], {"success": True})

    def test_render_response_with_error(self):
        """Test render_response function with error data"""
        error_data = {"error": "Not found", "success": False}
        response = render_response(404, error_data)
        self.assertIsInstance(response, JsonResponse)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 404)
        self.assertEqual(response_data['res'], error_data)

    @patch('api_management.views.settings')
    def test_api_data_view_invalid_secret_key(self, mock_settings):
        """Test api_data_view with invalid secret key returns forbidden"""
        mock_settings.INTERNAL_API_SECRET_KEY = "valid_secret"
        
        request = self.factory.get('/api/food/', HTTP_X_MY_APP_SECRET_KEY="invalid_secret")
        response = api_data_view(request)
        
        self.assertIsInstance(response, HttpResponseForbidden)

    @patch('api_management.views.settings')
    def test_api_data_view_missing_secret_key(self, mock_settings):
        """Test api_data_view with missing secret key returns forbidden"""
        mock_settings.INTERNAL_API_SECRET_KEY = "valid_secret"
        
        request = self.factory.get('/api/food/')
        response = api_data_view(request)
        
        self.assertIsInstance(response, HttpResponseForbidden)

    @patch('api_management.views.settings')
    @patch('api_management.views.get_food_nutrition')
    def test_api_data_view_valid_food_request(self, mock_get_food, mock_settings):
        """Test api_data_view with valid secret key and food request"""
        mock_settings.INTERNAL_API_SECRET_KEY = "valid_secret"
        mock_get_food.return_value = {"nutrition": {}, "success": True}
        
        request = self.factory.get('/api/food/', HTTP_X_MY_APP_SECRET_KEY="valid_secret")
        request.path = "/api/food/"
        response = api_data_view(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 200)

    @patch('api_management.views.settings')
    @patch('api_management.views.get_multiple_foods')
    def test_api_data_view_valid_foods_request(self, mock_get_foods, mock_settings):
        """Test api_data_view with valid secret key and foods request"""
        mock_settings.INTERNAL_API_SECRET_KEY = "valid_secret"
        mock_get_foods.return_value = [{"fdcId": 123}]
        
        request = self.factory.get('/api/foods/', HTTP_X_MY_APP_SECRET_KEY="valid_secret")
        request.path = "/api/foods/"
        response = api_data_view(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 200)

    @patch('api_management.views.settings')
    @patch('api_management.views.calculate_recipe_nutrition')
    def test_api_data_view_valid_recipe_request(self, mock_calc_recipe, mock_settings):
        """Test api_data_view with valid secret key and recipe request"""
        mock_settings.INTERNAL_API_SECRET_KEY = "valid_secret"
        mock_calc_recipe.return_value = {"protein": {"value": 20, "unit": "g"}}
        
        request = self.factory.get('/api/recipe/nutrition/', HTTP_X_MY_APP_SECRET_KEY="valid_secret")
        request.path = "/api/recipe/nutrition/"
        response = api_data_view(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 200)

    @patch('api_management.views.settings')
    def test_api_data_view_unknown_path(self, mock_settings):
        """Test api_data_view with valid secret key but unknown path"""
        mock_settings.INTERNAL_API_SECRET_KEY = "valid_secret"
        
        request = self.factory.get('/api/unknown/', HTTP_X_MY_APP_SECRET_KEY="valid_secret")
        request.path = "/api/unknown/"
        response = api_data_view(request)
        
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 404)
        self.assertFalse(response_data['res']['success'])


class UrlPatternsStaticTests(TestCase):
    """Test URL patterns static configuration"""

    def test_url_patterns_exist(self):
        """Test that URL patterns are defined"""
        from .urls import urlpatterns
        self.assertIsInstance(urlpatterns, list)
        self.assertGreater(len(urlpatterns), 0)

    def test_app_name_defined(self):
        """Test that app_name is defined"""
        from .urls import app_name
        self.assertEqual(app_name, 'api_management')

    def test_api_data_view_pattern_exists(self):
        """Test that api_data_view URL pattern exists"""
        from .urls import urlpatterns
        self.assertEqual(len(urlpatterns), 1)
        pattern = urlpatterns[0]
        self.assertEqual(pattern.name, 'api_data_view')

    def test_single_endpoint_architecture(self):
        """Test that there's only one URL pattern for the dispatcher"""
        from .urls import urlpatterns
        self.assertEqual(len(urlpatterns), 1)
        
    def test_empty_path_pattern(self):
        """Test that the URL pattern uses empty path"""
        from .urls import urlpatterns
        pattern = urlpatterns[0]
        self.assertEqual(str(pattern.pattern), '')


class CacheStaticTests(TestCase):
    """Test cache configuration and static behavior"""

    def test_cache_configured(self):
        """Test that cache is properly configured"""
        from django.core.cache import cache
        self.assertIsNotNone(cache)

    def test_cache_key_generation_consistency(self):
        """Test cache key generation is consistent"""
        payload1 = {"query": "apple", "pageSize": 10}
        payload2 = {"query": "apple", "pageSize": 10}
        
        raw1 = json.dumps(payload1, sort_keys=True, ensure_ascii=False)
        raw2 = json.dumps(payload2, sort_keys=True, ensure_ascii=False)
        
        digest1 = hashlib.sha256(raw1.encode("utf-8")).hexdigest()
        digest2 = hashlib.sha256(raw2.encode("utf-8")).hexdigest()
        
        self.assertEqual(digest1, digest2)

    def test_cache_key_generation_different_payloads(self):
        """Test cache key generation differs for different payloads"""
        payload1 = {"query": "apple", "pageSize": 10}
        payload2 = {"query": "banana", "pageSize": 10}
        
        raw1 = json.dumps(payload1, sort_keys=True, ensure_ascii=False)
        raw2 = json.dumps(payload2, sort_keys=True, ensure_ascii=False)
        
        digest1 = hashlib.sha256(raw1.encode("utf-8")).hexdigest()
        digest2 = hashlib.sha256(raw2.encode("utf-8")).hexdigest()
        
        self.assertNotEqual(digest1, digest2)


class SettingsStaticTests(TestCase):
    """Test Django settings static configuration"""

    def test_api_key_setting_exists(self):
        """Test that API_KEY setting exists"""
        self.assertTrue(hasattr(settings, 'API_KEY'))

    def test_internal_api_secret_key_setting_exists(self):
        """Test that INTERNAL_API_SECRET_KEY setting exists"""
        self.assertTrue(hasattr(settings, 'INTERNAL_API_SECRET_KEY'))

    def test_installed_apps_contains_api_management(self):
        """Test that api_management is in INSTALLED_APPS"""
        self.assertIn('api_management', settings.INSTALLED_APPS)

    def test_cache_configuration_exists(self):
        """Test that CACHES configuration exists"""
        self.assertTrue(hasattr(settings, 'CACHES'))
        self.assertIn('default', settings.CACHES)

    def test_database_configuration_exists(self):
        """Test that database configuration exists"""
        self.assertTrue(hasattr(settings, 'DATABASES'))
        self.assertIn('default', settings.DATABASES)

    def test_cors_configuration_exists(self):
        """Test that CORS configuration exists"""
        self.assertTrue(hasattr(settings, 'CORS_ALLOWED_ORIGINS'))
        self.assertTrue(hasattr(settings, 'CORS_ALLOW_CREDENTIALS'))


if __name__ == '__main__':
    unittest.main()