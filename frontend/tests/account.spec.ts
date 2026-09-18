import { test, expect } from './fixtures';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

test.describe('User Account', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto(`${BASE_URL}/dang-nhap/`);
    await page.fill('input[name="username"]', 'nguyenvanA');
    await page.fill('input[name="password"]', 'user123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/^(?!.*dang-nhap).*/);
  });

  test('should access profile page', async ({ page }) => {
    await page.goto(`${BASE_URL}/tai-khoan/`);
    await expect(page.getByRole('heading', { name: 'Thông tin cá nhân' })).toBeVisible();
  });

  test('should display order history', async ({ page }) => {
    await page.goto(`${BASE_URL}/don-hang-cua-toi/`);
    await expect(page.locator('.order-list, .empty-state')).toBeVisible({ timeout: 10000 });
  });

  test('should view order detail', async ({ page }) => {
    await page.goto(`${BASE_URL}/don-hang-cua-toi/`);
    
    const orderLink = page.locator('a[href*="/don-hang/"][href*="/xem-lai/"]').first();
    if (await orderLink.isVisible()) {
      await orderLink.click();
      await expect(page).toHaveURL(/\/don-hang\/\d+\/xem-lai\//);
      await expect(page.locator('.review-main')).toBeVisible();
    }
  });

  test('should update profile', async ({ page }) => {
    await page.goto(`${BASE_URL}/tai-khoan/`);
    
    await page.fill('input[name="first_name"]', 'Updated');
    await page.fill('input[name="last_name"]', 'Name');
    await page.click('button[type="submit"]:has-text("Lưu"), button:has-text("Cập nhật")');
    
    await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  });

  test('should add address', async ({ page }) => {
    await page.goto(`${BASE_URL}/tai-khoan/`);
    
    await page.click('#addr-toggle');
    
    await page.fill('input[name="recipient_name"]', 'Test Recipient');
    await page.fill('input[name="phone"]', '0901234567');
    await page.fill('textarea[name="address"], input[name="address"]', '456 New Street, District 2, HCMC');
    
    await page.click('#addr-form button[type="submit"]');
    
    await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  });

  test('should display the change-password form', async ({ page }) => {
    await page.goto(`${BASE_URL}/tai-khoan/doi-mat-khau/`);
    await expect(page.locator('input[name="current_password"]')).toBeVisible();
    await expect(page.locator('input[name="new_password1"]')).toBeVisible();
    await expect(page.locator('input[name="new_password2"]')).toBeVisible();
  });
});
