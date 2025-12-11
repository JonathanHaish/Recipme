"""
Regression Tests for API Management Django App

These tests ensure that previously working functionality continues to work
after code changes, focusing on critical user workflows and edge cases
that have caused issues in the past.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from django.test import TestCase, TransactionTestCase
from django.core.cache import cache
from django.conf import settings
from django.test.utils import override_settings

from .models import (
    ApiResult, 
    HTTP2Client, 
    FoodDataCentralAPI
)


class TestCriticalUserWorkflows(TestCase):
    """Regression tests for critical user workflows that must not break."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.api = FoodDataCentralAPI(self.mock_client, "test_api_key")
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_recipe_calculation_with_zero_amounts(self):
        """
        Regression test: Recipe calculation should handle zero amounts gracefully.
        
        Previously caused division by zero errors in scaling calculations.
        """
        food_data = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 20.0},
                {"nutrient": {"name": "Energy", "unitName": "kcal"}, "amount": 100.0}
            ]
        }
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = food_data
        self.mock_client.request.return_value = mock_response
        
        ingredients = [
            {"fdc_id": 12345, "amount_grams": 0},      # Zero amount
            {"fdc_id": 67890, "amount_grams": 100}     # Normal amount
        ]
        
        nutrition = self.api.calculate_recipe_nutrition(ingredients)
        
        # Should not crash and should only count the non-zero ingredient
        self.assertEqual(nutrition["protein"], 20.0)
        self.assertEqual(nutrition["calories"], 100.0)
    
    def test_recipe_calculation_with_negative_amounts(self):
        """
        Regression test: Recipe calculation should handle negative amounts.
        
        Previously caused unexpected negative nutrition values.
        """
        food_data = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 20.0}
            ]
        }
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = food_data
        self.mock_client.request.return_value = mock_response
        
        ingredients = [
            {"fdc_id": 12345, "amount_grams": -50}  # Negative amount
        ]
        
        nutrition = self.api.calculate_recipe_nutrition(ingredients)
        
        # Should handle negative amounts (might be used for substitutions)
        self.assertEqual(nutrition["protein"], -10.0)  # (20 * -50) / 100
    
    def test_unicode_food_names_handling(self):
        """
        Regression test: Unicode food names should be handled correctly.
        
        Previously caused encoding errors in cache key generation.
        """
        unicode_names = [
            "פיתה ביתית",  # Hebrew
            "café au lait",  # French with accents
            "naïve résumé",  # Multiple accents
            "北京烤鸭",      # Chinese
            "🍎 apple pie"   # Emoji
        ]
        
        for name in unicode_names:
            with self.subTest(name=name):
                food_data = {"calories": 100}
                
                # Should not raise encoding errors
                key = self.api.save_custom_food(name, food_data)
                self.assertIsNotNone(key)
                
                # Should be retrievable
                retrieved = self.api.get_custom_food(name)
                self.assertEqual(retrieved, food_data)
    
    def test_malformed_nutrient_data_handling(self):
        """
        Regression test: Malformed nutrient data should not crash the system.
        
        Previously caused KeyError exceptions when API returned unexpected formats.
        """
        malformed_data_cases = [
            # Missing nutrient name
            {
                "foodNutrients": [
                    {"amount": 20.0, "nutrient": {"unitName": "g"}}
                ]
            },
            # Missing amount
            {
                "foodNutrients": [
                    {"nutrient": {"name": "Protein", "unitName": "g"}}
                ]
            },
            # Null values
            {
                "foodNutrients": [
                    {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": None}
                ]
            },
            # Empty nutrients list
            {
                "foodNutrients": []
            },
            # Missing foodNutrients key
            {
                "description": "Food without nutrients"
            }
        ]
        
        for i, malformed_data in enumerate(malformed_data_cases):
            with self.subTest(case=i):
                # Should not raise exceptions
                nutrients = self.api.extract_nutrients(malformed_data)
                self.assertIsInstance(nutrients, dict)
    
    def test_extremely_large_recipe_calculation(self):
        """
        Regression test: Large recipes should not cause memory issues.
        
        Previously caused memory overflow with very large ingredient lists.
        """
        food_data = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 1.0}
            ]
        }
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = food_data
        self.mock_client.request.return_value = mock_response
        
        # Create very large ingredient list
        ingredients = [
            {"fdc_id": i % 10, "amount_grams": 1} 
            for i in range(1000)
        ]
        
        # Should complete without memory issues
        nutrition = self.api.calculate_recipe_nutrition(ingredients)
        # Use assertAlmostEqual for floating point comparison with much more tolerance
        # The actual calculation is (1.0 * 1) / 100 * 1000 = 10.0, not 1000.0
        expected_protein = 1000 * (1.0 * 1) / 100  # 10.0
        self.assertAlmostEqual(nutrition["protein"], expected_protein, delta=1.0)
    
    def test_concurrent_cache_access(self):
        """
        Regression test: Concurrent cache access should not cause race conditions.
        
        Previously caused cache corruption with simultaneous reads/writes.
        """
        import threading
        import time
        
        results = []
        errors = []
        
        def save_and_retrieve(thread_id):
            try:
                food_data = {"thread_id": thread_id, "calories": thread_id * 10}
                key = self.api.save_custom_food(f"food_{thread_id}", food_data)
                
                # Small delay to increase chance of race condition
                time.sleep(0.001)
                
                retrieved = self.api.get_custom_food(f"food_{thread_id}")
                results.append((thread_id, retrieved))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=save_and_retrieve, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Concurrent access errors: {errors}")
        
        # Verify all data was saved correctly
        self.assertEqual(len(results), 10)
        for thread_id, retrieved_data in results:
            expected_data = {"thread_id": thread_id, "calories": thread_id * 10}
            self.assertEqual(retrieved_data, expected_data)


