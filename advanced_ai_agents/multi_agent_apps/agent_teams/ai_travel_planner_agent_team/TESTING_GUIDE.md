# TripCraft AI - Comprehensive Testing Guide

This guide covers all testing for the TripCraft AI application, including backend, frontend, and end-to-end tests.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Quick Start](#quick-start)
4. [Backend Testing](#backend-testing)
5. [Frontend Testing](#frontend-testing)
6. [E2E Testing](#e2e-testing)
7. [Running All Tests](#running-all-tests)
8. [CI/CD Integration](#cicd-integration)
9. [Best Practices](#best-practices)

## Overview

TripCraft AI uses a comprehensive testing strategy covering:

- **Backend Tests**: Python/FastAPI tests using pytest
  - Unit tests for models and repositories
  - Integration tests for API endpoints

- **Frontend Tests**: Next.js/React tests using Jest and React Testing Library
  - Unit tests for utilities and components
  - Integration tests for API routes

- **E2E Tests**: Full application tests using Playwright
  - Complete user journey tests
  - Cross-browser testing
  - Mobile/responsive testing

## Test Structure

```
ai_travel_planner_agent_team/
├── backend/
│   ├── tests/
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_models.py       # 10+ tests
│   │   │   └── test_repositories.py # 8+ tests
│   │   └── integration/
│   │       └── test_api.py          # 7+ tests
│   ├── pytest.ini                   # Pytest configuration
│   └── pyproject.toml               # Dependencies with [dev] extras
│
└── client/
    ├── __tests__/
    │   ├── lib/
    │   │   └── utils.test.ts        # 7+ tests
    │   ├── components/ui/
    │   │   └── button.test.tsx      # 17+ tests
    │   └── app/api/plan/submit/
    │       └── route.test.ts        # 7+ tests
    ├── e2e/
    │   └── trip-planning.spec.ts    # 12+ tests
    ├── jest.config.js               # Jest configuration
    ├── jest.setup.js                # Jest setup
    ├── playwright.config.ts         # Playwright configuration
    └── package.json                 # Test scripts
```

## Quick Start

### Prerequisites

**Backend:**
```bash
cd backend
pip install -e ".[dev]"
# or
uv pip install -e ".[dev]"
```

**Frontend:**
```bash
cd client
npm install
# or
pnpm install

# Install Playwright browsers
npx playwright install
```

### Run All Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend Unit/Integration:**
```bash
cd client
npm test
```

**Frontend E2E:**
```bash
cd client
npm run test:e2e
```

## Backend Testing

### Test Coverage

1. **Models Tests** (`tests/unit/test_models.py`)
   - TravelDates model validation
   - TravelPlanRequest with defaults
   - TravelPlanAgentRequest
   - TravelPlanResponse
   - DayByDayPlan
   - Attraction, FlightResult, RestaurantResult
   - TravelPlanTeamResponse
   - TaskStatus enum

2. **Repository Tests** (`tests/unit/test_repositories.py`)
   - Create plan task
   - Update task status (success/error)
   - Get task by ID
   - Get tasks by trip plan
   - Get tasks by status
   - Handle not found scenarios

3. **API Tests** (`tests/integration/test_api.py`)
   - Health check endpoint
   - Trip planning trigger (success/failure)
   - Request validation
   - Error handling
   - CORS middleware
   - Background task creation

### Running Backend Tests

```bash
cd backend

# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/unit/test_models.py

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Backend Test Markers

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests

## Frontend Testing

### Test Coverage

1. **Utils Tests** (`__tests__/lib/utils.test.ts`)
   - Class name merging
   - Conditional classes
   - Tailwind merge conflicts
   - Edge cases (empty, null, undefined)

2. **Component Tests** (`__tests__/components/ui/button.test.tsx`)
   - Rendering
   - Click events
   - All variants (default, destructive, outline, secondary, ghost, link)
   - All sizes (default, sm, lg, icon)
   - Disabled state
   - Custom className
   - Props forwarding

3. **API Route Tests** (`__tests__/app/api/plan/submit/route.test.ts`)
   - Successful submission
   - Validation errors
   - Database errors
   - Backend API errors
   - Data transformation
   - Request payload validation

### Running Frontend Tests

```bash
cd client

# All Jest tests
npm test

# Watch mode
npm run test:watch

# With coverage
npm run test:coverage

# Specific test file
npm test -- __tests__/lib/utils.test.ts

# Update snapshots
npm test -- -u
```

## E2E Testing

### Test Coverage

1. **Trip Planning Flow** (`e2e/trip-planning.spec.ts`)
   - Home page display
   - Navigation to planning form
   - Form filling with valid data
   - Required field validation
   - Form submission
   - Loading states
   - Error handling

2. **Trip Plan Viewing**
   - Display plan details
   - List all plans

3. **Responsive Design**
   - Mobile viewport
   - Tablet viewport

### Running E2E Tests

```bash
cd client

# All E2E tests
npm run test:e2e

# With UI mode (recommended for development)
npm run test:e2e:ui

# Debug mode
npm run test:e2e:debug

# Specific browser
npx playwright test --project=chromium

# Headed mode (see browser)
npx playwright test --headed

# Specific test file
npx playwright test e2e/trip-planning.spec.ts

# View last test report
npx playwright show-report
```

### E2E Test Projects

- chromium (Desktop Chrome)
- firefox (Desktop Firefox)
- webkit (Desktop Safari)
- Mobile Chrome (Pixel 5)
- Mobile Safari (iPhone 12)

## Running All Tests

### Complete Test Suite

**Option 1: Sequential**
```bash
# Terminal 1 - Backend
cd backend
pytest

# Terminal 2 - Frontend Unit/Integration
cd client
npm test

# Terminal 3 - Frontend E2E
cd client
npm run test:e2e
```

**Option 2: Create a test script**

Create `run_all_tests.sh`:
```bash
#!/bin/bash

echo "🧪 Running Backend Tests..."
cd backend
pytest -v
BACKEND_EXIT=$?

echo ""
echo "🧪 Running Frontend Unit/Integration Tests..."
cd ../client
npm test -- --passWithNoTests
FRONTEND_EXIT=$?

echo ""
echo "🧪 Running E2E Tests..."
npm run test:e2e
E2E_EXIT=$?

echo ""
echo "📊 Test Results Summary"
echo "======================="
echo "Backend: $([ $BACKEND_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "Frontend: $([ $FRONTEND_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "E2E: $([ $E2E_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"

exit $(($BACKEND_EXIT + $FRONTEND_EXIT + $E2E_EXIT))
```

Make it executable and run:
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd client
          npm ci
      - name: Run tests
        run: |
          cd client
          npm test -- --coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd client
          npm ci
          npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd client
          npm run test:e2e
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: client/playwright-report/
```

## Best Practices

### General Testing Principles

1. **Write tests before fixing bugs** - Reproduce the bug with a test first
2. **Keep tests independent** - Each test should run in isolation
3. **Test behavior, not implementation** - Focus on what the code does, not how
4. **Use descriptive test names** - Should explain what is being tested
5. **Follow AAA pattern** - Arrange, Act, Assert
6. **Mock external dependencies** - Don't make real API calls in unit tests
7. **Clean up after tests** - Reset state between tests

### Backend Testing Best Practices

```python
# Good: Descriptive test name
def test_create_plan_task_with_valid_data():
    pass

# Good: Mock external dependencies
@patch('repository.plan_task_repository.get_db_session')
async def test_update_task_status(mock_session):
    pass

# Good: Test edge cases
def test_task_status_case_insensitive():
    assert TaskStatus._missing_("QUEUED") == TaskStatus.queued
```

### Frontend Testing Best Practices

```typescript
// Good: Test user interaction
it('handles click events', async () => {
  const handleClick = jest.fn()
  render(<Button onClick={handleClick}>Click</Button>)
  await userEvent.click(screen.getByRole('button'))
  expect(handleClick).toHaveBeenCalledTimes(1)
})

// Good: Use accessible queries
screen.getByRole('button', { name: /submit/i })

// Avoid: Testing implementation details
// Don't test internal state or private methods
```

### E2E Testing Best Practices

```typescript
// Good: Use page object pattern for complex tests
class TripPlanPage {
  async fillTripDetails(data) {
    await this.page.fill('[name="destination"]', data.destination)
  }
}

// Good: Mock API responses for faster tests
await page.route('**/api/**', route => route.fulfill({...}))

// Good: Take screenshots on failure (configured in playwright.config.ts)
```

## Test Maintenance

### When to Update Tests

1. **When features change** - Update corresponding tests
2. **When bugs are fixed** - Add regression tests
3. **When APIs change** - Update API tests and mocks
4. **When UI changes** - Update E2E tests and snapshots
5. **When dependencies update** - Verify tests still pass

### Debugging Failed Tests

**Backend:**
```bash
# Run single test with output
pytest tests/unit/test_models.py::test_name -s

# Debug with pdb
pytest --pdb
```

**Frontend:**
```bash
# Debug single test
npm test -- --testNamePattern="button handles click"

# Node debugging
node --inspect-brk node_modules/.bin/jest --runInBand
```

**E2E:**
```bash
# Debug mode with inspector
npm run test:e2e:debug

# View trace
npx playwright show-trace trace.zip
```

## Coverage Goals

- **Backend**: Aim for >80% code coverage
- **Frontend**: Aim for >75% code coverage
- **E2E**: Cover all critical user journeys

## Troubleshooting

### Common Issues

1. **Import errors**: Check Python path (backend) or tsconfig paths (frontend)
2. **Database errors**: Ensure test database is configured
3. **Flaky E2E tests**: Add proper wait conditions, avoid hardcoded sleeps
4. **Timeout errors**: Increase timeout in configuration files
5. **Mock issues**: Verify mock setup and cleanup

## Additional Resources

- [Backend Tests README](./backend/tests/README.md)
- [Frontend Tests README](./client/TEST_README.md)
- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [Playwright Documentation](https://playwright.dev/)
- [React Testing Library](https://testing-library.com/react)

---

**Happy Testing! 🧪**
