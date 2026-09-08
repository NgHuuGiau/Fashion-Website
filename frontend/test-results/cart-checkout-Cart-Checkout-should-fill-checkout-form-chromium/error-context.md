# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: cart-checkout.spec.ts >> Cart & Checkout >> should fill checkout form
- Location: tests\cart-checkout.spec.ts:57:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('input[name="customer_name"]')
    - locator resolved to <input type="text" required="" maxlength="150" name="customer_name" id="id_customer_name"/>
    - fill("Test User")
  - attempting fill action
    - waiting for element to be visible, enabled and editable

```

# Page snapshot

```yaml
- generic [active] [ref=f3e1]:
  - generic [ref=f3e2]:
    - text: Chào mùa mới —
    - strong [ref=f3e3]: giảm thêm 10%
    - text: cho đơn từ 800K, mã
    - strong [ref=f3e4]: FREESHIP20K
    - text: · Freeship toàn quốc từ 499K
  - banner [ref=f3e5]:
    - generic [ref=f3e6]:
      - generic [ref=f3e7]:
        - button "Menu" [ref=f3e8] [cursor=pointer]
        - generic [ref=f3e10]:
          - link "Trang chủ" [ref=f3e11] [cursor=pointer]:
            - /url: /
            - text: HUUGIAU
          - generic [ref=f3e12]: ATELIER / FASHION STUDIO
      - navigation "Điều hướng chính" [ref=f3e13]:
        - generic [ref=f3e14]:
          - generic [ref=f3e15]:
            - link "HUUGIAU" [ref=f3e16] [cursor=pointer]:
              - /url: /
            - button "Đóng menu" [ref=f3e17] [cursor=pointer]
          - textbox "Tìm kiếm..." [ref=f3e24]
          - generic [ref=f3e25]:
            - generic [ref=f3e26]: Danh mục
            - link "New in" [ref=f3e27] [cursor=pointer]:
              - /url: /?sort=newest
            - link "Áo" [ref=f3e31] [cursor=pointer]:
              - /url: /?category=ao
            - link "Quần" [ref=f3e35] [cursor=pointer]:
              - /url: /?category=quan
            - link "Phụ kiện" [ref=f3e41] [cursor=pointer]:
              - /url: /?category=phu-kien
            - link "Lookbook" [ref=f3e44] [cursor=pointer]:
              - /url: /lookbook/
          - generic [ref=f3e49]:
            - generic [ref=f3e50]: Cửa hàng
            - link "Câu chuyện thương hiệu" [ref=f3e51] [cursor=pointer]:
              - /url: /ve-chung-toi/
            - link "Khuyến mãi" [ref=f3e54] [cursor=pointer]:
              - /url: /khuyen-mai/
            - link "Liên hệ" [ref=f3e57] [cursor=pointer]:
              - /url: /lien-he/
            - link "Chính sách đổi trả" [ref=f3e61] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
            - link "Hỏi đáp" [ref=f3e65] [cursor=pointer]:
              - /url: /hoi-dap-chung/
          - generic [ref=f3e69]:
            - generic [ref=f3e70]: Tài khoản
            - link "Đăng nhập" [ref=f3e71] [cursor=pointer]:
              - /url: /dang-nhap/
            - link "Đăng ký" [ref=f3e75] [cursor=pointer]:
              - /url: /dang-ky/
          - link "Giỏ hàng 1" [ref=f3e79] [cursor=pointer]:
            - /url: /gio-hang/
            - text: Giỏ hàng
            - generic [ref=f3e83]: "1"
          - generic [ref=f3e84]: HUUGIAU Atelier © 2026
      - generic [ref=f3e85]:
        - generic [ref=f3e86]:
          - text: 
          - textbox "Tìm áo, quần, phụ kiện..." [ref=f3e87]
        - link "Giỏ hàng" [ref=f3e88] [cursor=pointer]:
          - /url: /gio-hang/
          - generic [aria-hidden] [ref=f3e89]: 
          - generic [ref=f3e90]: "1"
        - link "Yêu thích" [ref=f3e91] [cursor=pointer]:
          - /url: /yeu-thich/
          - generic [aria-hidden] [ref=f3e92]: 
        - group [ref=f3e93]:
          - generic "Tài khoản" [ref=f3e94] [cursor=pointer]:
            - generic [aria-hidden] [ref=f3e95]: 
            - generic [aria-hidden] [ref=f3e97]: 
  - main [ref=f3e98]:
    - navigation "Bạn đang ở" [ref=f3e99]:
      - link "Trang chủ" [ref=f3e100] [cursor=pointer]:
        - /url: /
      - generic [ref=f3e101]: /
      - link "Giỏ hàng" [ref=f3e102] [cursor=pointer]:
        - /url: /gio-hang/
      - generic [ref=f3e103]: /
      - generic [ref=f3e104]: Thanh toán
    - generic [ref=f3e105]:
      - generic [ref=f3e107]:
        - paragraph [ref=f3e108]: Thanh toán
        - heading "Thanh toán nhanh trong một trang" [level=1] [ref=f3e109]
        - paragraph [ref=f3e110]: Nhập thông tin, chọn phương thức và hoàn tất đơn hàng ngay.
      - generic [ref=f3e111]:
        - generic [ref=f3e113]:
          - generic [ref=f3e114]:
            - generic [ref=f3e115]:
              - generic [ref=f3e116]: Họ và tên
              - textbox "Họ và tên" [ref=f3e117]
            - generic [ref=f3e118]:
              - generic [ref=f3e119]: Email
              - textbox "Email" [ref=f3e120]
            - generic [ref=f3e121]:
              - generic [ref=f3e122]: Số điện thoại
              - textbox "Số điện thoại" [ref=f3e123]
            - generic [ref=f3e124]:
              - generic [ref=f3e125]: Địa chỉ nhận hàng
              - textbox "Địa chỉ nhận hàng" [ref=f3e126]
            - generic [ref=f3e127]:
              - generic [ref=f3e128]:
                - textbox "Tìm địa chỉ giao hàng" [ref=f3e129]:
                  - /placeholder: "Tìm địa chỉ... ví dụ: 12 Nguyễn Hữu Thọ, Q7"
                - button "Định vị" [ref=f3e130] [cursor=pointer]:
                  - generic [aria-hidden] [ref=f3e131]: 
                  - text: Định vị
                - link "Mở Google Maps" [ref=f3e132] [cursor=pointer]:
                  - /url: "#"
                  - text: Mở Google Maps
                  - generic [aria-hidden] [ref=f3e133]: 
              - generic "Bản đồ chọn vị trí giao hàng" [ref=f3e134]:
                - button "Marker" [ref=f3e135] [cursor=pointer]
                - generic:
                  - generic [ref=f3e136]:
                    - button "Zoom in" [ref=f3e137] [cursor=pointer]: +
                    - button "Zoom out" [ref=f3e138] [cursor=pointer]: −
                  - generic [ref=f3e139]:
                    - link "Leaflet" [ref=f3e140] [cursor=pointer]:
                      - /url: https://leafletjs.com
                    - text: "| ©"
                    - link "Google Maps" [ref=f3e145] [cursor=pointer]:
                      - /url: https://www.google.com/maps
              - paragraph [ref=f3e146]: Gõ địa chỉ rồi bấm Enter để tìm trên map, hoặc click trực tiếp lên map để chọn đúng vị trí giao hàng.
              - paragraph [ref=f3e147]: "Map đã sẵn sàng: gõ địa chỉ + Enter để tìm, hoặc click lên map."
            - generic [ref=f3e148]:
              - generic [ref=f3e149]: Phương thức thanh toán
              - combobox "Phương thức thanh toán" [ref=f3e150]:
                - option "Thanh toán tiền mặt khi nhận hàng" [selected]
                - option "Chuyển khoản ngân hàng"
                - option "Thanh toán VNPay"
          - generic [ref=f3e151]:
            - heading "Thanh toán khi nhận hàng" [level=3] [ref=f3e152]
            - paragraph [ref=f3e153]: Bạn chỉ cần xác nhận đơn, shop sẽ liên hệ và giao đến địa chỉ đã nhập.
          - generic [ref=f3e154]:
            - generic [ref=f3e155]:
              - generic [ref=f3e156]: Mã giảm giá
              - 'textbox "Mã giảm giá Ví dụ: GIAM10, FREESHIP" [ref=f3e157]'
              - generic [ref=f3e158]: "Ví dụ: GIAM10, FREESHIP"
            - generic [ref=f3e159]:
              - generic [ref=f3e160]: Ghi chú
              - textbox "Ghi chú" [ref=f3e161]
            - generic [ref=f3e162]:
              - generic [ref=f3e163]: Khung giờ nhận hàng
              - combobox "Khung giờ nhận hàng" [ref=f3e164]:
                - option "-- Chọn khung giờ --" [selected]
                - option "8:00 – 11:00"
                - option "13:00 – 17:00"
                - option "18:00 – 21:00"
            - generic [ref=f3e165]:
              - generic [ref=f3e166]:
                - checkbox "🎁 Đóng gói quà tặng (miễn phí)" [ref=f3e167]
                - text: 🎁 Đóng gói quà tặng (miễn phí)
              - 'textbox "Lời chúc viết trên thiệp (VD: Chúc mừng sinh nhật!)" [disabled] [ref=f3e168]'
          - button "Xác nhận đặt hàng" [ref=f3e169] [cursor=pointer]
        - complementary [ref=f3e170]:
          - paragraph [ref=f3e171]: Đơn hàng
          - heading "Tóm tắt" [level=2] [ref=f3e172]
          - generic [ref=f3e174]:
            - generic [ref=f3e175]: Quần jeans Baggy Fade Blue x 1
            - strong [ref=f3e176]: 590.000đ
          - generic [ref=f3e177]:
            - generic [ref=f3e178]:
              - generic [ref=f3e179]: Tạm tính
              - strong [ref=f3e180]: 590.000đ
            - generic [ref=f3e181]:
              - generic [ref=f3e182]: Phí vận chuyển
              - strong [ref=f3e183]: 0đ
            - generic [ref=f3e184]:
              - generic [ref=f3e185]: Tổng cộng
              - strong [ref=f3e186]: 590.000đ
  - contentinfo [ref=f3e187]:
    - generic [ref=f3e188]:
      - generic [ref=f3e189]:
        - heading "HUUGIAU Atelier" [level=3] [ref=f3e190]
        - paragraph [ref=f3e191]: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
        - paragraph [ref=f3e192]:
          - generic [aria-hidden] [ref=f3e193]: 
          - text: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
        - generic [ref=f3e194]:
          - link "Instagram" [ref=f3e195] [cursor=pointer]:
            - /url: https://www.instagram.com/
            - generic [aria-hidden] [ref=f3e196]: 
          - link "Facebook" [ref=f3e197] [cursor=pointer]:
            - /url: https://www.facebook.com/
            - generic [aria-hidden] [ref=f3e198]: 
          - link "TikTok" [ref=f3e199] [cursor=pointer]:
            - /url: https://www.tiktok.com/
            - generic [aria-hidden] [ref=f3e200]: 
        - generic [ref=f3e201]:
          - textbox "Email nhận tin" [ref=f3e202]:
            - /placeholder: Nhận tin khuyến mãi...
          - button "" [ref=f3e203] [cursor=pointer]
      - generic [ref=f3e205]:
        - heading "Hỗ trợ" [level=3] [ref=f3e206]
        - list [ref=f3e207]:
          - listitem [ref=f3e208]:
            - link "Tra cứu đơn hàng" [ref=f3e209] [cursor=pointer]:
              - /url: /tra-cuu-don/
          - listitem [ref=f3e210]:
            - link "Đơn hàng của tôi" [ref=f3e211] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
          - listitem [ref=f3e212]:
            - link "Chính sách đổi trả" [ref=f3e213] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
          - listitem [ref=f3e214]:
            - link "Hướng dẫn chọn size" [ref=f3e215] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f3e216]:
            - link "Chất liệu & bảo quản" [ref=f3e217] [cursor=pointer]:
              - /url: /chat-lieu-bao-quan/
          - listitem [ref=f3e218]:
            - link "Khuyến mãi" [ref=f3e219] [cursor=pointer]:
              - /url: /khuyen-mai/
          - listitem [ref=f3e220]:
            - link "Câu hỏi thường gặp" [ref=f3e221] [cursor=pointer]:
              - /url: /hoi-dap-chung/
        - paragraph [ref=f3e222]:
          - text: "Hotline:"
          - link "0932047365" [ref=f3e223] [cursor=pointer]:
            - /url: tel:0932047365
          - text: · 9:00–21:30 mỗi ngày
      - generic [ref=f3e224]:
        - heading "Danh mục" [level=3] [ref=f3e225]
        - list [ref=f3e226]:
          - listitem [ref=f3e227]:
            - link "Áo" [ref=f3e228] [cursor=pointer]:
              - /url: /?category=ao
          - listitem [ref=f3e229]:
            - link "Quần" [ref=f3e230] [cursor=pointer]:
              - /url: /?category=quan
          - listitem [ref=f3e231]:
            - link "Phụ kiện" [ref=f3e232] [cursor=pointer]:
              - /url: /?category=phu-kien
          - listitem [ref=f3e233]:
            - link "Hàng mới về" [ref=f3e234] [cursor=pointer]:
              - /url: /?sort=newest
          - listitem [ref=f3e235]:
            - link "Tất cả sản phẩm" [ref=f3e236] [cursor=pointer]:
              - /url: /
      - generic [ref=f3e237]:
        - heading "Về HUUGIAU" [level=3] [ref=f3e238]
        - list [ref=f3e239]:
          - listitem [ref=f3e240]:
            - link "Câu chuyện thương hiệu" [ref=f3e241] [cursor=pointer]:
              - /url: /ve-chung-toi/
          - listitem [ref=f3e242]:
            - link "Hướng dẫn chọn size" [ref=f3e243] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f3e244]:
            - link "Tuyển dụng" [ref=f3e245] [cursor=pointer]:
              - /url: /tuyen-dung/
          - listitem [ref=f3e246]:
            - link "Liên hệ" [ref=f3e247] [cursor=pointer]:
              - /url: /lien-he/
          - listitem [ref=f3e248]:
            - link "Lookbook" [ref=f3e249] [cursor=pointer]:
              - /url: /lookbook/
    - generic [ref=f3e250]:
      - generic [ref=f3e251]:
        - generic [ref=f3e252]:
          - generic [ref=f3e253]: © 2026 HUUGIAU Atelier
          - link "Chính sách bảo mật" [ref=f3e254] [cursor=pointer]:
            - /url: /chinh-sach-bao-mat/
          - link "Điều khoản" [ref=f3e255] [cursor=pointer]:
            - /url: /dieu-khoan/
        - generic [ref=f3e256]:
          - generic "Visa" [ref=f3e257]: 
          - generic "Mastercard" [ref=f3e258]: 
          - generic "PayPal" [ref=f3e259]: 
          - generic "Chuyển khoản ngân hàng" [ref=f3e260]: 
          - generic "COD" [ref=f3e261]: 
      - generic [ref=f3e262]: "MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
  - button "Mở hỗ trợ mua hàng" [ref=f3e263] [cursor=pointer]:
    - generic [aria-hidden] [ref=f3e264]: 
  - dialog [aria-hidden] [ref=f3e265]:
    - generic [ref=f3e266]:
      - heading [level=3] [ref=f3e267]: Giỏ hàng (0)
      - button [ref=f3e268] [cursor=pointer]: ×
    - generic [ref=f3e270]:
      - generic [ref=f3e271]:
        - generic [ref=f3e272]: Tạm tính
        - strong [ref=f3e273]: 0đ
      - generic [ref=f3e274]:
        - link [ref=f3e275] [cursor=pointer]:
          - /url: /gio-hang/
          - text: Xem giỏ hàng
        - link [ref=f3e276] [cursor=pointer]:
          - /url: /thanh-toan/
          - text: Thanh toán
  - text: 
  - dialog [ref=f3e277]:
    - generic [ref=f3e278]:
      - generic [ref=f3e279]:
        - strong [ref=f3e280]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=f3e281]:
        - button "Tùy chỉnh" [ref=f3e282] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=f3e283] [cursor=pointer]
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
  54 |     await expect(page.locator('form')).toBeVisible();
  55 |   });
  56 | 
  57 |   test('should fill checkout form', async ({ page }) => {
  58 |     await page.goto(`${BASE_URL}/thanh-toan/`);
  59 |     
  60 |     // Fill required fields
> 61 |     await page.fill('input[name="customer_name"]', 'Test User');
     |                ^ Error: page.fill: Test timeout of 30000ms exceeded.
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