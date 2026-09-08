# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin.spec.ts >> Admin Dashboard >> should access admin dashboard
- Location: tests\admin.spec.ts:15:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('input[name="password"]')
    - locator resolved to <input required="" type="password" name="password" id="id_password" placeholder="Nhập mật khẩu"/>

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
  4  | 
  5  | test.describe('Admin Dashboard', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     // Login as admin
  8  |     await page.goto(`${BASE_URL}/dang-nhap/`);
  9  |     await page.fill('input[name="username"]', 'admin');
> 10 |     await page.fill('input[name="password"]', 'admin123');
     |                ^ Error: page.fill: Test timeout of 30000ms exceeded.
  11 |     await page.click('button[type="submit"]');
  12 |     await page.waitForURL(/^(?!.*dang-nhap).*/);
  13 |   });
  14 | 
  15 |   test('should access admin dashboard', async ({ page }) => {
  16 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  17 |     await expect(page.locator('h1')).toContainText(/Dashboard|Bảng điều khiển|Admin/);
  18 |   });
  19 | 
  20 |   test('should display order statistics', async ({ page }) => {
  21 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  22 |     
  23 |     await expect(page.locator('.stat-card, .stats-grid, .stat-value')).toBeVisible({ timeout: 10000 });
  24 |   });
  25 | 
  26 |   test('should filter orders', async ({ page }) => {
  27 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  28 |     
  29 |     const statusSelect = page.locator('select[name="status"], select#status');
  30 |     if (await statusSelect.isVisible()) {
  31 |       await statusSelect.selectOption('delivered');
  32 |       await page.click('button:has-text("Lọc"), button:has-text("Tìm kiếm")');
  33 |       await page.waitForTimeout(1000);
  34 |     }
  35 |   });
  36 | 
  37 |   test('should export orders CSV', async ({ page }) => {
  38 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  39 |     
  40 |     const exportBtn = page.locator('a[href*="xuat-don"], button:has-text("Xuất đơn")');
  41 |     if (await exportBtn.isVisible()) {
  42 |       const downloadPromise = page.waitForEvent('download');
  43 |       await exportBtn.click();
  44 |       const download = await downloadPromise;
  45 |       expect(download.suggestedFilename()).toMatch(/\.csv$/);
  46 |     }
  47 |   });
  48 | 
  49 |   test('should change order status', async ({ page }) => {
  50 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  51 |     
  52 |     const firstOrder = page.locator('tr[data-order-id], .order-row').first();
  53 |     if (await firstOrder.isVisible()) {
  54 |       await firstOrder.click();
  55 |       
  56 |       const statusSelect = page.locator('select[name="new_status"], select[name="status"]');
  57 |       if (await statusSelect.isVisible()) {
  58 |         await statusSelect.selectOption('shipping');
  59 |         await page.click('button:has-text("Cập nhật"), button:has-text("Lưu")');
  60 |         await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  61 |       }
  62 |     }
  63 |   });
  64 | 
  65 |   test('should print invoice', async ({ page }) => {
  66 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  67 |     
  68 |     const invoiceLink = page.locator('a[href*="in-hoa-don"], a:has-text("In")').first();
  69 |     if (await invoiceLink.isVisible()) {
  70 |       const newPagePromise = page.waitForEvent('popup');
  71 |       await invoiceLink.click();
  72 |       const newPage = await newPagePromise;
  73 |       await expect(newPage).toHaveURL(/\/in-hoa-don\//);
  74 |     }
  75 |   });
  76 | });
```