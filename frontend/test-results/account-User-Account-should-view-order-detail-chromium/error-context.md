# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: account.spec.ts >> User Account >> should view order detail
- Location: tests\account.spec.ts:25:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('button[type="submit"]')
    - locator resolved to 4 elements. Proceeding with the first one: <button class="btn" type="submit">…</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <strong>Chúng tôi sử dụng cookie</strong> from <div role="dialog" aria-live="polite" id="cookie-consent" class="cookie-consent visible">…</div> subtree intercepts pointer events
    - retrying click action
    - waiting 20ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <strong>Chúng tôi sử dụng cookie</strong> from <div role="dialog" aria-live="polite" id="cookie-consent" class="cookie-consent visible">…</div> subtree intercepts pointer events
  - retrying click action
    - waiting 100ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <main class="container page-wrap">…</main> intercepts pointer events
  - retrying click action
    - waiting 100ms
    - waiting for element to be visible, enabled and stable
    - element is not stable
  - retrying click action
    - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <div class="container nav-wrap">…</div> from <header class="site-header">…</header> subtree intercepts pointer events
  - retrying click action
    - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <strong>Chúng tôi sử dụng cookie</strong> from <div role="dialog" aria-live="polite" id="cookie-consent" class="cookie-consent visible">…</div> subtree intercepts pointer events
  - retrying click action
    - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <p class="social-auth-label">Hoặc tiếp tục bằng</p> from <div class="social-auth">…</div> subtree intercepts pointer events
  2 × retrying click action
      - waiting 500ms
      - waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <div class="container nav-wrap">…</div> from <header class="site-header">…</header> subtree intercepts pointer events
  - retrying click action
    - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <strong>Chúng tôi sử dụng cookie</strong> from <div role="dialog" aria-live="polite" id="cookie-consent" class="cookie-consent visible">…</div> subtree intercepts pointer events
  - retrying click action
    - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <div class="container footer-wrap">…</div> from <footer class="site-footer">…</footer> subtree intercepts pointer events
  - retrying click action
    - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <div class="container nav-wrap">…</div> from <header class="site-header">…</header> subtree intercepts pointer events
  - retrying click action
    - waiting 500ms

```

# Page snapshot

```yaml
- generic [ref=e1]:
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
              - text: testuser
          - generic [ref=e110]:
            - generic [ref=e111]:
              - generic [ref=e112]: 
              - text: Mật khẩu
            - textbox " Mật khẩu" [active] [ref=e113]:
              - /placeholder: Nhập mật khẩu
              - text: TestPass123!
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
  - button "Lên đầu trang" [ref=e237] [cursor=pointer]:
    - generic [aria-hidden] [ref=e238]: 
  - dialog [ref=e239]:
    - generic [ref=e240]:
      - generic [ref=e241]:
        - strong [ref=e242]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=e243]:
        - button "Tùy chỉnh" [ref=e244] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=e245] [cursor=pointer]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
  4  | 
  5  | test.describe('User Account', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     // Login first
  8  |     await page.goto(`${BASE_URL}/dang-nhap/`);
  9  |     await page.fill('input[name="username"]', 'testuser');
  10 |     await page.fill('input[name="password"]', 'TestPass123!');
> 11 |     await page.click('button[type="submit"]');
     |                ^ Error: page.click: Test timeout of 30000ms exceeded.
  12 |     await page.waitForURL(/^(?!.*dang-nhap).*/);
  13 |   });
  14 | 
  15 |   test('should access profile page', async ({ page }) => {
  16 |     await page.goto(`${BASE_URL}/tai-khoan/`);
  17 |     await expect(page.locator('h1, h2')).toContainText(/Tài khoản|Profile|Tài khoản của bạn/);
  18 |   });
  19 | 
  20 |   test('should display order history', async ({ page }) => {
  21 |     await page.goto(`${BASE_URL}/don-hang-cua-toi/`);
  22 |     await expect(page.locator('.orders-list, .order-history, table')).toBeVisible({ timeout: 10000 });
  23 |   });
  24 | 
  25 |   test('should view order detail', async ({ page }) => {
  26 |     await page.goto(`${BASE_URL}/don-hang-cua-toi/`);
  27 |     
  28 |     const orderLink = page.locator('a[href*="/don-hang/"][href*="/xem-lai/"]').first();
  29 |     if (await orderLink.isVisible()) {
  30 |       await orderLink.click();
  31 |       await expect(page).toHaveURL(/\/don-hang\/\d+\/xem-lai\//);
  32 |       await expect(page.locator('.order-detail, .order-info')).toBeVisible();
  33 |     }
  34 |   });
  35 | 
  36 |   test('should update profile', async ({ page }) => {
  37 |     await page.goto(`${BASE_URL}/tai-khoan/`);
  38 |     
  39 |     await page.fill('input[name="first_name"]', 'Updated');
  40 |     await page.fill('input[name="last_name"]', 'Name');
  41 |     await page.click('button[type="submit"]:has-text("Lưu"), button:has-text("Cập nhật")');
  42 |     
  43 |     await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  44 |   });
  45 | 
  46 |   test('should add address', async ({ page }) => {
  47 |     await page.goto(`${BASE_URL}/tai-khoan/`);
  48 |     
  49 |     // Navigate to addresses
  50 |     await page.click('a[href*="dia-chi"], a:has-text("Địa chỉ")');
  51 |     
  52 |     await page.click('a:has-text("Thêm"), button:has-text("Thêm địa chỉ")');
  53 |     
  54 |     await page.fill('input[name="recipient_name"]', 'Test Recipient');
  55 |     await page.fill('input[name="phone"]', '0901234567');
  56 |     await page.fill('textarea[name="address"], input[name="address"]', '456 New Street, District 2, HCMC');
  57 |     
  58 |     await page.click('button[type="submit"]:has-text("Lưu"), button:has-text("Thêm")');
  59 |     
  60 |     await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  61 |   });
  62 | 
  63 |   test('should change password', async ({ page }) => {
  64 |     await page.goto(`${BASE_URL}/tai-khoan/doi-mat-khau/`);
  65 |     
  66 |     await page.fill('input[name="old_password"]', 'TestPass123!');
  67 |     await page.fill('input[name="new_password1"]', 'NewPass123!');
  68 |     await page.fill('input[name="new_password2"]', 'NewPass123!');
  69 |     
  70 |     await page.click('button[type="submit"]');
  71 |     
  72 |     await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  73 |   });
  74 | });
```