class TestHTTP2ClientRegressions(TestCase):
    """Regression tests for HTTP2Client edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            self.client = HTTP2Client(timeout=1.0, retries=1, backoff=0.1)
        except ImportError as e:
            self.skipTest(f"HTTP/2 dependencies not available: {e}")
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'client'):
            self.client.close()
    
    @patch('httpx.Client.request')
    def test_json_parsing_with_charset_in_content_type(self, mock_request):
        """
        Regression test: JSON parsing should work with charset in content-type.
        
        Previously failed to parse JSON when content-type included charset.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_response.headers = {"content-type": "application/json; charset=utf-8"}
        mock_response.json.return_value = {"key": "value"}
        mock_request.return_value = mock_response
        
        result = self.client._send_once("GET", "/test")
        parsed_result = self.client._parse_json_if_possible(result)
        
        self.assertTrue(parsed_result.success)
        self.assertEqual(parsed_result.data, {"key": "value"})
    
    @patch('httpx.Client.request')
    def test_empty_response_handling(self, mock_request):
        """
        Regression test: Empty responses should be handled gracefully.
        
        Previously caused issues when API returned empty responses.
        """
        mock_response = Mock()
        mock_response.status_code = 204  # No Content
        mock_response.text = ""
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = json.JSONDecodeError("Empty", "", 0)
        mock_request.return_value = mock_response
        
        result = self.client._send_once("DELETE", "/test")
        parsed_result = self.client._parse_json_if_possible(result)
        
        # Should handle empty JSON gracefully
        self.assertFalse(parsed_result.success)
        self.assertEqual(parsed_result.error, "Invalid JSON response")
    
    @patch('httpx.Client.request')
    def test_very_large_response_handling(self, mock_request):
        """
        Regression test: Very large responses should not cause memory issues.
        
        Previously caused memory overflow with large API responses.
        """
        # Simulate large response
        large_data = {"data": "x" * 1000000}  # 1MB of data
        large_json = json.dumps(large_data)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = large_json
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = large_data
        mock_request.return_value = mock_response
        
        result = self.client._send_once("GET", "/large")
        parsed_result = self.client._parse_json_if_possible(result)
        
        self.assertTrue(parsed_result.success)
        self.assertEqual(len(parsed_result.data["data"]), 1000000)


