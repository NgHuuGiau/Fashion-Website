# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: cart-checkout.spec.ts >> Cart & Checkout >> should display cart summary
- Location: tests\cart-checkout.spec.ts:22:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: expect(locator).toBeVisible() failed

Locator: locator('.cart-items, .cart-table, .cart-items-list')
Expected: visible
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('.cart-items, .cart-table, .cart-items-list') with timeout 10000ms
  - waiting for locator('.cart-items, .cart-table, .cart-items-list')
  - Test timeout of 30000ms exceeded.

```

```yaml
- text: Chào mùa mới —
- strong: giảm thêm 10%
- text: cho đơn từ 800K, mã
- strong: FREESHIP20K
- text: · Freeship toàn quốc từ 499K
- banner:
  - button "Menu":
    - img
  - link "Trang chủ":
    - /url: /
    - text: HUUGIAU
  - text: ATELIER / FASHION STUDIO
  - navigation "Điều hướng chính":
    - link "HUUGIAU":
      - /url: /
    - button "Đóng menu":
      - img
    - img
    - textbox "Tìm kiếm..."
    - text: Danh mục
    - link "New in":
      - /url: /?sort=newest
      - img
      - text: New in
    - link "Áo":
      - /url: /?category=ao
      - img
      - text: Áo
    - link "Quần":
      - /url: /?category=quan
      - img
      - text: Quần
    - link "Phụ kiện":
      - /url: /?category=phu-kien
      - img
      - text: Phụ kiện
    - link "Lookbook":
      - /url: /lookbook/
      - img
      - text: Lookbook
    - text: Cửa hàng
    - link "Câu chuyện thương hiệu":
      - /url: /ve-chung-toi/
      - img
      - text: Câu chuyện thương hiệu
    - link "Khuyến mãi":
      - /url: /khuyen-mai/
      - img
      - text: Khuyến mãi
    - link "Liên hệ":
      - /url: /lien-he/
      - img
      - text: Liên hệ
    - link "Chính sách đổi trả":
      - /url: /chinh-sach-doi-tra/
      - img
      - text: Chính sách đổi trả
    - link "Hỏi đáp":
      - /url: /hoi-dap-chung/
      - img
      - text: Hỏi đáp
    - text: Tài khoản
    - link "Đăng nhập":
      - /url: /dang-nhap/
      - img
      - text: Đăng nhập
    - link "Đăng ký":
      - /url: /dang-ky/
      - img
      - text: Đăng ký
    - link "Giỏ hàng 1":
      - /url: /gio-hang/
      - img
      - text: Giỏ hàng 1
    - text: HUUGIAU Atelier © 2026
  - text: 
  - textbox "Tìm áo, quần, phụ kiện..."
  - link "Giỏ hàng":
    - /url: /gio-hang/
    - text: "1"
  - link "Yêu thích":
    - /url: /yeu-thich/
  - group: Tài khoản
- main:
  - navigation "Bạn đang ở":
    - link "Trang chủ":
      - /url: /
    - text: / Giỏ hàng
  - paragraph: Giỏ hàng
  - heading "Giỏ hàng của bạn" [level=1]
  - paragraph: Kiểm tra số lượng, tổng tiền và sang checkout trong một bước.
  - link "Tiếp tục mua":
    - /url: /
  - article:
    - link "Quần jeans Baggy Fade Blue":
      - /url: /san-pham/3/jeans-baggy-fade-blue/
      - img "Quần jeans Baggy Fade Blue"
    - paragraph: Quần
    - heading "Quần jeans Baggy Fade Blue" [level=3]:
      - link "Quần jeans Baggy Fade Blue":
        - /url: /san-pham/3/jeans-baggy-fade-blue/
    - paragraph: Màu Den · Size L
    - button "Xóa sản phẩm"
    - button "Giảm số lượng": "-"
    - spinbutton: "1"
    - button "Tăng số lượng": +
    - button "Cập nhật"
    - strong: 590.000đ
  - complementary:
    - paragraph: Tóm tắt
    - paragraph:
      - text: Bạn đã được
      - strong: miễn phí vận chuyển
      - text: "! 🎉"
    - text: Tạm tính
    - strong: 590.000đ
    - text: Phí vận chuyển
    - strong: 0đ
    - paragraph: Bạn đã được miễn phí vận chuyển cho đơn từ 499.000đ.
    - text: Tổng tiền
    - strong: 590.000đ
    - button "Xóa toàn bộ giỏ"
    - link "Đăng nhập để thanh toán":
      - /url: /dang-nhap/?next=/thanh-toan/
