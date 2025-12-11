#!/usr/bin/env python
"""
Test Environment Validation Script

This script checks if the test environment is properly configured
and all dependencies are available.
"""

import sys
import os
import importlib

def check_django_setup():
    """Check if Django is properly configured."""
    try:
        import django
        from django.conf import settings
        
        # Set up Django if not already configured
        if not settings.configured:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
            django.setup()
        
        print("✅ Django setup: OK")
        return True
    except Exception as e:
        print(f"❌ Django setup: FAILED - {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available."""
    dependencies = {
        'httpx': 'HTTP client library',
        'django': 'Django framework',
        'unittest.mock': 'Mock library (built-in)',
    }
    
    optional_dependencies = {
        'h2': 'HTTP/2 support (optional)',
        'coverage': 'Code coverage analysis (optional)',
        'redis': 'Redis client (optional)',
    }
    
    all_good = True
    
    print("\nChecking required dependencies:")
    for dep, desc in dependencies.items():
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}: OK - {desc}")
        except ImportError:
            print(f"❌ {dep}: MISSING - {desc}")
            all_good = False
    
    print("\nChecking optional dependencies:")
    for dep, desc in optional_dependencies.items():
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}: OK - {desc}")
        except ImportError:
            print(f"⚠️  {dep}: MISSING - {desc}")
    
    return all_good

def check_http2_support():
    """Check if HTTP/2 support is available."""
    try:
        import httpx
        # Try to create an HTTP/2 client
        client = httpx.Client(http2=True)
        client.close()
        print("✅ HTTP/2 support: OK")
        return True
    except ImportError as e:
        print(f"⚠️  HTTP/2 support: MISSING - {e}")
        print("   Install with: pip install httpx[http2]")
        return False

def check_cache_backend():
    """Check if cache backend is working."""
    try:
        from django.core.cache import cache
        
        # Test cache operations
        test_key = "test_validation_key"
        test_value = "test_validation_value"
        
        cache.set(test_key, test_value, 10)
        retrieved = cache.get(test_key)
        cache.delete(test_key)
        
        if retrieved == test_value:
            print("✅ Cache backend: OK")
            return True
        else:
            print("❌ Cache backend: FAILED - Value mismatch")
            return False
    except Exception as e:
        print(f"❌ Cache backend: FAILED - {e}")
        return False

def check_test_imports():
    """Check if test modules can be imported."""
    test_modules = [
        'api_management.models',
        'api_management.test_static',
        'api_management.test_dynamic',
        'api_management.test_regression',
        'api_management.test_config',
    ]
    
    all_good = True
    print("\nChecking test module imports:")
    
    for module in test_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}: OK")
        except ImportError as e:
            print(f"❌ {module}: FAILED - {e}")
            all_good = False
    
    return all_good

def run_quick_functionality_test():
    """Run a quick functionality test."""
    try:
        from api_management.models import ApiResult, FoodDataCentralAPI
        from unittest.mock import Mock
        
        # Test ApiResult
        result = ApiResult(success=True, status=200, data={"test": "data"})
        assert result.success == True
        assert result.status == 200
        
        # Test FoodDataCentralAPI basic functionality
        mock_client = Mock()
        api = FoodDataCentralAPI(mock_client, "test_key")
        sanitized = api.sanitize_name("Test Food")
        assert sanitized == "test-food"
        
        print("✅ Quick functionality test: OK")
        return True
    except Exception as e:
        print(f"❌ Quick functionality test: FAILED - {e}")
        return False

def main():
    """Main validation function."""
    print("API Management Test Environment Validation")
    print("=" * 50)
    
    checks = [
        ("Django Setup", check_django_setup),
        ("Dependencies", check_dependencies),
        ("HTTP/2 Support", check_http2_support),
        ("Cache Backend", check_cache_backend),
        ("Test Imports", check_test_imports),
        ("Quick Functionality", run_quick_functionality_test),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        result = check_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "✅" if result else "❌"
        print(f"{icon} {name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Environment is ready for testing!")
        print("\nYou can now run:")
        print("  python manage.py test api_management")
        print("  python api_management/test_suite.py --quick")
        return True
    else:
        print(f"\n⚠️  {total - passed} issues found. Please address them before running tests.")
        print("\nFor help, see:")
        print("  api_management/INSTALLATION_GUIDE.md")
        print("  api_management/TEST_DOCUMENTATION.md")
        return False

if __name__ == '__main__':
    # Add project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    success = main()
    sys.exit(0 if success else 1)