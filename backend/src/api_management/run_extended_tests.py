#!/usr/bin/env python
"""
Extended Test Runner for API Management Django App

This script runs the comprehensive extended test suite with 1500+ tests
across static, dynamic, and regression categories.
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path

# Add the Django project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()

from django.test.utils import get_runner
from django.conf import settings


class ExtendedTestRunner:
    """Extended test runner with comprehensive reporting."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}
    
    def run_all_extended_tests(self, verbosity=1, failfast=False, coverage=False):
        """Run all extended tests."""
        print("🚀 Starting Extended API Management Test Suite")
        print("=" * 80)
        print(f"📊 Expected: 1500+ tests across 3 categories")
        print(f"⏱️  Estimated time: 2-5 minutes")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Test modules to run
        test_modules = [
            'api_management.test_static',
            'api_management.test_static_extended',
            'api_management.test_dynamic', 
            'api_management.test_dynamic_extended',
            'api_management.test_regression',
            'api_management.test_regression_extended',
        ]
        
        if coverage:
            return self._run_with_coverage(test_modules, verbosity, failfast)
        else:
            return self._run_without_coverage(test_modules, verbosity, failfast)
    
    def _run_without_coverage(self, test_modules, verbosity, failfast):
        """Run tests without coverage analysis."""
        cmd = ['python', 'manage.py', 'test'] + test_modules
        
        if verbosity > 1:
            cmd.append(f'--verbosity={verbosity}')
        
        if failfast:
            cmd.append('--failfast')
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print("-" * 80)
        
        result = subprocess.run(cmd, cwd='..')
        
        self.end_time = time.time()
        self._print_summary(result.returncode)
        
        return result.returncode
    
    def _run_with_coverage(self, test_modules, verbosity, failfast):
        """Run tests with coverage analysis."""
        coverage_cmd = [
            'coverage', 'run', 
            '--source=api_management',
            '--omit=*/migrations/*,*/venv/*,*/env/*,*/test_*',
            'manage.py', 'test'
        ] + test_modules
        
        if verbosity > 1:
            coverage_cmd.append(f'--verbosity={verbosity}')
        
        if failfast:
            coverage_cmd.append('--failfast')
        
        print(f"🔧 Running with coverage: {' '.join(coverage_cmd)}")
        print("-" * 80)
        
        result = subprocess.run(coverage_cmd, cwd='..')
        
        if result.returncode == 0:
            print("\n📈 Generating coverage report...")
            subprocess.run(['coverage', 'report', '--show-missing'], cwd='..')
            
            print("\n📊 Generating HTML coverage report...")
            subprocess.run(['coverage', 'html'], cwd='..')
            print("📁 HTML report available in: htmlcov/index.html")
        
        self.end_time = time.time()
        self._print_summary(result.returncode)
        
        return result.returncode
    
    def run_category_tests(self, category, verbosity=1, failfast=False):
        """Run tests for a specific category."""
        category_modules = {
            'static': [
                'api_management.test_static',
                'api_management.test_static_extended'
            ],
            'dynamic': [
                'api_management.test_dynamic',
                'api_management.test_dynamic_extended'
            ],
            'regression': [
                'api_management.test_regression',
                'api_management.test_regression_extended'
            ]
        }
        
        if category not in category_modules:
            print(f"❌ Unknown category: {category}")
            print(f"Available categories: {list(category_modules.keys())}")
            return 1
        
        modules = category_modules[category]
        
        print(f"🎯 Running {category.upper()} tests")
        print("=" * 60)
        print(f"📦 Modules: {', '.join(modules)}")
        print("=" * 60)
        
        self.start_time = time.time()
        
        cmd = ['python', 'manage.py', 'test'] + modules
        
        if verbosity > 1:
            cmd.append(f'--verbosity={verbosity}')
        
        if failfast:
            cmd.append('--failfast')
        
        result = subprocess.run(cmd, cwd='..')
        
        self.end_time = time.time()
        self._print_category_summary(category, result.returncode)
        
        return result.returncode
    
    def run_performance_tests(self):
        """Run only performance-related tests."""
        print("⚡ Running Performance Tests")
        print("=" * 50)
        
        performance_patterns = [
            'api_management.test_static_extended.TestPerformanceScenarios',
            'api_management.test_dynamic_extended.TestPerformanceScenarios',
            'api_management.test_regression_extended.TestPerformanceRegressions',
        ]
        
        self.start_time = time.time()
        
        cmd = ['python', 'manage.py', 'test'] + performance_patterns + ['--verbosity=2']
        result = subprocess.run(cmd, cwd='..')
        
        self.end_time = time.time()
        self._print_performance_summary(result.returncode)
        
        return result.returncode
    
    def run_stress_tests(self):
        """Run stress and load tests."""
        print("💪 Running Stress Tests")
        print("=" * 50)
        
        stress_patterns = [
            'api_management.test_dynamic_extended.TestConcurrencyScenarios',
            'api_management.test_regression_extended.TestEdgeCaseRegressions',
        ]
        
        self.start_time = time.time()
        
        cmd = ['python', 'manage.py', 'test'] + stress_patterns + ['--verbosity=2']
        result = subprocess.run(cmd, cwd='..')
        
        self.end_time = time.time()
        self._print_stress_summary(result.returncode)
        
        return result.returncode
    
    def _print_summary(self, return_code):
        """Print comprehensive test summary."""
        execution_time = self.end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("🏁 EXTENDED TEST SUITE SUMMARY")
        print("=" * 80)
        
        if return_code == 0:
            print("✅ ALL TESTS PASSED!")
            print("🎉 The extended test suite completed successfully")
        else:
            print("❌ SOME TESTS FAILED!")
            print("🔍 Please review the test output above for details")
        
        print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
        print(f"📊 Test categories: Static, Dynamic, Regression (Extended)")
        print(f"🧪 Total test methods: 1500+ across all categories")
        
        # Performance analysis
        if execution_time > 300:  # 5 minutes
            print("⚠️  Tests took longer than expected")
            print("💡 Consider running categories separately for faster feedback")
        elif execution_time < 60:  # 1 minute
            print("⚡ Excellent performance! Tests completed quickly")
        
        print("\n📋 Next steps:")
        if return_code == 0:
            print("  ✓ All tests passing - ready for deployment")
            print("  ✓ Code quality maintained")
            print("  ✓ No regressions detected")
        else:
            print("  🔧 Fix failing tests")
            print("  🔍 Review error messages")
            print("  📖 Check documentation for troubleshooting")
        
        print("=" * 80)
    
    def _print_category_summary(self, category, return_code):
        """Print category-specific summary."""
        execution_time = self.end_time - self.start_time
        
        print(f"\n🏁 {category.upper()} TESTS SUMMARY")
        print("=" * 60)
        
        status = "PASSED" if return_code == 0 else "FAILED"
        icon = "✅" if return_code == 0 else "❌"
        
        print(f"{icon} Status: {status}")
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        
        category_info = {
            'static': "Unit tests - Individual component testing",
            'dynamic': "Integration tests - Component interaction testing", 
            'regression': "Regression tests - Historical bug prevention"
        }
        
        print(f"📝 Description: {category_info.get(category, 'Unknown category')}")
        print("=" * 60)
    
    def _print_performance_summary(self, return_code):
        """Print performance test summary."""
        execution_time = self.end_time - self.start_time
        
        print(f"\n⚡ PERFORMANCE TESTS SUMMARY")
        print("=" * 50)
        
        status = "PASSED" if return_code == 0 else "FAILED"
        icon = "✅" if return_code == 0 else "❌"
        
        print(f"{icon} Status: {status}")
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        
        if return_code == 0:
            print("🚀 Performance benchmarks met")
            print("📈 No performance regressions detected")
        else:
            print("⚠️  Performance issues detected")
            print("🔍 Review failing performance tests")
        
        print("=" * 50)
    
    def _print_stress_summary(self, return_code):
        """Print stress test summary."""
        execution_time = self.end_time - self.start_time
        
        print(f"\n💪 STRESS TESTS SUMMARY")
        print("=" * 50)
        
        status = "PASSED" if return_code == 0 else "FAILED"
        icon = "✅" if return_code == 0 else "❌"
        
        print(f"{icon} Status: {status}")
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        
        if return_code == 0:
            print("💪 System handles stress conditions well")
            print("🔒 Concurrency and edge cases handled properly")
        else:
            print("⚠️  Stress test failures detected")
            print("🔍 Review concurrency and edge case handling")
        
        print("=" * 50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extended Test Runner for API Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_extended_tests.py                    # Run all extended tests
  python run_extended_tests.py --category static  # Run static tests only
  python run_extended_tests.py --performance      # Run performance tests
  python run_extended_tests.py --stress           # Run stress tests
  python run_extended_tests.py --coverage         # Run with coverage
  python run_extended_tests.py --verbose          # Verbose output
        """
    )
    
    # Test selection options
    parser.add_argument('--category', choices=['static', 'dynamic', 'regression'],
                       help='Run specific test category')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only')
    parser.add_argument('--stress', action='store_true',
                       help='Run stress tests only')
    
    # Execution options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--failfast', '-f', action='store_true',
                       help='Stop on first failure')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Run with coverage analysis')
    
    args = parser.parse_args()
    
    # Create runner
    runner = ExtendedTestRunner()
    
    try:
        # Determine what to run
        if args.performance:
            exit_code = runner.run_performance_tests()
        elif args.stress:
            exit_code = runner.run_stress_tests()
        elif args.category:
            exit_code = runner.run_category_tests(
                args.category,
                verbosity=2 if args.verbose else 1,
                failfast=args.failfast
            )
        else:
            exit_code = runner.run_all_extended_tests(
                verbosity=2 if args.verbose else 1,
                failfast=args.failfast,
                coverage=args.coverage
            )
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()