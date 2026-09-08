# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: products.spec.ts >> Product Browsing >> should search products
- Location: tests\products.spec.ts:86:7

# Error details

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /search|tim-kiem/
Received string:  "http://localhost:8000/?q=%C3%A1o"
Timeout: 5000ms

Call log:
  - Expect "toHaveURL" with timeout 5000ms
    11 × locator resolved to <html lang="vi">…</html>
       - unexpected value "http://localhost:8000/?q=%C3%A1o"

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
    - textbox "Tìm kiếm...": áo
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
  - textbox "Tìm áo, quần, phụ kiện...": áo
  - link "Giỏ hàng":
    - /url: /gio-hang/
    - text: "0"
  - link "Yêu thích":
    - /url: /yeu-thich/
  - group: Tài khoản
- main:
  - navigation "Bạn đang ở":
    - link "Trang chủ":
      - /url: /
    - text: / Danh mục
  - paragraph: TẤT CẢ SẢN PHẨM
  - heading "Catalog" [level=2]
  - paragraph: 62 sản phẩm đang có sẵn.
  - link "Mới nhất":
    - /url: /?q=%C3%A1o&sort=newest
  - link "Bán chạy":
    - /url: /?q=%C3%A1o&sort=bestseller
  - link "Giá thấp":
    - /url: /?q=%C3%A1o&sort=price_asc
  - link "Giá cao":
    - /url: /?q=%C3%A1o&sort=price_desc
  - link "Đánh giá cao":
    - /url: /?q=%C3%A1o&sort=rating
  - complementary:
    - heading "Bộ lọc" [level=3]
    - link "Xóa":
      - /url: /
    - text: Danh mục
    - link "Tất cả":
      - /url: /?q=%C3%A1o&sort=newest
    - link "Áo":
      - /url: /?q=%C3%A1o&category=ao
    - link "Phụ Kiện":
      - /url: /?q=%C3%A1o&category=phu-kien
    - link "Quần":
      - /url: /?q=%C3%A1o&category=quan
    - link "Test Cat":
      - /url: /?q=%C3%A1o&category=test-cat
    - text: Khoảng giá
    - textbox "Giá tối thiểu":
      - /placeholder: Từ
    - text: –
    - textbox "Giá tối đa":
      - /placeholder: Đến
    - text: Size
    - checkbox "S"
    - text: S
    - checkbox "M"
    - text: M
    - checkbox "L"
    - text: L
    - checkbox "XL"
    - text: XL
    - checkbox "XXL"
    - text: XXL
    - checkbox "FREE"
    - text: FREE Màu sắc
    - checkbox "Be"
    - text: Be
    - checkbox "Trắng"
    - text: Trắng
    - checkbox "Xám"
    - text: Xám
    - checkbox "Đen"
    - text: Đen
    - button "Áp dụng"
  - link "Mũ beret Pháp":
    - /url: /san-pham/76/mu-beret-phap/
    - img "Mũ beret Pháp"
    - paragraph: Phụ Kiện
    - heading "Mũ beret Pháp" [level=3]
    - text:      5
    - strong: 140.000đ
    - text: Đã bán 24 Xem chi tiết
  - button "So sánh Mũ beret Pháp": So sánh
  - link "Giày sneaker Platform":
    - /url: /san-pham/75/giay-sneaker-platform/
    - img "Giày sneaker Platform"
    - text: NỔI BẬT
    - paragraph: Phụ Kiện
    - heading "Giày sneaker Platform" [level=3]
    - text:      4
    - strong: 950.000đ
    - text: Đã bán 8 Xem chi tiết
  - button "So sánh Giày sneaker Platform": So sánh
  - link "Áo len cổ lọ Tight":
    - /url: /san-pham/74/ao-len-co-lo-tight/
    - img "Áo len cổ lọ Tight"
    - paragraph: Áo
    - heading "Áo len cổ lọ Tight" [level=3]
    - text:      4
    - strong: 420.000đ
    - text: Đã bán 15 Xem chi tiết
  - button "So sánh Áo len cổ lọ Tight": So sánh
  - link "Túi đeo hông Waist Bag":
    - /url: /san-pham/73/tui-deo-hong-waist-bag/
    - img "Túi đeo hông Waist Bag"
    - paragraph: Phụ Kiện
    - heading "Túi đeo hông Waist Bag" [level=3]
    - text:      4
    - strong: 280.000đ
    - text: Đã bán 15 Xem chi tiết
  - button "So sánh Túi đeo hông Waist Bag": So sánh
  - link "Áo polo Pique Basic":
    - /url: /san-pham/71/ao-polo-pique-basic/
    - img "Áo polo Pique Basic"
    - paragraph: Áo
    - heading "Áo polo Pique Basic" [level=3]
    - text:      4
    - strong: 340.000đ
    - text: Đã bán 9 Xem chi tiết
  - button "So sánh Áo polo Pique Basic": So sánh
  - link "Khăn choàng cổ Len":
    - /url: /san-pham/70/khan-choang-co-len/
    - img "Khăn choàng cổ Len"
    - paragraph: Phụ Kiện
    - heading "Khăn choàng cổ Len" [level=3]
    - text:      4
    - strong: 320.000đ
    - text: Đã bán 6 Xem chi tiết
  - button "So sánh Khăn choàng cổ Len": So sánh
  - link "Áo khoác dạ Cashmere":
    - /url: /san-pham/69/ao-khoac-da-cashmere/
    - img "Áo khoác dạ Cashmere"
    - paragraph: Áo
    - heading "Áo khoác dạ Cashmere" [level=3]
    - text:      4
    - strong: 1.200.000đ
    - text: Đã bán 15 Xem chi tiết
  - button "So sánh Áo khoác dạ Cashmere": So sánh
  - link "Quần tây ống côn Slim":
    - /url: /san-pham/68/quan-tay-ong-con-slim/
    - img "Quần tây ống côn Slim"
    - paragraph: Quần
    - heading "Quần tây ống côn Slim" [level=3]
    - text:      4
    - strong: 480.000đ
    - text: Đã bán 11 Xem chi tiết
  - button "So sánh Quần tây ống côn Slim": So sánh
  - link "Áo hoodie Zip Up":
    - /url: /san-pham/67/ao-hoodie-zip-up/
    - img "Áo hoodie Zip Up"
    - text: NỔI BẬT
    - paragraph: Áo
    - heading "Áo hoodie Zip Up" [level=3]
    - text:      4
    - strong: 650.000đ
    - text: Đã bán 23 Xem chi tiết
  - button "So sánh Áo hoodie Zip Up": So sánh
  - link "Vòng tay da Bracelet":
    - /url: /san-pham/66/vong-tay-da-bracelet/
    - img "Vòng tay da Bracelet"
    - paragraph: Phụ Kiện
    - heading "Vòng tay da Bracelet" [level=3]
    - text:      4
    - strong: 160.000đ
    - text: Đã bán 11 Xem chi tiết
  - button "So sánh Vòng tay da Bracelet": So sánh
  - link "Quần short kaki Basic":
    - /url: /san-pham/64/quan-short-kaki-basic/
    - img "Quần short kaki Basic"
    - paragraph: Quần
    - heading "Quần short kaki Basic" [level=3]
    - text:      4
    - strong: 350.000đ
    - text: Đã bán 10 Xem chi tiết
  - button "So sánh Quần short kaki Basic": So sánh
  - link "Áo sơ mi linen Relax":
    - /url: /san-pham/63/ao-so-mi-linen-relax/
    - img "Áo sơ mi linen Relax"
    - text: NỔI BẬT
    - paragraph: Áo
    - heading "Áo sơ mi linen Relax" [level=3]
    - text:      4
    - strong: 380.000đ
    - text: Đã bán 17 Xem chi tiết
  - button "So sánh Áo sơ mi linen Relax": So sánh
  - text: "1"
  - link "2":
    - /url: "?page=2&q=%C3%A1o"
  - link "3":
    - /url: "?page=3&q=%C3%A1o"
  - link "Sau":
    - /url: "?page=2&q=%C3%A1o"
    - text: Sau
    - img
  - dialog "Xem nhanh sản phẩm":
    - button "Đóng": ×
    - heading [level=3]
    - paragraph
    - strong
    - link "Xem chi tiết":
      - /url: "#"
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
  5  | test.describe('Product Browsing', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     await page.goto(`${BASE_URL}/`);
  8  |   });
  9  | 
  10 |   test('should display home page with products', async ({ page }) => {
  11 |     await expect(page.locator('h1, .hero, .product-grid, .products')).toBeVisible({ timeout: 10000 });
  12 |   });
  13 | 
  14 |   test('should navigate to product detail', async ({ page }) => {
  15 |     // Click first product link
  16 |     const productLink = page.locator('a[href*="/san-pham/"]').first();
  17 |     await expect(productLink).toBeVisible();
  18 |     await productLink.click();
  19 |     
  20 |     // Should be on product detail page
  21 |     await expect(page).toHaveURL(/\/san-pham\/\d+\//);
  22 |     await expect(page.locator('h1')).toBeVisible();
  23 |   });
  24 | 
  25 |   test('should display product images', async ({ page }) => {
  26 |     await page.goto(`${BASE_URL}/`);
  27 |     const productLink = page.locator('a[href*="/san-pham/"]').first();
  28 |     await productLink.click();
  29 |     
  30 |     // Main image should be visible
  31 |     await expect(page.locator('#detail-main-image, .product-image img')).toBeVisible();
  32 |   });
  33 | 
  34 |   test('should select variant (color/size)', async ({ page }) => {
  35 |     await page.goto(`${BASE_URL}/`);
  36 |     const productLink = page.locator('a[href*="/san-pham/"]').first();
  37 |     await productLink.click();
  38 |     
  39 |     // Wait for variant picker
  40 |     await page.waitForSelector('[data-variant-color], [data-variant-size]', { timeout: 5000 });
  41 |     
  42 |     // Click first color if available
  43 |     const colorBtn = page.locator('[data-variant-color]').first();
  44 |     if (await colorBtn.isVisible()) {
  45 |       await colorBtn.click();
  46 |     }
  47 |     
  48 |     // Click first size if available
  49 |     const sizeBtn = page.locator('[data-variant-size]').first();
  50 |     if (await sizeBtn.isVisible()) {
  51 |       await sizeBtn.click();
  52 |     }
  53 |     
  54 |     // Variant ID should be set
  55 |     const variantInput = page.locator('#variant-id-input');
  56 |     await expect(variantInput).toHaveValue(/\d+/);
  57 |   });
  58 | 
  59 |   test('should add to cart', async ({ page }) => {
  60 |     await page.goto(`${BASE_URL}/`);
  61 |     const productLink = page.locator('a[href*="/san-pham/"]').first();
  62 |     await productLink.click();
  63 |     
  64 |     // Select variant if needed
  65 |     const sizeBtn = page.locator('[data-variant-size]').first();
  66 |     if (await sizeBtn.isVisible()) {
  67 |       await sizeBtn.click();
  68 |     }
  69 |     
  70 |     // Click add to cart
  71 |     await page.click('button:has-text("Thêm vào giỏ"), button[name="add_to_cart"], button:has-text("Mua ngay")');
  72 |     
  73 |     // Should show success message or redirect to cart
  74 |     await expect(page.locator('.alert-success, .toast-success, .cart-count, .icon-count')).toBeVisible({ timeout: 5000 });
  75 |   });
  76 | 
  77 |   test('should filter by category', async ({ page }) => {
  78 |     // Click category link if available
  79 |     const categoryLink = page.locator('a[href*="category"], a[href*="danh-muc"]').first();
  80 |     if (await categoryLink.isVisible()) {
  81 |       await categoryLink.click();
  82 |       await expect(page).toHaveURL(/category|danh-muc/);
  83 |     }
  84 |   });
  85 | 
  86 |   test('should search products', async ({ page }) => {
  87 |     const searchInput = page.locator('input[name="q"], input[placeholder*="tìm"], input[placeholder*="search"]').first();
  88 |     if (await searchInput.isVisible()) {
  89 |       await searchInput.fill('áo');
  90 |       await searchInput.press('Enter');
> 91 |       await expect(page).toHaveURL(/search|tim-kiem/);
     |                          ^ Error: expect(page).toHaveURL(expected) failed
  92 |     }
  93 |   });
  94 | });
```