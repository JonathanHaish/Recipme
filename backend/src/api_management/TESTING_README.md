# API Management Testing Suite

This directory contains a comprehensive testing suite for the `api_management` Django app, including static tests, dynamic tests, and regression tests.

## Quick Start

### Validate Environment
```bash
# Check if environment is ready for testing
python api_management/validate_test_environment.py
```

### Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install HTTP/2 support (optional but recommended)
pip install httpx[http2]

# Install testing dependencies (optional)
pip install coverage
```

### Run All Tests (Original Suite - 67 tests)
```bash
# From the Django project root (/backend/src/)
python manage.py test api_management
```

### Run Extended Test Suite (1500+ tests)
```bash
# From the api_management directory
python run_extended_tests.py

# Or use the final comprehensive runner
python run_final_tests.py
```

### Run Quick Verification
```bash
# From the api_management directory
python test_suite.py --quick
```

### Run Comprehensive Test Suite
```bash
# From the api_management directory
python test_suite.py
```

## Test Files Overview

| File | Purpose | Test Count | Test Type |
|------|---------|------------|-----------|
| `test_static.py` | Unit tests for individual components | ~67 | Static |
| `test_static_extended.py` | Extended unit tests with edge cases | ~500 | Static |
| `test_dynamic.py` | Integration tests for component interactions | ~25 | Dynamic |
| `test_dynamic_extended.py` | Extended integration and workflow tests | ~500 | Dynamic |
| `test_regression.py` | Tests to prevent previously fixed bugs | ~20 | Regression |
| `test_regression_extended.py` | Extended regression and historical bug tests | ~500 | Regression |
| `test_config.py` | Test configuration and utilities | N/A | Configuration |
| `test_suite.py` | Comprehensive test runner with reporting | N/A | Runner |
| `run_tests.py` | Advanced test runner with options | N/A | Runner |
| `run_extended_tests.py` | Extended test suite runner (1500+ tests) | N/A | Runner |
| `run_final_tests.py` | Final comprehensive runner with environment detection | N/A | Runner |

## Test Categories

### 1. Static Tests (Unit Tests)
- **Purpose**: Test individual methods and classes in isolation
- **Coverage**: ApiResult, HTTP2Client, FoodDataCentralAPI core methods
- **Execution Time**: ~5-10 seconds
- **Dependencies**: Minimal (uses mocks)

**Key Test Classes:**
- `TestApiResult` - Data structure validation
- `TestHTTP2Client` - HTTP client functionality
- `TestFoodDataCentralAPI` - Core API methods

### 2. Dynamic Tests (Integration Tests)
- **Purpose**: Test component interactions and realistic scenarios
- **Coverage**: End-to-end workflows, performance, caching
- **Execution Time**: ~10-20 seconds
- **Dependencies**: Cache backend, mocked HTTP responses

**Key Test Classes:**
- `TestHTTP2ClientIntegration` - HTTP client with retry logic
- `TestFoodDataCentralAPIIntegration` - Complete food processing workflows
- `TestFoodDataCentralAPIPerformance` - Performance benchmarks

### 3. Regression Tests
- **Purpose**: Prevent previously fixed bugs from reoccurring
- **Coverage**: Edge cases, error handling, data consistency
- **Execution Time**: ~15-25 seconds
- **Dependencies**: Full system simulation

**Key Test Classes:**
- `TestCriticalUserWorkflows` - Essential user scenarios
- `TestHTTP2ClientRegressions` - HTTP client edge cases
- `TestCacheRegressions` - Cache-related issues
- `TestAPIErrorHandlingRegressions` - Error handling scenarios
- `TestDataConsistencyRegressions` - Data integrity checks

## Running Specific Tests

### By Category
```bash
# Original test categories
python manage.py test api_management.test_static          # ~67 tests
python manage.py test api_management.test_dynamic         # ~25 tests  
python manage.py test api_management.test_regression      # ~20 tests

# Extended test categories (500+ tests each)
python run_extended_tests.py --category static           # ~500 tests
python run_extended_tests.py --category dynamic          # ~500 tests
python run_extended_tests.py --category regression       # ~500 tests

# Specialized test runs
python run_extended_tests.py --performance               # Performance tests only
python run_extended_tests.py --stress                    # Stress tests only

# Final comprehensive runner options
python run_final_tests.py --core-only                    # Core tests only (67 tests)
python run_final_tests.py --smoke                        # Quick smoke test
python run_final_tests.py --benchmark                    # Performance benchmarks
python run_final_tests.py --coverage                     # With coverage analysis
python run_final_tests.py --report                       # Generate execution report
```

### By Test Class
```bash
# Specific test class
python manage.py test api_management.test_static.TestApiResult

# Specific test method
python manage.py test api_management.test_static.TestApiResult.test_successful_result_creation
```

### Using Custom Runner
```bash
# With coverage
python run_tests.py --coverage

# With HTML coverage report
python run_tests.py --coverage --html

