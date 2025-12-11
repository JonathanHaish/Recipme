# API Management Testing Documentation

This document provides comprehensive information about the test suite for the `api_management` Django app.

## Overview

The test suite is organized into three main categories:

1. **Static Tests** (`test_static.py`) - Unit tests for individual components
2. **Dynamic Tests** (`test_dynamic.py`) - Integration tests for component interactions
3. **Regression Tests** (`test_regression.py`) - Tests to prevent previously fixed bugs from reoccurring

## Test Structure

### Static Tests (Unit Tests) - 500+ Tests

These tests focus on testing individual methods and classes in isolation, using mocks to eliminate external dependencies.

#### Core Test Classes:
- **TestApiResult** - Data structure validation
- **TestHTTP2Client** - HTTP client functionality  
- **TestFoodDataCentralAPI** - Core API methods

#### Extended Test Classes:
- **TestApiResultExtended** - Complex data structures, edge cases
- **TestHTTP2ClientExtended** - URL building variations, Unicode handling
- **TestFoodDataCentralAPIExtended** - Comprehensive name sanitization, stress testing
- **TestBoundaryConditions** - Boundary value testing
- **TestPerformanceScenarios** - Performance benchmarks
- **TestDataValidation** - Invalid data handling
- **TestStringHandling** - Unicode and string edge cases

### Dynamic Tests (Integration Tests) - 500+ Tests

These tests focus on the interaction between components and simulate more realistic usage scenarios.

#### Core Integration Classes:
- **TestHTTP2ClientIntegration** - Retry mechanisms, status validation
- **TestFoodDataCentralAPIIntegration** - Complete workflows
- **TestFoodDataCentralAPIPerformance** - Performance benchmarks

#### Extended Integration Classes:
- **TestComplexWorkflows** - Meal planning, recipe substitution, batch processing
- **TestConcurrencyScenarios** - Thread safety, concurrent operations
- **TestPerformanceScenarios** - Large-scale processing, optimization
- **TestErrorRecoveryScenarios** - Failure recovery, resilience testing
- **TestWorkflowVariations** - Different meal types and scenarios
- **TestIntegrationScenarios** - Mixed data source integration

### Regression Tests - 500+ Tests

These tests ensure that previously working functionality continues to work after code changes.

#### Core Regression Classes:
- **TestCriticalUserWorkflows** - Essential user scenarios
- **TestHTTP2ClientRegressions** - HTTP client edge cases
- **TestCacheRegressions** - Cache-related issues
- **TestAPIErrorHandlingRegressions** - Error handling scenarios
- **TestDataConsistencyRegressions** - Data integrity checks

#### Extended Regression Classes:
- **TestHistoricalBugFixes** - Previously reported and fixed bugs
- **TestEdgeCaseRegressions** - Extreme values, malformed data
- **TestPerformanceRegressions** - Performance degradation prevention
- **TestSpecificHistoricalBugs** - Targeted bug scenario tests
- **TestCompatibilityRegressions** - Data format compatibility

## Running the Tests

### Prerequisites

Ensure you have the following installed:
- Django
- Redis (for cache backend, optional - tests use in-memory cache by default)
- Required Python packages from `requirements.txt`
- HTTP/2 support: `pip install httpx[http2]` (optional - tests will skip if missing)

### Installation

```bash
# Install core dependencies
pip install -r requirements.txt

# Install testing dependencies (optional)
pip install -r api_management/test_requirements.txt

# Or install HTTP/2 support separately
pip install httpx[http2]
```

### Running All Tests

```bash
# From the Django project root (/backend/src/)
python manage.py test api_management
```

### Running Specific Test Categories

```bash
# Static tests only
python manage.py test api_management.test_static

# Dynamic tests only
python manage.py test api_management.test_dynamic

# Regression tests only
python manage.py test api_management.test_regression
```

### Running Individual Test Classes

```bash
# Example: Run only HTTP2Client tests
python manage.py test api_management.test_static.TestHTTP2Client
```

### Running with Coverage

```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test api_management
coverage report
coverage html  # Generate HTML report
```

## Test Configuration

### Cache Settings

Tests use Django's cache framework. For testing, you may want to use a separate cache backend:

