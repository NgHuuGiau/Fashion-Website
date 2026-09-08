# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: account.spec.ts >> User Account >> should add address
- Location: tests\account.spec.ts:46:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('input[name="username"]')
    - locator resolved to <input type="text" required="" name="username" id="id_username" placeholder="Nhập email hoặc số điện thoại"/>
    - fill("testuser")
  - attempting fill action
    - waiting for element to be visible, enabled and editable

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
  4  | 
  5  | test.describe('User Account', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     // Login first
  8  |     await page.goto(`${BASE_URL}/dang-nhap/`);
> 9  |     await page.fill('input[name="username"]', 'testuser');
     |                ^ Error: page.fill: Test timeout of 30000ms exceeded.
  10 |     await page.fill('input[name="password"]', 'TestPass123!');
  11 |     await page.click('button[type="submit"]');
  12 |     await page.waitForURL(/^(?!.*dang-nhap).*/);
  13 |   });
  14 | 
  15 |   test('should access profile page', async ({ page }) => {
  16 |     await page.goto(`${BASE_URL}/tai-khoan/`);
  17 |     await expect(page.locator('h1, h2')).toContainText(/Tài khoản|Profile|Tài khoản của bạn/);
  18 |   });
  19 | 
  20 |   test('should display order history', async ({ page }) => {
  21 |     await page.goto(`${BASE_URL}/don-hang-cua-toi/`);
  22 |     await expect(page.locator('.orders-list, .order-history, table')).toBeVisible({ timeout: 10000 });
  23 |   });
  24 | 
  25 |   test('should view order detail', async ({ page }) => {
  26 |     await page.goto(`${BASE_URL}/don-hang-cua-toi/`);
  27 |     
  28 |     const orderLink = page.locator('a[href*="/don-hang/"][href*="/xem-lai/"]').first();
  29 |     if (await orderLink.isVisible()) {
  30 |       await orderLink.click();
  31 |       await expect(page).toHaveURL(/\/don-hang\/\d+\/xem-lai\//);
  32 |       await expect(page.locator('.order-detail, .order-info')).toBeVisible();
  33 |     }
  34 |   });
  35 | 
  36 |   test('should update profile', async ({ page }) => {
  37 |     await page.goto(`${BASE_URL}/tai-khoan/`);
  38 |     
  39 |     await page.fill('input[name="first_name"]', 'Updated');
  40 |     await page.fill('input[name="last_name"]', 'Name');
  41 |     await page.click('button[type="submit"]:has-text("Lưu"), button:has-text("Cập nhật")');
  42 |     
  43 |     await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  44 |   });
  45 | 
  46 |   test('should add address', async ({ page }) => {
  47 |     await page.goto(`${BASE_URL}/tai-khoan/`);
  48 |     
  49 |     // Navigate to addresses
  50 |     await page.click('a[href*="dia-chi"], a:has-text("Địa chỉ")');
  51 |     
  52 |     await page.click('a:has-text("Thêm"), button:has-text("Thêm địa chỉ")');
  53 |     
  54 |     await page.fill('input[name="recipient_name"]', 'Test Recipient');
  55 |     await page.fill('input[name="phone"]', '0901234567');
  56 |     await page.fill('textarea[name="address"], input[name="address"]', '456 New Street, District 2, HCMC');
  57 |     
  58 |     await page.click('button[type="submit"]:has-text("Lưu"), button:has-text("Thêm")');
  59 |     
  60 |     await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  61 |   });
  62 | 
  63 |   test('should change password', async ({ page }) => {
  64 |     await page.goto(`${BASE_URL}/tai-khoan/doi-mat-khau/`);
  65 |     
  66 |     await page.fill('input[name="old_password"]', 'TestPass123!');
  67 |     await page.fill('input[name="new_password1"]', 'NewPass123!');
  68 |     await page.fill('input[name="new_password2"]', 'NewPass123!');
  69 |     
  70 |     await page.click('button[type="submit"]');
  71 |     
  72 |     await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  73 |   });
  74 | });
```