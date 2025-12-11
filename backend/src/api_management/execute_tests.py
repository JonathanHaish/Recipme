#!/usr/bin/env python
"""
Simple Test Execution Script for API Management Django App

This script provides a straightforward way to run the test suite.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the Django project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def run_tests():
    """Run the API management tests."""
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    print("Running API Management Test Suite...")
    print("=" * 50)
    
    # Run all api_management tests
    failures = test_runner.run_tests(["api_management"])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_specific_tests(test_type):
    """Run specific type of tests."""
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    test_module = f"api_management.test_{test_type}"
    print(f"Running {test_type.upper()} tests...")
    print("=" * 50)
    
    failures = test_runner.run_tests([test_module])
    
    if failures:
        print(f"\n❌ {failures} {test_type} test(s) failed!")
        return False
    else:
        print(f"\n✅ All {test_type} tests passed!")
        return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type in ['static', 'dynamic', 'regression']:
            success = run_specific_tests(test_type)
        else:
            print("Usage: python execute_tests.py [static|dynamic|regression]")
            sys.exit(1)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)