```python
# In settings.py or test settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

### Environment Variables

Some tests may require environment variables:

```bash
export API_KEY="your_test_api_key"
export POSTGRES_DB="test_recipme"
export POSTGRES_USER="test_user"
export POSTGRES_PASSWORD="test_password"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export REDIS_HOST="localhost"
```

## Test Data and Fixtures

### Mock Data Patterns

The tests use consistent mock data patterns:

```python
# Standard food nutrient data
food_data = {
    "foodNutrients": [
        {
            "nutrient": {"name": "Protein", "unitName": "g"},
            "amount": 20.0
        },
        {
            "nutrient": {"name": "Energy", "unitName": "kcal"},
            "amount": 100.0
        }
    ]
}

# Standard ingredient format
ingredients = [
    {"fdc_id": 12345, "amount_grams": 100},
    {"custom_name": "homemade bread", "amount_grams": 50}
]
```

### Custom Test Utilities

The test suite includes several utility methods for common operations:

- `setUp()` and `tearDown()` methods for test isolation
- Mock response creation helpers
- Cache clearing between tests
- Consistent error simulation

## Performance Benchmarks

### Expected Performance Metrics

- Single food lookup: < 100ms (with cache miss)
- Recipe calculation (10 ingredients): < 50ms
- Recipe calculation (100 ingredients): < 500ms
- Cache operations: < 10ms

### Memory Usage

- Single food data: ~1KB
- Recipe with 100 ingredients: ~100KB
- Cache overhead: ~10% of data size

## Common Issues and Troubleshooting

### Cache-Related Issues

1. **Cache not clearing between tests**
   - Ensure `cache.clear()` is called in `setUp()` and `tearDown()`
   - Check cache backend configuration

2. **Cache key collisions**
   - Tests include specific scenarios for handling key collisions
   - Verify sanitization logic is working correctly

### Network-Related Issues

1. **Mock not working properly**
   - Ensure proper patching of `httpx.Client.request`
   - Check mock return values and side effects

2. **Timeout issues in tests**
   - Use shorter timeouts in test configurations
   - Mock time.sleep() for faster test execution

### Data Consistency Issues

1. **Floating point precision**
   - Use `assertAlmostEqual()` for floating point comparisons
   - Consider rounding in production code if needed

2. **Unicode handling**
   - Test with various Unicode characters
   - Ensure proper encoding/decoding throughout the pipeline

## Continuous Integration

### GitHub Actions Example

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
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
    
    - name: Run tests
      run: |
        python manage.py test api_management
      env:
        POSTGRES_HOST: localhost
        REDIS_HOST: localhost
```

## Test Maintenance

### Adding New Tests

When adding new functionality:

1. Add unit tests to `test_static.py`
2. Add integration tests to `test_dynamic.py`
3. Consider regression scenarios for `test_regression.py`
4. Update this documentation

### Updating Existing Tests

When modifying existing functionality:

1. Update affected tests
2. Run full test suite to ensure no regressions
3. Update mock data if API contracts change
4. Review performance benchmarks

### Test Review Checklist

- [ ] All test methods have descriptive names
- [ ] Tests are isolated and don't depend on each other
- [ ] Mocks are properly configured and cleaned up
- [ ] Edge cases are covered
- [ ] Performance implications are considered
- [ ] Documentation is updated

## Metrics and Reporting

### Test Coverage Goals

- Overall coverage: > 95%
- Critical paths: 100%
- Error handling: > 98%
- Edge cases: > 90%

### Test Execution Time

- Full extended test suite: 2-5 minutes (1500+ tests)
- Individual test categories: 30-90 seconds (500+ tests each)
- Original test suite: < 30 seconds (67 tests)
- Single test class: < 10 seconds

## Future Improvements

### Planned Enhancements

1. **Property-based testing** with Hypothesis
2. **Load testing** with realistic data volumes
3. **Integration with external APIs** (sandbox environments)
4. **Automated performance regression detection**
5. **Test data factories** for more realistic scenarios

### Known Limitations

1. Tests use mocked HTTP responses (no real API calls)
2. Limited testing of concurrent scenarios
3. Cache backend differences between test and production
4. Time-dependent tests may be flaky

---

For questions or issues with the test suite, please refer to the project documentation or contact the development team.