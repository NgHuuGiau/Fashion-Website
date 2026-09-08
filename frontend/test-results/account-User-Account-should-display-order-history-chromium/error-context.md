# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: account.spec.ts >> User Account >> should display order history
- Location: tests\account.spec.ts:20:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.waitForURL: Test timeout of 30000ms exceeded.
=========================== logs ===========================
waiting for navigation until "load"
============================================================
```

# Page snapshot

```yaml
- generic [active] [ref=f1e1]:
  - generic [ref=f1e2]:
    - text: Chào mùa mới —
    - strong [ref=f1e3]: giảm thêm 10%
    - text: cho đơn từ 800K, mã
    - strong [ref=f1e4]: FREESHIP20K
    - text: · Freeship toàn quốc từ 499K
  - banner [ref=f1e5]:
    - generic [ref=f1e6]:
      - generic [ref=f1e7]:
        - button "Menu" [ref=f1e8] [cursor=pointer]
        - generic [ref=f1e10]:
          - link "Trang chủ" [ref=f1e11] [cursor=pointer]:
            - /url: /
            - text: HUUGIAU
          - generic [ref=f1e12]: ATELIER / FASHION STUDIO
      - navigation "Điều hướng chính" [ref=f1e13]:
        - generic [ref=f1e14]:
          - generic [ref=f1e15]:
            - link "HUUGIAU" [ref=f1e16] [cursor=pointer]:
              - /url: /
            - button "Đóng menu" [ref=f1e17] [cursor=pointer]
          - textbox "Tìm kiếm..." [ref=f1e24]
          - generic [ref=f1e25]:
            - generic [ref=f1e26]: Danh mục
            - link "New in" [ref=f1e27] [cursor=pointer]:
              - /url: /?sort=newest
            - link "Áo" [ref=f1e31] [cursor=pointer]:
              - /url: /?category=ao
            - link "Quần" [ref=f1e35] [cursor=pointer]:
              - /url: /?category=quan
            - link "Phụ kiện" [ref=f1e41] [cursor=pointer]:
              - /url: /?category=phu-kien
            - link "Lookbook" [ref=f1e44] [cursor=pointer]:
              - /url: /lookbook/
          - generic [ref=f1e49]:
            - generic [ref=f1e50]: Cửa hàng
            - link "Câu chuyện thương hiệu" [ref=f1e51] [cursor=pointer]:
              - /url: /ve-chung-toi/
            - link "Khuyến mãi" [ref=f1e54] [cursor=pointer]:
              - /url: /khuyen-mai/
            - link "Liên hệ" [ref=f1e57] [cursor=pointer]:
              - /url: /lien-he/
            - link "Chính sách đổi trả" [ref=f1e61] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
            - link "Hỏi đáp" [ref=f1e65] [cursor=pointer]:
              - /url: /hoi-dap-chung/
          - generic [ref=f1e69]:
            - generic [ref=f1e70]: Tài khoản
            - link "Đăng nhập" [ref=f1e71] [cursor=pointer]:
              - /url: /dang-nhap/
            - link "Đăng ký" [ref=f1e75] [cursor=pointer]:
              - /url: /dang-ky/
          - link "Giỏ hàng" [ref=f1e79] [cursor=pointer]:
            - /url: /gio-hang/
          - generic [ref=f1e83]: HUUGIAU Atelier © 2026
      - generic [ref=f1e84]:
        - generic [ref=f1e85]:
          - text: 
          - textbox "Tìm áo, quần, phụ kiện..." [ref=f1e86]
        - link "Giỏ hàng" [ref=f1e87] [cursor=pointer]:
          - /url: /gio-hang/
          - generic [aria-hidden] [ref=f1e88]: 
          - generic [ref=f1e89]: "0"
        - link "Yêu thích" [ref=f1e90] [cursor=pointer]:
          - /url: /yeu-thich/
          - generic [aria-hidden] [ref=f1e91]: 
        - group [ref=f1e92]:
          - generic "Tài khoản" [ref=f1e93] [cursor=pointer]:
            - generic [aria-hidden] [ref=f1e94]: 
            - generic [aria-hidden] [ref=f1e96]: 
  - main [ref=f1e97]:
    - generic [ref=f1e98]:
      - generic [ref=f1e99]:
        - generic [ref=f1e100]:
          - generic [ref=f1e101]: 
          - heading "Chào mừng quay lại" [level=1] [ref=f1e103]
          - paragraph [ref=f1e104]: Dùng email hoặc số điện thoại đã đăng ký để vào tài khoản nhanh hơn.
        - generic [ref=f1e105]:
          - generic [ref=f1e106]:
            - generic [ref=f1e107]:
              - generic [ref=f1e108]: 
              - text: Email hoặc số điện thoại
            - textbox " Email hoặc số điện thoại" [ref=f1e109]:
              - /placeholder: Nhập email hoặc số điện thoại
          - generic [ref=f1e110]:
            - generic [ref=f1e111]:
              - generic [ref=f1e112]: 
              - text: Mật khẩu
            - textbox " Mật khẩu" [ref=f1e113]:
              - /placeholder: Nhập mật khẩu
            - link "Quên mật khẩu?" [ref=f1e114] [cursor=pointer]:
              - /url: /quen-mat-khau/
          - button " Đăng nhập" [ref=f1e115] [cursor=pointer]:
            - generic [ref=f1e116]: 
            - text: Đăng nhập
        - generic [ref=f1e117]:
          - paragraph [ref=f1e118]: Hoặc tiếp tục bằng
          - generic [ref=f1e119]:
            - link "Google" [ref=f1e120] [cursor=pointer]:
              - /url: /dang-nhap/google/?next=
              - generic [aria-hidden] [ref=f1e121]: 
            - link "Facebook" [ref=f1e123] [cursor=pointer]:
              - /url: /dang-nhap/facebook/?next=
              - generic [aria-hidden] [ref=f1e124]: 
            - link "Apple" [ref=f1e126] [cursor=pointer]:
              - /url: /dang-nhap/apple/?next=
              - generic [aria-hidden] [ref=f1e127]: 
        - paragraph [ref=f1e129]:
          - text: Chưa có tài khoản?
          - link "Đăng ký ngay" [ref=f1e130] [cursor=pointer]:
            - /url: /dang-ky/
      - complementary [ref=f1e131]:
        - generic [ref=f1e132]:
          - generic [ref=f1e133]:
            - generic [ref=f1e134]: 
            - generic [ref=f1e135]: HUUGIAU Atelier
          - heading "Đăng nhập để tiếp tục mua sắm nhanh hơn" [level=2] [ref=f1e136]
          - paragraph [ref=f1e137]: Mở tài khoản để xem đơn hàng, lưu wishlist và thanh toán thuận tiện trên mọi thiết bị.
        - list [ref=f1e138]:
          - listitem [ref=f1e139]:
            - generic [ref=f1e140]: 
            - text: Đơn hàng của tôi
          - listitem [ref=f1e141]:
            - generic [ref=f1e142]: 
            - text: Danh sách yêu thích
          - listitem [ref=f1e143]:
            - generic [ref=f1e144]: 
            - text: Theo dõi thanh toán
          - listitem [ref=f1e145]:
            - generic [ref=f1e146]: 
            - text: Tư vấn size ngay trên web
  - contentinfo [ref=f1e147]:
    - generic [ref=f1e148]:
      - generic [ref=f1e149]:
        - heading "HUUGIAU Atelier" [level=3] [ref=f1e150]
        - paragraph [ref=f1e151]: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
        - paragraph [ref=f1e152]:
          - generic [aria-hidden] [ref=f1e153]: 
          - text: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
        - generic [ref=f1e154]:
          - link "Instagram" [ref=f1e155] [cursor=pointer]:
            - /url: https://www.instagram.com/
            - generic [aria-hidden] [ref=f1e156]: 
          - link "Facebook" [ref=f1e157] [cursor=pointer]:
            - /url: https://www.facebook.com/
            - generic [aria-hidden] [ref=f1e158]: 
          - link "TikTok" [ref=f1e159] [cursor=pointer]:
            - /url: https://www.tiktok.com/
            - generic [aria-hidden] [ref=f1e160]: 
        - generic [ref=f1e161]:
          - textbox "Email nhận tin" [ref=f1e162]:
            - /placeholder: Nhận tin khuyến mãi...
          - button "" [ref=f1e163] [cursor=pointer]
      - generic [ref=f1e165]:
        - heading "Hỗ trợ" [level=3] [ref=f1e166]
        - list [ref=f1e167]:
          - listitem [ref=f1e168]:
            - link "Tra cứu đơn hàng" [ref=f1e169] [cursor=pointer]:
              - /url: /tra-cuu-don/
          - listitem [ref=f1e170]:
            - link "Đơn hàng của tôi" [ref=f1e171] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
          - listitem [ref=f1e172]:
            - link "Chính sách đổi trả" [ref=f1e173] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
          - listitem [ref=f1e174]:
            - link "Hướng dẫn chọn size" [ref=f1e175] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f1e176]:
            - link "Chất liệu & bảo quản" [ref=f1e177] [cursor=pointer]:
              - /url: /chat-lieu-bao-quan/
          - listitem [ref=f1e178]:
            - link "Khuyến mãi" [ref=f1e179] [cursor=pointer]:
              - /url: /khuyen-mai/
          - listitem [ref=f1e180]:
            - link "Câu hỏi thường gặp" [ref=f1e181] [cursor=pointer]:
              - /url: /hoi-dap-chung/
        - paragraph [ref=f1e182]:
          - text: "Hotline:"
          - link "0932047365" [ref=f1e183] [cursor=pointer]:
            - /url: tel:0932047365
          - text: · 9:00–21:30 mỗi ngày
      - generic [ref=f1e184]:
        - heading "Danh mục" [level=3] [ref=f1e185]
        - list [ref=f1e186]:
          - listitem [ref=f1e187]:
            - link "Áo" [ref=f1e188] [cursor=pointer]:
              - /url: /?category=ao
          - listitem [ref=f1e189]:
            - link "Quần" [ref=f1e190] [cursor=pointer]:
              - /url: /?category=quan
          - listitem [ref=f1e191]:
            - link "Phụ kiện" [ref=f1e192] [cursor=pointer]:
              - /url: /?category=phu-kien
          - listitem [ref=f1e193]:
            - link "Hàng mới về" [ref=f1e194] [cursor=pointer]:
              - /url: /?sort=newest
          - listitem [ref=f1e195]:
            - link "Tất cả sản phẩm" [ref=f1e196] [cursor=pointer]:
              - /url: /
      - generic [ref=f1e197]:
        - heading "Về HUUGIAU" [level=3] [ref=f1e198]
        - list [ref=f1e199]:
          - listitem [ref=f1e200]:
            - link "Câu chuyện thương hiệu" [ref=f1e201] [cursor=pointer]:
              - /url: /ve-chung-toi/
          - listitem [ref=f1e202]:
            - link "Hướng dẫn chọn size" [ref=f1e203] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f1e204]:
            - link "Tuyển dụng" [ref=f1e205] [cursor=pointer]:
              - /url: /tuyen-dung/
          - listitem [ref=f1e206]:
            - link "Liên hệ" [ref=f1e207] [cursor=pointer]:
              - /url: /lien-he/
          - listitem [ref=f1e208]:
            - link "Lookbook" [ref=f1e209] [cursor=pointer]:
              - /url: /lookbook/
    - generic [ref=f1e210]:
      - generic [ref=f1e211]:
        - generic [ref=f1e212]:
          - generic [ref=f1e213]: © 2026 HUUGIAU Atelier
          - link "Chính sách bảo mật" [ref=f1e214] [cursor=pointer]:
            - /url: /chinh-sach-bao-mat/
          - link "Điều khoản" [ref=f1e215] [cursor=pointer]:
            - /url: /dieu-khoan/
        - generic [ref=f1e216]:
          - generic "Visa" [ref=f1e217]: 
          - generic "Mastercard" [ref=f1e218]: 
          - generic "PayPal" [ref=f1e219]: 
          - generic "Chuyển khoản ngân hàng" [ref=f1e220]: 
          - generic "COD" [ref=f1e221]: 
      - generic [ref=f1e222]: "MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
  - button "Mở hỗ trợ mua hàng" [ref=f1e223] [cursor=pointer]:
    - generic [aria-hidden] [ref=f1e224]: 
  - dialog [aria-hidden] [ref=f1e225]:
    - generic [ref=f1e226]:
      - heading [level=3] [ref=f1e227]: Giỏ hàng (0)
      - button [ref=f1e228] [cursor=pointer]: ×
    - generic [ref=f1e230]:
      - generic [ref=f1e231]:
        - generic [ref=f1e232]: Tạm tính
        - strong [ref=f1e233]: 0đ
      - generic [ref=f1e234]:
        - link [ref=f1e235] [cursor=pointer]:
          - /url: /gio-hang/
          - text: Xem giỏ hàng
        - link [ref=f1e236] [cursor=pointer]:
          - /url: /thanh-toan/
          - text: Thanh toán
  - text: 
  - dialog [ref=f1e237]:
    - generic [ref=f1e238]:
      - generic [ref=f1e239]:
        - strong [ref=f1e240]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=f1e241]:
        - button "Tùy chỉnh" [ref=f1e242] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=f1e243] [cursor=pointer]
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
  11 |     await page.click('button[type="submit"]');
> 12 |     await page.waitForURL(/^(?!.*dang-nhap).*/);
     |                ^ Error: page.waitForURL: Test timeout of 30000ms exceeded.
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