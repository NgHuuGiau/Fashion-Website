import { test, expect } from './fixtures';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

test.describe('Product Browsing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
  });

  test('should display home page with products', async ({ page }) => {
    await expect(page.locator('.hero-shell h1')).toBeVisible({ timeout: 10000 });
  });

  test('should navigate to product detail', async ({ page }) => {
    // Click first product link
    const productLink = page.locator('a[href*="/san-pham/"]').first();
    await expect(productLink).toBeVisible();
    await productLink.click();
    
    // Should be on product detail page
    await expect(page).toHaveURL(/\/san-pham\/\d+\//);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should display product images', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    const productLink = page.locator('a[href*="/san-pham/"]').first();
    await productLink.click();
    
    // Main image should be visible
    await expect(page.locator('#detail-main-image, .product-image img')).toBeVisible();
  });

  test('should select variant (color/size)', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    const productLink = page.locator('a[href*="/san-pham/"]').first();
    await productLink.click();
    
    // Wait for variant picker
    await page.waitForSelector('[data-variant-color], [data-variant-size]', { timeout: 5000 });
    
    // Click first color if available
    const colorBtn = page.locator('[data-variant-color]').first();
    if (await colorBtn.isVisible()) {
      await colorBtn.click();
    }
    
    // Click first size if available
    const sizeBtn = page.locator('[data-variant-size]').first();
    if (await sizeBtn.isVisible()) {
      await sizeBtn.click();
    }
    
    // Variant ID should be set
    const variantInput = page.locator('#variant-id-input');
    await expect(variantInput).toHaveValue(/\d+/);
  });

  test('should add to cart', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    const productLink = page.locator('a[href*="/san-pham/"]').first();
    await productLink.click();
    
    // Select variant if needed
    const sizeBtn = page.locator('[data-variant-size]').first();
    if (await sizeBtn.isVisible()) {
      await sizeBtn.click();
    }
    
    // Click add to cart
    await page.click('button:has-text("Thêm vào giỏ"), button[name="add_to_cart"], button:has-text("Mua ngay")');
    
    // Should show success message or redirect to cart
    await expect(page.locator('.alert-success, .toast-success, .cart-count, .icon-count')).toBeVisible({ timeout: 5000 });
  });

  test('should filter by category', async ({ page }) => {
    // Click category link if available
    await page.locator('a.collection-card-ao').click();
    await expect(page).toHaveURL(/\?category=ao/);
  });

  test('should search products', async ({ page }) => {
    const searchInput = page.locator('input[name="q"], input[placeholder*="tìm"], input[placeholder*="search"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('áo');
      await searchInput.press('Enter');
      await expect(page).toHaveURL(/[?&]q=/);
    }
  });
});
