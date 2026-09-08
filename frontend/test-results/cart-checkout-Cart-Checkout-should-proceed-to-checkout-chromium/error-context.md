# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: cart-checkout.spec.ts >> Cart & Checkout >> should proceed to checkout
- Location: tests\cart-checkout.spec.ts:49:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('form')
Expected: visible
Error: strict mode violation: locator('form') resolved to 6 elements:
    1) <form action="/" method="get" class="site-nav-search">…</form> aka getByRole('navigation', { name: 'Điều hướng chính' }).locator('form')
    2) <form action="/" method="get" autocomplete="off" class="header-search" id="header-search-form" data-suggest-url="/tim-kiem/goi-y/">…</form> aka locator('#header-search-form')
    3) <form method="post" class="auth-form">…</form> aka getByText('Email hoặc số điện thoại Mật')
    4) <form method="post" class="footer-newsletter" action="/nhan-tin/dang-ky/">…</form> aka getByRole('contentinfo').locator('form')
    5) <form id="chatbox-form" class="chatbox-form">…</form> aka locator('#chatbox-form')
    6) <form method="post" id="exit-popup-form" class="exit-popup-form" action="/nhan-tin/dang-ky/">…</form> aka getByText('Email Nhận mã ưu đãi')

Call log:
  - Expect "toBeVisible" locator('form') with timeout 5000ms
  - waiting for locator('form')

