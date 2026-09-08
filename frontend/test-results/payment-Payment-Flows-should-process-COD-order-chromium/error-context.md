# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: payment.spec.ts >> Payment Flows >> should process COD order
- Location: tests\payment.spec.ts:28:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('input[name="customer_name"]')

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
            - link "Đăng nhập" [ref=f2e71] [cursor=pointer]:
              - /url: /dang-nhap/
            - link "Đăng ký" [ref=f2e75] [cursor=pointer]:
              - /url: /dang-ky/
          - link "Giỏ hàng" [ref=f2e79] [cursor=pointer]:
            - /url: /gio-hang/
          - generic [ref=f2e83]: HUUGIAU Atelier © 2026
      - generic [ref=f2e84]:
        - generic [ref=f2e85]:
          - text: 
          - textbox "Tìm áo, quần, phụ kiện..." [ref=f2e86]
        - link "Giỏ hàng" [ref=f2e87] [cursor=pointer]:
          - /url: /gio-hang/
          - generic [aria-hidden] [ref=f2e88]: 
          - generic [ref=f2e89]: "0"
        - link "Yêu thích" [ref=f2e90] [cursor=pointer]:
          - /url: /yeu-thich/
          - generic [aria-hidden] [ref=f2e91]: 
        - group [ref=f2e92]:
          - generic "Tài khoản" [ref=f2e93] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e94]: 
            - generic [aria-hidden] [ref=f2e96]: 
  - main [ref=f2e97]:
    - article [ref=f2e100]:
      - img "Lookbook HUUGIAU" [ref=f2e101]
      - generic [ref=f2e102]:
        - paragraph [ref=f2e103]: HUUGIAU Atelier
        - heading "Gọn mà có gu, mặc mỗi ngày." [level=1] [ref=f2e104]
        - paragraph [ref=f2e105]: Nơi gói gọn mọi câu trả lời cho outfit mỗi ngày của bạn. Streetwear tối giản, sắc nét và cực dễ match. Lướt nhanh, chọn chất, chốt đơn trong một nốt nhạc.
        - generic [ref=f2e106]:
          - link "Mua ngay" [ref=f2e107] [cursor=pointer]:
            - /url: "#featured-products"
          - link "Xem catalog" [ref=f2e108] [cursor=pointer]:
            - /url: /?sort=newest
    - generic "Cam kết của shop" [ref=f2e109]:
      - generic [ref=f2e110]:
        - generic [aria-hidden] [ref=f2e111]: 
        - generic [ref=f2e112]:
          - strong [ref=f2e113]: Freeship từ 499K
          - generic [ref=f2e114]: Toàn quốc, giao nhanh 2-4 ngày
      - generic [ref=f2e115]:
        - generic [aria-hidden] [ref=f2e116]: 
        - generic [ref=f2e117]:
          - strong [ref=f2e118]: Đổi size 7 ngày
          - generic [ref=f2e119]: Miễn phí, sản phẩm nguyên trạng
      - generic [ref=f2e120]:
        - generic [aria-hidden] [ref=f2e121]: 
        - generic [ref=f2e122]:
          - strong [ref=f2e123]: Kiểm tra hàng
          - generic [ref=f2e124]: Trước khi thanh toán khi nhận
      - generic [ref=f2e125]:
        - generic [aria-hidden] [ref=f2e126]: 
        - generic [ref=f2e127]:
          - strong [ref=f2e128]: Hỗ trợ 9:00-21:30
          - generic [ref=f2e129]: Chat tư vấn size & phối đồ
    - generic "Số liệu cửa hàng" [ref=f2e130]:
      - generic [ref=f2e131]:
        - strong [ref=f2e132]: 1247+
        - generic [ref=f2e133]: sản phẩm đã bán
      - generic [ref=f2e134]:
        - strong [ref=f2e135]: 4,3/5
        - generic [ref=f2e136]: từ 305 đánh giá
      - generic [ref=f2e137]:
        - strong [ref=f2e138]: "76"
        - generic [ref=f2e139]: thiết kế đang bán
    - generic "Flash sale" [ref=f2e140]:
      - generic [ref=f2e141]:
        - generic [ref=f2e142]:
          - generic [aria-hidden] [ref=f2e143]: 
          - text: FLASH SALE
        - generic [ref=f2e144]: Deal trong ngày — giảm thêm 10% trên vài mẫu chọn lọc
      - generic [ref=f2e145]:
        - generic [ref=f2e146]: Kết thúc trong
        - generic [ref=f2e147]: 21:57:20
    - generic [ref=f2e148]:
      - generic [ref=f2e150]:
        - paragraph [ref=f2e151]: BỘ SƯU TẬP
        - heading "Mua theo danh mục" [level=2] [ref=f2e152]
        - paragraph [ref=f2e153]: Chọn đúng khoản cần, lên đồ nhanh, ít chọn nhầm.
      - generic [ref=f2e154]:
        - link "01 Áo Tee, sweatshirt, hoodie — lớp nền cho mọi outfit. Khám phá" [ref=f2e155] [cursor=pointer]:
          - /url: /?category=ao
          - generic [ref=f2e156]: "01"
          - heading "Áo" [level=3] [ref=f2e157]
          - paragraph [ref=f2e158]: Tee, sweatshirt, hoodie — lớp nền cho mọi outfit.
          - generic [ref=f2e159]:
            - text: Khám phá
            - generic [aria-hidden] [ref=f2e160]: 
        - link "02 Quần Denim, cargo, short — form gọn, dễ phối giày. Khám phá" [ref=f2e161] [cursor=pointer]:
          - /url: /?category=quan
          - generic [ref=f2e162]: "02"
          - heading "Quần" [level=3] [ref=f2e163]
          - paragraph [ref=f2e164]: Denim, cargo, short — form gọn, dễ phối giày.
          - generic [ref=f2e165]:
            - text: Khám phá
            - generic [aria-hidden] [ref=f2e166]: 
        - link "03 Phụ kiện Nón, túi, tất — điểm nhấn cuối cho bộ đồ. Khám phá" [ref=f2e167] [cursor=pointer]:
          - /url: /?category=phu-kien
          - generic [ref=f2e168]: "03"
          - heading "Phụ kiện" [level=3] [ref=f2e169]
          - paragraph [ref=f2e170]: Nón, túi, tất — điểm nhấn cuối cho bộ đồ.
          - generic [ref=f2e171]:
            - text: Khám phá
            - generic [aria-hidden] [ref=f2e172]: 
    - generic [ref=f2e173]:
      - generic [ref=f2e174]:
        - generic [ref=f2e175]:
          - paragraph [ref=f2e176]: SẢN PHẨM NỔI BẬT
          - heading "Lookbook hôm nay" [level=2] [ref=f2e177]
          - paragraph [ref=f2e178]: Những món dễ mặc nhưng vẫn giữ được cá tính riêng.
        - generic [ref=f2e179]:
          - link "Mới nhất" [ref=f2e180] [cursor=pointer]:
            - /url: /?sort=newest
          - link "Bán chạy" [ref=f2e181] [cursor=pointer]:
            - /url: /?sort=bestseller
          - link "Giá thấp" [ref=f2e182] [cursor=pointer]:
            - /url: /?sort=price_asc
          - link "Giá cao" [ref=f2e183] [cursor=pointer]:
            - /url: /?sort=price_desc
          - link "Đánh giá cao" [ref=f2e184] [cursor=pointer]:
            - /url: /?sort=rating
      - generic [ref=f2e185]:
        - generic [ref=f2e186]:
          - link "Quần jeans Baggy Fade Blue" [ref=f2e187] [cursor=pointer]:
            - /url: /san-pham/3/jeans-baggy-fade-blue/
            - generic [ref=f2e188]:
              - img "Quần jeans Baggy Fade Blue" [ref=f2e189]
              - generic [ref=f2e190]: NỔI BẬT
            - generic [ref=f2e192]:
              - paragraph [ref=f2e193]: Quần
              - heading "Quần jeans Baggy Fade Blue" [level=3] [ref=f2e194]
              - generic [ref=f2e195]:
                - generic [ref=f2e196]: 
                - generic [ref=f2e197]: 
                - generic [ref=f2e198]: 
                - generic [ref=f2e199]: 
                - generic [ref=f2e200]: 
                - generic [ref=f2e201]: "4"
              - generic [ref=f2e202]:
                - strong [ref=f2e203]: 590.000đ
                - generic [ref=f2e204]:
                  - generic [aria-hidden] [ref=f2e205]: 
                  - text: Đã bán 16
                - generic [ref=f2e206]: Xem chi tiết
          - button "Xem nhanh Quần jeans Baggy Fade Blue":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Quần jeans Baggy Fade Blue" [ref=f2e208] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e209]: 
            - text: So sánh
        - generic [ref=f2e210]:
          - link "Khẩu trang 3 lớp" [ref=f2e211] [cursor=pointer]:
            - /url: /san-pham/7/khau-trang-3-lop-swe/
            - generic [ref=f2e212]:
              - img "Khẩu trang 3 lớp" [ref=f2e213]
              - generic [ref=f2e214]: NỔI BẬT
            - generic [ref=f2e216]:
              - paragraph [ref=f2e217]: Phụ Kiện
              - heading "Khẩu trang 3 lớp" [level=3] [ref=f2e218]
              - generic [ref=f2e219]:
                - generic [ref=f2e220]: 
                - generic [ref=f2e221]: 
                - generic [ref=f2e222]: 
                - generic [ref=f2e223]: 
                - generic [ref=f2e224]: 
                - generic [ref=f2e225]: "4"
              - generic [ref=f2e226]:
                - strong [ref=f2e227]: 345.000đ
                - generic [ref=f2e228]:
                  - generic [aria-hidden] [ref=f2e229]: 
                  - text: Đã bán 19
                - generic [ref=f2e230]: Xem chi tiết
          - button "Xem nhanh Khẩu trang 3 lớp":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Khẩu trang 3 lớp" [ref=f2e232] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e233]: 
            - text: So sánh
        - generic [ref=f2e234]:
          - link "Dây đeo điện thoại" [ref=f2e235] [cursor=pointer]:
            - /url: /san-pham/10/day-deo-dien-thoai/
            - generic [ref=f2e236]:
              - img "Dây đeo điện thoại" [ref=f2e237]
              - generic [ref=f2e238]: NỔI BẬT
            - generic [ref=f2e240]:
              - paragraph [ref=f2e241]: Phụ Kiện
              - heading "Dây đeo điện thoại" [level=3] [ref=f2e242]
              - generic [ref=f2e243]:
                - generic [ref=f2e244]: 
                - generic [ref=f2e245]: 
                - generic [ref=f2e246]: 
                - generic [ref=f2e247]: 
                - generic [ref=f2e248]: 
                - generic [ref=f2e249]: "4"
              - generic [ref=f2e250]:
                - strong [ref=f2e251]: 300.000đ
                - generic [ref=f2e252]:
                  - generic [aria-hidden] [ref=f2e253]: 
                  - text: Đã bán 29
                - generic [ref=f2e254]: Xem chi tiết
          - button "Xem nhanh Dây đeo điện thoại":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Dây đeo điện thoại" [ref=f2e256] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e257]: 
            - text: So sánh
        - generic [ref=f2e258]:
          - link "Móc khóa Carabiner" [ref=f2e259] [cursor=pointer]:
            - /url: /san-pham/13/moc-khoa-carabiner/
            - generic [ref=f2e260]:
              - img "Móc khóa Carabiner" [ref=f2e261]
              - generic [ref=f2e262]:
                - generic [ref=f2e263]: NỔI BẬT
                - generic [ref=f2e264]: HẾT HÀNG
                - generic [ref=f2e265]: "-16%"
            - generic [ref=f2e266]:
              - paragraph [ref=f2e267]: Phụ Kiện
              - heading "Móc khóa Carabiner" [level=3] [ref=f2e268]
              - generic [ref=f2e269]:
                - generic [ref=f2e270]: 
                - generic [ref=f2e271]: 
                - generic [ref=f2e272]: 
                - generic [ref=f2e273]: 
                - generic [ref=f2e274]: 
                - generic [ref=f2e275]: "4"
              - generic [ref=f2e276]:
                - strong [ref=f2e277]: 306.000đ 255.000đ
                - generic [ref=f2e278]:
                  - generic [aria-hidden] [ref=f2e279]: 
                  - text: Đã bán 23
                - generic [ref=f2e280]: Xem chi tiết
          - button "Xem nhanh Móc khóa Carabiner":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Móc khóa Carabiner" [ref=f2e282] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e283]: 
            - text: So sánh
        - generic [ref=f2e284]:
          - link "Ví mini Reflect" [ref=f2e285] [cursor=pointer]:
            - /url: /san-pham/15/vi-mini-reflect/
            - generic [ref=f2e286]:
              - img "Ví mini Reflect" [ref=f2e287]
              - generic [ref=f2e288]:
                - generic [ref=f2e289]: NỔI BẬT
                - generic [ref=f2e290]: "-23%"
            - generic [ref=f2e291]:
              - paragraph [ref=f2e292]: Phụ Kiện
              - heading "Ví mini Reflect" [level=3] [ref=f2e293]
              - generic [ref=f2e294]:
                - generic [ref=f2e295]: 
                - generic [ref=f2e296]: 
                - generic [ref=f2e297]: 
                - generic [ref=f2e298]: 
                - generic [ref=f2e299]: 
                - generic [ref=f2e300]: "4"
              - generic [ref=f2e301]:
                - strong [ref=f2e302]: 292.500đ 225.000đ
                - generic [ref=f2e303]:
                  - generic [aria-hidden] [ref=f2e304]: 
                  - text: Đã bán 9
                - generic [ref=f2e305]: Xem chi tiết
          - button "Xem nhanh Ví mini Reflect":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Ví mini Reflect" [ref=f2e307] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e308]: 
            - text: So sánh
        - generic [ref=f2e309]:
          - link "Quần nỉ Daily" [ref=f2e310] [cursor=pointer]:
            - /url: /san-pham/27/quan-ni-daily/
            - generic [ref=f2e311]:
              - img "Quần nỉ Daily" [ref=f2e312]
              - generic [ref=f2e313]: NỔI BẬT
            - generic [ref=f2e315]:
              - paragraph [ref=f2e316]: Quần
              - heading "Quần nỉ Daily" [level=3] [ref=f2e317]
              - generic [ref=f2e318]:
                - generic [ref=f2e319]: 
                - generic [ref=f2e320]: 
                - generic [ref=f2e321]: 
                - generic [ref=f2e322]: 
                - generic [ref=f2e323]: 
                - generic [ref=f2e324]: "4"
              - generic [ref=f2e325]:
                - strong [ref=f2e326]: 570.000đ
                - generic [ref=f2e327]:
                  - generic [aria-hidden] [ref=f2e328]: 
                  - text: Đã bán 16
                - generic [ref=f2e329]: Xem chi tiết
          - button "Xem nhanh Quần nỉ Daily":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Quần nỉ Daily" [ref=f2e331] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e332]: 
            - text: So sánh
        - generic [ref=f2e333]:
          - link "Quần short nỉ Basic" [ref=f2e334] [cursor=pointer]:
            - /url: /san-pham/31/quan-short-sweat-basic/
            - generic [ref=f2e335]:
              - img "Quần short nỉ Basic" [ref=f2e336]
              - generic [ref=f2e337]: NỔI BẬT
            - generic [ref=f2e339]:
              - paragraph [ref=f2e340]: Quần
              - heading "Quần short nỉ Basic" [level=3] [ref=f2e341]
              - generic [ref=f2e342]:
                - generic [ref=f2e343]: 
                - generic [ref=f2e344]: 
                - generic [ref=f2e345]: 
                - generic [ref=f2e346]: 
                - generic [ref=f2e347]: 
                - generic [ref=f2e348]: "4"
              - generic [ref=f2e349]:
                - strong [ref=f2e350]: 510.000đ
                - generic [ref=f2e351]:
                  - generic [aria-hidden] [ref=f2e352]: 
                  - text: Đã bán 14
                - generic [ref=f2e353]: Xem chi tiết
          - button "Xem nhanh Quần short nỉ Basic":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Quần short nỉ Basic" [ref=f2e355] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e356]: 
            - text: So sánh
        - generic [ref=f2e357]:
          - link "Quần jeans Straight 90s" [ref=f2e358] [cursor=pointer]:
            - /url: /san-pham/34/quan-jeans-straight-90s/
            - generic [ref=f2e359]:
              - img "Quần jeans Straight 90s" [ref=f2e360]
              - generic [ref=f2e361]: NỔI BẬT
            - generic [ref=f2e363]:
              - paragraph [ref=f2e364]: Quần
              - heading "Quần jeans Straight 90s" [level=3] [ref=f2e365]
              - generic [ref=f2e366]:
                - generic [ref=f2e367]: 
                - generic [ref=f2e368]: 
                - generic [ref=f2e369]: 
                - generic [ref=f2e370]: 
                - generic [ref=f2e371]: 
                - generic [ref=f2e372]: "4"
              - generic [ref=f2e373]:
                - strong [ref=f2e374]: 465.000đ
                - generic [ref=f2e375]:
                  - generic [aria-hidden] [ref=f2e376]: 
                  - text: Đã bán 22
                - generic [ref=f2e377]: Xem chi tiết
          - button "Xem nhanh Quần jeans Straight 90s":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Quần jeans Straight 90s" [ref=f2e379] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e380]: 
            - text: So sánh
        - generic [ref=f2e381]:
          - link "Áo thun Graphic No.01" [ref=f2e382] [cursor=pointer]:
            - /url: /san-pham/40/ao-thun-graphic-no01/
            - generic [ref=f2e383]:
              - img "Áo thun Graphic No.01" [ref=f2e384]
              - generic [ref=f2e385]:
                - generic [ref=f2e386]: NỔI BẬT
                - generic [ref=f2e387]: Sắp hết hàng
            - generic [ref=f2e388]:
              - paragraph [ref=f2e389]: Áo
              - heading "Áo thun Graphic No.01" [level=3] [ref=f2e390]
              - generic [ref=f2e391]:
                - generic [ref=f2e392]: 
                - generic [ref=f2e393]: 
                - generic [ref=f2e394]: 
                - generic [ref=f2e395]: 
                - generic [ref=f2e396]: 
                - generic [ref=f2e397]: "4"
              - generic [ref=f2e398]:
                - strong [ref=f2e399]: 545.000đ
                - generic [ref=f2e400]:
                  - generic [aria-hidden] [ref=f2e401]: 
                  - text: Đã bán 21
                - generic [ref=f2e402]: Xem chi tiết
          - button "Xem nhanh Áo thun Graphic No.01":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Áo thun Graphic No.01" [ref=f2e404] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e405]: 
            - text: So sánh
        - generic [ref=f2e406]:
          - link "Áo khoác gió Wind Layer" [ref=f2e407] [cursor=pointer]:
            - /url: /san-pham/48/ao-khoac-gio-wind-layer/
            - generic [ref=f2e408]:
              - img "Áo khoác gió Wind Layer" [ref=f2e409]
              - generic [ref=f2e410]: NỔI BẬT
            - generic [ref=f2e412]:
              - paragraph [ref=f2e413]: Áo
              - heading "Áo khoác gió Wind Layer" [level=3] [ref=f2e414]
              - generic [ref=f2e415]:
                - generic [ref=f2e416]: 
                - generic [ref=f2e417]: 
                - generic [ref=f2e418]: 
                - generic [ref=f2e419]: 
                - generic [ref=f2e420]: 
                - generic [ref=f2e421]: "4"
              - generic [ref=f2e422]:
                - strong [ref=f2e423]: 425.000đ
                - generic [ref=f2e424]:
                  - generic [aria-hidden] [ref=f2e425]: 
                  - text: Đã bán 14
                - generic [ref=f2e426]: Xem chi tiết
          - button "Xem nhanh Áo khoác gió Wind Layer":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Áo khoác gió Wind Layer" [ref=f2e428] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e429]: 
            - text: So sánh
        - generic [ref=f2e430]:
          - link "Áo sweatshirt Varsity" [ref=f2e431] [cursor=pointer]:
            - /url: /san-pham/50/ao-sweatshirt-varsity/
            - generic [ref=f2e432]:
              - img "Áo sweatshirt Varsity" [ref=f2e433]
              - generic [ref=f2e434]: NỔI BẬT
            - generic [ref=f2e436]:
              - paragraph [ref=f2e437]: Áo
              - heading "Áo sweatshirt Varsity" [level=3] [ref=f2e438]
              - generic [ref=f2e439]:
                - generic [ref=f2e440]: 
                - generic [ref=f2e441]: 
                - generic [ref=f2e442]: 
                - generic [ref=f2e443]: 
                - generic [ref=f2e444]: 
                - generic [ref=f2e445]: "4"
              - generic [ref=f2e446]:
                - strong [ref=f2e447]: 395.000đ
                - generic [ref=f2e448]:
                  - generic [aria-hidden] [ref=f2e449]: 
                  - text: Đã bán 22
                - generic [ref=f2e450]: Xem chi tiết
          - button "Xem nhanh Áo sweatshirt Varsity":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Áo sweatshirt Varsity" [ref=f2e452] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e453]: 
            - text: So sánh
        - generic [ref=f2e454]:
          - link "Áo polo Dệt Urban" [ref=f2e455] [cursor=pointer]:
            - /url: /san-pham/53/ao-polo-knit-urban/
            - generic [ref=f2e456]:
              - img "Áo polo Dệt Urban" [ref=f2e457]
              - generic [ref=f2e458]: NỔI BẬT
            - generic [ref=f2e460]:
              - paragraph [ref=f2e461]: Áo
              - heading "Áo polo Dệt Urban" [level=3] [ref=f2e462]
              - generic [ref=f2e463]:
                - generic [ref=f2e464]: 
                - generic [ref=f2e465]: 
                - generic [ref=f2e466]: 
                - generic [ref=f2e467]: 
                - generic [ref=f2e468]: 
                - generic [ref=f2e469]: "4"
              - generic [ref=f2e470]:
                - strong [ref=f2e471]: 350.000đ
                - generic [ref=f2e472]:
                  - generic [aria-hidden] [ref=f2e473]: 
                  - text: Đã bán 22
                - generic [ref=f2e474]: Xem chi tiết
          - button "Xem nhanh Áo polo Dệt Urban":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Áo polo Dệt Urban" [ref=f2e476] [cursor=pointer]:
            - generic [aria-hidden] [ref=f2e477]: 
            - text: So sánh
    - generic [ref=f2e478]:
      - generic [ref=f2e479]:
        - generic [ref=f2e480]:
          - paragraph [ref=f2e481]: "@huugiau.atelier"
          - heading "Khoảnh khắc cùng HUUGIAU" [level=2] [ref=f2e482]
          - paragraph [ref=f2e483]:
            - text: Gắn thẻ
            - strong [ref=f2e484]: "#huugiau"
            - text: để xuất hiện trên trang của shop nhé.
        - link "Theo dõi chúng tôi" [ref=f2e485] [cursor=pointer]:
          - /url: https://www.instagram.com
      - generic [ref=f2e486]:
        - link "Mặc thử Quần jeans Baggy Fade Blue" [ref=f2e487] [cursor=pointer]:
          - /url: /san-pham/3/jeans-baggy-fade-blue/
          - img "Quần jeans Baggy Fade Blue" [ref=f2e488]
          - generic [ref=f2e489]: Mặc thử
        - link "Mặc thử Khẩu trang 3 lớp" [ref=f2e490] [cursor=pointer]:
          - /url: /san-pham/7/khau-trang-3-lop-swe/
          - img "Khẩu trang 3 lớp" [ref=f2e491]
          - generic [ref=f2e492]: Mặc thử
        - link "Mặc thử Dây đeo điện thoại" [ref=f2e493] [cursor=pointer]:
          - /url: /san-pham/10/day-deo-dien-thoai/
          - img "Dây đeo điện thoại" [ref=f2e494]
          - generic [ref=f2e495]: Mặc thử
        - link "Mặc thử Móc khóa Carabiner" [ref=f2e496] [cursor=pointer]:
          - /url: /san-pham/13/moc-khoa-carabiner/
          - img "Móc khóa Carabiner" [ref=f2e497]
          - generic [ref=f2e498]: Mặc thử
        - link "Mặc thử Ví mini Reflect" [ref=f2e499] [cursor=pointer]:
          - /url: /san-pham/15/vi-mini-reflect/
          - img "Ví mini Reflect" [ref=f2e500]
          - generic [ref=f2e501]: Mặc thử
        - link "Mặc thử Quần nỉ Daily" [ref=f2e502] [cursor=pointer]:
          - /url: /san-pham/27/quan-ni-daily/
          - img "Quần nỉ Daily" [ref=f2e503]
          - generic [ref=f2e504]: Mặc thử
    - dialog "Xem nhanh sản phẩm":
      - generic:
        - button "Đóng": ×
        - generic:
          - heading [level=3]
          - paragraph
          - strong
          - generic:
            - link "Xem chi tiết":
              - /url: "#"
  - contentinfo [ref=f2e505]:
    - generic [ref=f2e506]:
      - generic [ref=f2e507]:
        - heading "HUUGIAU Atelier" [level=3] [ref=f2e508]
        - paragraph [ref=f2e509]: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
        - paragraph [ref=f2e510]:
          - generic [aria-hidden] [ref=f2e511]: 
          - text: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
        - generic [ref=f2e512]:
          - link "Instagram" [ref=f2e513] [cursor=pointer]:
            - /url: https://www.instagram.com/
            - generic [aria-hidden] [ref=f2e514]: 
          - link "Facebook" [ref=f2e515] [cursor=pointer]:
            - /url: https://www.facebook.com/
            - generic [aria-hidden] [ref=f2e516]: 
          - link "TikTok" [ref=f2e517] [cursor=pointer]:
            - /url: https://www.tiktok.com/
            - generic [aria-hidden] [ref=f2e518]: 
        - generic [ref=f2e519]:
          - textbox "Email nhận tin" [ref=f2e520]:
            - /placeholder: Nhận tin khuyến mãi...
          - button "" [ref=f2e521] [cursor=pointer]
      - generic [ref=f2e523]:
        - heading "Hỗ trợ" [level=3] [ref=f2e524]
        - list [ref=f2e525]:
          - listitem [ref=f2e526]:
            - link "Tra cứu đơn hàng" [ref=f2e527] [cursor=pointer]:
              - /url: /tra-cuu-don/
          - listitem [ref=f2e528]:
            - link "Đơn hàng của tôi" [ref=f2e529] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
          - listitem [ref=f2e530]:
            - link "Chính sách đổi trả" [ref=f2e531] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
          - listitem [ref=f2e532]:
            - link "Hướng dẫn chọn size" [ref=f2e533] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f2e534]:
            - link "Chất liệu & bảo quản" [ref=f2e535] [cursor=pointer]:
              - /url: /chat-lieu-bao-quan/
          - listitem [ref=f2e536]:
            - link "Khuyến mãi" [ref=f2e537] [cursor=pointer]:
              - /url: /khuyen-mai/
          - listitem [ref=f2e538]:
            - link "Câu hỏi thường gặp" [ref=f2e539] [cursor=pointer]:
              - /url: /hoi-dap-chung/
        - paragraph [ref=f2e540]:
          - text: "Hotline:"
          - link "0932047365" [ref=f2e541] [cursor=pointer]:
            - /url: tel:0932047365
          - text: · 9:00–21:30 mỗi ngày
      - generic [ref=f2e542]:
        - heading "Danh mục" [level=3] [ref=f2e543]
        - list [ref=f2e544]:
          - listitem [ref=f2e545]:
            - link "Áo" [ref=f2e546] [cursor=pointer]:
              - /url: /?category=ao
          - listitem [ref=f2e547]:
            - link "Quần" [ref=f2e548] [cursor=pointer]:
              - /url: /?category=quan
          - listitem [ref=f2e549]:
            - link "Phụ kiện" [ref=f2e550] [cursor=pointer]:
              - /url: /?category=phu-kien
          - listitem [ref=f2e551]:
            - link "Hàng mới về" [ref=f2e552] [cursor=pointer]:
              - /url: /?sort=newest
          - listitem [ref=f2e553]:
            - link "Tất cả sản phẩm" [ref=f2e554] [cursor=pointer]:
              - /url: /
      - generic [ref=f2e555]:
        - heading "Về HUUGIAU" [level=3] [ref=f2e556]
        - list [ref=f2e557]:
          - listitem [ref=f2e558]:
            - link "Câu chuyện thương hiệu" [ref=f2e559] [cursor=pointer]:
              - /url: /ve-chung-toi/
          - listitem [ref=f2e560]:
            - link "Hướng dẫn chọn size" [ref=f2e561] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=f2e562]:
            - link "Tuyển dụng" [ref=f2e563] [cursor=pointer]:
              - /url: /tuyen-dung/
          - listitem [ref=f2e564]:
            - link "Liên hệ" [ref=f2e565] [cursor=pointer]:
              - /url: /lien-he/
          - listitem [ref=f2e566]:
            - link "Lookbook" [ref=f2e567] [cursor=pointer]:
              - /url: /lookbook/
    - generic [ref=f2e568]:
      - generic [ref=f2e569]:
        - generic [ref=f2e570]:
          - generic [ref=f2e571]: © 2026 HUUGIAU Atelier
          - link "Chính sách bảo mật" [ref=f2e572] [cursor=pointer]:
            - /url: /chinh-sach-bao-mat/
          - link "Điều khoản" [ref=f2e573] [cursor=pointer]:
            - /url: /dieu-khoan/
        - generic [ref=f2e574]:
          - generic "Visa" [ref=f2e575]: 
          - generic "Mastercard" [ref=f2e576]: 
          - generic "PayPal" [ref=f2e577]: 
          - generic "Chuyển khoản ngân hàng" [ref=f2e578]: 
          - generic "COD" [ref=f2e579]: 
      - generic [ref=f2e580]: "MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
  - button "Mở hỗ trợ mua hàng" [ref=f2e581] [cursor=pointer]:
    - generic [aria-hidden] [ref=f2e582]: 
  - dialog [aria-hidden] [ref=f2e583]:
    - generic [ref=f2e584]:
      - heading [level=3] [ref=f2e585]: Giỏ hàng (0)
      - button [ref=f2e586] [cursor=pointer]: ×
    - generic [ref=f2e588]:
      - generic [ref=f2e589]:
        - generic [ref=f2e590]: Tạm tính
        - strong [ref=f2e591]: 0đ
      - generic [ref=f2e592]:
        - link [ref=f2e593] [cursor=pointer]:
          - /url: /gio-hang/
          - text: Xem giỏ hàng
        - link [ref=f2e594] [cursor=pointer]:
          - /url: /thanh-toan/
          - text: Thanh toán
  - text: 
  - dialog [ref=f2e595]:
    - generic [ref=f2e596]:
      - generic [ref=f2e597]:
        - strong [ref=f2e598]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=f2e599]:
        - button "Tùy chỉnh" [ref=f2e600] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=f2e601] [cursor=pointer]
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
> 22 |     await page.fill('input[name="customer_name"]', 'Test User');
     |                ^ Error: page.fill: Test timeout of 30000ms exceeded.
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
  67 |     await expect(page).toHaveURL(/\/cho-thanh-toan-ngan-hang\//);
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