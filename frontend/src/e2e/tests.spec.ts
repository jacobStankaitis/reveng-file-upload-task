import { test, expect } from '@playwright/test';

test('page renders', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('File Upload Demo')).toBeVisible();
});