```

# Page snapshot

```yaml
- generic [active] [ref=f4e1]:
  - generic [ref=f4e2]:
    - text: Chào mùa mới —
    - strong [ref=f4e3]: giảm thêm 10%
    - text: cho đơn từ 800K, mã
    - strong [ref=f4e4]: FREESHIP20K
    - text: · Freeship toàn quốc từ 499K
  - banner [ref=f4e5]:
    - generic [ref=f4e6]:
      - generic [ref=f4e7]:
        - button "Menu" [ref=f4e8] [cursor=pointer]
        - generic [ref=f4e10]:
          - link "Trang chủ" [ref=f4e11] [cursor=pointer]:
            - /url: /
            - text: HUUGIAU
          - generic [ref=f4e12]: ATELIER / FASHION STUDIO
      - navigation "Điều hướng chính" [ref=f4e13]:
        - generic [ref=f4e14]:
          - generic [ref=f4e15]:
            - link "HUUGIAU" [ref=f4e16] [cursor=pointer]:
              - /url: /
            - button "Đóng menu" [ref=f4e17] [cursor=pointer]
          - textbox "Tìm kiếm..." [ref=f4e24]
          - generic [ref=f4e25]:
            - generic [ref=f4e26]: Danh mục
            - link "New in" [ref=f4e27] [cursor=pointer]:
              - /url: /?sort=newest
            - link "Áo" [ref=f4e31] [cursor=pointer]:
              - /url: /?category=ao
            - link "Quần" [ref=f4e35] [cursor=pointer]:
              - /url: /?category=quan
            - link "Phụ kiện" [ref=f4e41] [cursor=pointer]:
              - /url: /?category=phu-kien
            - link "Lookbook" [ref=f4e44] [cursor=pointer]:
              - /url: /lookbook/
          - generic [ref=f4e49]:
            - generic [ref=f4e50]: Cửa hàng
            - link "Câu chuyện thương hiệu" [ref=f4e51] [cursor=pointer]:
              - /url: /ve-chung-toi/
            - link "Khuyến mãi" [ref=f4e54] [cursor=pointer]:
              - /url: /khuyen-mai/
            - link "Liên hệ" [ref=f4e57] [cursor=pointer]:
              - /url: /lien-he/
            - link "Chính sách đổi trả" [ref=f4e61] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
            - link "Hỏi đáp" [ref=f4e65] [cursor=pointer]:
              - /url: /hoi-dap-chung/
          - generic [ref=f4e69]:
            - generic [ref=f4e70]: Tài khoản
            - link "Đăng nhập" [ref=f4e71] [cursor=pointer]:
              - /url: /dang-nhap/
            - link "Đăng ký" [ref=f4e75] [cursor=pointer]:
              - /url: /dang-ky/
          - link "Giỏ hàng 1" [ref=f4e79] [cursor=pointer]:
            - /url: /gio-hang/
            - text: Giỏ hàng
            - generic [ref=f4e83]: "1"
          - generic [ref=f4e84]: HUUGIAU Atelier © 2026
      - generic [ref=f4e85]:
        - generic [ref=f4e86]:
          - text: 
          - textbox "Tìm áo, quần, phụ kiện..." [ref=f4e87]
        - link "Giỏ hàng" [ref=f4e88] [cursor=pointer]:
          - /url: /gio-hang/
          - generic [aria-hidden] [ref=f4e89]: 
          - generic [ref=f4e90]: "1"
        - link "Yêu thích" [ref=f4e91] [cursor=pointer]:
          - /url: /yeu-thich/
          - generic [aria-hidden] [ref=f4e92]: 
        - group [ref=f4e93]:
          - generic "Tài khoản" [ref=f4e94] [cursor=pointer]:
            - generic [aria-hidden] [ref=f4e95]: 
            - generic [aria-hidden] [ref=f4e97]: 
  - main [ref=f4e98]:
    - generic [ref=f4e99]:
      - generic [ref=f4e100]:
        - generic [ref=f4e101]:
          - generic [ref=f4e102]: 
          - heading "Chào mừng quay lại" [level=1] [ref=f4e104]
          - paragraph [ref=f4e105]: Dùng email hoặc số điện thoại đã đăng ký để vào tài khoản nhanh hơn.
        - generic [ref=f4e106]:
          - generic [ref=f4e107]:
            - generic [ref=f4e108]:
              - generic [ref=f4e109]: 
              - text: Email hoặc số điện thoại
            - textbox " Email hoặc số điện thoại" [ref=f4e110]:
              - /placeholder: Nhập email hoặc số điện thoại
          - generic [ref=f4e111]:
            - generic [ref=f4e112]:
              - generic [ref=f4e113]: 
              - text: Mật khẩu
            - textbox " Mật khẩu" [ref=f4e114]:
              - /placeholder: Nhập mật khẩu
            - link "Quên mật khẩu?" [ref=f4e115] [cursor=pointer]:
              - /url: /quen-mat-khau/
          - button " Đăng nhập" [ref=f4e116] [cursor=pointer]:
            - generic [ref=f4e117]: 
            - text: Đăng nhập
        - generic [ref=f4e118]:
          - paragraph [ref=f4e119]: Hoặc tiếp tục bằng
          - generic [ref=f4e120]:
            - link "Google" [ref=f4e121] [cursor=pointer]:
              - /url: /dang-nhap/google/?next=/thanh-toan/
              - generic [aria-hidden] [ref=f4e122]: 
            - link "Facebook" [ref=f4e124] [cursor=pointer]:
              - /url: /dang-nhap/facebook/?next=/thanh-toan/
              - generic [aria-hidden] [ref=f4e125]: 
            - link "Apple" [ref=f4e127] [cursor=pointer]:
              - /url: /dang-nhap/apple/?next=/thanh-toan/
              - generic [aria-hidden] [ref=f4e128]: 
        - paragraph [ref=f4e130]:
          - text: Chưa có tài khoản?
          - link "Đăng ký ngay" [ref=f4e131] [cursor=pointer]:
            - /url: /dang-ky/
      - complementary [ref=f4e132]:
        - generic [ref=f4e133]:
          - generic [ref=f4e134]:
            - generic [ref=f4e135]: 
            - generic [ref=f4e136]: HUUGIAU Atelier
          - heading "Đăng nhập để tiếp tục mua sắm nhanh hơn" [level=2] [ref=f4e137]
          - paragraph [ref=f4e138]: Mở tài khoản để xem đơn hàng, lưu wishlist và thanh toán thuận tiện trên mọi thiết bị.
        - list [ref=f4e139]:
          - listitem [ref=f4e140]:
            - generic [ref=f4e141]: 
            - text: Đơn hàng của tôi
          - listitem [ref=f4e142]:
            - generic [ref=f4e143]: 
            - text: Danh sách yêu thích
          - listitem [ref=f4e144]:
            - generic [ref=f4e145]: 
            - text: Theo dõi thanh toán
          - listitem [ref=f4e146]:
            - generic [ref=f4e147]: 
            - text: Tư vấn size ngay trên web
  - contentinfo [ref=f4e148]:
    - generic [ref=f4e149]:
      - generic [ref=f4e150]:
        - heading "HUUGIAU Atelier" [level=3] [ref=f4e151]
        - paragraph [ref=f4e152]: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
        - paragraph [ref=f4e153]:
          - generic [aria-hidden] [ref=f4e154]: 
          - text: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
        - generic [ref=f4e155]:
          - link "Instagram" [ref=f4e156] [cursor=pointer]:
            - /url: https://www.instagram.com/
            - generic [aria-hidden] [ref=f4e157]: 
          - link "Facebook" [ref=f4e158] [cursor=pointer]:
            - /url: https://www.facebook.com/
            - generic [aria-hidden] [ref=f4e159]: 
          - link "TikTok" [ref=f4e160] [cursor=pointer]:
            - /url: https://www.tiktok.com/
            - generic [aria-hidden] [ref=f4e161]: 
        - generic [ref=f4e162]:
          - textbox "Email nhận tin" [ref=f4e163]:
            - /placeholder: Nhận tin khuyến mãi...
          - button "" [ref=f4e164] [cursor=pointer]
      - generic [ref=f4e166]:
        - heading "Hỗ trợ" [level=3] [ref=f4e167]
        - list [ref=f4e168]:
          - listitem [ref=f4e169]:
            - link "Tra cứu đơn hàng" [ref=f4e170] [cursor=pointer]:
              - /url: /tra-cuu-don/
          - listitem [ref=f4e171]:
            - link "Đơn hàng của tôi" [ref=f4e172] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
          - listitem [ref=f4e173]:
            - link "Chính sách đổi trả" [ref=f4e174] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
          - listitem [ref=f4e175]:
            - link "Hướng dẫn chọn size" [ref=f4e176] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f4e177]:
            - link "Chất liệu & bảo quản" [ref=f4e178] [cursor=pointer]:
              - /url: /chat-lieu-bao-quan/
          - listitem [ref=f4e179]:
            - link "Khuyến mãi" [ref=f4e180] [cursor=pointer]:
              - /url: /khuyen-mai/
          - listitem [ref=f4e181]:
            - link "Câu hỏi thường gặp" [ref=f4e182] [cursor=pointer]:
              - /url: /hoi-dap-chung/
        - paragraph [ref=f4e183]:
          - text: "Hotline:"
          - link "0932047365" [ref=f4e184] [cursor=pointer]:
            - /url: tel:0932047365
          - text: · 9:00–21:30 mỗi ngày
      - generic [ref=f4e185]:
        - heading "Danh mục" [level=3] [ref=f4e186]
        - list [ref=f4e187]:
          - listitem [ref=f4e188]:
            - link "Áo" [ref=f4e189] [cursor=pointer]:
              - /url: /?category=ao
          - listitem [ref=f4e190]:
            - link "Quần" [ref=f4e191] [cursor=pointer]:
              - /url: /?category=quan
          - listitem [ref=f4e192]:
            - link "Phụ kiện" [ref=f4e193] [cursor=pointer]:
              - /url: /?category=phu-kien
          - listitem [ref=f4e194]:
            - link "Hàng mới về" [ref=f4e195] [cursor=pointer]:
              - /url: /?sort=newest
          - listitem [ref=f4e196]:
            - link "Tất cả sản phẩm" [ref=f4e197] [cursor=pointer]:
              - /url: /
      - generic [ref=f4e198]:
        - heading "Về HUUGIAU" [level=3] [ref=f4e199]
        - list [ref=f4e200]:
          - listitem [ref=f4e201]:
            - link "Câu chuyện thương hiệu" [ref=f4e202] [cursor=pointer]:
              - /url: /ve-chung-toi/
          - listitem [ref=f4e203]:
            - link "Hướng dẫn chọn size" [ref=f4e204] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f4e205]:
            - link "Tuyển dụng" [ref=f4e206] [cursor=pointer]:
              - /url: /tuyen-dung/
          - listitem [ref=f4e207]:
            - link "Liên hệ" [ref=f4e208] [cursor=pointer]:
              - /url: /lien-he/
          - listitem [ref=f4e209]:
            - link "Lookbook" [ref=f4e210] [cursor=pointer]:
              - /url: /lookbook/
    - generic [ref=f4e211]:
      - generic [ref=f4e212]:
        - generic [ref=f4e213]:
          - generic [ref=f4e214]: © 2026 HUUGIAU Atelier
          - link "Chính sách bảo mật" [ref=f4e215] [cursor=pointer]:
            - /url: /chinh-sach-bao-mat/
          - link "Điều khoản" [ref=f4e216] [cursor=pointer]:
            - /url: /dieu-khoan/
        - generic [ref=f4e217]:
          - generic "Visa" [ref=f4e218]: 
          - generic "Mastercard" [ref=f4e219]: 
          - generic "PayPal" [ref=f4e220]: 
          - generic "Chuyển khoản ngân hàng" [ref=f4e221]: 
          - generic "COD" [ref=f4e222]: 
      - generic [ref=f4e223]: "MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
  - button "Mở hỗ trợ mua hàng" [ref=f4e224] [cursor=pointer]:
    - generic [aria-hidden] [ref=f4e225]: 
  - dialog [aria-hidden] [ref=f4e226]:
    - generic [ref=f4e227]:
      - heading [level=3] [ref=f4e228]: Giỏ hàng (0)
      - button [ref=f4e229] [cursor=pointer]: ×
    - generic [ref=f4e231]:
      - generic [ref=f4e232]:
        - generic [ref=f4e233]: Tạm tính
        - strong [ref=f4e234]: 0đ
      - generic [ref=f4e235]:
        - link [ref=f4e236] [cursor=pointer]:
          - /url: /gio-hang/
          - text: Xem giỏ hàng
        - link [ref=f4e237] [cursor=pointer]:
          - /url: /thanh-toan/
          - text: Thanh toán
  - text: 
  - dialog [ref=f4e238]:
    - generic [ref=f4e239]:
      - generic [ref=f4e240]:
        - strong [ref=f4e241]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=f4e242]:
        - button "Tùy chỉnh" [ref=f4e243] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=f4e244] [cursor=pointer]
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
  24 |     await expect(page.locator('.cart-items, .cart-table, .cart-items-list')).toBeVisible({ timeout: 10000 });
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
> 54 |     await expect(page.locator('form')).toBeVisible();
     |                                        ^ Error: expect(locator).toBeVisible() failed
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