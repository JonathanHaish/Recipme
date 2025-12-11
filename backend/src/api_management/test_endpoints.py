#!/usr/bin/env python
"""
Test script for API Management endpoints.

This script tests all the API endpoints to ensure they work correctly.
Run this after starting the Django development server.
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_FDC_ID = 123456  # Replace with a valid FDC ID for testing

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health/")
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print("✅ Health check passed")
            print(f"   Status: {data['data']['status']}")
            print(f"   Checks: {data['data']['checks']}")
            return True
        else:
            print(f"❌ Health check failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_get_food_nutrition():
    """Test the get food nutrition endpoint."""
    print(f"🔍 Testing get food nutrition endpoint (FDC ID: {TEST_FDC_ID})...")
    
    try:
        response = requests.get(f"{BASE_URL}/food/{TEST_FDC_ID}/")
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print("✅ Get food nutrition passed")
            print(f"   Food: {data['data']['description']}")
            nutrients = data['data']['nutrients']
            if 'calories' in nutrients:
                print(f"   Calories: {nutrients['calories']['value']} {nutrients['calories']['unit']}")
            return True
        elif response.status_code == 404:
            print(f"⚠️  Food not found (FDC ID: {TEST_FDC_ID})")
            print("   This is expected if the FDC ID doesn't exist")
            return True  # Not a failure, just no data
        else:
            print(f"❌ Get food nutrition failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Get food nutrition error: {e}")
        return False

def test_save_custom_food():
    """Test the save custom food endpoint."""
    print("🔍 Testing save custom food endpoint...")
    
    custom_food = {
        "name": "Test Granola Bar",
        "nutrients": [
            {
                "nutrient": {"name": "Protein", "unitName": "g"},
                "amount": 8.5
            },
            {
                "nutrient": {"name": "Energy", "unitName": "kcal"},
                "amount": 180.0
            },
            {
                "nutrient": {"name": "Total lipid (fat)", "unitName": "g"},
                "amount": 7.2
            },
            {
                "nutrient": {"name": "Carbohydrate, by difference", "unitName": "g"},
                "amount": 22.1
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/custom-food/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(custom_food)
        )
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print("✅ Save custom food passed")
            print(f"   Key: {data['data']['key']}")
            print(f"   Name: {data['data']['name']}")
            return data['data']['key']  # Return key for later use
        else:
            print(f"❌ Save custom food failed: {data.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Save custom food error: {e}")
        return None

def test_calculate_recipe_nutrition(custom_food_key=None):
    """Test the calculate recipe nutrition endpoint."""
    print("🔍 Testing calculate recipe nutrition endpoint...")
    
    # Create a recipe with mixed ingredients
    ingredients = [
        {"fdc_id": TEST_FDC_ID, "amount_grams": 100}
    ]
    
    # Add custom food if available
    if custom_food_key:
        ingredients.append({
            "custom_name": "Test Granola Bar",
            "amount_grams": 50
        })
    
    recipe = {"ingredients": ingredients}
    
    try:
        response = requests.post(
            f"{BASE_URL}/recipe/nutrition/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(recipe)
        )
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print("✅ Calculate recipe nutrition passed")
            nutrition = data['data']['nutrition']
            print(f"   Total calories: {nutrition.get('calories', 0):.1f}")
            print(f"   Total protein: {nutrition.get('protein', 0):.1f}g")
            print(f"   Ingredients: {data['data']['ingredients_count']}")
            print(f"   Total weight: {data['data']['total_weight']}g")
            return True
        else:
            print(f"❌ Calculate recipe nutrition failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Calculate recipe nutrition error: {e}")
        return False

def test_usage_examples():
    """Test the usage examples endpoint."""
    print("🔍 Testing usage examples endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/examples/")
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print("✅ Usage examples passed")
            service_info = data['data']['service_info']
            print(f"   Service: {service_info['name']}")
            print(f"   Version: {service_info['version']}")
            endpoints_count = len(data['data']['endpoints'])
            print(f"   Endpoints documented: {endpoints_count}")
            return True
        else:
            print(f"❌ Usage examples failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Usage examples error: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios."""
    print("🔍 Testing error handling...")
    
    tests_passed = 0
    total_tests = 0
    
    # Test invalid FDC ID
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/food/invalid/")
        if response.status_code == 400:
            print("✅ Invalid FDC ID handled correctly")
            tests_passed += 1
        else:
            print("❌ Invalid FDC ID not handled correctly")
    except Exception as e:
        print(f"❌ Error testing invalid FDC ID: {e}")
    
    # Test invalid JSON
    total_tests += 1
    try:
        response = requests.post(
            f"{BASE_URL}/custom-food/",
            headers={"Content-Type": "application/json"},
            data="invalid json"
        )
        if response.status_code == 400:
            print("✅ Invalid JSON handled correctly")
            tests_passed += 1
        else:
            print("❌ Invalid JSON not handled correctly")
    except Exception as e:
        print(f"❌ Error testing invalid JSON: {e}")
    
    # Test missing required fields
    total_tests += 1
    try:
        response = requests.post(
            f"{BASE_URL}/custom-food/",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"name": "Test"})  # Missing nutrients
        )
        if response.status_code == 400:
            print("✅ Missing required fields handled correctly")
            tests_passed += 1
        else:
            print("❌ Missing required fields not handled correctly")
    except Exception as e:
        print(f"❌ Error testing missing fields: {e}")
    
    return tests_passed == total_tests

def main():
    """Run all tests."""
    print("🚀 Starting API Management Endpoint Tests")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("   Make sure the Django development server is running:")
        print("   python manage.py runserver")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)
    
    tests_passed = 0
    total_tests = 0
    
    # Run tests
    test_functions = [
        ("Health Check", test_health_check),
        ("Get Food Nutrition", test_get_food_nutrition),
        ("Usage Examples", test_usage_examples),
        ("Error Handling", test_error_handling),
    ]
    
    custom_food_key = None
    
    # Test save custom food separately to get the key
    print("\n" + "=" * 50)
    custom_food_key = test_save_custom_food()
    if custom_food_key:
        tests_passed += 1
    total_tests += 1
    
    # Test recipe calculation with custom food
    print("\n" + "=" * 50)
    if test_calculate_recipe_nutrition(custom_food_key):
        tests_passed += 1
    total_tests += 1
    
    # Run other tests
    for test_name, test_func in test_functions:
        print("\n" + "=" * 50)
        total_tests += 1
        if test_func():
            tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        print("✅ API endpoints are working correctly")
    else:
        print(f"⚠️  {total_tests - tests_passed} test(s) failed")
        print("🔍 Check the output above for details")
    
    print("\n📋 Next steps:")
    print("  • Test with real FDC IDs from USDA database")
    print("  • Configure API key in Django settings")
    print("  • Test with frontend integration")
    print("  • Monitor logs for any issues")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)