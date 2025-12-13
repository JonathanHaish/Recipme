#!/usr/bin/env python
"""
Test Runner for API Management Django Application
Runs all test suites: static, dynamic, and regression tests
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import unittest
from io import StringIO


def setup_django():
    """Setup Django environment for testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    django.setup()


def run_test_suite(test_module_name, suite_name):
    """Run a specific test suite and return results"""
    print(f"\n{'='*60}")
    print(f"Running {suite_name}")
    print(f"{'='*60}")
    
    # Capture test output
    test_output = StringIO()
    
    # Load and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module_name)
    
    runner = unittest.TextTestRunner(
        stream=test_output,
        verbosity=2,
        buffer=True
    )
    
    result = runner.run(suite)
    
    # Print results
    output = test_output.getvalue()
    print(output)
    
    # Print summary
    print(f"\n{suite_name} Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFailures in {suite_name}:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nErrors in {suite_name}:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Error:')[-1].strip()}")
    
    return result


def main():
    """Main test runner function"""
    print("API Management Test Suite Runner")
    print("="*60)
    
    # Setup Django
    try:
        setup_django()
        print("✓ Django environment setup complete")
    except Exception as e:
        print(f"✗ Failed to setup Django environment: {e}")
        return 1
    
    # Test suites to run
    test_suites = [
        ('api_management.test_static', 'Static Tests (100 tests)'),
        ('api_management.test_dynamic', 'Dynamic Tests (200 tests)'),
        ('api_management.test_regression', 'Regression Tests (200 tests)')
    ]
    
    total_results = {
        'tests_run': 0,
        'failures': 0,
        'errors': 0,
        'skipped': 0
    }
    
    all_passed = True
    
    # Run each test suite
    for module_name, suite_name in test_suites:
        try:
            result = run_test_suite(module_name, suite_name)
            
            # Accumulate results
            total_results['tests_run'] += result.testsRun
            total_results['failures'] += len(result.failures)
            total_results['errors'] += len(result.errors)
            total_results['skipped'] += len(result.skipped) if hasattr(result, 'skipped') else 0
            
            if result.failures or result.errors:
                all_passed = False
                
        except Exception as e:
            print(f"✗ Failed to run {suite_name}: {e}")
            all_passed = False
    
    # Print overall summary
    print(f"\n{'='*60}")
    print("OVERALL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests run: {total_results['tests_run']}")
    print(f"Total failures: {total_results['failures']}")
    print(f"Total errors: {total_results['errors']}")
    print(f"Total skipped: {total_results['skipped']}")
    
    if all_passed and total_results['failures'] == 0 and total_results['errors'] == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ SOME TESTS FAILED")
        return 1


def run_specific_test(test_name):
    """Run a specific test class or method"""
    print(f"Running specific test: {test_name}")
    
    setup_django()
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def list_available_tests():
    """List all available test classes and methods"""
    print("Available test classes:")
    print("\nStatic Tests:")
    print("- api_management.test_static.ApiResultStaticTests")
    print("- api_management.test_static.HTTP2ClientStaticTests")
    print("- api_management.test_static.FoodDataCentralAPIStaticTests")
    print("- api_management.test_static.ViewsStaticTests")
    print("- api_management.test_static.UrlPatternsStaticTests")
    print("- api_management.test_static.CacheStaticTests")
    print("- api_management.test_static.SettingsStaticTests")
    
    print("\nDynamic Tests:")
    print("- api_management.test_dynamic.HTTP2ClientDynamicTests")
    print("- api_management.test_dynamic.FoodDataCentralAPIDynamicTests")
    print("- api_management.test_dynamic.ViewsDynamicTests")
    print("- api_management.test_dynamic.IntegrationDynamicTests")
    
    print("\nRegression Tests:")
    print("- api_management.test_regression.BackwardCompatibilityTests")
    print("- api_management.test_regression.DataFormatRegressionTests")
    print("- api_management.test_regression.PerformanceRegressionTests")
    print("- api_management.test_regression.ErrorHandlingRegressionTests")
    print("- api_management.test_regression.ConfigurationRegressionTests")
    print("- api_management.test_regression.DatabaseRegressionTests")
    print("- api_management.test_regression.SecurityRegressionTests")
    print("- api_management.test_regression.IntegrationRegressionTests")
    print("- api_management.test_regression.VersionCompatibilityTests")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            list_available_tests()
            sys.exit(0)
        elif command == 'run':
            if len(sys.argv) > 2:
                test_name = sys.argv[2]
                sys.exit(run_specific_test(test_name))
            else:
                print("Usage: python run_tests.py run <test_name>")
                sys.exit(1)
        else:
            print("Unknown command. Use 'list' to see available tests or 'run <test_name>' to run specific test.")
            sys.exit(1)
    else:
        # Run all tests
        sys.exit(main())