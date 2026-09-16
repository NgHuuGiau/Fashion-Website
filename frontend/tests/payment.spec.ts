import { test, expect } from './fixtures';

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
    await page.selectOption('select[name="payment_method"]', 'cod');
    
    await page.click('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Đặt hàng")');
    
    // Should redirect to success page
    await expect(page).toHaveURL(/\/dat-hang-thanh-cong\//);
  });

  test('should hide bank transfer until real account details are configured', async ({ page }) => {
    const paymentSelect = page.locator('select[name="payment_method"]');
    await expect(paymentSelect.locator('option[value="bank"]')).toHaveCount(0);
  });

  test('should hide VNPay until merchant credentials are configured', async ({ page }) => {
    const paymentSelect = page.locator('select[name="payment_method"]');
    await expect(paymentSelect.locator('option[value="vnpay"]')).toHaveCount(0);
    await expect(paymentSelect.locator('option[value="cod"]')).toHaveCount(1);
  });
});
