# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin.spec.ts >> Admin Dashboard >> should print invoice
- Location: tests\admin.spec.ts:65:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.waitForEvent: Test timeout of 30000ms exceeded.
=========================== logs ===========================
waiting for event "popup"
============================================================
```

# Page snapshot

```yaml
- generic [active] [ref=f2e1]:
  - generic [ref=f2e2]:
    - text: Chào mùa mới —
    - strong [ref=f2e3]: giảm thêm 10%
    - text: cho đơn từ 800K, mã
    - strong [ref=f2e4]: FREESHIP20K
    - text: · Freeship toàn quốc từ 499K
  - banner [ref=f2e5]:
    - generic [ref=f2e6]:
      - generic [ref=f2e7]:
        - button "Menu" [ref=f2e8] [cursor=pointer]
        - generic [ref=f2e10]:
          - link "Trang chủ" [ref=f2e11] [cursor=pointer]:
            - /url: /
            - text: HUUGIAU
          - generic [ref=f2e12]: ATELIER / FASHION STUDIO
      - navigation "Điều hướng chính" [ref=f2e13]:
        - generic [ref=f2e14]:
          - generic [ref=f2e15]:
            - link "HUUGIAU" [ref=f2e16] [cursor=pointer]:
              - /url: /
            - button "Đóng menu" [ref=f2e17] [cursor=pointer]
          - textbox "Tìm kiếm..." [ref=f2e24]
          - generic [ref=f2e25]:
            - generic [ref=f2e26]: Danh mục
            - link "New in" [ref=f2e27] [cursor=pointer]:
              - /url: /?sort=newest
            - link "Áo" [ref=f2e31] [cursor=pointer]:
              - /url: /?category=ao
            - link "Quần" [ref=f2e35] [cursor=pointer]:
              - /url: /?category=quan
            - link "Phụ kiện" [ref=f2e41] [cursor=pointer]:
              - /url: /?category=phu-kien
            - link "Lookbook" [ref=f2e44] [cursor=pointer]:
              - /url: /lookbook/
          - generic [ref=f2e49]:
            - generic [ref=f2e50]: Cửa hàng
            - link "Câu chuyện thương hiệu" [ref=f2e51] [cursor=pointer]:
              - /url: /ve-chung-toi/
            - link "Khuyến mãi" [ref=f2e54] [cursor=pointer]:
              - /url: /khuyen-mai/
            - link "Liên hệ" [ref=f2e57] [cursor=pointer]:
              - /url: /lien-he/
            - link "Chính sách đổi trả" [ref=f2e61] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
            - link "Hỏi đáp" [ref=f2e65] [cursor=pointer]:
              - /url: /hoi-dap-chung/
          - generic [ref=f2e69]:
            - generic [ref=f2e70]: Tài khoản
            - link "Hồ sơ" [ref=f2e71] [cursor=pointer]:
              - /url: /tai-khoan/
            - link "Đơn hàng" [ref=f2e75] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
            - link "Yêu thích" [ref=f2e79] [cursor=pointer]:
              - /url: /yeu-thich/
            - link "Đăng xuất" [ref=f2e82] [cursor=pointer]:
              - /url: /dang-xuat/
          - link "Giỏ hàng" [ref=f2e86] [cursor=pointer]:
            - /url: /gio-hang/
          - generic [ref=f2e90]:
            - generic [ref=f2e91]: Quản trị
            - link "Bảng điều khiển" [ref=f2e92] [cursor=pointer]:
              - /url: /admin-dashboard/
            - link "Quản trị" [ref=f2e98] [cursor=pointer]:
              - /url: /admin/
          - generic [ref=f2e102]: HUUGIAU Atelier © 2026
      - generic [ref=f2e103]:
        - generic [ref=f2e104]:
          - text: 
          - textbox "Tìm áo, quần, phụ kiện..." [ref=f2e105]
        - link "Giỏ hàng" [ref=f2e106] [cursor=pointer]:
          - /url: /gio-hang/
          - generic [aria-hidden] [ref=f2e107]: 
          - generic [ref=f2e108]: "0"
        - link "Yêu thích" [ref=f2e109] [cursor=pointer]:
          - /url: /yeu-thich/
          - generic [aria-hidden] [ref=f2e110]: 
        - group [ref=f2e111]:
          - generic "Tài khoản" [ref=f2e112] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e113]: 
            - generic [aria-hidden] [ref=f2e115]: 
  - main [ref=f2e116]:
    - generic [ref=f2e117]:
      - complementary [ref=f2e118]:
        - generic [ref=f2e119]:
          - generic [ref=f2e120]: HG
          - generic [ref=f2e121]:
            - strong [ref=f2e122]: HUUGIAU Studio
            - generic [ref=f2e123]: Bảng điều khiển quản trị
        - navigation "Điều hướng quản trị" [ref=f2e124]:
          - generic [ref=f2e125]: Điều hướng
          - button " Tổng quan" [ref=f2e126] [cursor=pointer]:
            - generic [ref=f2e127]: 
            - text: Tổng quan
          - button " Thêm sản phẩm" [ref=f2e128] [cursor=pointer]:
            - generic [ref=f2e129]: 
            - text: Thêm sản phẩm
          - button " Sản phẩm" [ref=f2e130] [cursor=pointer]:
            - generic [ref=f2e131]: 
            - text: Sản phẩm
          - button " Kho hàng" [ref=f2e132] [cursor=pointer]:
            - generic [ref=f2e133]: 
            - text: Kho hàng
          - button " Báo cáo" [ref=f2e134] [cursor=pointer]:
            - generic [ref=f2e135]: 
            - text: Báo cáo
          - button " Đơn hàng" [ref=f2e136] [cursor=pointer]:
            - generic [ref=f2e137]: 
            - text: Đơn hàng
          - button " Mã giảm giá" [ref=f2e138] [cursor=pointer]:
            - generic [ref=f2e139]: 
            - text: Mã giảm giá
          - button " Nhân viên & Phân quyền" [ref=f2e140] [cursor=pointer]:
            - generic [ref=f2e141]: 
            - text: Nhân viên & Phân quyền
          - link " Xuất đơn hàng" [ref=f2e142] [cursor=pointer]:
            - /url: /admin-dashboard/xuat-don/
            - generic [ref=f2e143]: 
            - text: Xuất đơn hàng
        - generic [ref=f2e144]:
          - generic [ref=f2e145]:
            - generic [ref=f2e146]: AD
            - generic [ref=f2e147]:
              - strong [ref=f2e148]: admin
              - generic [ref=f2e149]: Quản trị viên
          - link " Về trang chủ" [ref=f2e150] [cursor=pointer]:
            - /url: /
            - generic [ref=f2e151]: 
            - text: Về trang chủ
          - link " Đăng xuất" [ref=f2e152] [cursor=pointer]:
            - /url: /dang-xuat/
            - generic [ref=f2e153]: 
            - text: Đăng xuất
      - generic [ref=f2e154]:
        - generic [ref=f2e155]:
          - generic [ref=f2e156]:
            - paragraph [ref=f2e157]: STUDIO CONTROL PANEL
            - heading "Bảng điều khiển" [level=1] [ref=f2e158]
            - paragraph [ref=f2e159]: Đơn hàng, doanh thu, tồn kho và sản phẩm — gom thành một bảng điều khiển.
          - generic [ref=f2e160]:
            - generic [ref=f2e161]:
              - generic [ref=f2e162]: 
              - text: 09/09/2026
            - generic [ref=f2e163]:
              - generic [ref=f2e164]: 
              - text: 5 mã giảm giá đang hoạt động
        - generic [ref=f2e165]:
          - generic [ref=f2e166]:
            - article [ref=f2e167]:
              - generic [ref=f2e168]: 
              - generic [ref=f2e170]:
                - generic [ref=f2e171]: Doanh thu tháng
                - strong [ref=f2e172]: 0đ
                - generic [ref=f2e173]: Đơn hoàn thành từ đầu tháng
            - article [ref=f2e174]:
              - generic [ref=f2e175]: 
              - generic [ref=f2e177]:
                - generic [ref=f2e178]: Đơn hôm nay
                - strong [ref=f2e179]: "5"
                - generic [ref=f2e180]: Doanh thu 0đ
            - article [ref=f2e181]:
              - generic [ref=f2e182]: 
              - generic [ref=f2e184]:
                - generic [ref=f2e185]: Tồn kho thấp
                - strong [ref=f2e186]: "3"
                - generic [ref=f2e187]: Sản phẩm còn lại ≤ 5
            - article [ref=f2e188]:
              - generic [ref=f2e189]: 
              - generic [ref=f2e191]:
                - generic [ref=f2e192]: Tài khoản mới
                - strong [ref=f2e193]: "2"
                - generic [ref=f2e194]: Đăng ký trong hôm nay
          - generic [ref=f2e195]:
            - generic [ref=f2e196]:
              - generic [ref=f2e197]:
                - paragraph [ref=f2e198]: Trạng thái đơn hàng
                - heading "Luồng xử lý đơn" [level=2] [ref=f2e199]
              - generic [ref=f2e200]:
                - strong [ref=f2e201]: "605"
                - text: Tổng đơn
            - generic [ref=f2e208]:
              - generic [ref=f2e209]: Chờ xử lý 5
              - generic [ref=f2e211]: Đang xử lý 91
              - generic [ref=f2e213]: Đang giao 0
              - generic [ref=f2e215]: Hoàn thành 332
              - generic [ref=f2e217]: Đã hủy 177
          - article [ref=f2e219]:
            - generic [ref=f2e220]:
              - generic [ref=f2e221]:
                - paragraph [ref=f2e222]: Phân tích
                - heading "Thống kê cửa hàng" [level=2] [ref=f2e223]
              - tablist "Chuyển biểu đồ" [ref=f2e224]:
                - tab "Doanh thu" [selected] [ref=f2e225] [cursor=pointer]
                - tab "Đơn hàng" [ref=f2e226] [cursor=pointer]
                - tab "Bán chạy" [ref=f2e227] [cursor=pointer]
                - tab "Theo danh mục" [ref=f2e228] [cursor=pointer]
                - tab "Theo trạng thái" [ref=f2e229] [cursor=pointer]
                - tab "Tỷ trọng" [ref=f2e230] [cursor=pointer]
            - generic [ref=f2e232]:
              - heading "Doanh thu 7 ngày" [level=3] [ref=f2e233]
              - generic [ref=f2e234]:
                - generic [ref=f2e235]:
                  - generic [ref=f2e236]: 
                  - text: Giảm 100% so với 7 ngày trước
                - strong [ref=f2e237]: 0đ
                - generic [ref=f2e238]: 7 ngày gần nhất
              - generic [ref=f2e239]:
                - generic [ref=f2e240]:
                  - strong [ref=f2e243]: 0đ
                  - generic [ref=f2e244]: T5 03/09
                - generic [ref=f2e245]:
                  - strong [ref=f2e248]: 0đ
                  - generic [ref=f2e249]: T6 04/09
                - generic [ref=f2e250]:
                  - strong [ref=f2e253]: 0đ
                  - generic [ref=f2e254]: T7 05/09
                - generic [ref=f2e255]:
                  - strong [ref=f2e258]: 0đ
                  - generic [ref=f2e259]: CN 06/09
                - generic [ref=f2e260]:
                  - strong [ref=f2e263]: 0đ
                  - generic [ref=f2e264]: T2 07/09
                - generic [ref=f2e265]:
                  - strong [ref=f2e268]: 0đ
                  - generic [ref=f2e269]: T3 08/09
                - generic [ref=f2e270]:
                  - strong [ref=f2e273]: 0đ
                  - generic [ref=f2e274]: T4 09/09
          - generic [ref=f2e275]:
            - article [ref=f2e276]:
              - generic [ref=f2e278]:
                - heading "Tồn kho thấp" [level=2] [ref=f2e279]
                - paragraph [ref=f2e280]: Nên bổ sung sớm để không mất đơn.
              - generic [ref=f2e281]:
                - generic [ref=f2e282]:
                  - generic [ref=f2e283]:
                    - generic [ref=f2e284]: "?"
                    - generic [ref=f2e285]:
                      - strong [ref=f2e286]: Móc khóa Carabiner
                      - generic [ref=f2e287]: Phụ Kiện
                  - generic [ref=f2e288]: Còn 0
                - generic [ref=f2e289]:
                  - generic [ref=f2e290]:
                    - generic [ref=f2e291]: "?"
                    - generic [ref=f2e292]:
                      - strong [ref=f2e293]: Áo thun Graphic No.01
                      - generic [ref=f2e294]: Áo
                  - generic [ref=f2e295]: Còn 3
                - generic [ref=f2e296]:
                  - generic [ref=f2e297]:
                    - generic [ref=f2e298]: "?"
                    - generic [ref=f2e299]:
                      - strong [ref=f2e300]: Áo khoác bomber Mono
                      - generic [ref=f2e301]: Áo
                  - generic [ref=f2e302]: Còn 4
            - article [ref=f2e303]:
              - generic [ref=f2e304]:
                - generic [ref=f2e305]:
                  - heading "Đơn hàng gần đây" [level=2] [ref=f2e306]
                  - paragraph [ref=f2e307]: 5 đơn mới nhất.
                - button "Xem tất cả" [ref=f2e308] [cursor=pointer]
              - generic [ref=f2e309]:
                - link "#50759 Test QR Chờ xử lý 590.000đ" [ref=f2e310] [cursor=pointer]:
                  - /url: /don-hang/50759/xem-lai/
                  - generic [ref=f2e311]:
                    - strong [ref=f2e312]: "#50759"
                    - generic [ref=f2e313]: Test QR
                  - generic [ref=f2e314]: Chờ xử lý
                  - strong [ref=f2e315]: 590.000đ
                - link "#50758 Test Bank Chờ xử lý 590.000đ" [ref=f2e316] [cursor=pointer]:
                  - /url: /don-hang/50758/xem-lai/
                  - generic [ref=f2e317]:
                    - strong [ref=f2e318]: "#50758"
                    - generic [ref=f2e319]: Test Bank
                  - generic [ref=f2e320]: Chờ xử lý
                  - strong [ref=f2e321]: 590.000đ
                - link "#50757 Test COD Chờ xử lý 590.000đ" [ref=f2e322] [cursor=pointer]:
                  - /url: /don-hang/50757/xem-lai/
                  - generic [ref=f2e323]:
                    - strong [ref=f2e324]: "#50757"
                    - generic [ref=f2e325]: Test COD
                  - generic [ref=f2e326]: Chờ xử lý
                  - strong [ref=f2e327]: 590.000đ
                - link "#50756 Test Bank Chờ xử lý 590.000đ" [ref=f2e328] [cursor=pointer]:
                  - /url: /don-hang/50756/xem-lai/
                  - generic [ref=f2e329]:
                    - strong [ref=f2e330]: "#50756"
                    - generic [ref=f2e331]: Test Bank
                  - generic [ref=f2e332]: Chờ xử lý
                  - strong [ref=f2e333]: 590.000đ
                - link "#50755 Test COD Chờ xử lý 590.000đ" [ref=f2e334] [cursor=pointer]:
                  - /url: /don-hang/50755/xem-lai/
                  - generic [ref=f2e335]:
                    - strong [ref=f2e336]: "#50755"
                    - generic [ref=f2e337]: Test COD
                  - generic [ref=f2e338]: Chờ xử lý
                  - strong [ref=f2e339]: 590.000đ
        - text:      
  - contentinfo [ref=f2e340]:
    - generic [ref=f2e341]:
      - generic [ref=f2e342]:
        - heading "HUUGIAU Atelier" [level=3] [ref=f2e343]
        - paragraph [ref=f2e344]: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
        - paragraph [ref=f2e345]:
          - generic [aria-hidden] [ref=f2e346]: 
          - text: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
        - generic [ref=f2e347]:
          - link "Instagram" [ref=f2e348] [cursor=pointer]:
            - /url: https://www.instagram.com/
            - generic [aria-hidden] [ref=f2e349]: 
          - link "Facebook" [ref=f2e350] [cursor=pointer]:
            - /url: https://www.facebook.com/
            - generic [aria-hidden] [ref=f2e351]: 
          - link "TikTok" [ref=f2e352] [cursor=pointer]:
            - /url: https://www.tiktok.com/
            - generic [aria-hidden] [ref=f2e353]: 
        - generic [ref=f2e354]:
          - textbox "Email nhận tin" [ref=f2e355]:
            - /placeholder: Nhận tin khuyến mãi...
          - button "" [ref=f2e356] [cursor=pointer]
      - generic [ref=f2e358]:
        - heading "Hỗ trợ" [level=3] [ref=f2e359]
        - list [ref=f2e360]:
          - listitem [ref=f2e361]:
            - link "Tra cứu đơn hàng" [ref=f2e362] [cursor=pointer]:
              - /url: /tra-cuu-don/
          - listitem [ref=f2e363]:
            - link "Đơn hàng của tôi" [ref=f2e364] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
          - listitem [ref=f2e365]:
            - link "Chính sách đổi trả" [ref=f2e366] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
          - listitem [ref=f2e367]:
            - link "Hướng dẫn chọn size" [ref=f2e368] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f2e369]:
            - link "Chất liệu & bảo quản" [ref=f2e370] [cursor=pointer]:
              - /url: /chat-lieu-bao-quan/
          - listitem [ref=f2e371]:
            - link "Khuyến mãi" [ref=f2e372] [cursor=pointer]:
              - /url: /khuyen-mai/
          - listitem [ref=f2e373]:
            - link "Câu hỏi thường gặp" [ref=f2e374] [cursor=pointer]:
              - /url: /hoi-dap-chung/
        - paragraph [ref=f2e375]:
          - text: "Hotline:"
          - link "0932047365" [ref=f2e376] [cursor=pointer]:
            - /url: tel:0932047365
          - text: · 9:00–21:30 mỗi ngày
      - generic [ref=f2e377]:
        - heading "Danh mục" [level=3] [ref=f2e378]
        - list [ref=f2e379]:
          - listitem [ref=f2e380]:
            - link "Áo" [ref=f2e381] [cursor=pointer]:
              - /url: /?category=ao
          - listitem [ref=f2e382]:
            - link "Quần" [ref=f2e383] [cursor=pointer]:
              - /url: /?category=quan
          - listitem [ref=f2e384]:
            - link "Phụ kiện" [ref=f2e385] [cursor=pointer]:
              - /url: /?category=phu-kien
          - listitem [ref=f2e386]:
            - link "Hàng mới về" [ref=f2e387] [cursor=pointer]:
              - /url: /?sort=newest
          - listitem [ref=f2e388]:
            - link "Tất cả sản phẩm" [ref=f2e389] [cursor=pointer]:
              - /url: /
      - generic [ref=f2e390]:
        - heading "Về HUUGIAU" [level=3] [ref=f2e391]
        - list [ref=f2e392]:
          - listitem [ref=f2e393]:
            - link "Câu chuyện thương hiệu" [ref=f2e394] [cursor=pointer]:
              - /url: /ve-chung-toi/
          - listitem [ref=f2e395]:
            - link "Hướng dẫn chọn size" [ref=f2e396] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f2e397]:
            - link "Tuyển dụng" [ref=f2e398] [cursor=pointer]:
              - /url: /tuyen-dung/
          - listitem [ref=f2e399]:
            - link "Liên hệ" [ref=f2e400] [cursor=pointer]:
              - /url: /lien-he/
          - listitem [ref=f2e401]:
            - link "Lookbook" [ref=f2e402] [cursor=pointer]:
              - /url: /lookbook/
    - generic [ref=f2e403]:
      - generic [ref=f2e404]:
        - generic [ref=f2e405]:
          - generic [ref=f2e406]: © 2026 HUUGIAU Atelier
          - link "Chính sách bảo mật" [ref=f2e407] [cursor=pointer]:
            - /url: /chinh-sach-bao-mat/
          - link "Điều khoản" [ref=f2e408] [cursor=pointer]:
            - /url: /dieu-khoan/
        - generic [ref=f2e409]:
          - generic "Visa" [ref=f2e410]: 
          - generic "Mastercard" [ref=f2e411]: 
          - generic "PayPal" [ref=f2e412]: 
          - generic "Chuyển khoản ngân hàng" [ref=f2e413]: 
          - generic "COD" [ref=f2e414]: 
      - generic [ref=f2e415]: "MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
  - button "Mở hỗ trợ mua hàng" [ref=f2e416] [cursor=pointer]:
    - generic [aria-hidden] [ref=f2e417]: 
  - dialog [aria-hidden] [ref=f2e418]:
    - generic [ref=f2e419]:
      - heading [level=3] [ref=f2e420]: Giỏ hàng (0)
      - button [ref=f2e421] [cursor=pointer]: ×
    - generic [ref=f2e423]:
      - generic [ref=f2e424]:
        - generic [ref=f2e425]: Tạm tính
        - strong [ref=f2e426]: 0đ
      - generic [ref=f2e427]:
        - link [ref=f2e428] [cursor=pointer]:
          - /url: /gio-hang/
          - text: Xem giỏ hàng
        - link [ref=f2e429] [cursor=pointer]:
          - /url: /thanh-toan/
          - text: Thanh toán
  - text: 
  - dialog [ref=f2e430]:
    - generic [ref=f2e431]:
      - generic [ref=f2e432]:
        - strong [ref=f2e433]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=f2e434]:
        - button "Tùy chỉnh" [ref=f2e435] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=f2e436] [cursor=pointer]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
  4  | 
  5  | test.describe('Admin Dashboard', () => {
  6  |   test.beforeEach(async ({ page }) => {
  7  |     // Login as admin
  8  |     await page.goto(`${BASE_URL}/dang-nhap/`);
  9  |     await page.fill('input[name="username"]', 'admin');
  10 |     await page.fill('input[name="password"]', 'admin123');
  11 |     await page.click('button[type="submit"]');
  12 |     await page.waitForURL(/^(?!.*dang-nhap).*/);
  13 |   });
  14 | 
  15 |   test('should access admin dashboard', async ({ page }) => {
  16 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  17 |     await expect(page.locator('h1')).toContainText(/Dashboard|Bảng điều khiển|Admin/);
  18 |   });
  19 | 
  20 |   test('should display order statistics', async ({ page }) => {
  21 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  22 |     
  23 |     await expect(page.locator('.stat-card, .stats-grid, .stat-value')).toBeVisible({ timeout: 10000 });
  24 |   });
  25 | 
  26 |   test('should filter orders', async ({ page }) => {
  27 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  28 |     
  29 |     const statusSelect = page.locator('select[name="status"], select#status');
  30 |     if (await statusSelect.isVisible()) {
  31 |       await statusSelect.selectOption('delivered');
  32 |       await page.click('button:has-text("Lọc"), button:has-text("Tìm kiếm")');
  33 |       await page.waitForTimeout(1000);
  34 |     }
  35 |   });
  36 | 
  37 |   test('should export orders CSV', async ({ page }) => {
  38 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  39 |     
  40 |     const exportBtn = page.locator('a[href*="xuat-don"], button:has-text("Xuất đơn")');
  41 |     if (await exportBtn.isVisible()) {
  42 |       const downloadPromise = page.waitForEvent('download');
  43 |       await exportBtn.click();
  44 |       const download = await downloadPromise;
  45 |       expect(download.suggestedFilename()).toMatch(/\.csv$/);
  46 |     }
  47 |   });
  48 | 
  49 |   test('should change order status', async ({ page }) => {
  50 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  51 |     
  52 |     const firstOrder = page.locator('tr[data-order-id], .order-row').first();
  53 |     if (await firstOrder.isVisible()) {
  54 |       await firstOrder.click();
  55 |       
  56 |       const statusSelect = page.locator('select[name="new_status"], select[name="status"]');
  57 |       if (await statusSelect.isVisible()) {
  58 |         await statusSelect.selectOption('shipping');
  59 |         await page.click('button:has-text("Cập nhật"), button:has-text("Lưu")');
  60 |         await expect(page.locator('.alert-success, .toast-success')).toBeVisible({ timeout: 5000 });
  61 |       }
  62 |     }
  63 |   });
  64 | 
  65 |   test('should print invoice', async ({ page }) => {
  66 |     await page.goto(`${BASE_URL}/admin-dashboard/`);
  67 |     
  68 |     const invoiceLink = page.locator('a[href*="in-hoa-don"], a:has-text("In")').first();
  69 |     if (await invoiceLink.isVisible()) {
> 70 |       const newPagePromise = page.waitForEvent('popup');
     |                                   ^ Error: page.waitForEvent: Test timeout of 30000ms exceeded.
  71 |       await invoiceLink.click();
  72 |       const newPage = await newPagePromise;
  73 |       await expect(newPage).toHaveURL(/\/in-hoa-don\//);
  74 |     }
  75 |   });
  76 | });
```