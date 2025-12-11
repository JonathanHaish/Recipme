"""
Comprehensive Test Suite for API Management Django App

This module provides a unified interface for running all types of tests
with detailed reporting and analysis.
"""

import unittest
import sys
import time
import json
from io import StringIO
from unittest.mock import patch
from django.test import TestCase
from django.core.cache import cache

# Import all test modules
from .test_static import *
from .test_dynamic import *
from .test_regression import *
from .test_static_extended import *
from .test_dynamic_extended import *
from .test_regression_extended import *
from .test_config import TestConfig, TestAssertions, TestDataFactory


class TestSuiteRunner:
    """Comprehensive test suite runner with reporting."""
    
    def __init__(self):
        self.results = {
            'static': {'passed': 0, 'failed': 0, 'errors': 0, 'time': 0},
            'dynamic': {'passed': 0, 'failed': 0, 'errors': 0, 'time': 0},
            'regression': {'passed': 0, 'failed': 0, 'errors': 0, 'time': 0},
            'total': {'passed': 0, 'failed': 0, 'errors': 0, 'time': 0}
        }
        self.detailed_results = []
    
    def run_test_category(self, category_name, test_classes):
        """Run a specific category of tests."""
        print(f"\n{'='*60}")
        print(f"Running {category_name.upper()} Tests")
        print(f"{'='*60}")
        
        start_time = time.time()
        suite = unittest.TestSuite()
        
        # Add all test classes to the suite
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Run tests with custom result handler
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream, 
            verbosity=2,
            buffer=True
        )
        result = runner.run(suite)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Store results
        self.results[category_name.lower()] = {
            'passed': result.testsRun - len(result.failures) - len(result.errors),
            'failed': len(result.failures),
            'errors': len(result.errors),
            'time': execution_time
        }
        
        # Print summary
        print(f"\n{category_name} Tests Summary:")
        print(f"  Tests run: {result.testsRun}")
        print(f"  Passed: {self.results[category_name.lower()]['passed']}")
        print(f"  Failed: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Time: {execution_time:.2f}s")
        
        # Print failures and errors
        if result.failures:
            print(f"\nFailures in {category_name}:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\nErrors in {category_name}:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
        
        return result
    
    def run_all_tests(self):
        """Run all test categories."""
        print("Starting Comprehensive Test Suite")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_start_time = time.time()
        
        # Define test categories
        test_categories = {
            'Static': [
                # Original static tests
                TestApiResult,
                TestHTTP2Client,
                TestFoodDataCentralAPI,
                TestFoodDataCentralAPIIntegration,
                # Extended static tests
                TestApiResultExtended,
                TestHTTP2ClientExtended,
                TestFoodDataCentralAPIExtended,
                TestBoundaryConditions,
                TestPerformanceScenarios,
                TestDataValidation,
                TestStringHandling
            ],
            'Dynamic': [
                # Original dynamic tests
                TestHTTP2ClientIntegration,
                TestFoodDataCentralAPIIntegration,
                TestFoodDataCentralAPIPerformance,
                TestFoodDataCentralAPIWithRealCache,
                # Extended dynamic tests
                TestComplexWorkflows,
                TestConcurrencyScenarios,
                TestPerformanceScenarios,
                TestErrorRecoveryScenarios,
                TestWorkflowVariations,
                TestIntegrationScenarios
            ],
            'Regression': [
                # Original regression tests
                TestCriticalUserWorkflows,
                TestHTTP2ClientRegressions,
                TestCacheRegressions,
                TestAPIErrorHandlingRegressions,
                TestDataConsistencyRegressions,
                # Extended regression tests
                TestHistoricalBugFixes,
                TestEdgeCaseRegressions,
                TestPerformanceRegressions,
                TestSpecificHistoricalBugs,
                TestCompatibilityRegressions
            ]
        }
        
        # Run each category
        all_results = []
        for category, test_classes in test_categories.items():
            result = self.run_test_category(category, test_classes)
            all_results.append(result)
        
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        
        # Calculate totals
        total_tests = sum(r.testsRun for r in all_results)
        total_failures = sum(len(r.failures) for r in all_results)
        total_errors = sum(len(r.errors) for r in all_results)
        total_passed = total_tests - total_failures - total_errors
        
        self.results['total'] = {
            'passed': total_passed,
            'failed': total_failures,
            'errors': total_errors,
            'time': total_time
        }
        
        # Print final summary
        self.print_final_summary()
        
        return all_results
    
    def print_final_summary(self):
        """Print comprehensive test summary."""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST SUITE SUMMARY")
        print(f"{'='*80}")
        
        # Category breakdown
        for category in ['static', 'dynamic', 'regression']:
            if category in self.results:
                r = self.results[category]
                print(f"{category.capitalize():12} | "
                      f"Passed: {r['passed']:3d} | "
                      f"Failed: {r['failed']:3d} | "
                      f"Errors: {r['errors']:3d} | "
                      f"Time: {r['time']:6.2f}s")
        
        print(f"{'-'*80}")
        
        # Total summary
        r = self.results['total']
        total_tests = r['passed'] + r['failed'] + r['errors']
        success_rate = (r['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{'TOTAL':12} | "
              f"Passed: {r['passed']:3d} | "
              f"Failed: {r['failed']:3d} | "
              f"Errors: {r['errors']:3d} | "
              f"Time: {r['time']:6.2f}s")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Performance analysis
        self.print_performance_analysis()
        
        # Recommendations
        self.print_recommendations()
    
    def print_performance_analysis(self):
        """Print performance analysis."""
        print(f"\n{'='*60}")
        print("PERFORMANCE ANALYSIS")
        print(f"{'='*60}")
        
        # Time per category
        for category in ['static', 'dynamic', 'regression']:
            if category in self.results:
                r = self.results[category]
                total_tests = r['passed'] + r['failed'] + r['errors']
                avg_time = r['time'] / total_tests if total_tests > 0 else 0
                print(f"{category.capitalize():12}: {r['time']:6.2f}s total, "
                      f"{avg_time*1000:6.1f}ms per test")
        
        # Performance thresholds
        print(f"\nPerformance Thresholds:")
        for key, threshold in TestConfig.PERFORMANCE_THRESHOLDS.items():
            print(f"  {key:25}: < {threshold*1000:6.0f}ms")
    
    def print_recommendations(self):
        """Print recommendations based on test results."""
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}")
        
        r = self.results['total']
        
        if r['failed'] > 0:
            print("⚠️  FAILURES DETECTED:")
            print("   - Review failed test cases")
            print("   - Check for breaking changes")
            print("   - Update tests if API contracts changed")
        
        if r['errors'] > 0:
            print("❌ ERRORS DETECTED:")
            print("   - Fix syntax or import errors")
            print("   - Check test environment setup")
            print("   - Verify mock configurations")
        
        if r['time'] > 30:
            print("🐌 SLOW TEST EXECUTION:")
            print("   - Consider optimizing slow tests")
            print("   - Use more mocking for external dependencies")
            print("   - Parallelize test execution")
        
        if r['failed'] == 0 and r['errors'] == 0:
            print("✅ ALL TESTS PASSED!")
            print("   - Code quality is maintained")
            print("   - No regressions detected")
            print("   - Ready for deployment")
    
    def generate_json_report(self, filename='test_report.json'):
        """Generate JSON report of test results."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': self.results,
            'summary': {
                'total_tests': sum(r['passed'] + r['failed'] + r['errors'] 
                                 for r in self.results.values() if isinstance(r, dict)),
                'success_rate': (self.results['total']['passed'] / 
                               (self.results['total']['passed'] + 
                                self.results['total']['failed'] + 
                                self.results['total']['errors']) * 100)
                               if (self.results['total']['passed'] + 
                                   self.results['total']['failed'] + 
                                   self.results['total']['errors']) > 0 else 0
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nJSON report saved to: {filename}")


class QuickTestSuite(TestCase):
    """Quick test suite for basic functionality verification."""
    
    def setUp(self):
        """Set up quick test fixtures."""
        cache.clear()
    
    def tearDown(self):
        """Clean up after quick tests."""
        cache.clear()
    
    def test_basic_api_result_functionality(self):
        """Quick test of ApiResult basic functionality."""
        result = ApiResult(success=True, status=200, data={"test": "data"})
        self.assertTrue(result.success)
        self.assertEqual(result.status, 200)
        self.assertTrue(bool(result))
    
    def test_basic_http_client_functionality(self):
        """Quick test of HTTP2Client basic functionality."""
        try:
            client = HTTP2Client(base_url="https://example.com")
            url = client.build_url("/test")
            self.assertEqual(url, "https://example.com/test")
            client.close()
        except ImportError:
            self.skipTest("HTTP/2 dependencies not available")
    
    def test_basic_food_api_functionality(self):
        """Quick test of FoodDataCentralAPI basic functionality."""
        mock_client = unittest.mock.Mock()
        api = FoodDataCentralAPI(mock_client, "test_key")
        
        # Test name sanitization
        sanitized = api.sanitize_name("Test Food Name")
        self.assertEqual(sanitized, "test-food-name")
        
        # Test custom food storage
        food_data = {"calories": 100}
        key = api.save_custom_food("test_food", food_data)
        retrieved = api.get_custom_food("test_food")
        self.assertEqual(retrieved, food_data)


def run_quick_tests():
    """Run quick verification tests."""
    print("Running Quick Test Suite...")
    suite = unittest.TestLoader().loadTestsFromTestCase(QuickTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def main():
    """Main entry point for comprehensive test suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Test Suite Runner')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick verification tests only')
    parser.add_argument('--json-report', action='store_true',
                       help='Generate JSON report')
    parser.add_argument('--report-file', default='test_report.json',
                       help='JSON report filename')
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_tests()
        sys.exit(0 if success else 1)
    
    # Run comprehensive test suite
    runner = TestSuiteRunner()
    results = runner.run_all_tests()
    
    if args.json_report:
        runner.generate_json_report(args.report_file)
    
    # Exit with appropriate code
    total_failures = runner.results['total']['failed']
    total_errors = runner.results['total']['errors']
    sys.exit(0 if (total_failures == 0 and total_errors == 0) else 1)


if __name__ == '__main__':
    main()