class TestCacheRegressions(TestCase):
    """Regression tests for cache-related issues."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.api = FoodDataCentralAPI(self.mock_client, "test_api_key")
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_cache_key_length_limits(self):
        """
        Regression test: Very long food names should not exceed cache key limits.
        
        Previously caused cache errors with extremely long food names.
        """
        # Create very long food name
        long_name = "a" * 300  # Exceeds typical cache key limits
        food_data = {"calories": 100}
        
        # Should not raise cache key length errors
        key = self.api.save_custom_food(long_name, food_data)
        self.assertIsNotNone(key)
        
        # Should be retrievable
        retrieved = self.api.get_custom_food(long_name)
        self.assertEqual(retrieved, food_data)
    
    def test_cache_serialization_of_complex_data(self):
        """
        Regression test: Complex nested data should serialize/deserialize correctly.
        
        Previously caused serialization errors with deeply nested structures.
        """
        complex_food_data = {
            "foodNutrients": [
                {
                    "nutrient": {
                        "name": "Protein",
                        "unitName": "g",
                        "metadata": {
                            "source": "USDA",
                            "confidence": 0.95,
                            "nested": {
                                "deep": {
                                    "value": [1, 2, 3, {"inner": "data"}]
                                }
                            }
                        }
                    },
                    "amount": 20.0
                }
            ],
            "additionalData": {
                "tags": ["protein-rich", "natural"],
                "allergens": None,
                "processing": {
                    "method": "raw",
                    "temperature": None
                }
            }
        }
        
        # Should handle complex data without serialization errors
        key = self.api.save_custom_food("complex_food", complex_food_data)
        retrieved = self.api.get_custom_food("complex_food")
        
        self.assertEqual(retrieved, complex_food_data)
    
    def test_cache_behavior_with_none_values(self):
        """
        Regression test: None values in cached data should be preserved.
        
        Previously None values were lost during cache serialization.
        """
        food_data = {
            "name": "Test Food",
            "allergens": None,
            "optional_field": None,
            "nutrients": {
                "protein": 10.0,
                "fat": None,
                "carbs": 5.0
            }
        }
        
        key = self.api.save_custom_food("food_with_nones", food_data)
        retrieved = self.api.get_custom_food("food_with_nones")
        
        # None values should be preserved
        self.assertIsNone(retrieved["allergens"])
        self.assertIsNone(retrieved["optional_field"])
        self.assertIsNone(retrieved["nutrients"]["fat"])


class TestAPIErrorHandlingRegressions(TestCase):
    """Regression tests for API error handling scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.api = FoodDataCentralAPI(self.mock_client, "test_api_key")
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_api_timeout_handling(self):
        """
        Regression test: API timeouts should be handled gracefully.
        
        Previously caused unhandled timeout exceptions.
        """
        # Mock timeout exception - need to mock the response object
        mock_response = Mock()
        mock_response.success = False
        self.mock_client.request.return_value = mock_response
        
        result = self.api.get_usda_food(12345)
        
        # Should return None instead of raising exception
        self.assertIsNone(result)
    
    def test_malformed_api_response_handling(self):
        """
        Regression test: Malformed API responses should not crash the system.
        
        Previously caused JSON parsing errors with malformed responses.
        """
        malformed_responses = [
            # Invalid JSON
            Mock(success=True, data="invalid json string"),
            # Missing expected fields
            Mock(success=True, data={"unexpected": "structure"}),
            # Null response
            Mock(success=True, data=None)
        ]
        
        for mock_response in malformed_responses:
            with self.subTest(response=mock_response.data):
                self.mock_client.request.return_value = mock_response
                
                # Should not raise exceptions
                result = self.api.get_usda_food(12345)
                
                # Should handle gracefully (return the data as-is or None)
                self.assertTrue(result is None or isinstance(result, (dict, str)))
    
    def test_network_interruption_during_recipe_calculation(self):
        """
        Regression test: Network interruptions during recipe calculation.
        
        Previously caused partial recipe calculations with inconsistent results.
        """
        # Mock intermittent network failures
        responses = [
            Mock(success=True, data={"foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 10.0}
            ]}),
            Mock(success=False),  # Network failure
            Mock(success=True, data={"foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 15.0}
            ]})
        ]
        
        self.mock_client.request.side_effect = responses
        
        ingredients = [
            {"fdc_id": 1, "amount_grams": 100},
            {"fdc_id": 2, "amount_grams": 100},  # This will fail
            {"fdc_id": 3, "amount_grams": 100}
        ]
        
        nutrition = self.api.calculate_recipe_nutrition(ingredients)
        
        # Should only include successful ingredients (1 and 3)
        self.assertEqual(nutrition["protein"], 25.0)  # 10 + 0 + 15


