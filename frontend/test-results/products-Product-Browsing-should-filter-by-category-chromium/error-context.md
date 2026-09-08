# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: products.spec.ts >> Product Browsing >> should filter by category
- Location: tests\products.spec.ts:77:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('a[href*="category"], a[href*="danh-muc"]').first()
    - locator resolved to <a href="/?category=ao">…</a>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - element is outside of the viewport
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - element is outside of the viewport
    - retrying click action
      - waiting 100ms
    38 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - element is outside of the viewport
     - retrying click action
       - waiting 500ms

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
    - article [ref=e100]:
      - img "Lookbook HUUGIAU" [ref=e101]
      - generic [ref=e102]:
        - paragraph [ref=e103]: HUUGIAU Atelier
        - heading "Gọn mà có gu, mặc mỗi ngày." [level=1] [ref=e104]
        - paragraph [ref=e105]: Nơi gói gọn mọi câu trả lời cho outfit mỗi ngày của bạn. Streetwear tối giản, sắc nét và cực dễ match. Lướt nhanh, chọn chất, chốt đơn trong một nốt nhạc.
        - generic [ref=e106]:
          - link "Mua ngay" [ref=e107] [cursor=pointer]:
            - /url: "#featured-products"
          - link "Xem catalog" [ref=e108] [cursor=pointer]:
            - /url: /?sort=newest
    - generic "Cam kết của shop" [ref=e109]:
      - generic [ref=e110]:
        - generic [aria-hidden] [ref=e111]: 
        - generic [ref=e112]:
          - strong [ref=e113]: Freeship từ 499K
          - generic [ref=e114]: Toàn quốc, giao nhanh 2-4 ngày
      - generic [ref=e115]:
        - generic [aria-hidden] [ref=e116]: 
        - generic [ref=e117]:
          - strong [ref=e118]: Đổi size 7 ngày
          - generic [ref=e119]: Miễn phí, sản phẩm nguyên trạng
      - generic [ref=e120]:
        - generic [aria-hidden] [ref=e121]: 
        - generic [ref=e122]:
          - strong [ref=e123]: Kiểm tra hàng
          - generic [ref=e124]: Trước khi thanh toán khi nhận
      - generic [ref=e125]:
        - generic [aria-hidden] [ref=e126]: 
        - generic [ref=e127]:
          - strong [ref=e128]: Hỗ trợ 9:00-21:30
          - generic [ref=e129]: Chat tư vấn size & phối đồ
    - generic "Số liệu cửa hàng" [ref=e130]:
      - generic [ref=e131]:
        - strong [ref=e132]: 1247+
        - generic [ref=e133]: sản phẩm đã bán
      - generic [ref=e134]:
        - strong [ref=e135]: 4,3/5
        - generic [ref=e136]: từ 305 đánh giá
      - generic [ref=e137]:
        - strong [ref=e138]: "76"
        - generic [ref=e139]: thiết kế đang bán
    - generic "Flash sale" [ref=e140]:
      - generic [ref=e141]:
        - generic [ref=e142]:
          - generic [aria-hidden] [ref=e143]: 
          - text: FLASH SALE
        - generic [ref=e144]: Deal trong ngày — giảm thêm 10% trên vài mẫu chọn lọc
      - generic [ref=e145]:
        - generic [ref=e146]: Kết thúc trong
        - generic [ref=e147]: 21:56:20
    - generic [ref=e148]:
      - generic [ref=e150]:
        - paragraph [ref=e151]: BỘ SƯU TẬP
        - heading "Mua theo danh mục" [level=2] [ref=e152]
        - paragraph [ref=e153]: Chọn đúng khoản cần, lên đồ nhanh, ít chọn nhầm.
      - generic [ref=e154]:
        - link "01 Áo Tee, sweatshirt, hoodie — lớp nền cho mọi outfit. Khám phá" [ref=e155] [cursor=pointer]:
          - /url: /?category=ao
          - generic [ref=e156]: "01"
          - heading "Áo" [level=3] [ref=e157]
          - paragraph [ref=e158]: Tee, sweatshirt, hoodie — lớp nền cho mọi outfit.
          - generic [ref=e159]:
            - text: Khám phá
            - generic [aria-hidden] [ref=e160]: 
        - link "02 Quần Denim, cargo, short — form gọn, dễ phối giày. Khám phá" [ref=e161] [cursor=pointer]:
          - /url: /?category=quan
          - generic [ref=e162]: "02"
          - heading "Quần" [level=3] [ref=e163]
          - paragraph [ref=e164]: Denim, cargo, short — form gọn, dễ phối giày.
          - generic [ref=e165]:
            - text: Khám phá
            - generic [aria-hidden] [ref=e166]: 
        - link "03 Phụ kiện Nón, túi, tất — điểm nhấn cuối cho bộ đồ. Khám phá" [ref=e167] [cursor=pointer]:
          - /url: /?category=phu-kien
          - generic [ref=e168]: "03"
          - heading "Phụ kiện" [level=3] [ref=e169]
          - paragraph [ref=e170]: Nón, túi, tất — điểm nhấn cuối cho bộ đồ.
          - generic [ref=e171]:
            - text: Khám phá
            - generic [aria-hidden] [ref=e172]: 
    - generic [ref=e173]:
      - generic [ref=e174]:
        - generic [ref=e175]:
          - paragraph [ref=e176]: SẢN PHẨM NỔI BẬT
          - heading "Lookbook hôm nay" [level=2] [ref=e177]
          - paragraph [ref=e178]: Những món dễ mặc nhưng vẫn giữ được cá tính riêng.
        - generic [ref=e179]:
          - link "Mới nhất" [ref=e180] [cursor=pointer]:
            - /url: /?sort=newest
          - link "Bán chạy" [ref=e181] [cursor=pointer]:
            - /url: /?sort=bestseller
          - link "Giá thấp" [ref=e182] [cursor=pointer]:
            - /url: /?sort=price_asc
          - link "Giá cao" [ref=e183] [cursor=pointer]:
            - /url: /?sort=price_desc
          - link "Đánh giá cao" [ref=e184] [cursor=pointer]:
            - /url: /?sort=rating
      - generic [ref=e185]:
        - generic [ref=e186]:
          - link "Quần jeans Baggy Fade Blue" [ref=e187] [cursor=pointer]:
            - /url: /san-pham/3/jeans-baggy-fade-blue/
            - generic [ref=e188]:
              - img "Quần jeans Baggy Fade Blue" [ref=e189]
              - generic [ref=e190]: NỔI BẬT
            - generic [ref=e192]:
              - paragraph [ref=e193]: Quần
              - heading "Quần jeans Baggy Fade Blue" [level=3] [ref=e194]
              - generic [ref=e195]:
                - generic [ref=e196]: 
                - generic [ref=e197]: 
                - generic [ref=e198]: 
                - generic [ref=e199]: 
                - generic [ref=e200]: 
                - generic [ref=e201]: "4"
              - generic [ref=e202]:
                - strong [ref=e203]: 590.000đ
                - generic [ref=e204]:
                  - generic [aria-hidden] [ref=e205]: 
                  - text: Đã bán 16
                - generic [ref=e206]: Xem chi tiết
          - button "Xem nhanh Quần jeans Baggy Fade Blue":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Quần jeans Baggy Fade Blue" [ref=e208] [cursor=pointer]:
            - generic [aria-hidden] [ref=e209]: 
            - text: So sánh
        - generic [ref=e210]:
          - link "Khẩu trang 3 lớp" [ref=e211] [cursor=pointer]:
            - /url: /san-pham/7/khau-trang-3-lop-swe/
            - generic [ref=e212]:
              - img "Khẩu trang 3 lớp" [ref=e213]
              - generic [ref=e214]: NỔI BẬT
            - generic [ref=e216]:
              - paragraph [ref=e217]: Phụ Kiện
              - heading "Khẩu trang 3 lớp" [level=3] [ref=e218]
              - generic [ref=e219]:
                - generic [ref=e220]: 
                - generic [ref=e221]: 
                - generic [ref=e222]: 
                - generic [ref=e223]: 
                - generic [ref=e224]: 
                - generic [ref=e225]: "4"
              - generic [ref=e226]:
                - strong [ref=e227]: 345.000đ
                - generic [ref=e228]:
                  - generic [aria-hidden] [ref=e229]: 
                  - text: Đã bán 19
                - generic [ref=e230]: Xem chi tiết
          - button "Xem nhanh Khẩu trang 3 lớp":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Khẩu trang 3 lớp" [ref=e232] [cursor=pointer]:
            - generic [aria-hidden] [ref=e233]: 
            - text: So sánh
        - generic [ref=e234]:
          - link "Dây đeo điện thoại" [ref=e235] [cursor=pointer]:
            - /url: /san-pham/10/day-deo-dien-thoai/
            - generic [ref=e236]:
              - img "Dây đeo điện thoại" [ref=e237]
              - generic [ref=e238]: NỔI BẬT
            - generic [ref=e240]:
              - paragraph [ref=e241]: Phụ Kiện
              - heading "Dây đeo điện thoại" [level=3] [ref=e242]
              - generic [ref=e243]:
                - generic [ref=e244]: 
                - generic [ref=e245]: 
                - generic [ref=e246]: 
                - generic [ref=e247]: 
                - generic [ref=e248]: 
                - generic [ref=e249]: "4"
              - generic [ref=e250]:
                - strong [ref=e251]: 300.000đ
                - generic [ref=e252]:
                  - generic [aria-hidden] [ref=e253]: 
                  - text: Đã bán 29
                - generic [ref=e254]: Xem chi tiết
          - button "Xem nhanh Dây đeo điện thoại":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Dây đeo điện thoại" [ref=e256] [cursor=pointer]:
            - generic [aria-hidden] [ref=e257]: 
            - text: So sánh
        - generic [ref=e258]:
          - link "Móc khóa Carabiner" [ref=e259] [cursor=pointer]:
            - /url: /san-pham/13/moc-khoa-carabiner/
            - generic [ref=e260]:
              - img "Móc khóa Carabiner" [ref=e261]
              - generic [ref=e262]:
                - generic [ref=e263]: NỔI BẬT
                - generic [ref=e264]: HẾT HÀNG
                - generic [ref=e265]: "-16%"
            - generic [ref=e266]:
              - paragraph [ref=e267]: Phụ Kiện
              - heading "Móc khóa Carabiner" [level=3] [ref=e268]
              - generic [ref=e269]:
                - generic [ref=e270]: 
                - generic [ref=e271]: 
                - generic [ref=e272]: 
                - generic [ref=e273]: 
                - generic [ref=e274]: 
                - generic [ref=e275]: "4"
              - generic [ref=e276]:
                - strong [ref=e277]: 306.000đ 255.000đ
                - generic [ref=e278]:
                  - generic [aria-hidden] [ref=e279]: 
                  - text: Đã bán 23
                - generic [ref=e280]: Xem chi tiết
          - button "Xem nhanh Móc khóa Carabiner":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Móc khóa Carabiner" [ref=e282] [cursor=pointer]:
            - generic [aria-hidden] [ref=e283]: 
            - text: So sánh
        - generic [ref=e284]:
          - link "Ví mini Reflect" [ref=e285] [cursor=pointer]:
            - /url: /san-pham/15/vi-mini-reflect/
            - generic [ref=e286]:
              - img "Ví mini Reflect" [ref=e287]
              - generic [ref=e288]:
                - generic [ref=e289]: NỔI BẬT
                - generic [ref=e290]: "-23%"
            - generic [ref=e291]:
              - paragraph [ref=e292]: Phụ Kiện
              - heading "Ví mini Reflect" [level=3] [ref=e293]
              - generic [ref=e294]:
                - generic [ref=e295]: 
                - generic [ref=e296]: 
                - generic [ref=e297]: 
                - generic [ref=e298]: 
                - generic [ref=e299]: 
                - generic [ref=e300]: "4"
              - generic [ref=e301]:
                - strong [ref=e302]: 292.500đ 225.000đ
                - generic [ref=e303]:
                  - generic [aria-hidden] [ref=e304]: 
                  - text: Đã bán 9
                - generic [ref=e305]: Xem chi tiết
          - button "Xem nhanh Ví mini Reflect":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Ví mini Reflect" [ref=e307] [cursor=pointer]:
            - generic [aria-hidden] [ref=e308]: 
            - text: So sánh
        - generic [ref=e309]:
          - link "Quần nỉ Daily" [ref=e310] [cursor=pointer]:
            - /url: /san-pham/27/quan-ni-daily/
            - generic [ref=e311]:
              - img "Quần nỉ Daily" [ref=e312]
              - generic [ref=e313]: NỔI BẬT
            - generic [ref=e315]:
              - paragraph [ref=e316]: Quần
              - heading "Quần nỉ Daily" [level=3] [ref=e317]
              - generic [ref=e318]:
                - generic [ref=e319]: 
                - generic [ref=e320]: 
                - generic [ref=e321]: 
                - generic [ref=e322]: 
                - generic [ref=e323]: 
                - generic [ref=e324]: "4"
              - generic [ref=e325]:
                - strong [ref=e326]: 570.000đ
                - generic [ref=e327]:
                  - generic [aria-hidden] [ref=e328]: 
                  - text: Đã bán 16
                - generic [ref=e329]: Xem chi tiết
          - button "Xem nhanh Quần nỉ Daily":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Quần nỉ Daily" [ref=e331] [cursor=pointer]:
            - generic [aria-hidden] [ref=e332]: 
            - text: So sánh
        - generic [ref=e333]:
          - link "Quần short nỉ Basic" [ref=e334] [cursor=pointer]:
            - /url: /san-pham/31/quan-short-sweat-basic/
            - generic [ref=e335]:
              - img "Quần short nỉ Basic" [ref=e336]
              - generic [ref=e337]: NỔI BẬT
            - generic [ref=e339]:
              - paragraph [ref=e340]: Quần
              - heading "Quần short nỉ Basic" [level=3] [ref=e341]
              - generic [ref=e342]:
                - generic [ref=e343]: 
                - generic [ref=e344]: 
                - generic [ref=e345]: 
                - generic [ref=e346]: 
                - generic [ref=e347]: 
                - generic [ref=e348]: "4"
              - generic [ref=e349]:
                - strong [ref=e350]: 510.000đ
                - generic [ref=e351]:
                  - generic [aria-hidden] [ref=e352]: 
                  - text: Đã bán 14
                - generic [ref=e353]: Xem chi tiết
          - button "Xem nhanh Quần short nỉ Basic":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Quần short nỉ Basic" [ref=e355] [cursor=pointer]:
            - generic [aria-hidden] [ref=e356]: 
            - text: So sánh
        - generic [ref=e357]:
          - link "Quần jeans Straight 90s" [ref=e358] [cursor=pointer]:
            - /url: /san-pham/34/quan-jeans-straight-90s/
            - generic [ref=e359]:
              - img "Quần jeans Straight 90s" [ref=e360]
              - generic [ref=e361]: NỔI BẬT
            - generic [ref=e363]:
              - paragraph [ref=e364]: Quần
              - heading "Quần jeans Straight 90s" [level=3] [ref=e365]
              - generic [ref=e366]:
                - generic [ref=e367]: 
                - generic [ref=e368]: 
                - generic [ref=e369]: 
                - generic [ref=e370]: 
                - generic [ref=e371]: 
                - generic [ref=e372]: "4"
              - generic [ref=e373]:
                - strong [ref=e374]: 465.000đ
                - generic [ref=e375]:
                  - generic [aria-hidden] [ref=e376]: 
                  - text: Đã bán 22
                - generic [ref=e377]: Xem chi tiết
          - button "Xem nhanh Quần jeans Straight 90s":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Quần jeans Straight 90s" [ref=e379] [cursor=pointer]:
            - generic [aria-hidden] [ref=e380]: 
            - text: So sánh
        - generic [ref=e381]:
          - link "Áo thun Graphic No.01" [ref=e382] [cursor=pointer]:
            - /url: /san-pham/40/ao-thun-graphic-no01/
            - generic [ref=e383]:
              - img "Áo thun Graphic No.01" [ref=e384]
              - generic [ref=e385]:
                - generic [ref=e386]: NỔI BẬT
                - generic [ref=e387]: Sắp hết hàng
            - generic [ref=e388]:
              - paragraph [ref=e389]: Áo
              - heading "Áo thun Graphic No.01" [level=3] [ref=e390]
              - generic [ref=e391]:
                - generic [ref=e392]: 
                - generic [ref=e393]: 
                - generic [ref=e394]: 
                - generic [ref=e395]: 
                - generic [ref=e396]: 
                - generic [ref=e397]: "4"
              - generic [ref=e398]:
                - strong [ref=e399]: 545.000đ
                - generic [ref=e400]:
                  - generic [aria-hidden] [ref=e401]: 
                  - text: Đã bán 21
                - generic [ref=e402]: Xem chi tiết
          - button "Xem nhanh Áo thun Graphic No.01":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Áo thun Graphic No.01" [ref=e404] [cursor=pointer]:
            - generic [aria-hidden] [ref=e405]: 
            - text: So sánh
        - generic [ref=e406]:
          - link "Áo khoác gió Wind Layer" [ref=e407] [cursor=pointer]:
            - /url: /san-pham/48/ao-khoac-gio-wind-layer/
            - generic [ref=e408]:
              - img "Áo khoác gió Wind Layer" [ref=e409]
              - generic [ref=e410]: NỔI BẬT
            - generic [ref=e412]:
              - paragraph [ref=e413]: Áo
              - heading "Áo khoác gió Wind Layer" [level=3] [ref=e414]
              - generic [ref=e415]:
                - generic [ref=e416]: 
                - generic [ref=e417]: 
                - generic [ref=e418]: 
                - generic [ref=e419]: 
                - generic [ref=e420]: 
                - generic [ref=e421]: "4"
              - generic [ref=e422]:
                - strong [ref=e423]: 425.000đ
                - generic [ref=e424]:
                  - generic [aria-hidden] [ref=e425]: 
                  - text: Đã bán 14
                - generic [ref=e426]: Xem chi tiết
          - button "Xem nhanh Áo khoác gió Wind Layer":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Áo khoác gió Wind Layer" [ref=e428] [cursor=pointer]:
            - generic [aria-hidden] [ref=e429]: 
            - text: So sánh
        - generic [ref=e430]:
          - link "Áo sweatshirt Varsity" [ref=e431] [cursor=pointer]:
            - /url: /san-pham/50/ao-sweatshirt-varsity/
            - generic [ref=e432]:
              - img "Áo sweatshirt Varsity" [ref=e433]
              - generic [ref=e434]: NỔI BẬT
            - generic [ref=e436]:
              - paragraph [ref=e437]: Áo
              - heading "Áo sweatshirt Varsity" [level=3] [ref=e438]
              - generic [ref=e439]:
                - generic [ref=e440]: 
                - generic [ref=e441]: 
                - generic [ref=e442]: 
                - generic [ref=e443]: 
                - generic [ref=e444]: 
                - generic [ref=e445]: "4"
              - generic [ref=e446]:
                - strong [ref=e447]: 395.000đ
                - generic [ref=e448]:
                  - generic [aria-hidden] [ref=e449]: 
                  - text: Đã bán 22
                - generic [ref=e450]: Xem chi tiết
          - button "Xem nhanh Áo sweatshirt Varsity":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Áo sweatshirt Varsity" [ref=e452] [cursor=pointer]:
            - generic [aria-hidden] [ref=e453]: 
            - text: So sánh
        - generic [ref=e454]:
          - link "Áo polo Dệt Urban" [ref=e455] [cursor=pointer]:
            - /url: /san-pham/53/ao-polo-knit-urban/
            - generic [ref=e456]:
              - img "Áo polo Dệt Urban" [ref=e457]
              - generic [ref=e458]: NỔI BẬT
            - generic [ref=e460]:
              - paragraph [ref=e461]: Áo
              - heading "Áo polo Dệt Urban" [level=3] [ref=e462]
              - generic [ref=e463]:
                - generic [ref=e464]: 
                - generic [ref=e465]: 
                - generic [ref=e466]: 
                - generic [ref=e467]: 
                - generic [ref=e468]: 
                - generic [ref=e469]: "4"
              - generic [ref=e470]:
                - strong [ref=e471]: 350.000đ
                - generic [ref=e472]:
                  - generic [aria-hidden] [ref=e473]: 
                  - text: Đã bán 22
                - generic [ref=e474]: Xem chi tiết
          - button "Xem nhanh Áo polo Dệt Urban":
            - generic [aria-hidden]: 
            - text: Xem nhanh
          - button "So sánh Áo polo Dệt Urban" [ref=e476] [cursor=pointer]:
            - generic [aria-hidden] [ref=e477]: 
            - text: So sánh
    - generic [ref=e478]:
      - generic [ref=e479]:
        - generic [ref=e480]:
          - paragraph [ref=e481]: "@huugiau.atelier"
          - heading "Khoảnh khắc cùng HUUGIAU" [level=2] [ref=e482]
          - paragraph [ref=e483]:
            - text: Gắn thẻ
            - strong [ref=e484]: "#huugiau"
            - text: để xuất hiện trên trang của shop nhé.
        - link "Theo dõi chúng tôi" [ref=e485] [cursor=pointer]:
          - /url: https://www.instagram.com
      - generic [ref=e486]:
        - link "Mặc thử Quần jeans Baggy Fade Blue" [ref=e487] [cursor=pointer]:
          - /url: /san-pham/3/jeans-baggy-fade-blue/
          - img "Quần jeans Baggy Fade Blue" [ref=e488]
          - generic [ref=e489]: Mặc thử
        - link "Mặc thử Khẩu trang 3 lớp" [ref=e490] [cursor=pointer]:
          - /url: /san-pham/7/khau-trang-3-lop-swe/
          - img "Khẩu trang 3 lớp" [ref=e491]
          - generic [ref=e492]: Mặc thử
        - link "Mặc thử Dây đeo điện thoại" [ref=e493] [cursor=pointer]:
          - /url: /san-pham/10/day-deo-dien-thoai/
          - img "Dây đeo điện thoại" [ref=e494]
          - generic [ref=e495]: Mặc thử
        - link "Mặc thử Móc khóa Carabiner" [ref=e496] [cursor=pointer]:
          - /url: /san-pham/13/moc-khoa-carabiner/
          - img "Móc khóa Carabiner" [ref=e497]
          - generic [ref=e498]: Mặc thử
        - link "Mặc thử Ví mini Reflect" [ref=e499] [cursor=pointer]:
          - /url: /san-pham/15/vi-mini-reflect/
          - img "Ví mini Reflect" [ref=e500]
          - generic [ref=e501]: Mặc thử
        - link "Mặc thử Quần nỉ Daily" [ref=e502] [cursor=pointer]:
          - /url: /san-pham/27/quan-ni-daily/
          - img "Quần nỉ Daily" [ref=e503]
          - generic [ref=e504]: Mặc thử
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
  - contentinfo [ref=e505]:
    - generic [ref=e506]:
      - generic [ref=e507]:
        - heading "HUUGIAU Atelier" [level=3] [ref=e508]
        - paragraph [ref=e509]: Streetwear local — gọn, dễ mặc, đủ điểm nhấn để lên đồ nhanh mỗi ngày.
        - paragraph [ref=e510]:
          - generic [aria-hidden] [ref=e511]: 
          - text: Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh
        - generic [ref=e512]:
          - link "Instagram" [ref=e513] [cursor=pointer]:
            - /url: https://www.instagram.com/
            - generic [aria-hidden] [ref=e514]: 
          - link "Facebook" [ref=e515] [cursor=pointer]:
            - /url: https://www.facebook.com/
            - generic [aria-hidden] [ref=e516]: 
          - link "TikTok" [ref=e517] [cursor=pointer]:
            - /url: https://www.tiktok.com/
            - generic [aria-hidden] [ref=e518]: 
        - generic [ref=e519]:
          - textbox "Email nhận tin" [ref=e520]:
            - /placeholder: Nhận tin khuyến mãi...
          - button "" [ref=e521] [cursor=pointer]
      - generic [ref=e523]:
        - heading "Hỗ trợ" [level=3] [ref=e524]
        - list [ref=e525]:
          - listitem [ref=e526]:
            - link "Tra cứu đơn hàng" [ref=e527] [cursor=pointer]:
              - /url: /tra-cuu-don/
          - listitem [ref=e528]:
            - link "Đơn hàng của tôi" [ref=e529] [cursor=pointer]:
              - /url: /don-hang-cua-toi/
          - listitem [ref=e530]:
            - link "Chính sách đổi trả" [ref=e531] [cursor=pointer]:
              - /url: /chinh-sach-doi-tra/
          - listitem [ref=e532]:
            - link "Hướng dẫn chọn size" [ref=e533] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=e534]:
            - link "Chất liệu & bảo quản" [ref=e535] [cursor=pointer]:
              - /url: /chat-lieu-bao-quan/
          - listitem [ref=e536]:
            - link "Khuyến mãi" [ref=e537] [cursor=pointer]:
              - /url: /khuyen-mai/
          - listitem [ref=e538]:
            - link "Câu hỏi thường gặp" [ref=e539] [cursor=pointer]:
              - /url: /hoi-dap-chung/
        - paragraph [ref=e540]:
          - text: "Hotline:"
          - link "0932047365" [ref=e541] [cursor=pointer]:
            - /url: tel:0932047365
          - text: · 9:00–21:30 mỗi ngày
      - generic [ref=e542]:
        - heading "Danh mục" [level=3] [ref=e543]
        - list [ref=e544]:
          - listitem [ref=e545]:
            - link "Áo" [ref=e546] [cursor=pointer]:
              - /url: /?category=ao
          - listitem [ref=e547]:
            - link "Quần" [ref=e548] [cursor=pointer]:
              - /url: /?category=quan
          - listitem [ref=e549]:
            - link "Phụ kiện" [ref=e550] [cursor=pointer]:
              - /url: /?category=phu-kien
          - listitem [ref=e551]:
            - link "Hàng mới về" [ref=e552] [cursor=pointer]:
              - /url: /?sort=newest
          - listitem [ref=e553]:
            - link "Tất cả sản phẩm" [ref=e554] [cursor=pointer]:
              - /url: /
      - generic [ref=e555]:
        - heading "Về HUUGIAU" [level=3] [ref=e556]
        - list [ref=e557]:
          - listitem [ref=e558]:
            - link "Câu chuyện thương hiệu" [ref=e559] [cursor=pointer]:
              - /url: /ve-chung-toi/
          - listitem [ref=e560]:
            - link "Hướng dẫn chọn size" [ref=e561] [cursor=pointer]:
              - /url: /huong-dan-chon-size/
          - listitem [ref=e562]:
            - link "Tuyển dụng" [ref=e563] [cursor=pointer]:
              - /url: /tuyen-dung/
          - listitem [ref=e564]:
            - link "Liên hệ" [ref=e565] [cursor=pointer]:
              - /url: /lien-he/
          - listitem [ref=e566]:
            - link "Lookbook" [ref=e567] [cursor=pointer]:
              - /url: /lookbook/
    - generic [ref=e568]:
      - generic [ref=e569]:
        - generic [ref=e570]:
          - generic [ref=e571]: © 2026 HUUGIAU Atelier
          - link "Chính sách bảo mật" [ref=e572] [cursor=pointer]:
            - /url: /chinh-sach-bao-mat/
          - link "Điều khoản" [ref=e573] [cursor=pointer]:
            - /url: /dieu-khoan/
        - generic [ref=e574]:
          - generic "Visa" [ref=e575]: 
          - generic "Mastercard" [ref=e576]: 
          - generic "PayPal" [ref=e577]: 
          - generic "Chuyển khoản ngân hàng" [ref=e578]: 
          - generic "COD" [ref=e579]: 
      - generic [ref=e580]: "MST: 0312 456 789 · ĐKKD số 0312345678 do Sở KH&ĐT TP.HCM cấp ngày 12/01/2020 · 92 Nguyễn Hữu Thọ, Quận 7, TP. Hồ Chí Minh"
  - button "Mở hỗ trợ mua hàng" [ref=e581] [cursor=pointer]:
    - generic [aria-hidden] [ref=e582]: 
  - dialog [aria-hidden] [ref=e583]:
    - generic [ref=e584]:
      - heading [level=3] [ref=e585]: Giỏ hàng (0)
      - button [ref=e586] [cursor=pointer]: ×
    - generic [ref=e588]:
      - generic [ref=e589]:
        - generic [ref=e590]: Tạm tính
        - strong [ref=e591]: 0đ
      - generic [ref=e592]:
        - link [ref=e593] [cursor=pointer]:
          - /url: /gio-hang/
          - text: Xem giỏ hàng
        - link [ref=e594] [cursor=pointer]:
          - /url: /thanh-toan/
          - text: Thanh toán
  - text: 
  - dialog [ref=e595]:
    - generic [ref=e596]:
      - generic [ref=e597]:
        - strong [ref=e598]: Chúng tôi sử dụng cookie
        - text: Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo. Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
      - generic [ref=e599]:
        - button "Tùy chỉnh" [ref=e600] [cursor=pointer]
        - button "Chấp nhận tất cả" [ref=e601] [cursor=pointer]
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
> 81 |       await categoryLink.click();
     |                          ^ Error: locator.click: Test timeout of 30000ms exceeded.
  82 |       await expect(page).toHaveURL(/category|danh-muc/);
  83 |     }
  84 |   });
  85 | 
  86 |   test('should search products', async ({ page }) => {
  87 |     const searchInput = page.locator('input[name="q"], input[placeholder*="tìm"], input[placeholder*="search"]').first();
  88 |     if (await searchInput.isVisible()) {
  89 |       await searchInput.fill('áo');
  90 |       await searchInput.press('Enter');
  91 |       await expect(page).toHaveURL(/search|tim-kiem/);
  92 |     }
  93 |   });
  94 | });
```