import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

test.describe('Payment Flows', () => {
  test.beforeEach(async ({ page }) => {
    // Add to cart and go to checkout
    await page.goto(`${BASE_URL}/`);
    const productLink = page.locator('a[href*="/san-pham/"]').first();
    await productLink.click();
    
    const sizeBtn = page.locator('[data-variant-size]').first();
    if (await sizeBtn.isVisible()) {
      await sizeBtn.click();
    }
    
    await page.click('button:has-text("Thêm vào giỏ"), button[name="add_to_cart"]');
    await page.waitForTimeout(1000);
    await page.goto(`${BASE_URL}/thanh-toan/`);
    
    // Fill minimum required fields
    await page.fill('input[name="customer_name"]', 'Test User');
    await page.fill('input[name="customer_email"]', 'test@example.com');
    await page.fill('input[name="phone"]', '0901234567');
    await page.fill('textarea[name="shipping_address"]', '123 Test Street');
  });

  test('should process COD order', async ({ page }) => {
    await page.fill('input[name="customer_name"]', 'Test COD');
    await page.fill('input[name="customer_email"]', 'cod@test.com');
    await page.fill('input[name="phone"]', '0901234567');
    await page.fill('textarea[name="shipping_address"]', '123 COD Street');
    
    // Select COD
    const codRadio = page.locator('input[name="payment_method"][value="cod"]');
    if (await codRadio.isVisible()) {
      await codRadio.check();
    }
    
    await page.click('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Đặt hàng")');
    
    // Should redirect to success page
    await expect(page).toHaveURL(/\/dat-hang-thanh-cong\//);
  });

  test('should process bank transfer', async ({ page }) => {
    await page.fill('input[name="customer_name"]', 'Test Bank');
    await page.fill('input[name="customer_email"]', 'bank@test.com');
    await page.fill('input[name="phone"]', '0901234567');
    await page.fill('textarea[name="shipping_address"]', '123 Bank Street');
    
    // Select bank transfer
    const bankRadio = page.locator('input[name="payment_method"][value="bank"]');
    if (await bankRadio.isVisible()) {
      await bankRadio.check();
    }
    
    // Select bank if dropdown
    const bankSelect = page.locator('select[name="bank_code"]');
    if (await bankSelect.isVisible()) {
      await bankSelect.selectOption({ index: 1 });
    }
    
    await page.click('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Đặt hàng")');
    
    // Should redirect to bank payment waiting page
    await expect(page).toHaveURL(/\/cho-thanh-toan-ngan-hang\//);
  });

  test('should show QR code for bank transfer', async ({ page }) => {
    await page.fill('input[name="customer_name"]', 'Test QR');
    await page.fill('input[name="customer_email"]', 'qr@test.com');
    await page.fill('input[name="phone"]', '0901234567');
    await page.fill('textarea[name="shipping_address"]', '123 QR Street');
    
    const bankRadio = page.locator('input[name="payment_method"][value="bank"]');
    if (await bankRadio.isVisible()) {
      await bankRadio.check();
    }
    
    await page.click('button[type="submit"]:has-text("Đặt hàng")');
    await expect(page).toHaveURL(/\/cho-thanh-toan-ngan-hang\//);
    
    // Click view QR
    await page.click('a:has-text("QR"), a[href*="qr-thanh-toan"]');
    
    await expect(page.locator('img[src*="qr"], canvas, .qr-code')).toBeVisible({ timeout: 5000 });
  });
});