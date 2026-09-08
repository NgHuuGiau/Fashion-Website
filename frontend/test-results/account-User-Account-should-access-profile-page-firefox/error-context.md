# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: account.spec.ts >> User Account >> should access profile page
- Location: tests\account.spec.ts:15:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('input[name="password"]')
    - locator resolved to <input required="" type="password" name="password" id="id_password" placeholder="Nhập mật khẩu"/>
    - fill("TestPass123!")
  - attempting fill action
    - waiting for element to be visible, enabled and editable

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
        - generic [ref=e13]:
          - link "Trang chủ" [ref=e14] [cursor=pointer]:
            - /url: /
            - text: HUUGIAU
          - generic [ref=e15]: ATELIER / FASHION STUDIO
      - navigation "Điều hướng chính" [ref=e16]:
        - generic [ref=e17]:
          - generic [ref=e18]:
            - link "HUUGIAU" [ref=e19] [cursor=pointer]:
              - /url: /
            - button "Đóng menu" [ref=e20] [cursor=pointer]
          - textbox "Tìm kiếm..." [ref=e27]
          - generic [ref=e28]:
            - generic [ref=e29]: Danh mục
            - link "New in" [ref=e30] [cursor=pointer]:
              - /url: /?sort=newest
            - link "Áo" [ref=e34] [cursor=pointer]:
              - /url: /?category=ao
            - link "Quần" [ref=e39] [cursor=pointer]:
              - /url: /?category=quan
            - link "Phụ kiện" [ref=e45] [cursor=pointer]:
              - /url: /?category=phu-kien
            - link "Lookbook" [ref=e52] [cursor=pointer]:
              - /url: /lookbook/
          - generic [ref=e57]:
            - generic [ref=e58]: Cửa hàng
            - link "Câu chuyện thương hiệu" [ref=e59] [cursor=pointer]:
              - /url: /ve-chung-toi/
            - link "Khuyến mãi" [ref=e62] [cursor=pointer]:
              - /url: /khuyen-mai/
            - link "Liên hệ" [ref=e66] [cursor=pointer]:
              - /url: /lien-he/
            - link "Chính sách đổi trả" [ref=e70] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
            - link "Hỏi đáp" [ref=e74] [cursor=pointer]:
              - /url: /hoi-dap-chung/
          - generic [ref=e79]:
            - generic [ref=e80]: Tài khoản
            - link "Đăng nhập" [ref=e81] [cursor=pointer]:
              - /url: /dang-nhap/
            - link "Đăng ký" [ref=e86] [cursor=pointer]:
              - /url: /dang-ky/
          - link "Giỏ hàng" [ref=e92] [cursor=pointer]:
            - /url: /gio-hang/
          - generic [ref=e97]: HUUGIAU Atelier © 2026
      - generic [ref=e98]:
        - generic [ref=e99]:
          - text: 
          - textbox "Tìm áo, quần, phụ kiện..." [ref=e100]
        - link "Giỏ hàng" [ref=e101] [cursor=pointer]:
          - /url: /gio-hang/
          - generic [aria-hidden] [ref=e102]: 
          - generic [ref=e103]: "0"
        - link "Yêu thích" [ref=e104] [cursor=pointer]:
          - /url: /yeu-thich/
          - generic [aria-hidden] [ref=e105]: 
        - group [ref=e106]:
          - generic "Tài khoản" [ref=e107] [cursor=pointer]:
            - generic [aria-hidden] [ref=e108]: 
            - generic [aria-hidden] [ref=e110]: 
  - main [ref=e111]:
    - generic [ref=e112]:
      - generic [ref=e113]:
        - generic [ref=e114]:
          - generic [ref=e115]: 
          - heading "Chào mừng quay lại" [level=1] [ref=e117]
          - paragraph [ref=e118]: Dùng email hoặc số điện thoại đã đăng ký để vào tài khoản nhanh hơn.
        - generic [ref=e119]:
          - generic [ref=e120]:
            - generic [ref=e121]:
              - generic [ref=e122]: 
              - text: Email hoặc số điện thoại
            - textbox " Email hoặc số điện thoại" [active] [ref=e123]:
              - /placeholder: Nhập email hoặc số điện thoại
              - text: testuser
          - generic [ref=e124]:
            - generic [ref=e125]:
              - generic [ref=e126]: 
              - text: Mật khẩu
            - textbox " Mật khẩu" [ref=e127]:
              - /placeholder: Nhập mật khẩu
            - link "Quên mật khẩu?" [ref=e128] [cursor=pointer]:
              - /url: /quen-mat-khau/
          - button " Đăng nhập" [ref=e129] [cursor=pointer]:
            - generic [ref=e130]: 
            - text: Đăng nhập
        - generic [ref=e131]:
          - paragraph [ref=e132]: Hoặc tiếp tục bằng
          - generic [ref=e133]:
            - link "Google" [ref=e134] [cursor=pointer]:
              - /url: /dang-nhap/google/?next=
              - generic [aria-hidden] [ref=e135]: 
            - link "Facebook" [ref=e137] [cursor=pointer]:
              - /url: /dang-nhap/facebook/?next=
              - generic [aria-hidden] [ref=e138]: 
            - link "Apple" [ref=e140] [cursor=pointer]:
              - /url: /dang-nhap/apple/?next=
              - generic [aria-hidden] [ref=e141]: 
        - paragraph [ref=e143]:
          - text: Chưa có tài khoản?
          - link "Đăng ký ngay" [ref=e144] [cursor=pointer]:
            - /url: /dang-ky/
      - complementary [ref=e145]:
        - generic [ref=e146]:
          - generic [ref=e147]:
            - generic [ref=e148]: 
            - generic [ref=e149]: HUUGIAU Atelier
          - heading "Đăng nhập để tiếp tục mua sắm nhanh hơn" [level=2] [ref=e150]
          - paragraph [ref=e151]: Mở tài khoản để xem đơn hàng, lưu wishlist và thanh toán thuận tiện trên mọi thiết bị.
        - list [ref=e152]:
          - listitem [ref=e153]:
            - generic [ref=e154]: 
            - text: Đơn hàng của tôi
          - listitem [ref=e155]:
            - generic [ref=e156]: 
            - text: Danh sách yêu thích
          - listitem [ref=e157]:
            - generic [ref=e158]: 
            - text: Theo dõi thanh toán
          - listitem [ref=e159]:
            - generic [ref=e160]: 
            - text: Tư vấn size ngay trên web
  - contentinfo [ref=e161]:
    - generic [ref=e162]:
      - generic [ref=e163]:
        - heading "HUUGIAU Atelier" [level=3] [ref=e164]
        - paragraph [ref=e165]: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
        - paragraph [ref=e166]:
          - generic [aria-hidden] [ref=e167]: 
          - text: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
        - generic [ref=e168]:
          - link "Instagram" [ref=e169] [cursor=pointer]:
            - /url: https://www.instagram.com/
            - generic [aria-hidden] [ref=e170]: 
          - link "Facebook" [ref=e171] [cursor=pointer]:
            - /url: https://www.facebook.com/
            - generic [aria-hidden] [ref=e172]: 
          - link "TikTok" [ref=e173] [cursor=pointer]:
            - /url: https://www.tiktok.com/
            - generic [aria-hidden] [ref=e174]: 
        - generic [ref=e175]:
          - textbox "Email nhận tin" [ref=e176]:
            - /placeholder: Nhận tin khuyến mãi...
          - button "" [ref=e177] [cursor=pointer]
      - generic [ref=e179]:
        - heading "Hỗ trợ" [level=3] [ref=e180]
        - list [ref=e181]:
          - listitem [ref=e182]:
            - link "Tra cứu đơn hàng" [ref=e183] [cursor=pointer]:
              - /url: /tra-cuu-don/
          - listitem [ref=e184]:
            - link "Đơn hàng của tôi" [ref=e185] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
          - listitem [ref=e186]:
            - link "Chính sách đổi trả" [ref=e187] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
          - listitem [ref=e188]:
            - link "Hướng dẫn chọn size" [ref=e189] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=e190]:
            - link "Chất liệu & bảo quản" [ref=e191] [cursor=pointer]:
              - /url: /chat-lieu-bao-quan/
          - listitem [ref=e192]:
            - link "Khuyến mãi" [ref=e193] [cursor=pointer]:
              - /url: /khuyen-mai/
          - listitem [ref=e194]:
            - link "Câu hỏi thường gặp" [ref=e195] [cursor=pointer]:
              - /url: /hoi-dap-chung/
        - paragraph [ref=e196]:
          - text: "Hotline:"
          - link "0932047365" [ref=e197] [cursor=pointer]:
            - /url: tel:0932047365
          - text: · 9:00–21:30 mỗi ngày
      - generic [ref=e198]:
        - heading "Danh mục" [level=3] [ref=e199]
        - list [ref=e200]:
          - listitem [ref=e201]:
            - link "Áo" [ref=e202] [cursor=pointer]:
              - /url: /?category=ao
          - listitem [ref=e203]:
            - link "Quần" [ref=e204] [cursor=pointer]:
              - /url: /?category=quan
          - listitem [ref=e205]:
            - link "Phụ kiện" [ref=e206] [cursor=pointer]:
              - /url: /?category=phu-kien
          - listitem [ref=e207]:
            - link "Hàng mới về" [ref=e208] [cursor=pointer]:
              - /url: /?sort=newest
          - listitem [ref=e209]:
            - link "Tất cả sản phẩm" [ref=e210] [cursor=pointer]:
              - /url: /
      - generic [ref=e211]:
        - heading "Về HUUGIAU" [level=3] [ref=e212]
        - list [ref=e213]:
          - listitem [ref=e214]:
            - link "Câu chuyện thương hiệu" [ref=e215] [cursor=pointer]:
              - /url: /ve-chung-toi/
          - listitem [ref=e216]:
            - link "Hướng dẫn chọn size" [ref=e217] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=e218]:
            - link "Tuyển dụng" [ref=e219] [cursor=pointer]:
              - /url: /tuyen-dung/
          - listitem [ref=e220]:
            - link "Liên hệ" [ref=e221] [cursor=pointer]:
              - /url: /lien-he/
          - listitem [ref=e222]:
            - link "Lookbook" [ref=e223] [cursor=pointer]:
              - /url: /lookbook/
    - generic [ref=e224]:
      - generic [ref=e225]:
        - generic [ref=e226]:
          - generic [ref=e227]: © 2026 HUUGIAU Atelier
          - link "Chính sách bảo mật" [ref=e228] [cursor=pointer]:
            - /url: /chinh-sach-bao-mat/
          - link "Điều khoản" [ref=e229] [cursor=pointer]:
            - /url: /dieu-khoan/
        - generic [ref=e230]:
          - generic "Visa" [ref=e231]: 
          - generic "Mastercard" [ref=e232]: 
          - generic "PayPal" [ref=e233]: 
          - generic "Chuyển khoản ngân hàng" [ref=e234]: 
          - generic "COD" [ref=e235]: 
      - generic [ref=e236]: "MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
  - button "Mở hỗ trợ mua hàng" [ref=e237] [cursor=pointer]:
    - generic [aria-hidden] [ref=e238]: 
  - dialog [aria-hidden] [ref=e239]:
    - generic [ref=e240]:
      - heading [level=3] [ref=e241]: Giỏ hàng (0)
      - button [ref=e242] [cursor=pointer]: ×
    - generic [ref=e244]:
      - generic [ref=e245]:
        - generic [ref=e246]: Tạm tính
        - strong [ref=e247]: 0đ
      - generic [ref=e248]:
        - link [ref=e249] [cursor=pointer]:
          - /url: /gio-hang/
          - text: Xem giỏ hàng
        - link [ref=e250] [cursor=pointer]:
          - /url: /thanh-toan/
          - text: Thanh toán
  - text: 
  - dialog [ref=e251]:
    - generic [ref=e252]:
      - generic [ref=e253]:
        - strong [ref=e254]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=e255]:
        - button "Tùy chỉnh" [ref=e256] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=e257] [cursor=pointer]
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
> 10 |     await page.fill('input[name="password"]', 'TestPass123!');
     |                ^ Error: page.fill: Test timeout of 30000ms exceeded.
  11 |     await page.click('button[type="submit"]');
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