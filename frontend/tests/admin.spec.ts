import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto(`${BASE_URL}/dang-nhap/`);
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/^(?!.*dang-nhap).*/);
  });

  test('should access admin dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    await expect(page.locator('h1')).toContainText(/Dashboard|Bảng điều khiển|Admin/);
  });

  test('should display order statistics', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    
    await expect(page.locator('.stat-card, .stats-grid, .stat-value')).toBeVisible({ timeout: 10000 });
  });

  test('should filter orders', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    
    const statusSelect = page.locator('select[name="status"], select#status');
    if (await statusSelect.isVisible()) {
      await statusSelect.selectOption('delivered');
      await page.click('button:has-text("Lọc"), button:has-text("Tìm kiếm")');
      await page.waitForTimeout(1000);
    }
  });

  test('should export orders CSV', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    
    const exportBtn = page.locator('a[href*="xuat-don"], button:has-text("Xuất đơn")');
    if (await exportBtn.isVisible()) {
      const downloadPromise = page.waitForEvent('download');
      await exportBtn.click();
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.csv$/);
    }
  });

  test('should change order status', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    
    const firstOrder = page.locator('tr[data-order-id], .order-row').first();
    if (await firstOrder.isVisible()) {
      await firstOrder.click();
      
      const statusSelect = page.locator('select[name="new_status"], select[name="status"]');
      if (await statusSelect.isVisible()) {
        await statusSelect.selectOption('shipping');
        await page.click('button:has-text("Cập nhật"), button:has-text("Lưu")');
        await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should print invoice', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    
    const invoiceLink = page.locator('a[href*="in-hoa-don"], a:has-text("In")').first();
    if (await invoiceLink.isVisible()) {
      const newPagePromise = page.waitForEvent('popup');
      await invoiceLink.click();
      const newPage = await newPagePromise;
      await expect(newPage).toHaveURL(/\/in-hoa-don\//);
    }
  });
});