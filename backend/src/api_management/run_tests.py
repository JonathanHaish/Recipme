#!/usr/bin/env python
"""
Test Runner Script for API Management Django App

This script provides various options for running the test suite with different
configurations and reporting options.
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# Add the Django project to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()

from django.test.utils import get_runner
from django.conf import settings
from django.core.management import execute_from_command_line


class TestRunner:
    """Custom test runner with additional features."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def run_tests(self, test_labels=None, verbosity=1, interactive=True, 
                  failfast=False, keepdb=False, reverse=False, debug_mode=False,
                  coverage=False, coverage_html=False):
        """Run tests with specified options."""
        
        self.start_time = time.time()
        
        # Prepare command
        cmd = ['python', 'manage.py', 'test']
        
        if test_labels:
            cmd.extend(test_labels)
        else:
            cmd.append('api_management')
        
        # Add options
        if verbosity > 1:
            cmd.append(f'--verbosity={verbosity}')
        
        if not interactive:
            cmd.append('--noinput')
        
        if failfast:
            cmd.append('--failfast')
        
        if keepdb:
            cmd.append('--keepdb')
        
        if reverse:
            cmd.append('--reverse')
        
        if debug_mode:
            cmd.append('--debug-mode')
        
        # Handle coverage
        if coverage or coverage_html:
            coverage_cmd = [
                'coverage', 'run', '--source=api_management',
                '--omit=*/migrations/*,*/venv/*,*/env/*'
            ] + cmd[1:]  # Skip 'python' from original command
            
            print(f"Running with coverage: {' '.join(coverage_cmd)}")
            result = subprocess.run(coverage_cmd, cwd='..')
            
            if result.returncode == 0:
                print("\nGenerating coverage report...")
                subprocess.run(['coverage', 'report'], cwd='..')
                
                if coverage_html:
                    print("Generating HTML coverage report...")
                    subprocess.run(['coverage', 'html'], cwd='..')
                    print("HTML coverage report generated in htmlcov/")
        else:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd='..')
        
        self.end_time = time.time()
        
        # Print execution time
        execution_time = self.end_time - self.start_time
        print(f"\nTest execution time: {execution_time:.2f} seconds")
        
        return result.returncode
    
    def run_specific_category(self, category, **kwargs):
        """Run a specific test category."""
        test_labels = [f'api_management.test_{category}']
        return self.run_tests(test_labels, **kwargs)
    
    def run_specific_class(self, test_class, **kwargs):
        """Run a specific test class."""
        test_labels = [test_class]
        return self.run_tests(test_labels, **kwargs)


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description='Run tests for API Management Django App',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run all tests
  python run_tests.py --static                 # Run only static tests
  python run_tests.py --dynamic                # Run only dynamic tests
  python run_tests.py --regression             # Run only regression tests
  python run_tests.py --coverage               # Run with coverage report
  python run_tests.py --coverage --html        # Run with HTML coverage report
  python run_tests.py --failfast               # Stop on first failure
  python run_tests.py --verbose                # Verbose output
  python run_tests.py --class TestApiResult    # Run specific test class
        """
    )
    
    # Test category options
    parser.add_argument('--static', action='store_true',
                       help='Run only static/unit tests')
    parser.add_argument('--dynamic', action='store_true',
                       help='Run only dynamic/integration tests')
    parser.add_argument('--regression', action='store_true',
                       help='Run only regression tests')
    
    # Test execution options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--failfast', '-f', action='store_true',
                       help='Stop on first failure')
    parser.add_argument('--keepdb', '-k', action='store_true',
                       help='Keep test database')
    parser.add_argument('--reverse', '-r', action='store_true',
                       help='Run tests in reverse order')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug mode')
    
    # Coverage options
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Run with coverage analysis')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML coverage report (requires --coverage)')
    
    # Specific test options
    parser.add_argument('--class', dest='test_class',
                       help='Run specific test class (e.g., TestApiResult)')
    parser.add_argument('--method', dest='test_method',
                       help='Run specific test method (e.g., test_successful_result_creation)')
    
    # Performance options
    parser.add_argument('--benchmark', action='store_true',
                       help='Run performance benchmark tests')
    parser.add_argument('--profile', action='store_true',
                       help='Profile test execution')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.html and not args.coverage:
        parser.error("--html requires --coverage")
    
    # Create test runner
    runner = TestRunner()
    
    # Determine what tests to run
    test_labels = []
    
    if args.static:
        test_labels.append('api_management.test_static')
    elif args.dynamic:
        test_labels.append('api_management.test_dynamic')
    elif args.regression:
        test_labels.append('api_management.test_regression')
    elif args.test_class:
        if args.test_method:
            test_labels.append(f'api_management.test_static.{args.test_class}.{args.test_method}')
        else:
            test_labels.append(f'api_management.test_static.{args.test_class}')
    elif args.benchmark:
        test_labels.append('api_management.test_dynamic.TestFoodDataCentralAPIPerformance')
    
    # Set verbosity
    verbosity = 2 if args.verbose else 1
    
    # Run tests
    try:
        exit_code = runner.run_tests(
            test_labels=test_labels if test_labels else None,
            verbosity=verbosity,
            failfast=args.failfast,
            keepdb=args.keepdb,
            reverse=args.reverse,
            debug_mode=args.debug,
            coverage=args.coverage,
            coverage_html=args.html
        )
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()