# Verbose output
python run_tests.py --verbose

# Stop on first failure
python run_tests.py --failfast

# Performance benchmarks only
python run_tests.py --benchmark
```

## Test Configuration

### Environment Variables
```bash
export API_KEY="test_api_key_12345"
export POSTGRES_DB="test_recipme"
export POSTGRES_USER="test_user"
export POSTGRES_PASSWORD="test_password"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export REDIS_HOST="localhost"
```

### Django Settings Override
The tests use optimized settings for faster execution:
- In-memory SQLite database
- Local memory cache backend
- Reduced logging verbosity
- Disabled migrations

## Performance Benchmarks

### Expected Performance Thresholds
- Single food lookup: < 100ms
- Recipe calculation (10 ingredients): < 50ms
- Recipe calculation (100 ingredients): < 500ms
- Cache operations: < 10ms

### Performance Test Results
Run performance tests to verify system meets benchmarks:
```bash
python run_tests.py --benchmark
```

## Coverage Analysis

### Generate Coverage Report
```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run --source='api_management' manage.py test api_management

# View report
coverage report

# Generate HTML report
coverage html
```

### Coverage Goals
- Overall coverage: > 90%
- Critical paths: 100%
- Error handling: > 95%

## Continuous Integration

### GitHub Actions Example
```yaml
name: API Management Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests with coverage
      run: |
        cd backend/src
        coverage run --source='api_management' manage.py test api_management
        coverage report --fail-under=90
      env:
        REDIS_HOST: localhost
        API_KEY: test_api_key_12345
```

## Test Data and Fixtures

### Mock Data Patterns
```python
# Standard USDA food response
MOCK_USDA_RESPONSE = {
    "fdc_id": 12345,
    "description": "Apple, raw",
    "foodNutrients": [
        {
            "nutrient": {"name": "Protein", "unitName": "g"},
            "amount": 0.26
        }
    ]
}

# Standard ingredient format
SAMPLE_INGREDIENTS = [
    {"fdc_id": 12345, "amount_grams": 150},
    {"custom_name": "homemade bread", "amount_grams": 100}
]
```

### Test Data Factory
Use `TestDataFactory` for creating consistent test data:
```python
from .test_config import TestDataFactory

# Create food nutrient
nutrient = TestDataFactory.create_food_nutrient("Protein", 20.0, "g")

# Create complete food data
food_data = TestDataFactory.create_food_data(12345, "Apple", [nutrient])

# Create ingredient
ingredient = TestDataFactory.create_ingredient(fdc_id=12345, amount_grams=100)

# Create recipe
recipe = TestDataFactory.create_recipe(num_ingredients=5, mix_types=True)
```

## Troubleshooting

### Common Issues

#### Cache Not Clearing
```python
# Ensure cache is cleared in setUp and tearDown
def setUp(self):
    cache.clear()

def tearDown(self):
    cache.clear()
```

#### Mock Not Working
```python
# Proper mock patching
@patch('httpx.Client.request')
def test_method(self, mock_request):
    mock_request.return_value = Mock(status_code=200, text='{"data": "test"}')
```

#### Floating Point Precision
```python
# Use assertAlmostEqual for floating point comparisons
self.assertAlmostEqual(actual, expected, places=2)
```

#### Unicode Issues
```python
# Test with various Unicode strings
unicode_names = ["פיתה ביתית", "café au lait", "北京烤鸭"]
for name in unicode_names:
    # Test Unicode handling
```

### Debug Mode
Run tests in debug mode for detailed error information:
```bash
python run_tests.py --debug
```

### Verbose Output
Get detailed test execution information:
```bash
python run_tests.py --verbose
```

## Test Maintenance

### Adding New Tests
1. Identify the appropriate test category (static/dynamic/regression)
2. Add test methods following naming convention: `test_<functionality>`
3. Use appropriate assertions and mock configurations
4. Update documentation if needed

### Updating Existing Tests
1. Run full test suite before changes
2. Update affected tests
3. Verify no regressions introduced
4. Update performance benchmarks if needed

### Test Review Checklist
- [ ] Test methods have descriptive names
- [ ] Tests are isolated and independent
- [ ] Mocks are properly configured and cleaned up
- [ ] Edge cases are covered
- [ ] Performance implications considered
- [ ] Documentation updated

## Reporting and Analysis

### JSON Report Generation
```bash
python test_suite.py --json-report --report-file results.json
```

### Test Metrics
The test suite tracks:
- Test execution time per category
- Success/failure rates
- Performance benchmarks
- Coverage percentages

### Recommendations
Based on test results, the suite provides:
- Performance optimization suggestions
- Error resolution guidance
- Code quality recommendations

## Support

For questions about the test suite:
1. Check this documentation
2. Review test configuration in `test_config.py`
3. Examine similar test patterns in existing tests
4. Contact the development team

---

**Last Updated**: December 2024  
**Test Suite Version**: 1.0  
**Django Version**: 5.2.8