import { test, expect } from './fixtures';

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
    await expect(page.locator('.cart-list .cart-item').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.cart-summary .summary-line.total')).toBeVisible();
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
    
    await page.locator('button[aria-label="Xóa sản phẩm"]').first().click();
    await expect(page.getByRole('heading', { name: 'Giỏ hàng đang trống' })).toBeVisible({ timeout: 5000 });
  });

  test('should proceed to checkout', async ({ page }) => {
    await page.goto(`${BASE_URL}/gio-hang/`);
    await page.click('a[href^="/dang-nhap/"][href*="next="]');
    await expect(page).toHaveURL(/\/dang-nhap\//);
    await page.fill('input[name="username"]', 'nguyenvanA');
    await page.fill('input[name="password"]', 'user123');
    await page.locator('form.auth-form button[type="submit"]').click();
    
    await expect(page).toHaveURL(/\/thanh-toan\//);
    await expect(page.locator('form.checkout-form')).toBeVisible();
  });

  test('should fill checkout form', async ({ page }) => {
    await page.goto(`${BASE_URL}/thanh-toan/`);
    
    // Fill required fields
    await page.fill('input[name="customer_name"]', 'Test User');
    await page.fill('input[name="customer_email"]', 'test@example.com');
    await page.fill('input[name="phone"]', '0901234567');
    await page.fill('textarea[name="shipping_address"], input[name="shipping_address"]', '123 Test Street, District 1, HCMC');
    
    // Select payment method
    await page.selectOption('select[name="payment_method"]', 'cod');
    
    // Submit
    await page.click('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Đặt hàng")');
    
    // Should redirect to success or payment page
    await expect(page).not.toHaveURL(/\/thanh-toan\//);
  });
});
