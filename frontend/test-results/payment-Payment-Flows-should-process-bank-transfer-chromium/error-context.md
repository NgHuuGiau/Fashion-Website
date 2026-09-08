# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: payment.spec.ts >> Payment Flows >> should process bank transfer
- Location: tests\payment.spec.ts:46:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /\/cho-thanh-toan-ngan-hang\//
Received string:  "http://localhost:8000/dat-hang-thanh-cong/50760/"

Call log:
  - Expect "toHaveURL" with timeout 5000ms
    3 × locator resolved to <html lang="vi">…</html>
      - unexpected value "http://localhost:8000/dat-hang-thanh-cong/50760/"
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
    - link "Giỏ hàng":
      - /url: /gio-hang/
      - img
      - text: Giỏ hàng
    - text: HUUGIAU Atelier © 2026
  - text: 
  - textbox "Tìm áo, quần, phụ kiện..."
  - link "Giỏ hàng":
    - /url: /gio-hang/
    - text: "0"
  - link "Yêu thích":
    - /url: /yeu-thich/
  - group: Tài khoản
- main:
  - text: Đặt hàng thành công. 
  - paragraph: Đặt hàng thành công
  - heading "Cảm ơn bạn!" [level=1]
  - paragraph:
    - text: Đơn hàng
    - strong: "#50760"
    - text: đã được tạo.
  - text: Phương thức
  - strong: Thanh toán khi nhận hàng
  - text: Trạng thái
  - strong: Chờ xử lý
  - text: Tổng thanh toán
  - strong: 590.000đ
  - text: Người nhận
  - strong: Test Bank
  - link " Xem đơn hàng":
    - /url: /don-hang-cua-toi/
  - link " Mua thêm":
    - /url: /
  - heading " Những điều cần biết" [level=3]
  - list:
    - listitem: Đơn hàng sẽ được xử lý sau khi shop xác nhận thanh toán.
    - listitem: Thời gian giao hàng dự kiến từ 2-5 ngày tùy khu vực.
    - listitem:
      - text: Bạn có thể theo dõi trạng thái đơn hàng trong mục
      - link "Đơn hàng của tôi":
        - /url: /don-hang-cua-toi/
      - text: .
    - listitem: Nếu cần hỗ trợ, hãy dùng chat hoặc liên hệ shop.
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
  5  | test.describe('Payment Flows', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     // Add to cart and go to checkout
  8  |     await page.goto(`${BASE_URL}/`);
  9  |     const productLink = page.locator('a[href*="/san-pham/"]').first();
  10 |     await productLink.click();
  11 |     
  12 |     const sizeBtn = page.locator('[data-variant-size]').first();
  13 |     if (await sizeBtn.isVisible()) {
  14 |       await sizeBtn.click();
  15 |     }
  16 |     
  17 |     await page.click('button:has-text("Thêm vào giỏ"), button[name="add_to_cart"]');
  18 |     await page.waitForTimeout(1000);
  19 |     await page.goto(`${BASE_URL}/thanh-toan/`);
  20 |     
  21 |     // Fill minimum required fields
  22 |     await page.fill('input[name="customer_name"]', 'Test User');
  23 |     await page.fill('input[name="customer_email"]', 'test@example.com');
  24 |     await page.fill('input[name="phone"]', '0901234567');
  25 |     await page.fill('textarea[name="shipping_address"]', '123 Test Street');
  26 |   });
  27 | 
  28 |   test('should process COD order', async ({ page }) => {
  29 |     await page.fill('input[name="customer_name"]', 'Test COD');
  30 |     await page.fill('input[name="customer_email"]', 'cod@test.com');
  31 |     await page.fill('input[name="phone"]', '0901234567');
  32 |     await page.fill('textarea[name="shipping_address"]', '123 COD Street');
  33 |     
  34 |     // Select COD
  35 |     const codRadio = page.locator('input[name="payment_method"][value="cod"]');
  36 |     if (await codRadio.isVisible()) {
  37 |       await codRadio.check();
  38 |     }
  39 |     
  40 |     await page.click('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Đặt hàng")');
  41 |     
  42 |     // Should redirect to success page
  43 |     await expect(page).toHaveURL(/\/dat-hang-thanh-cong\//);
  44 |   });
  45 | 
  46 |   test('should process bank transfer', async ({ page }) => {
  47 |     await page.fill('input[name="customer_name"]', 'Test Bank');
  48 |     await page.fill('input[name="customer_email"]', 'bank@test.com');
  49 |     await page.fill('input[name="phone"]', '0901234567');
  50 |     await page.fill('textarea[name="shipping_address"]', '123 Bank Street');
  51 |     
  52 |     // Select bank transfer
  53 |     const bankRadio = page.locator('input[name="payment_method"][value="bank"]');
  54 |     if (await bankRadio.isVisible()) {
  55 |       await bankRadio.check();
  56 |     }
  57 |     
  58 |     // Select bank if dropdown
  59 |     const bankSelect = page.locator('select[name="bank_code"]');
  60 |     if (await bankSelect.isVisible()) {
  61 |       await bankSelect.selectOption({ index: 1 });
  62 |     }
  63 |     
  64 |     await page.click('button[type="submit"]:has-text("Đặt hàng"), button:has-text("Đặt hàng")');
  65 |     
  66 |     // Should redirect to bank payment waiting page
> 67 |     await expect(page).toHaveURL(/\/cho-thanh-toan-ngan-hang\//);
     |                        ^ Error: expect(page).toHaveURL(expected) failed
  68 |   });
  69 | 
  70 |   test('should show QR code for bank transfer', async ({ page }) => {
  71 |     await page.fill('input[name="customer_name"]', 'Test QR');
  72 |     await page.fill('input[name="customer_email"]', 'qr@test.com');
  73 |     await page.fill('input[name="phone"]', '0901234567');
  74 |     await page.fill('textarea[name="shipping_address"]', '123 QR Street');
  75 |     
  76 |     const bankRadio = page.locator('input[name="payment_method"][value="bank"]');
  77 |     if (await bankRadio.isVisible()) {
  78 |       await bankRadio.check();
  79 |     }
  80 |     
  81 |     await page.click('button[type="submit"]:has-text("Đặt hàng")');
  82 |     await expect(page).toHaveURL(/\/cho-thanh-toan-ngan-hang\//);
  83 |     
  84 |     // Click view QR
  85 |     await page.click('a:has-text("QR"), a[href*="qr-thanh-toan"]');
  86 |     
  87 |     await expect(page.locator('img[src*="qr"], canvas, .qr-code')).toBeVisible({ timeout: 5000 });
  88 |   });
  89 | });
```