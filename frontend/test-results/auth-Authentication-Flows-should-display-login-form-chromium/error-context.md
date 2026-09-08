# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Authentication Flows >> should display login form
- Location: tests\auth.spec.ts:10:7

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
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - text: Chào mùa mới —
    - strong [ref=e3]: giảm thêm 10%
    - text: cho đơn từ 800K, mã
    - strong [ref=e4]: FREESHIP20K
    - text: · Freeship toàn quốc từ 499K
  - banner [ref=e5]:
    - generic [ref=e6]:
      - generic [ref=e7]:
        - button "Menu" [ref=e8] [cursor=pointer]
        - generic [ref=e10]:
          - link "Trang chủ" [ref=e11] [cursor=pointer]:
            - /url: /
            - text: HUUGIAU
          - generic [ref=e12]: ATELIER / FASHION STUDIO
      - navigation "Điều hướng chính" [ref=e13]:
        - generic [ref=e14]:
          - generic [ref=e15]:
            - link "HUUGIAU" [ref=e16] [cursor=pointer]:
              - /url: /
            - button "Đóng menu" [ref=e17] [cursor=pointer]
          - textbox "Tìm kiếm..." [ref=e24]
          - generic [ref=e25]:
            - generic [ref=e26]: Danh mục
            - link "New in" [ref=e27] [cursor=pointer]:
              - /url: /?sort=newest
            - link "Áo" [ref=e31] [cursor=pointer]:
              - /url: /?category=ao
            - link "Quần" [ref=e35] [cursor=pointer]:
              - /url: /?category=quan
            - link "Phụ kiện" [ref=e41] [cursor=pointer]:
              - /url: /?category=phu-kien
            - link "Lookbook" [ref=e44] [cursor=pointer]:
              - /url: /lookbook/
          - generic [ref=e49]:
            - generic [ref=e50]: Cửa hàng
            - link "Câu chuyện thương hiệu" [ref=e51] [cursor=pointer]:
              - /url: /ve-chung-toi/
            - link "Khuyến mãi" [ref=e54] [cursor=pointer]:
              - /url: /khuyen-mai/
            - link "Liên hệ" [ref=e57] [cursor=pointer]:
              - /url: /lien-he/
            - link "Chính sách đổi trả" [ref=e61] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
            - link "Hỏi đáp" [ref=e65] [cursor=pointer]:
              - /url: /hoi-dap-chung/
          - generic [ref=e69]:
            - generic [ref=e70]: Tài khoản
            - link "Đăng nhập" [ref=e71] [cursor=pointer]:
              - /url: /dang-nhap/
            - link "Đăng ký" [ref=e75] [cursor=pointer]:
              - /url: /dang-ky/
          - link "Giỏ hàng" [ref=e79] [cursor=pointer]:
            - /url: /gio-hang/
          - generic [ref=e83]: HUUGIAU Atelier © 2026
      - generic [ref=e84]:
        - generic [ref=e85]:
          - text: 
          - textbox "Tìm áo, quần, phụ kiện..." [ref=e86]
        - link "Giỏ hàng" [ref=e87] [cursor=pointer]:
          - /url: /gio-hang/
          - generic [aria-hidden] [ref=e88]: 
          - generic [ref=e89]: "0"
        - link "Yêu thích" [ref=e90] [cursor=pointer]:
          - /url: /yeu-thich/
          - generic [aria-hidden] [ref=e91]: 
        - group [ref=e92]:
          - generic "Tài khoản" [ref=e93] [cursor=pointer]:
            - generic [aria-hidden] [ref=e94]: 
            - generic [aria-hidden] [ref=e96]: 
  - main [ref=e97]:
    - generic [ref=e98]:
      - generic [ref=e99]:
        - generic [ref=e100]:
          - generic [ref=e101]: 
          - heading "Chào mừng quay lại" [level=1] [ref=e103]
          - paragraph [ref=e104]: Dùng email hoặc số điện thoại đã đăng ký để vào tài khoản nhanh hơn.
        - generic [ref=e105]:
          - generic [ref=e106]:
            - generic [ref=e107]:
              - generic [ref=e108]: 
              - text: Email hoặc số điện thoại
            - textbox " Email hoặc số điện thoại" [ref=e109]:
              - /placeholder: Nhập email hoặc số điện thoại
          - generic [ref=e110]:
            - generic [ref=e111]:
              - generic [ref=e112]: 
              - text: Mật khẩu
            - textbox " Mật khẩu" [ref=e113]:
              - /placeholder: Nhập mật khẩu
            - link "Quên mật khẩu?" [ref=e114] [cursor=pointer]:
              - /url: /quen-mat-khau/
          - button " Đăng nhập" [ref=e115] [cursor=pointer]:
            - generic [ref=e116]: 
            - text: Đăng nhập
        - generic [ref=e117]:
          - paragraph [ref=e118]: Hoặc tiếp tục bằng
          - generic [ref=e119]:
            - link "Google" [ref=e120] [cursor=pointer]:
              - /url: /dang-nhap/google/?next=
              - generic [aria-hidden] [ref=e121]: 
            - link "Facebook" [ref=e123] [cursor=pointer]:
              - /url: /dang-nhap/facebook/?next=
              - generic [aria-hidden] [ref=e124]: 
            - link "Apple" [ref=e126] [cursor=pointer]:
              - /url: /dang-nhap/apple/?next=
              - generic [aria-hidden] [ref=e127]: 
        - paragraph [ref=e129]:
          - text: Chưa có tài khoản?
          - link "Đăng ký ngay" [ref=e130] [cursor=pointer]:
            - /url: /dang-ky/
      - complementary [ref=e131]:
        - generic [ref=e132]:
          - generic [ref=e133]:
            - generic [ref=e134]: 
            - generic [ref=e135]: HUUGIAU Atelier
          - heading "Đăng nhập để tiếp tục mua sắm nhanh hơn" [level=2] [ref=e136]
          - paragraph [ref=e137]: Mở tài khoản để xem đơn hàng, lưu wishlist và thanh toán thuận tiện trên mọi thiết bị.
        - list [ref=e138]:
          - listitem [ref=e139]:
            - generic [ref=e140]: 
            - text: Đơn hàng của tôi
          - listitem [ref=e141]:
            - generic [ref=e142]: 
            - text: Danh sách yêu thích
          - listitem [ref=e143]:
            - generic [ref=e144]: 
            - text: Theo dõi thanh toán
          - listitem [ref=e145]:
            - generic [ref=e146]: 
            - text: Tư vấn size ngay trên web
  - contentinfo [ref=e147]:
    - generic [ref=e148]:
      - generic [ref=e149]:
        - heading "HUUGIAU Atelier" [level=3] [ref=e150]
        - paragraph [ref=e151]: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
        - paragraph [ref=e152]:
          - generic [aria-hidden] [ref=e153]: 
          - text: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
        - generic [ref=e154]:
          - link "Instagram" [ref=e155] [cursor=pointer]:
            - /url: https://www.instagram.com/
            - generic [aria-hidden] [ref=e156]: 
          - link "Facebook" [ref=e157] [cursor=pointer]:
            - /url: https://www.facebook.com/
            - generic [aria-hidden] [ref=e158]: 
          - link "TikTok" [ref=e159] [cursor=pointer]:
            - /url: https://www.tiktok.com/
            - generic [aria-hidden] [ref=e160]: 
        - generic [ref=e161]:
          - textbox "Email nhận tin" [ref=e162]:
            - /placeholder: Nhận tin khuyến mãi...
          - button "" [ref=e163] [cursor=pointer]
      - generic [ref=e165]:
        - heading "Hỗ trợ" [level=3] [ref=e166]
        - list [ref=e167]:
          - listitem [ref=e168]:
            - link "Tra cứu đơn hàng" [ref=e169] [cursor=pointer]:
              - /url: /tra-cuu-don/
          - listitem [ref=e170]:
            - link "Đơn hàng của tôi" [ref=e171] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
          - listitem [ref=e172]:
            - link "Chính sách đổi trả" [ref=e173] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
          - listitem [ref=e174]:
            - link "Hướng dẫn chọn size" [ref=e175] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=e176]:
            - link "Chất liệu & bảo quản" [ref=e177] [cursor=pointer]:
              - /url: /chat-lieu-bao-quan/
          - listitem [ref=e178]:
            - link "Khuyến mãi" [ref=e179] [cursor=pointer]:
              - /url: /khuyen-mai/
          - listitem [ref=e180]:
            - link "Câu hỏi thường gặp" [ref=e181] [cursor=pointer]:
              - /url: /hoi-dap-chung/
        - paragraph [ref=e182]:
          - text: "Hotline:"
          - link "0932047365" [ref=e183] [cursor=pointer]:
            - /url: tel:0932047365
          - text: · 9:00–21:30 mỗi ngày
      - generic [ref=e184]:
        - heading "Danh mục" [level=3] [ref=e185]
        - list [ref=e186]:
          - listitem [ref=e187]:
            - link "Áo" [ref=e188] [cursor=pointer]:
              - /url: /?category=ao
          - listitem [ref=e189]:
            - link "Quần" [ref=e190] [cursor=pointer]:
              - /url: /?category=quan
          - listitem [ref=e191]:
            - link "Phụ kiện" [ref=e192] [cursor=pointer]:
              - /url: /?category=phu-kien
          - listitem [ref=e193]:
            - link "Hàng mới về" [ref=e194] [cursor=pointer]:
              - /url: /?sort=newest
          - listitem [ref=e195]:
            - link "Tất cả sản phẩm" [ref=e196] [cursor=pointer]:
              - /url: /
      - generic [ref=e197]:
        - heading "Về HUUGIAU" [level=3] [ref=e198]
        - list [ref=e199]:
          - listitem [ref=e200]:
            - link "Câu chuyện thương hiệu" [ref=e201] [cursor=pointer]:
              - /url: /ve-chung-toi/
          - listitem [ref=e202]:
            - link "Hướng dẫn chọn size" [ref=e203] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=e204]:
            - link "Tuyển dụng" [ref=e205] [cursor=pointer]:
              - /url: /tuyen-dung/
          - listitem [ref=e206]:
            - link "Liên hệ" [ref=e207] [cursor=pointer]:
              - /url: /lien-he/
          - listitem [ref=e208]:
            - link "Lookbook" [ref=e209] [cursor=pointer]:
              - /url: /lookbook/
    - generic [ref=e210]:
      - generic [ref=e211]:
        - generic [ref=e212]:
          - generic [ref=e213]: © 2026 HUUGIAU Atelier
          - link "Chính sách bảo mật" [ref=e214] [cursor=pointer]:
            - /url: /chinh-sach-bao-mat/
          - link "Điều khoản" [ref=e215] [cursor=pointer]:
            - /url: /dieu-khoan/
        - generic [ref=e216]:
          - generic "Visa" [ref=e217]: 
          - generic "Mastercard" [ref=e218]: 
          - generic "PayPal" [ref=e219]: 
          - generic "Chuyển khoản ngân hàng" [ref=e220]: 
          - generic "COD" [ref=e221]: 
      - generic [ref=e222]: "MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
  - button "Mở hỗ trợ mua hàng" [ref=e223] [cursor=pointer]:
    - generic [aria-hidden] [ref=e224]: 
  - dialog [aria-hidden] [ref=e225]:
    - generic [ref=e226]:
      - heading [level=3] [ref=e227]: Giỏ hàng (0)
      - button [ref=e228] [cursor=pointer]: ×
    - generic [ref=e230]:
      - generic [ref=e231]:
        - generic [ref=e232]: Tạm tính
        - strong [ref=e233]: 0đ
      - generic [ref=e234]:
        - link [ref=e235] [cursor=pointer]:
          - /url: /gio-hang/
          - text: Xem giỏ hàng
        - link [ref=e236] [cursor=pointer]:
          - /url: /thanh-toan/
          - text: Thanh toán
  - text: 
  - dialog [ref=e237]:
    - generic [ref=e238]:
      - generic [ref=e239]:
        - strong [ref=e240]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=e241]:
        - button "Tùy chỉnh" [ref=e242] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=e243] [cursor=pointer]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
  4  | 
  5  | test.describe('Authentication Flows', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     await page.goto(`${BASE_URL}/dang-nhap/`);
  8  |   });
  9  | 
  10 |   test('should display login form', async ({ page }) => {
> 11 |     await expect(page.locator('form')).toBeVisible();
     |                                        ^ Error: expect(locator).toBeVisible() failed
  12 |     await expect(page.locator('input[name="username"]')).toBeVisible();
  13 |     await expect(page.locator('input[name="password"]')).toBeVisible();
  14 |     await expect(page.locator('button[type="submit"]')).toBeVisible();
  15 |   });
  16 | 
  17 |   test('should show error for invalid credentials', async ({ page }) => {
  18 |     await page.fill('input[name="username"]', 'invalid');
  19 |     await page.fill('input[name="password"]', 'wrong');
  20 |     await page.click('button[type="submit"]');
  21 |     await expect(page.locator('.alert-danger, .error, .messages .error')).toBeVisible();
  22 |   });
  23 | 
  24 |   test('should login successfully with valid credentials', async ({ page }) => {
  25 |     // Assuming test user exists: testuser / TestPass123!
  26 |     await page.fill('input[name="username"]', 'testuser');
  27 |     await page.fill('input[name="password"]', 'TestPass123!');
  28 |     await page.click('button[type="submit"]');
  29 |     
  30 |     // Should redirect to home or account page
  31 |     await expect(page).not.toHaveURL(/\/dang-nhap\//);
  32 |   });
  33 | 
  34 |   test('should logout successfully', async ({ page }) => {
  35 |     // Login first
  36 |     await page.fill('input[name="username"]', 'testuser');
  37 |     await page.fill('input[name="password"]', 'TestPass123!');
  38 |     await page.click('button[type="submit"]');
  39 |     
  40 |     // Click logout
  41 |     await page.click('a[href*="dang-xuat"], button[onclick*="logout"]');
  42 |     
  43 |     // Should redirect to home
  44 |     await expect(page).toHaveURL(/\/$/);
  45 |   });
  46 | 
  47 |   test('should register new user', async ({ page }) => {
  48 |     await page.goto(`${BASE_URL}/dang-ky/`);
  49 |     
  50 |     const uniqueUser = `testuser_${Date.now()}`;
  51 |     await page.fill('input[name="username"]', uniqueUser);
  52 |     await page.fill('input[name="email"]', `${uniqueUser}@test.com`);
  53 |     await page.fill('input[name="password1"]', 'TestPass123!');
  54 |     await page.fill('input[name="password2"]', 'TestPass123!');
  55 |     
  56 |     // Fill required fields
  57 |     await page.fill('input[name="first_name"]', 'Test');
  58 |     await page.fill('input[name="last_name"]', 'User');
  59 |     
  60 |     await page.click('button[type="submit"]');
  61 |     
  62 |     // Should redirect after successful registration
  63 |     await expect(page).not.toHaveURL(/\/dang-ky\//);
  64 |   });
  65 | });
```