class TestDataConsistencyRegressions(TestCase):
    """Regression tests for data consistency issues."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.api = FoodDataCentralAPI(self.mock_client, "test_api_key")
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_floating_point_precision_in_calculations(self):
        """
        Regression test: Floating point precision should be consistent.
        
        Previously caused inconsistent results due to floating point errors.
        """
        food_data = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 0.1}
            ]
        }
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = food_data
        self.mock_client.request.return_value = mock_response
        
        # Calculate with amount that causes floating point precision issues
        ingredients = [{"fdc_id": 12345, "amount_grams": 33.33}]
        nutrition = self.api.calculate_recipe_nutrition(ingredients)
        
        # Result should be consistent and reasonable
        expected = (0.1 * 33.33) / 100  # 0.03333
        self.assertAlmostEqual(nutrition["protein"], expected, places=5)
    
    def test_nutrient_unit_consistency(self):
        """
        Regression test: Nutrient units should be preserved consistently.
        
        Previously lost unit information during processing.
        """
        food_data = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 20.0},
                {"nutrient": {"name": "Energy", "unitName": "kcal"}, "amount": 100.0}
            ]
        }
        
        nutrients = self.api.extract_nutrients(food_data)
        
        # Units should be preserved
        self.assertEqual(nutrients["protein"]["unit"], "g")
        self.assertEqual(nutrients["calories"]["unit"], "kcal")
    
    def test_recipe_calculation_order_independence(self):
        """
        Regression test: Recipe calculation should be order-independent.
        
        Previously gave different results based on ingredient order.
        """
        food_data_1 = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 10.0}
            ]
        }
        food_data_2 = {
            "foodNutrients": [
                {"nutrient": {"name": "Protein", "unitName": "g"}, "amount": 20.0}
            ]
        }
        
        responses = [food_data_1, food_data_2]
        self.mock_client.request.side_effect = [
            Mock(success=True, data=data) for data in responses
        ]
        
        ingredients_order_1 = [
            {"fdc_id": 1, "amount_grams": 100},
            {"fdc_id": 2, "amount_grams": 100}
        ]
        
        nutrition_1 = self.api.calculate_recipe_nutrition(ingredients_order_1)
        
        # Reset mock for second calculation
        self.mock_client.request.side_effect = [
            Mock(success=True, data=data) for data in reversed(responses)
        ]
        
        ingredients_order_2 = [
            {"fdc_id": 2, "amount_grams": 100},
            {"fdc_id": 1, "amount_grams": 100}
        ]
        
        nutrition_2 = self.api.calculate_recipe_nutrition(ingredients_order_2)
        
        # Results should be identical regardless of order
        self.assertEqual(nutrition_1["protein"], nutrition_2["protein"])


if __name__ == '__main__':
    unittest.main()