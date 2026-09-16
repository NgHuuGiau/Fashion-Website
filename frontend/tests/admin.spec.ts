import { test, expect } from './fixtures';

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
    
    await expect(page.locator('.adm-kpi-card').first()).toBeVisible({ timeout: 10000 });
  });

  test('should filter orders', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    await page.locator('[data-target="admin-orders"]').click();
    const statusSelect = page.locator('select[name="order_status"]');
    if (await statusSelect.isVisible()) {
      await statusSelect.selectOption('delivered');
      await expect(page).toHaveURL(/order_status=delivered/);
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
    await page.locator('[data-target="admin-orders"]').click();
    const statusForm = page.locator('form.admin-quick-form:visible').filter({
      has: page.locator('input[name="action"][value="update_order_status"]'),
    }).first();
    await expect(statusForm).toBeVisible();
    await statusForm.locator('select[name="new_status"]').selectOption('shipping');
    const responsePromise = page.waitForResponse((response) =>
      response.request().method() === 'POST' && response.url().includes('/admin-dashboard/'),
    );
    await statusForm.locator('button[type="submit"]').click();
    expect((await responsePromise).status()).toBe(302);
  });

  test('should print invoice', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    await page.locator('[data-target="admin-orders"]').click();
    const invoiceLink = page.locator('a[href*="/admin-dashboard/in-hoa-don/"]:visible').first();
    await expect(invoiceLink).toHaveAttribute('target', '_blank');
    await expect(invoiceLink).toHaveAttribute('href', /\/in-hoa-don\//);
  });
});
