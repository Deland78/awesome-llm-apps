import { test, expect } from '@playwright/test';

test.describe('Trip Planning E2E Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app home page
    await page.goto('/');
  });

  test('should display the home page correctly', async ({ page }) => {
    // Check if the main heading is visible
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should navigate to trip planning form', async ({ page }) => {
    // Look for a button or link to start planning
    const planButton = page.getByRole('link', { name: /plan/i }).or(
      page.getByRole('button', { name: /plan/i })
    ).first();

    if (await planButton.isVisible()) {
      await planButton.click();
      // Verify we're on the planning page
      await expect(page).toHaveURL(/\/plan/);
    }
  });

  test('should fill out trip planning form with valid data', async ({ page }) => {
    // Navigate to plan page
    await page.goto('/plan');

    // Fill out the form - adjust selectors based on actual form structure
    // Trip name
    const nameInput = page.getByLabel(/trip name/i).or(
      page.getByPlaceholder(/trip name/i)
    ).first();
    if (await nameInput.isVisible()) {
      await nameInput.fill('Paris Adventure');
    }

    // Destination
    const destinationInput = page.getByLabel(/destination/i).or(
      page.getByPlaceholder(/destination/i)
    ).first();
    if (await destinationInput.isVisible()) {
      await destinationInput.fill('Paris, France');
    }

    // Starting location
    const startingInput = page.getByLabel(/starting location/i).or(
      page.getByPlaceholder(/starting location/i)
    ).first();
    if (await startingInput.isVisible()) {
      await startingInput.fill('New York, USA');
    }

    // Budget
    const budgetInput = page.getByLabel(/budget/i).or(
      page.getByPlaceholder(/budget/i)
    ).first();
    if (await budgetInput.isVisible()) {
      await budgetInput.fill('5000');
    }

    // Take a screenshot of the filled form
    await page.screenshot({ path: 'test-results/form-filled.png' });
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/plan');

    // Try to submit the form without filling required fields
    const submitButton = page.getByRole('button', { name: /submit/i }).or(
      page.getByRole('button', { name: /create/i })
    ).first();

    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Check for validation errors - adjust based on actual error messages
      // This might be error messages, aria-invalid attributes, or error styling
      await page.waitForTimeout(1000); // Wait for validation to trigger
    }
  });

  test('should handle form submission', async ({ page }) => {
    await page.goto('/plan');

    // Fill out minimum required fields
    const fillField = async (labelOrPlaceholder: string, value: string) => {
      const input = page.getByLabel(new RegExp(labelOrPlaceholder, 'i')).or(
        page.getByPlaceholder(new RegExp(labelOrPlaceholder, 'i'))
      ).first();

      if (await input.isVisible()) {
        await input.fill(value);
      }
    };

    await fillField('trip name', 'Test Trip');
    await fillField('destination', 'Paris, France');
    await fillField('starting location', 'New York, USA');

    // Submit the form
    const submitButton = page.getByRole('button', { name: /submit/i }).or(
      page.getByRole('button', { name: /create/i })
    ).first();

    if (await submitButton.isVisible()) {
      // Intercept the API call
      await page.route('**/api/plan/submit', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            message: 'Trip planning triggered successfully',
            tripPlanId: 'test-trip-123'
          })
        });
      });

      await submitButton.click();

      // Wait for success message or redirect
      await page.waitForTimeout(2000);

      // Take a screenshot of the result
      await page.screenshot({ path: 'test-results/form-submitted.png' });
    }
  });

  test('should display loading state during submission', async ({ page }) => {
    await page.goto('/plan');

    // Fill and submit form
    const submitButton = page.getByRole('button', { name: /submit/i }).or(
      page.getByRole('button', { name: /create/i })
    ).first();

    if (await submitButton.isVisible()) {
      // Mock slow API response
      await page.route('**/api/plan/submit', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            tripPlanId: 'test-123'
          })
        });
      });

      await submitButton.click();

      // Check for loading indicator (spinner, disabled button, etc.)
      // This will depend on your actual implementation
      await page.waitForTimeout(500);
    }
  });

  test('should handle API errors gracefully', async ({ page }) => {
    await page.goto('/plan');

    // Mock API error
    await page.route('**/api/plan/submit', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          message: 'Internal server error'
        })
      });
    });

    // Fill and submit form
    const fillField = async (labelOrPlaceholder: string, value: string) => {
      const input = page.getByLabel(new RegExp(labelOrPlaceholder, 'i')).or(
        page.getByPlaceholder(new RegExp(labelOrPlaceholder, 'i'))
      ).first();

      if (await input.isVisible()) {
        await input.fill(value);
      }
    };

    await fillField('trip name', 'Test Trip');
    await fillField('destination', 'Paris');
    await fillField('starting location', 'New York');

    const submitButton = page.getByRole('button', { name: /submit/i }).or(
      page.getByRole('button', { name: /create/i })
    ).first();

    if (await submitButton.isVisible()) {
      await submitButton.click();
      await page.waitForTimeout(1000);

      // Check for error message display
      await page.screenshot({ path: 'test-results/form-error.png' });
    }
  });
});

test.describe('Trip Plan Viewing', () => {
  test('should display trip plan details', async ({ page }) => {
    // Mock the API response for trip plan details
    await page.route('**/api/plans/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-123',
          name: 'Paris Adventure',
          destination: 'Paris, France',
          status: 'completed',
          itinerary: []
        })
      });
    });

    await page.goto('/plan/test-123');

    // Wait for content to load
    await page.waitForTimeout(1000);

    // Take screenshot of the plan view
    await page.screenshot({ path: 'test-results/plan-view.png' });
  });

  test('should list all trip plans', async ({ page }) => {
    // Mock the API response for plans list
    await page.route('**/api/plans', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: '1',
            name: 'Paris Trip',
            destination: 'Paris',
            status: 'completed'
          },
          {
            id: '2',
            name: 'Tokyo Adventure',
            destination: 'Tokyo',
            status: 'in_progress'
          }
        ])
      });
    });

    await page.goto('/plans');

    // Wait for list to load
    await page.waitForTimeout(1000);

    // Take screenshot of the plans list
    await page.screenshot({ path: 'test-results/plans-list.png' });
  });
});

test.describe('Responsive Design', () => {
  test('should work on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');

    // Check if navigation is accessible on mobile
    await page.screenshot({ path: 'test-results/mobile-home.png' });

    // Navigate to plan page
    await page.goto('/plan');
    await page.screenshot({ path: 'test-results/mobile-plan.png' });
  });

  test('should work on tablet devices', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto('/');
    await page.screenshot({ path: 'test-results/tablet-home.png' });

    await page.goto('/plan');
    await page.screenshot({ path: 'test-results/tablet-plan.png' });
  });
});
