import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

test.describe('Cart & Checkout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    // Add a product to cart first
    await page.goto(`${BASE_URL}/`);
    const productLink = page.locator('a[href*="/san-pham/"]').first();
    await productLink.click();
    
    const sizeBtn = page.locator('[data-variant-size]').first();
    if (await sizeBtn.isVisible()) {
      await sizeBtn.click();
    }
    
    await page.click('button:has-text("Thêm vào giỏ"), button[name="add_to_cart"], button:has-text("Mua ngay")');
    await page.waitForTimeout(1000);
  });

  test('should display cart summary', async ({ page }) => {
    await page.goto(`${BASE_URL}/gio-hang/`);
    await expect(page.locator('.cart-items, .cart-table, .cart-items-list')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.cart-total, .total-amount')).toBeVisible();
  });

  test('should update quantity', async ({ page }) => {
    await page.goto(`${BASE_URL}/gio-hang/`);
    
    const qtyInput = page.locator('input[name="quantity"], input[type="number"]').first();
    if (await qtyInput.isVisible()) {
      await qtyInput.fill('2');
      await page.click('button:has-text("Cập nhật"), button:has-text("Cập nhật giỏ")');
      await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should remove item from cart', async ({ page }) => {
    await page.goto(`${BASE_URL}/gio-hang/`);
    
    const removeBtn = page.locator('button:has-text("Xóa"), a:has-text("Xóa"), button[name="remove"]').first();
    if (await removeBtn.isVisible()) {
      await removeBtn.click();
      await expect(page.locator('.alert-success, .toast-success, .cart-empty')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should proceed to checkout', async ({ page }) => {
    await page.goto(`${BASE_URL}/gio-hang/`);
    await page.click('a:has-text("Thanh toán"), button:has-text("Thanh toán"), a[href*="thanh-toan"]');
    
    await expect(page).toHaveURL(/\/thanh-toan\//);
    await expect(page.locator('form')).toBeVisible();
  });

  test('should fill checkout form', async ({ page }) => {
    await page.goto(`${BASE_URL}/thanh-toan/`);
    
    // Fill required fields
    await page.fill('input[name="customer_name"]', 'Test User');
    await page.fill('input[name="customer_email"]', 'test@example.com');
    await page.fill('input[name="phone"]', '0901234567');
    await page.fill('textarea[name="shipping_address"], input[name="shipping_address"]', '123 Test Street, District 1, HCMC');
    
    // Select payment method
    const codRadio = page.locator('input[name="payment_method"][value="cod"]');
    if (await codRadio.isVisible()) {
      await codRadio.check();
    }
    
    // Submit
    await page.click('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Đặt hàng")');
    
    // Should redirect to success or payment page
    await expect(page).not.toHaveURL(/\/thanh-toan\//);
  });
});