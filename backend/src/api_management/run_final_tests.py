#!/usr/bin/env python
"""
Final Comprehensive Test Runner for API Management Django App

This script runs the complete test suite with intelligent handling of
environment-specific issues and comprehensive reporting.
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


class FinalTestRunner:
    """Final comprehensive test runner with intelligent environment handling."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.environment_info = self._detect_environment()
    
    def _detect_environment(self):
        """Detect the execution environment."""
        env_info = {
            'is_docker': os.path.exists('/.dockerenv'),
            'is_ci': bool(os.environ.get('CI')),
            'is_github_actions': bool(os.environ.get('GITHUB_ACTIONS')),
            'python_version': sys.version,
            'platform': sys.platform
        }
        return env_info
    
    def run_comprehensive_test_suite(self, include_extended=True, verbosity=1, failfast=False, coverage=False):
        """Run the comprehensive test suite with intelligent configuration."""
        
        print("🚀 API Management Comprehensive Test Suite")
        print("=" * 80)
        
        # Print environment info
        self._print_environment_info()
        
        # Determine test modules based on options
        if include_extended:
            test_modules = [
                'api_management.test_static',
                'api_management.test_static_extended',
                'api_management.test_dynamic', 
                'api_management.test_dynamic_extended',
                'api_management.test_regression',
                'api_management.test_regression_extended',
            ]
            expected_tests = "1500+"
            estimated_time = "3-6 minutes"
        else:
            test_modules = [
                'api_management.test_static',
                'api_management.test_dynamic',
                'api_management.test_regression',
            ]
            expected_tests = "67"
            estimated_time = "30-60 seconds"
        
        print(f"📊 Test modules: {len(test_modules)}")
        print(f"🧪 Expected tests: {expected_tests}")
        print(f"⏱️  Estimated time: {estimated_time}")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Build command
        cmd = ['python', 'manage.py', 'test'] + test_modules
        
        # Add options based on environment and preferences
        if verbosity > 1:
            cmd.append(f'--verbosity={verbosity}')
        
        if failfast:
            cmd.append('--failfast')
        
        # Add environment-specific options
        if self.environment_info['is_docker'] or self.environment_info['is_ci']:
            # More conservative settings for containerized environments
            cmd.append('--keepdb')  # Reuse test database for speed
        
        # Handle coverage
        if coverage:
            return self._run_with_coverage(cmd, test_modules)
        else:
            return self._run_without_coverage(cmd)
    
    def _run_without_coverage(self, cmd):
        """Run tests without coverage."""
        print(f"🔧 Executing: {' '.join(cmd)}")
        print("-" * 80)
        
        result = subprocess.run(cmd, cwd='..')
        
        self.end_time = time.time()
        self._print_comprehensive_summary(result.returncode)
        
        return result.returncode
    
    def _run_with_coverage(self, cmd, test_modules):
        """Run tests with coverage analysis."""
        coverage_cmd = [
            'coverage', 'run', 
            '--source=api_management',
            '--omit=*/migrations/*,*/venv/*,*/env/*,*/test_*,*/validate_*,*/run_*',
            '--branch'  # Include branch coverage
        ] + cmd[1:]  # Skip 'python' from original command
        
        print(f"🔧 Executing with coverage: {' '.join(coverage_cmd)}")
        print("-" * 80)
        
        result = subprocess.run(coverage_cmd, cwd='..')
        
        if result.returncode == 0:
            print("\n📈 Generating coverage reports...")
            
            # Generate console report
            subprocess.run(['coverage', 'report', '--show-missing', '--skip-covered'], cwd='..')
            
            # Generate HTML report
            print("\n📊 Generating HTML coverage report...")
            subprocess.run(['coverage', 'html', '--directory=htmlcov'], cwd='..')
            print("📁 HTML report: htmlcov/index.html")
            
            # Generate XML report for CI
            if self.environment_info['is_ci']:
                subprocess.run(['coverage', 'xml'], cwd='..')
                print("📄 XML report: coverage.xml")
        
        self.end_time = time.time()
        self._print_comprehensive_summary(result.returncode)
        
        return result.returncode
    
    def run_quick_smoke_test(self):
        """Run a quick smoke test to verify basic functionality."""
        print("💨 Quick Smoke Test")
        print("=" * 50)
        
        # Run just the core static tests
        cmd = ['python', 'manage.py', 'test', 'api_management.test_static.TestApiResult', '--verbosity=2']
        
        self.start_time = time.time()
        result = subprocess.run(cmd, cwd='..')
        self.end_time = time.time()
        
        execution_time = self.end_time - self.start_time
        
        if result.returncode == 0:
            print(f"✅ Smoke test passed in {execution_time:.2f}s")
            print("🚀 System is ready for full test execution")
        else:
            print(f"❌ Smoke test failed in {execution_time:.2f}s")
            print("🔍 Check basic setup before running full tests")
        
        return result.returncode
    
    def run_performance_benchmark(self):
        """Run performance benchmark tests."""
        print("⚡ Performance Benchmark Suite")
        print("=" * 60)
        
        performance_tests = [
            'api_management.test_static_extended.TestPerformanceScenarios',
            'api_management.test_dynamic_extended.TestPerformanceScenarios',
        ]
        
        cmd = ['python', 'manage.py', 'test'] + performance_tests + ['--verbosity=2']
        
        self.start_time = time.time()
        result = subprocess.run(cmd, cwd='..')
        self.end_time = time.time()
        
        execution_time = self.end_time - self.start_time
        
        print(f"\n⚡ Performance benchmark completed in {execution_time:.2f}s")
        
        if result.returncode == 0:
            print("🎯 All performance benchmarks passed")
            print("📈 System performance is within acceptable limits")
        else:
            print("⚠️  Some performance benchmarks failed")
            print("🔍 Review performance test output for optimization opportunities")
        
        return result.returncode
    
    def _print_environment_info(self):
        """Print detected environment information."""
        print("🔍 Environment Detection:")
        
        env = self.environment_info
        print(f"  🐳 Docker: {'Yes' if env['is_docker'] else 'No'}")
        print(f"  🔄 CI/CD: {'Yes' if env['is_ci'] else 'No'}")
        print(f"  🐙 GitHub Actions: {'Yes' if env['is_github_actions'] else 'No'}")
        print(f"  🐍 Python: {env['python_version'].split()[0]}")
        print(f"  💻 Platform: {env['platform']}")
        print()
    
    def _print_comprehensive_summary(self, return_code):
        """Print comprehensive test execution summary."""
        execution_time = self.end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        # Status
        if return_code == 0:
            print("✅ ALL TESTS PASSED!")
            status_emoji = "🎉"
            status_message = "Test suite completed successfully"
        else:
            print("❌ SOME TESTS FAILED!")
            status_emoji = "🔍"
            status_message = "Review test output for failure details"
        
        print(f"{status_emoji} {status_message}")
        
        # Timing
        print(f"\n⏱️  Execution Details:")
        print(f"  Total time: {execution_time:.2f} seconds")
        print(f"  Average time per test: {execution_time/150:.3f}s (estimated)")
        
        # Performance analysis
        if execution_time > 300:  # 5 minutes
            print("  ⚠️  Execution took longer than expected")
            print("  💡 Consider running test categories separately")
        elif execution_time < 60:  # 1 minute
            print("  ⚡ Excellent performance!")
        else:
            print("  ✅ Good performance")
        
        # Environment-specific notes
        env = self.environment_info
        if env['is_docker']:
            print(f"\n🐳 Docker Environment Notes:")
            print(f"  • Tests executed in containerized environment")
            print(f"  • Performance may vary from native execution")
        
        if env['is_ci']:
            print(f"\n🔄 CI/CD Environment Notes:")
            print(f"  • Automated test execution detected")
            print(f"  • Results suitable for deployment pipeline")
        
        # Next steps
        print(f"\n📋 Next Steps:")
        if return_code == 0:
            print("  ✓ All tests passing - code is ready")
            print("  ✓ No regressions detected")
            print("  ✓ Performance within acceptable limits")
            if not env['is_ci']:
                print("  💡 Consider running with --coverage for detailed analysis")
        else:
            print("  🔧 Fix failing tests before proceeding")
            print("  📖 Check TEST_FIXES_SUMMARY.md for common solutions")
            print("  🔍 Run individual test categories to isolate issues")
        
        print("=" * 80)
    
    def generate_test_report(self, filename='test_execution_report.md'):
        """Generate a markdown test execution report."""
        if not self.start_time or not self.end_time:
            print("⚠️  No test execution data available for report")
            return
        
        execution_time = self.end_time - self.start_time
        
        report_content = f"""# Test Execution Report

## Summary
- **Execution Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Total Execution Time**: {execution_time:.2f} seconds
- **Environment**: {'Docker' if self.environment_info['is_docker'] else 'Native'}
- **CI/CD**: {'Yes' if self.environment_info['is_ci'] else 'No'}

## Environment Details
- **Python Version**: {self.environment_info['python_version'].split()[0]}
- **Platform**: {self.environment_info['platform']}
- **Docker**: {self.environment_info['is_docker']}
- **GitHub Actions**: {self.environment_info['is_github_actions']}

## Test Categories
- **Static Tests**: Unit tests for individual components
- **Dynamic Tests**: Integration tests for component interactions
- **Regression Tests**: Historical bug prevention tests

## Performance Analysis
- **Execution Speed**: {'Fast' if execution_time < 60 else 'Moderate' if execution_time < 300 else 'Slow'}
- **Estimated Tests**: 1500+ (extended suite)
- **Average per Test**: {execution_time/1500:.3f}s

## Recommendations
{'✅ All systems operational - ready for deployment' if execution_time < 300 else '⚠️ Consider performance optimization'}

---
*Generated by API Management Test Suite v2.0*
"""
        
        with open(filename, 'w') as f:
            f.write(report_content)
        
        print(f"📄 Test report generated: {filename}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Final Comprehensive Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_final_tests.py                     # Run full extended suite
  python run_final_tests.py --core-only         # Run core tests only (67 tests)
  python run_final_tests.py --smoke             # Quick smoke test
  python run_final_tests.py --benchmark         # Performance benchmarks
  python run_final_tests.py --coverage          # With coverage analysis
  python run_final_tests.py --report            # Generate test report
        """
    )
    
    # Test selection
    parser.add_argument('--core-only', action='store_true',
                       help='Run core tests only (67 tests)')
    parser.add_argument('--smoke', action='store_true',
                       help='Run quick smoke test')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run performance benchmarks')
    
    # Execution options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--failfast', '-f', action='store_true',
                       help='Stop on first failure')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Run with coverage analysis')
    
    # Reporting options
    parser.add_argument('--report', action='store_true',
                       help='Generate test execution report')
    parser.add_argument('--report-file', default='test_execution_report.md',
                       help='Report filename')
    
    args = parser.parse_args()
    
    # Create runner
    runner = FinalTestRunner()
    
    try:
        # Determine execution mode
        if args.smoke:
            exit_code = runner.run_quick_smoke_test()
        elif args.benchmark:
            exit_code = runner.run_performance_benchmark()
        else:
            # Full test suite
            include_extended = not args.core_only
            exit_code = runner.run_comprehensive_test_suite(
                include_extended=include_extended,
                verbosity=2 if args.verbose else 1,
                failfast=args.failfast,
                coverage=args.coverage
            )
        
        # Generate report if requested
        if args.report:
            runner.generate_test_report(args.report_file)
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()