- contentinfo:
  - heading "HUUGIAU Atelier" [level=3]
  - paragraph: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
  - paragraph: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
  - link "Instagram":
    - /url: https://www.instagram.com/
  - link "Facebook":
    - /url: https://www.facebook.com/
  - link "TikTok":
    - /url: https://www.tiktok.com/
  - textbox "Email nhận tin":
    - /placeholder: Nhận tin khuyến mãi...
  - button ""
  - heading "Hỗ trợ" [level=3]
  - list:
    - listitem:
      - link "Tra cứu đơn hàng":
        - /url: /tra-cuu-don/
    - listitem:
      - link "Đơn hàng của tôi":
        - /url: /don-hang-cua-toi/
    - listitem:
      - link "Chính sách đổi trả":
        - /url: /chinh-sach-doi-tra/
    - listitem:
      - link "Hướng dẫn chọn size":
        - /url: /huong-dan-chon-size/
    - listitem:
      - link "Chất liệu & bảo quản":
        - /url: /chat-lieu-bao-quan/
    - listitem:
      - link "Khuyến mãi":
        - /url: /khuyen-mai/
    - listitem:
      - link "Câu hỏi thường gặp":
        - /url: /hoi-dap-chung/
  - paragraph:
    - text: "Hotline:"
    - link "0932047365":
      - /url: tel:0932047365
    - text: · 9:00–21:30 mỗi ngày
  - heading "Danh mục" [level=3]
  - list:
    - listitem:
      - link "Áo":
        - /url: /?category=ao
    - listitem:
      - link "Quần":
        - /url: /?category=quan
    - listitem:
      - link "Phụ kiện":
        - /url: /?category=phu-kien
    - listitem:
      - link "Hàng mới về":
        - /url: /?sort=newest
    - listitem:
      - link "Tất cả sản phẩm":
        - /url: /
  - heading "Về HUUGIAU" [level=3]
  - list:
    - listitem:
      - link "Câu chuyện thương hiệu":
        - /url: /ve-chung-toi/
    - listitem:
      - link "Hướng dẫn chọn size":
        - /url: /huong-dan-chon-size/
    - listitem:
      - link "Tuyển dụng":
        - /url: /tuyen-dung/
    - listitem:
      - link "Liên hệ":
        - /url: /lien-he/
    - listitem:
      - link "Lookbook":
        - /url: /lookbook/
  - text: © 2026 HUUGIAU Atelier
  - link "Chính sách bảo mật":
    - /url: /chinh-sach-bao-mat/
  - link "Điều khoản":
    - /url: /dieu-khoan/
  - text: "     MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
- button "Mở hỗ trợ mua hàng"
- dialog:
  - strong: Chúng tôi sử dụng cookie
  - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
  - button "Tùy chỉnh"
  - button "Chấp nhận tất cả"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
  4  | 
  5  | test.describe('Cart & Checkout', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     await page.goto(`${BASE_URL}/`);
  8  |     // Add a product to cart first
  9  |     await page.goto(`${BASE_URL}/`);
  10 |     const productLink = page.locator('a[href*="/san-pham/"]').first();
  11 |     await productLink.click();
  12 |     
  13 |     const sizeBtn = page.locator('[data-variant-size]').first();
  14 |     if (await sizeBtn.isVisible()) {
  15 |       await sizeBtn.click();
  16 |     }
  17 |     
  18 |     await page.click('button:has-text("Thêm vào giỏ"), button[name="add_to_cart"], button:has-text("Mua ngay")');
  19 |     await page.waitForTimeout(1000);
  20 |   });
  21 | 
  22 |   test('should display cart summary', async ({ page }) => {
  23 |     await page.goto(`${BASE_URL}/gio-hang/`);
> 24 |     await expect(page.locator('.cart-items, .cart-table, .cart-items-list')).toBeVisible({ timeout: 10000 });
     |                                                                              ^ Error: expect(locator).toBeVisible() failed
  25 |     await expect(page.locator('.cart-total, .total-amount')).toBeVisible();
  26 |   });
  27 | 
  28 |   test('should update quantity', async ({ page }) => {
  29 |     await page.goto(`${BASE_URL}/gio-hang/`);
  30 |     
  31 |     const qtyInput = page.locator('input[name="quantity"], input[type="number"]').first();
  32 |     if (await qtyInput.isVisible()) {
  33 |       await qtyInput.fill('2');
  34 |       await page.click('button:has-text("Cập nhật"), button:has-text("Cập nhật giỏ")');
  35 |       await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  36 |     }
  37 |   });
  38 | 
  39 |   test('should remove item from cart', async ({ page }) => {
  40 |     await page.goto(`${BASE_URL}/gio-hang/`);
  41 |     
  42 |     const removeBtn = page.locator('button:has-text("Xóa"), a:has-text("Xóa"), button[name="remove"]').first();
  43 |     if (await removeBtn.isVisible()) {
  44 |       await removeBtn.click();
  45 |       await expect(page.locator('.alert-success, .toast-success, .cart-empty')).toBeVisible({ timeout: 5000 });
  46 |     }
  47 |   });
  48 | 
  49 |   test('should proceed to checkout', async ({ page }) => {
  50 |     await page.goto(`${BASE_URL}/gio-hang/`);
  51 |     await page.click('a:has-text("Thanh toán"), button:has-text("Thanh toán"), a[href*="thanh-toan"]');
  52 |     
  53 |     await expect(page).toHaveURL(/\/thanh-toan\//);
  54 |     await expect(page.locator('form')).toBeVisible();
  55 |   });
  56 | 
  57 |   test('should fill checkout form', async ({ page }) => {
  58 |     await page.goto(`${BASE_URL}/thanh-toan/`);
  59 |     
  60 |     // Fill required fields
  61 |     await page.fill('input[name="customer_name"]', 'Test User');
  62 |     await page.fill('input[name="customer_email"]', 'test@example.com');
  63 |     await page.fill('input[name="phone"]', '0901234567');
  64 |     await page.fill('textarea[name="shipping_address"], input[name="shipping_address"]', '123 Test Street, District 1, HCMC');
  65 |     
  66 |     // Select payment method
  67 |     const codRadio = page.locator('input[name="payment_method"][value="cod"]');
  68 |     if (await codRadio.isVisible()) {
  69 |       await codRadio.check();
  70 |     }
  71 |     
  72 |     // Submit
  73 |     await page.click('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Đặt hàng")');
  74 |     
  75 |     // Should redirect to success or payment page
  76 |     await expect(page).not.toHaveURL(/\/thanh-toan\//);
  77 |   });
  78 | });
```