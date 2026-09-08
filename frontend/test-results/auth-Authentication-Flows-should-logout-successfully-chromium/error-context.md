# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Authentication Flows >> should logout successfully
- Location: tests\auth.spec.ts:34:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('a[href*="dang-xuat"], button[onclick*="logout"]')

```

# Page snapshot

```yaml
- generic [active] [ref=f1e1]: Quá nhiều lần đăng nhập. Vui lòng thử lại sau 5 phút.
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
  4  | 
  5  | test.describe('Authentication Flows', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     await page.goto(`${BASE_URL}/dang-nhap/`);
  8  |   });
  9  | 
  10 |   test('should display login form', async ({ page }) => {
  11 |     await expect(page.locator('form')).toBeVisible();
  12 |     await expect(page.locator('input[name="username"]')).toBeVisible();
  13 |     await expect(page.locator('input[name="password"]')).toBeVisible();
  14 |     await expect(page.locator('button[type="submit"]')).toBeVisible();
  15 |   });
  16 | 
  17 |   test('should show error for invalid credentials', async ({ page }) => {
  18 |     await page.fill('input[name="username"]', 'invalid');
  19 |     await page.fill('input[name="password"]', 'wrong');
  20 |     await page.click('button[type="submit"]');
  21 |     await expect(page.locator('.alert-danger, .error, .messages .error')).toBeVisible();
  22 |   });
  23 | 
  24 |   test('should login successfully with valid credentials', async ({ page }) => {
  25 |     // Assuming test user exists: testuser / TestPass123!
  26 |     await page.fill('input[name="username"]', 'testuser');
  27 |     await page.fill('input[name="password"]', 'TestPass123!');
  28 |     await page.click('button[type="submit"]');
  29 |     
  30 |     // Should redirect to home or account page
  31 |     await expect(page).not.toHaveURL(/\/dang-nhap\//);
  32 |   });
  33 | 
  34 |   test('should logout successfully', async ({ page }) => {
  35 |     // Login first
  36 |     await page.fill('input[name="username"]', 'testuser');
  37 |     await page.fill('input[name="password"]', 'TestPass123!');
  38 |     await page.click('button[type="submit"]');
  39 |     
  40 |     // Click logout
> 41 |     await page.click('a[href*="dang-xuat"], button[onclick*="logout"]');
     |                ^ Error: page.click: Test timeout of 30000ms exceeded.
  42 |     
  43 |     // Should redirect to home
  44 |     await expect(page).toHaveURL(/\/$/);
  45 |   });
  46 | 
  47 |   test('should register new user', async ({ page }) => {
  48 |     await page.goto(`${BASE_URL}/dang-ky/`);
  49 |     
  50 |     const uniqueUser = `testuser_${Date.now()}`;
  51 |     await page.fill('input[name="username"]', uniqueUser);
  52 |     await page.fill('input[name="email"]', `${uniqueUser}@test.com`);
  53 |     await page.fill('input[name="password1"]', 'TestPass123!');
  54 |     await page.fill('input[name="password2"]', 'TestPass123!');
  55 |     
  56 |     // Fill required fields
  57 |     await page.fill('input[name="first_name"]', 'Test');
  58 |     await page.fill('input[name="last_name"]', 'User');
  59 |     
  60 |     await page.click('button[type="submit"]');
  61 |     
  62 |     // Should redirect after successful registration
  63 |     await expect(page).not.toHaveURL(/\/dang-ky\//);
  64 |   });
  65 | });
```