# Test Installation Guide

## Prerequisites

Before running the tests, ensure you have the following dependencies installed:

### Required Dependencies

1. **Django and Core Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **HTTP/2 Support (Optional but Recommended)**
   ```bash
   pip install httpx[http2]
   # OR install h2 separately
   pip install h2>=4.0.0
   ```

3. **Testing Dependencies**
   ```bash
   pip install coverage>=7.0.0
   ```

### Full Installation

```bash
# Install all dependencies at once
pip install -r requirements.txt -r api_management/test_requirements.txt
```

## Dependency Issues and Solutions

### HTTP/2 Support Missing

**Error**: `ImportError: Using http2=True, but the 'h2' package is not installed`

**Solution**:
```bash
pip install httpx[http2]
```

**Alternative**: The tests will automatically skip HTTP/2 specific tests if the dependency is missing.

### Redis Connection Issues

**Error**: Redis connection errors during cache tests

**Solution**:
```bash
# Start Redis server
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:6-alpine
```

**Alternative**: Tests use in-memory cache backend by default for isolation.

### Database Issues

**Error**: Database connection or migration issues

**Solution**: Tests use SQLite in-memory database by default, no setup required.

## Environment Setup

### Environment Variables (Optional)

```bash
export API_KEY="test_api_key_12345"
export REDIS_HOST="localhost"
export POSTGRES_HOST="localhost"
```

### Django Settings

Tests use optimized settings automatically:
- In-memory SQLite database
- Local memory cache backend
- Reduced logging verbosity

## Verification

### Quick Test
```bash
python api_management/test_suite.py --quick
```

### Full Test Suite
```bash
python manage.py test api_management
```

### With Coverage
```bash
coverage run --source='api_management' manage.py test api_management
coverage report
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure Django project is in Python path
   - Check DJANGO_SETTINGS_MODULE environment variable

2. **Cache Errors**
   - Tests clear cache automatically
   - Use in-memory cache for testing

3. **Mock Errors**
   - Tests use unittest.mock extensively
   - Ensure proper mock cleanup in tearDown methods

4. **Floating Point Precision**
   - Tests use assertAlmostEqual for floating point comparisons
   - Precision issues are handled gracefully

### Debug Mode

Run tests with verbose output:
```bash
python manage.py test api_management -v 2
```

### Skip Problematic Tests

If HTTP/2 dependencies cannot be installed:
```bash
# Tests will automatically skip HTTP/2 related tests
python manage.py test api_management
```

## Docker Setup

### Using Docker Compose

```yaml
# Add to docker-compose.yml
services:
  test:
    build: .
    command: python manage.py test api_management
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
```

### Dockerfile for Testing

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
COPY api_management/test_requirements.txt .

RUN pip install -r requirements.txt -r test_requirements.txt

COPY . .
CMD ["python", "manage.py", "test", "api_management"]
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install -r api_management/test_requirements.txt

- name: Run tests
  run: |
    python manage.py test api_management
```

### GitLab CI

```yaml
test:
  script:
    - pip install -r requirements.txt -r api_management/test_requirements.txt
    - python manage.py test api_management
```

## Performance Optimization

### Faster Test Execution

1. **Use in-memory database** (default in test config)
2. **Disable migrations** (configured in test settings)
3. **Use local memory cache** (configured in test settings)
4. **Run specific test categories**:
   ```bash
   python manage.py test api_management.test_static  # Fastest
   python manage.py test api_management.test_dynamic
   python manage.py test api_management.test_regression
   ```

### Parallel Execution

```bash
# Install django-parallel-tests
pip install django-parallel-tests

# Run tests in parallel
python manage.py test api_management --parallel
```

## Support

If you encounter issues not covered in this guide:

1. Check the main [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md)
2. Review the [TESTING_README.md](TESTING_README.md)
3. Examine test configuration in [test_config.py](test_config.py)
4. Contact the development team

---

**Last Updated**: December 2024