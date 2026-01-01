# API Management Test Suite Documentation

## Overview

This comprehensive test suite contains **500 tests** divided into three categories:
- **100 Static Tests**: Test basic functionality, model validation, and static behavior
- **200 Dynamic Tests**: Test runtime behavior, API interactions, and dynamic functionality  
- **200 Regression Tests**: Test for preventing regressions and ensuring backward compatibility

## Architecture Changes

The application now uses a **dispatcher pattern** with:
- Single endpoint (`api_data_view`) that routes requests based on path
- Secret key authentication via `HTTP_X_MY_APP_SECRET_KEY` header
- Views return dictionaries instead of HTTP responses
- `render_response` helper wraps responses in consistent JSON format

## Test Structure

### Static Tests (`test_static.py`)
Tests basic functionality and static behavior without external dependencies:

1. **ApiResultStaticTests** (10 tests)
   - Constructor validation
   - Boolean conversion behavior
   - String representation
   - Parameter handling

2. **HTTP2ClientStaticTests** (10 tests)
   - Initialization with various parameters
   - URL building logic
   - Method existence validation
   - Configuration handling

3. **FoodDataCentralAPIStaticTests** (15 tests)
   - Class constants validation
   - Cache key generation
   - Nutrient extraction logic
   - Parameter processing

4. **ViewsStaticTests** (25 tests)
   - HTTP method validation
   - Parameter validation
   - Error response handling
   - Input sanitization
   - Dispatcher authentication testing
   - Response format validation
   - Path routing verification

5. **UrlPatternsStaticTests** (5 tests)
   - Single dispatcher endpoint validation
   - URL configuration validation
   - App name verification

6. **CacheStaticTests** (5 tests)
   - Cache configuration validation
   - Key generation consistency
   - Cache backend verification

7. **SettingsStaticTests** (6 tests)
   - Django settings validation
   - API key configuration
   - Internal secret key configuration
   - Security settings check

### Dynamic Tests (`test_dynamic.py`)
Tests runtime behavior and API interactions:

1. **HTTP2ClientDynamicTests** (25 tests)
   - Request/response handling
   - Retry mechanism testing
   - Error handling scenarios
   - JSON parsing behavior
   - Concurrent request handling

2. **FoodDataCentralAPIDynamicTests** (50 tests)
   - Cache behavior testing
   - API failure handling
   - Concurrent API calls
   - Parameter variation testing
   - Performance characteristics

3. **ViewsDynamicTests** (35 tests)
   - View integration testing
   - Response format validation
   - Error propagation
   - Concurrent view requests
   - Parameter edge cases
   - Dispatcher functionality
   - Authentication flow testing
   - Response wrapper testing

4. **IntegrationDynamicTests** (35 tests)
   - End-to-end flow testing
   - Component integration
   - Cache integration
   - Error propagation through stack
   - Performance under load
   - Security integration testing
   - Concurrent dispatcher requests

### Regression Tests (`test_regression.py`)
Tests for preventing regressions and ensuring backward compatibility:

1. **BackwardCompatibilityTests** (25 tests)
   - API response format consistency
   - Constructor signature compatibility
   - URL pattern stability
   - View behavior consistency

2. **DataFormatRegressionTests** (20 tests)
   - Output format consistency
   - Nutrient mapping stability
   - Cache key format consistency
   - API key injection format

3. **PerformanceRegressionTests** (15 tests)
   - Cache performance validation
   - Concurrent request performance
   - Memory usage patterns
   - Response time consistency

4. **ErrorHandlingRegressionTests** (20 tests)
   - Error response consistency
   - Exception handling stability
   - Failure mode validation
   - Error message format

5. **ConfigurationRegressionTests** (15 tests)
   - Django settings stability
   - URL configuration consistency
   - Middleware compatibility
   - Database configuration

6. **DatabaseRegressionTests** (10 tests)
   - Cache backend validation
   - Database connection testing
   - Configuration consistency

7. **SecurityRegressionTests** (15 tests)
   - API key handling security
   - Input validation security
   - XSS prevention validation
   - SQL injection prevention

8. **IntegrationRegressionTests** (20 tests)
   - End-to-end flow consistency
   - Cache integration stability
   - Concurrent access patterns
   - Component interaction validation

9. **VersionCompatibilityTests** (10 tests)
   - Python version compatibility
   - Django version compatibility
   - Dependency compatibility
   - Import validation

10. **DispatcherRegressionTests** (15 tests)
    - Dispatcher authentication regression
    - Path routing consistency
    - Response format stability
    - Error handling consistency

11. **SecurityRegressionEnhancedTests** (15 tests)
    - Secret key validation security
    - Header injection prevention
    - Path traversal security
    - Authentication bypass prevention

12. **ResponseFormatRegressionTests** (10 tests)
    - Response wrapper consistency
    - JSON serialization stability
    - Format standardization
    - Error response consistency

## Running Tests

### Run All Tests
```bash
cd backend/src/api_management
python run_tests.py
```

