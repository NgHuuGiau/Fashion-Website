import { test, expect } from './fixtures';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

test.describe('Authentication Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/dang-nhap/`);
  });

  test('should display login form', async ({ page }) => {
    await expect(page.locator('form.auth-form')).toBeVisible();
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('form.auth-form button[type="submit"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('input[name="username"]', 'invalid');
    await page.fill('input[name="password"]', 'wrong');
    await page.click('button[type="submit"]');
    await expect(page.locator('#toast-container .toast-error')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.fill('input[name="username"]', 'nguyenvanA');
    await page.fill('input[name="password"]', 'user123');
    await page.click('button[type="submit"]');
    
    // Should redirect to home or account page
    await expect(page).not.toHaveURL(/\/dang-nhap\//);
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[name="username"]', 'nguyenvanA');
    await page.fill('input[name="password"]', 'user123');
    await page.click('button[type="submit"]');
    
    // Click logout
    await page.locator('details.account-menu summary').click();
    await page.locator('details.account-menu a[href="/dang-xuat/"]').click();
    
    // Should redirect to home
    await expect(page).toHaveURL(/\/$/);
  });

  test('should register new user', async ({ page }) => {
    await page.goto(`${BASE_URL}/dang-ky/`);
    
    const uniqueUser = `testuser_${Date.now()}`;
    await page.fill('input[name="username"]', uniqueUser);
    await page.fill('input[name="email"]', `${uniqueUser}@test.com`);
    await page.fill('input[name="password1"]', 'TestPass123!');
    await page.fill('input[name="password2"]', 'TestPass123!');
    
    // Fill required fields
    await page.fill('input[name="first_name"]', 'Test');
    await page.fill('input[name="last_name"]', 'User');
    
    await page.click('button[type="submit"]');
    
    // Should redirect after successful registration
    await expect(page).not.toHaveURL(/\/dang-ky\//);
  });
});
