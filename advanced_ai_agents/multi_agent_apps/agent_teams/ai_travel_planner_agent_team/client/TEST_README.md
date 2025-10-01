# Frontend Tests

This directory contains the test suite for the TripCraft AI frontend (Next.js application).

## Test Structure

```
client/
├── __tests__/            # Jest unit and integration tests
│   ├── lib/              # Utility function tests
│   ├── components/       # Component tests
│   └── app/api/          # API route tests
├── e2e/                  # Playwright E2E tests
│   └── trip-planning.spec.ts
├── jest.config.js        # Jest configuration
├── jest.setup.js         # Jest setup file
└── playwright.config.ts  # Playwright configuration
```

## Setup

1. Install dependencies:
```bash
npm install
# or
pnpm install
```

2. Set up environment variables (create a `.env.test` or `.env.local` file):
```bash
BACKEND_API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@localhost:5432/test_db
```

3. For Playwright E2E tests, install browsers:
```bash
npx playwright install
```

## Running Tests

### Jest (Unit & Integration Tests)

Run all Jest tests:
```bash
npm test
# or
pnpm test
```

Run tests in watch mode:
```bash
npm run test:watch
```

Run tests with coverage:
```bash
npm run test:coverage
```

Run specific test file:
```bash
npm test -- __tests__/lib/utils.test.ts
```

### Playwright (E2E Tests)

Run all E2E tests:
```bash
npm run test:e2e
# or
pnpm test:e2e
```

Run E2E tests with UI:
```bash
npm run test:e2e:ui
```

Run E2E tests in debug mode:
```bash
npm run test:e2e:debug
```

Run specific browser:
```bash
npx playwright test --project=chromium
```

Run specific test file:
```bash
npx playwright test e2e/trip-planning.spec.ts
```

## Test Types

### Unit Tests
- **Location**: `__tests__/lib/`, `__tests__/components/`
- **Purpose**: Test individual functions and components in isolation
- **Tools**: Jest, React Testing Library
- **Example**: Testing utility functions, button components

### Integration Tests
- **Location**: `__tests__/app/api/`
- **Purpose**: Test API routes and their interactions
- **Tools**: Jest with Node environment
- **Example**: Testing form submission API routes

### E2E Tests
- **Location**: `e2e/`
- **Purpose**: Test complete user journeys
- **Tools**: Playwright
- **Example**: Testing full trip planning flow from form to submission

## Coverage

After running Jest with coverage:
```bash
npm run test:coverage
```

View the coverage report:
```bash
open coverage/lcov-report/index.html  # macOS
start coverage/lcov-report/index.html # Windows
xdg-open coverage/lcov-report/index.html # Linux
```

## E2E Test Reports

Playwright generates HTML reports automatically. After running E2E tests:
```bash
npx playwright show-report
```

## Writing New Tests

### Jest Tests

```typescript
import { render, screen } from '@testing-library/react'
import { MyComponent } from '@/components/MyComponent'

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

### Playwright E2E Tests

```typescript
import { test, expect } from '@playwright/test'

test('should complete user journey', async ({ page }) => {
  await page.goto('/')
  await page.click('text=Start Planning')
  await expect(page).toHaveURL('/plan')
})
```

## Mocking

### Mock API calls in Jest:
```typescript
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: async () => ({ success: true })
  })
)
```

### Mock API calls in Playwright:
```typescript
await page.route('**/api/plan/submit', async route => {
  await route.fulfill({
    status: 200,
    body: JSON.stringify({ success: true })
  })
})
```

## CI/CD

Tests are configured to run in CI/CD pipelines:
- Jest tests run on every commit
- Playwright tests run on pull requests
- Coverage reports are generated automatically

## Troubleshooting

### Jest Tests Failing
1. Clear Jest cache: `npm test -- --clearCache`
2. Check environment variables in `jest.setup.js`
3. Ensure all dependencies are installed

### Playwright Tests Failing
1. Ensure dev server is running (Playwright config handles this)
2. Check browser installations: `npx playwright install`
3. View trace files for failed tests in `test-results/`

### Import Path Issues
- Use `@/` alias for imports (configured in tsconfig.json)
- Check `moduleNameMapper` in jest.config.js

### TypeScript Errors
- Ensure `@types/jest` and `@playwright/test` types are installed
- Check tsconfig.json includes test files

## Best Practices

1. **Keep tests focused**: One test should test one thing
2. **Use descriptive names**: Test names should clearly describe what they test
3. **Mock external dependencies**: Don't make real API calls in unit tests
4. **Clean up after tests**: Use `afterEach` hooks to reset state
5. **Use data-testid sparingly**: Prefer accessible queries (getByRole, getByLabel)
6. **Test user behavior**: Test what users do, not implementation details
7. **Run tests before commits**: Use pre-commit hooks if desired

## Additional Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [Next.js Testing](https://nextjs.org/docs/testing)