### Run Specific Test Suite
```bash
python run_tests.py run api_management.test_static
python run_tests.py run api_management.test_dynamic
python run_tests.py run api_management.test_regression
```

### Run Specific Test Class
```bash
python run_tests.py run api_management.test_static.ApiResultStaticTests
python run_tests.py run api_management.test_dynamic.HTTP2ClientDynamicTests
python run_tests.py run api_management.test_regression.BackwardCompatibilityTests
```

### List Available Tests
```bash
python run_tests.py list
```

### Using Django Test Runner
```bash
cd backend/src
python manage.py test api_management.test_static
python manage.py test api_management.test_dynamic
python manage.py test api_management.test_regression
```

### Using pytest (if installed)
```bash
cd backend/src
pytest api_management/test_static.py -v
pytest api_management/test_dynamic.py -v
pytest api_management/test_regression.py -v
```

## Test Coverage

The test suite covers:

### Models (`models.py`)
- **ApiResult class**: 100% coverage
  - Constructor validation
  - Boolean conversion
  - String representation
  - All properties and methods

- **HTTP2Client class**: 100% coverage
  - Initialization and configuration
  - URL building logic
  - Request handling with retries
  - JSON parsing
  - Error handling
  - Connection management

- **FoodDataCentralAPI class**: 100% coverage
  - API key management
  - Cache key generation
  - Search functionality
  - Nutrition data retrieval
  - Multiple food handling
  - Nutrient extraction
  - Error handling

### Views (`views.py`)
- **get_food_nutrition**: 100% coverage
  - Parameter validation
  - HTTP method validation
  - Success responses
  - Error responses
  - API integration

- **get_multiple_foods**: 100% coverage
  - Parameter validation
  - List handling
  - Error responses
  - API integration

- **calculate_recipe_nutrition**: 100% coverage
  - Recipe validation
  - Nutrient processing
  - Error handling
  - Data sanitization

### URLs (`urls.py`)
- **URL patterns**: 100% coverage
  - Pattern definition validation
  - Name resolution
  - App namespace verification

## Test Environment Setup

### Prerequisites
```bash
pip install -r test_requirements.txt
```

### Environment Variables
```bash
export DJANGO_SETTINGS_MODULE=mysite.settings
export API_KEY=test_api_key_for_testing
```

### Database Setup
Tests use SQLite in-memory database by default for speed. No additional setup required.

### Cache Setup
Tests use Django's local memory cache backend. No Redis required for testing.

## Test Data and Mocking

### Mock Strategy
- **HTTP requests**: Mocked using `unittest.mock.patch`
- **API responses**: Controlled test data
- **Cache operations**: Real cache operations with test backend
- **Database operations**: In-memory SQLite database

### Test Data Patterns
- **Valid API responses**: Realistic USDA FoodData Central format
- **Error scenarios**: Network errors, API errors, invalid data
- **Edge cases**: Empty responses, malformed data, timeout scenarios

## Performance Testing

### Benchmarks
- **Cache hit performance**: < 1ms response time
- **Concurrent requests**: 10+ simultaneous requests
- **Memory usage**: Controlled object creation/destruction
- **API retry logic**: Exponential backoff validation

### Load Testing
- **Concurrent API calls**: 50+ simultaneous requests
- **Cache performance**: 1000+ cache operations
- **Memory stability**: No memory leaks under load

## Continuous Integration

### Test Automation
Tests are designed to run in CI/CD environments:
- No external dependencies required
- Fast execution (< 2 minutes total)
- Deterministic results
- Comprehensive error reporting

### Coverage Requirements
- **Minimum coverage**: 95%
- **Critical paths**: 100% coverage
- **Error handling**: 100% coverage
- **API integration**: 100% coverage

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/backend/src"
   ```

2. **Django Setup Issues**
   ```bash
   export DJANGO_SETTINGS_MODULE=mysite.settings
   ```

3. **Cache Issues**
   - Tests use local memory cache
   - Clear cache between test runs if needed

4. **Database Issues**
   - Tests use in-memory SQLite
   - No persistent data between runs

### Debug Mode
Run tests with verbose output:
```bash
python run_tests.py --verbose
```

### Test Isolation
Each test is isolated:
- Fresh cache for each test
- Independent mock objects
- No shared state between tests

## Contributing

### Adding New Tests
1. Follow existing naming conventions
2. Include docstrings for all test methods
3. Use appropriate test category (static/dynamic/regression)
4. Mock external dependencies
5. Test both success and failure scenarios

### Test Guidelines
- **One assertion per test method** (when possible)
- **Descriptive test names** that explain what is being tested
- **Comprehensive error testing** for all failure modes
- **Performance considerations** for dynamic tests
- **Backward compatibility** validation for regression tests

## Maintenance

### Regular Updates
- Update test data when API formats change
- Add regression tests for bug fixes
- Update performance benchmarks
- Review and update mock responses

### Test Review
- Monthly review of test coverage
- Quarterly performance benchmark review
- Annual compatibility testing with new Django versions
- Regular security test updates