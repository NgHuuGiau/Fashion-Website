-- ============================================================
-- HUUGIAU Fashion - INSERT DATA
-- Open in SSMS and press F5 (run after 01_CREATE_TABLES.sql)
-- ============================================================

USE [HUUGIAU_Fashion];
GO

-- Tài khoản người dùng (8 rows)
SET IDENTITY_INSERT [Users] ON;
GO
INSERT INTO [Users] ([id], [username], [email], [password], [role], [is_active], [date_joined], [phone]) VALUES
(1, N'admin', N'admin@example.com', N'pbkdf2_sha256$1200000$K3AlovVJR4GQQzRQrafZUh$pfKPgpJK+xgXKt/RRG9n68XH0sSgwPFWgNofepPmSgM=', 0, 1, N'2026-07-29 07:14:07.174474', N''),
(2, N'codexstaff', N'staff@codex.com', N'pbkdf2_sha256$1200000$YglQOMUax9xTdkSV0rGekX$i19RhyRNBxmZQEx2A7xCJjP+1Mn7G1NRfeeY1v7vjmI=', 1, 1, N'2026-07-29 07:14:07.974154', N''),
(3, N'readmestaff', N'readme@staff.com', N'pbkdf2_sha256$1200000$vu78zLjOwD8l91cAJl3rec$KhWTPrgUNUSYqBfX1Oqs4gk7eRgjaJWsppERDAS1sv0=', 1, 1, N'2026-07-29 07:14:08.726297', N''),
(4, N'nguyenvanA', N'nguyenvana@email.com', N'pbkdf2_sha256$1200000$KQtzQK4Wwzk2NaNO24FXn9$0+eZ6ha6eoVblSk8qv6XOg2jscprdlkg1veeAALlrNA=', 2, 1, N'2026-07-29 07:14:09.514670', N''),
(5, N'tranthib', N'tranthib@email.com', N'pbkdf2_sha256$1200000$nEJO69pXugv88XGchrgKtX$prZqZz2rDYSuSGKl0iNBgSlT0DsCDdDgrXsd3lqa+Ec=', 2, 1, N'2026-07-29 07:14:10.315180', N''),
(6, N'lethic', N'lethic@email.com', N'pbkdf2_sha256$1200000$p4FBIVRmF6pkTdEIxnqAkP$mc+x18S0AHTZQY17wktiOoNrWBO2SWr3s9AY9CxRTbw=', 2, 1, N'2026-07-29 07:14:11.111345', N''),
(7, N'phamvand', N'phamvand@email.com', N'pbkdf2_sha256$1200000$3vKlnEy8IxxoXayWs6shvm$5pl2nrsXrnlnbEZF3+HIeTahRGlYL8nJIOg2YDLbzZk=', 2, 1, N'2026-07-29 07:14:11.853581', N''),
(8, N'hoangthie', N'hoangthie@email.com', N'pbkdf2_sha256$1200000$0P3KGbieRYWZyPHzakHGQ5$0DlryNLxs6Ghjxopk8XWjfsgrwIhvQfp1HhghFla0H0=', 2, 1, N'2026-07-29 07:14:12.700696', N'');
GO
SET IDENTITY_INSERT [Users] OFF;
GO

-- Danh mục sản phẩm (3 rows)
SET IDENTITY_INSERT [Categories] ON;
GO
INSERT INTO [Categories] ([id], [name], [slug]) VALUES
(1, N'Quần', N'quan'),
(2, N'Phụ Kiện', N'phu-kien'),
(3, N'Áo', N'ao');
GO
SET IDENTITY_INSERT [Categories] OFF;
GO

-- Sản phẩm (56 rows)
SET IDENTITY_INSERT [Products] ON;
GO
INSERT INTO [Products] ([id], [name], [slug], [category_id], [price], [stock], [available], [featured], [image_url], [created]) VALUES
(1, N'Quần jogger Tech Cuff', N'jogger-cuff-tech', 1, 490000, 300, 1, 0, N'', N'2026-07-29 07:14:05.039275'),
(2, N'Mũ lưỡi trai Logo Minimal', N'cap-logo-minimal', 2, 190000, 100, 1, 0, N'', N'2026-07-29 07:14:05.082457'),
(3, N'Quần jeans Baggy Fade Blue', N'jeans-baggy-fade-blue', 1, 590000, 300, 1, 1, N'', N'2026-07-29 07:14:05.099980'),
(4, N'Quần cargo Street Fit', N'cargo-pants-street-fit', 1, 560000, 300, 1, 0, N'', N'2026-07-29 07:14:05.132911'),
(5, N'Áo hoodie Boxy Ash', N'hoodie-boxy-ash', 3, 620000, 300, 1, 0, N'', N'2026-07-29 07:14:05.169303'),
(6, N'Áo thun Oversize Core Black', N'ao-thun-oversize-core-black', 3, 390000, 300, 1, 0, N'', N'2026-07-29 07:14:05.203136'),
(7, N'Khẩu trang 3 lớp', N'khau-trang-3-lop-swe', 2, 345000, 100, 1, 1, N'', N'2026-07-29 07:14:05.237829'),
(8, N'Găng tay ngón cụt', N'gang-tay-ngon-cut', 2, 330000, 100, 1, 0, N'', N'2026-07-29 07:14:05.256899'),
(9, N'Kính mát gọng vuông', N'kinh-mat-frame-vuong', 2, 315000, 100, 1, 0, N'', N'2026-07-29 07:14:05.274827'),
(10, N'Dây đeo điện thoại', N'day-deo-dien-thoai', 2, 300000, 100, 1, 1, N'', N'2026-07-29 07:14:05.294823'),
(11, N'Bình nước thép 500ml', N'binh-nuoc-steel-500ml', 2, 285000, 100, 1, 0, N'', N'2026-07-29 07:14:05.314503'),
(12, N'Mũ bucket Nylon', N'mu-bucket-nylon', 2, 270000, 100, 1, 0, N'', N'2026-07-29 07:14:05.335675'),
(13, N'Móc khóa Carabiner', N'moc-khoa-carabiner', 2, 255000, 100, 1, 1, N'', N'2026-07-29 07:14:05.354800'),
(14, N'Khăn bandana Mono', N'khan-bandana-mono', 2, 240000, 100, 1, 0, N'', N'2026-07-29 07:14:05.373604'),
(15, N'Ví mini Reflect', N'vi-mini-reflect', 2, 225000, 100, 1, 1, N'', N'2026-07-29 07:14:05.393523'),
(16, N'Thắt lưng Webbing', N'that-lung-webbing', 2, 210000, 100, 1, 0, N'', N'2026-07-29 07:14:05.418064'),
(17, N'Vớ cổ cao Logo', N'vo-co-cao-logo', 2, 195000, 100, 1, 0, N'', N'2026-07-29 07:14:05.444298'),
(18, N'Túi tote Canvas Heavy', N'tui-tote-canvas-heavy', 2, 180000, 100, 1, 0, N'', N'2026-07-29 07:14:05.472122'),
(19, N'Túi đeo chéo Mini Pack', N'tui-deo-cheo-mini-pack', 2, 165000, 100, 1, 0, N'', N'2026-07-29 07:14:05.502016'),
(20, N'Mũ len Beanie Ribbed', N'beanie-ribbed', 2, 150000, 100, 1, 0, N'', N'2026-07-29 07:14:05.529016'),
(21, N'Nón lưỡi trai Basic', N'non-luoi-trai-swe', 2, 135000, 100, 1, 0, N'', N'2026-07-29 07:14:05.549690'),
(22, N'Quần ống rộng Pleated', N'quan-ong-rong-pleated', 1, 645000, 300, 1, 0, N'', N'2026-07-29 07:14:05.568545'),
(23, N'Quần chino Loose Fit', N'quan-chinos-loose', 1, 630000, 300, 1, 0, N'', N'2026-07-29 07:14:05.607458'),
(24, N'Quần short denim Washed', N'quan-shorts-denim-washed', 1, 615000, 300, 1, 0, N'', N'2026-07-29 07:14:05.646619'),
(25, N'Quần denim Raw Hem', N'quan-denim-raw-hem', 1, 600000, 300, 1, 0, N'', N'2026-07-29 07:14:05.684455'),
(26, N'Quần cargo Ripstop', N'quan-cargo-ripstop', 1, 585000, 300, 1, 0, N'', N'2026-07-29 07:14:05.723017'),
(27, N'Quần nỉ Daily', N'quan-ni-daily', 1, 570000, 300, 1, 1, N'', N'2026-07-29 07:14:05.765953'),
(28, N'Quần track pants Side Line', N'quan-track-pant-side-line', 1, 555000, 300, 1, 0, N'', N'2026-07-29 07:14:05.807306'),
(29, N'Quần dù Parachute', N'quan-du-parachute', 1, 540000, 300, 1, 0, N'', N'2026-07-29 07:14:05.847450'),
(30, N'Quần tây Relax Fit', N'quan-tay-relax-fit', 1, 525000, 300, 1, 0, N'', N'2026-07-29 07:14:05.888145'),
(31, N'Quần short nỉ Basic', N'quan-short-sweat-basic', 1, 510000, 300, 1, 1, N'', N'2026-07-29 07:14:05.929588'),
(32, N'Quần short Utility', N'quan-short-utility', 1, 495000, 300, 1, 0, N'', N'2026-07-29 07:14:05.978866'),
(33, N'Quần jeans Baggy Fade', N'quan-jeans-baggy-fade', 1, 480000, 300, 1, 0, N'', N'2026-07-29 07:14:06.039276'),
(34, N'Quần jeans Straight 90s', N'quan-jeans-straight-90s', 1, 465000, 300, 1, 1, N'', N'2026-07-29 07:14:06.096665'),
(35, N'Quần jogger Tech Cuff', N'quan-jogger-cuff-tech', 1, 450000, 300, 1, 0, N'', N'2026-07-29 07:14:06.152606'),
(36, N'Quần cargo Multi Pocket', N'quan-cargo-multi-pocket', 1, 435000, 300, 1, 0, N'', N'2026-07-29 07:14:06.199548'),
(37, N'Áo sơ mi Cuban Camp', N'ao-so-mi-cuban-camp', 3, 590000, 300, 1, 0, N'', N'2026-07-29 07:14:06.247999'),
(38, N'Áo hoodie Washed Ink', N'ao-hoodie-washed-ink', 3, 575000, 300, 1, 0, N'', N'2026-07-29 07:14:06.291727'),
(39, N'Áo thun Graphic No.02', N'ao-thun-graphic-no02', 3, 560000, 300, 1, 0, N'', N'2026-07-29 07:14:06.334777'),
(40, N'Áo thun Graphic No.01', N'ao-thun-graphic-no01', 3, 545000, 300, 1, 1, N'', N'2026-07-29 07:14:06.377027'),
(41, N'Áo khoác coach Track Unit', N'ao-coach-jacket-track-unit', 3, 530000, 300, 1, 0, N'', N'2026-07-29 07:14:06.415945'),
(42, N'Áo khoác denim Blue Stone', N'ao-denim-jacket-blue-stone', 3, 515000, 300, 1, 0, N'', N'2026-07-29 07:14:06.455742'),
(43, N'Áo cardigan Knit Loose', N'ao-cardigan-knit-loose', 3, 500000, 300, 1, 0, N'', N'2026-07-29 07:14:06.496928'),
(44, N'Áo thun cổ cao Mock Neck', N'ao-thun-co-cao-mock-neck', 3, 485000, 300, 1, 0, N'', N'2026-07-29 07:14:06.557235'),
(45, N'Áo tank top Base Layer', N'ao-tanktop-base-layer', 3, 470000, 300, 1, 0, N'', N'2026-07-29 07:14:06.613614'),
(46, N'Áo jersey Sport Line', N'ao-jersey-sportline', 3, 455000, 300, 1, 0, N'', N'2026-07-29 07:14:06.657717'),
(47, N'Áo khoác bomber Mono', N'ao-khoac-bomber-mono', 3, 440000, 300, 1, 0, N'', N'2026-07-29 07:14:06.708227'),
(48, N'Áo khoác gió Wind Layer', N'ao-khoac-gio-wind-layer', 3, 425000, 300, 1, 1, N'', N'2026-07-29 07:14:06.755964'),
(49, N'Áo sơ mi Flannel Street Check', N'ao-so-mi-flannel-street-check', 3, 410000, 300, 1, 0, N'', N'2026-07-29 07:14:06.818264'),
(50, N'Áo sweatshirt Varsity', N'ao-sweatshirt-varsity', 3, 395000, 300, 1, 1, N'', N'2026-07-29 07:14:06.868037');
GO
INSERT INTO [Products] ([id], [name], [slug], [category_id], [price], [stock], [available], [featured], [image_url], [created]) VALUES
(51, N'Áo hoodie Boxy Blackout', N'ao-hoodie-boxy-blackout', 3, 380000, 300, 1, 0, N'', N'2026-07-29 07:14:06.909905'),
(52, N'Áo hoodie khóa kéo Raw Edge', N'ao-hoodie-zip-raw-edge', 3, 365000, 300, 1, 0, N'', N'2026-07-29 07:14:06.960703'),
(53, N'Áo polo Dệt Urban', N'ao-polo-knit-urban', 3, 350000, 300, 1, 1, N'', N'2026-07-29 07:14:07.009928'),
(54, N'Áo thun Faded Wash', N'ao-thun-faded-wash', 3, 335000, 300, 1, 0, N'', N'2026-07-29 07:14:07.051805'),
(55, N'Áo thun Boxy Signature', N'ao-thun-boxy-signature', 3, 320000, 300, 1, 0, N'', N'2026-07-29 07:14:07.094384'),
(56, N'Áo thun Oversize Core Logo', N'ao-thun-oversize-core-logo', 3, 305000, 300, 1, 0, N'', N'2026-07-29 07:14:07.135085');
GO
SET IDENTITY_INSERT [Products] OFF;
GO

-- Biến thể sản phẩm (màu sắc, kích cỡ) (272 rows)
SET IDENTITY_INSERT [Variants] ON;
GO
INSERT INTO [Variants] ([id], [product_id], [color_name], [color_code], [size], [stock], [is_active]) VALUES
(1, 1, N'Đen', N'#111111', N'M', 50, 1),
(2, 1, N'Đen', N'#111111', N'L', 50, 1),
(3, 1, N'Đen', N'#111111', N'XL', 50, 1),
(4, 1, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(5, 1, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(6, 1, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(7, 2, N'Đen', N'#111111', N'FREE', 50, 1),
(8, 2, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(9, 3, N'Đen', N'#111111', N'M', 50, 1),
(10, 3, N'Đen', N'#111111', N'L', 50, 1),
(11, 3, N'Đen', N'#111111', N'XL', 50, 1),
(12, 3, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(13, 3, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(14, 3, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(15, 4, N'Đen', N'#111111', N'M', 50, 1),
(16, 4, N'Đen', N'#111111', N'L', 50, 1),
(17, 4, N'Đen', N'#111111', N'XL', 50, 1),
(18, 4, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(19, 4, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(20, 4, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(21, 5, N'Đen', N'#111111', N'M', 50, 1),
(22, 5, N'Đen', N'#111111', N'L', 50, 1),
(23, 5, N'Đen', N'#111111', N'XL', 50, 1),
(24, 5, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(25, 5, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(26, 5, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(27, 6, N'Đen', N'#111111', N'M', 50, 1),
(28, 6, N'Đen', N'#111111', N'L', 50, 1),
(29, 6, N'Đen', N'#111111', N'XL', 50, 1),
(30, 6, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(31, 6, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(32, 6, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(33, 7, N'Đen', N'#111111', N'FREE', 50, 1),
(34, 7, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(35, 8, N'Đen', N'#111111', N'FREE', 50, 1),
(36, 8, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(37, 9, N'Đen', N'#111111', N'FREE', 50, 1),
(38, 9, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(39, 10, N'Đen', N'#111111', N'FREE', 50, 1),
(40, 10, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(41, 11, N'Đen', N'#111111', N'FREE', 50, 1),
(42, 11, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(43, 12, N'Đen', N'#111111', N'FREE', 50, 1),
(44, 12, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(45, 13, N'Đen', N'#111111', N'FREE', 50, 1),
(46, 13, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(47, 14, N'Đen', N'#111111', N'FREE', 50, 1),
(48, 14, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(49, 15, N'Đen', N'#111111', N'FREE', 50, 1),
(50, 15, N'Trắng', N'#F5F5F5', N'FREE', 50, 1);
GO
INSERT INTO [Variants] ([id], [product_id], [color_name], [color_code], [size], [stock], [is_active]) VALUES
(51, 16, N'Đen', N'#111111', N'FREE', 50, 1),
(52, 16, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(53, 17, N'Đen', N'#111111', N'FREE', 50, 1),
(54, 17, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(55, 18, N'Đen', N'#111111', N'FREE', 50, 1),
(56, 18, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(57, 19, N'Đen', N'#111111', N'FREE', 50, 1),
(58, 19, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(59, 20, N'Đen', N'#111111', N'FREE', 50, 1),
(60, 20, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(61, 21, N'Đen', N'#111111', N'FREE', 50, 1),
(62, 21, N'Trắng', N'#F5F5F5', N'FREE', 50, 1),
(63, 22, N'Đen', N'#111111', N'M', 50, 1),
(64, 22, N'Đen', N'#111111', N'L', 50, 1),
(65, 22, N'Đen', N'#111111', N'XL', 50, 1),
(66, 22, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(67, 22, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(68, 22, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(69, 23, N'Đen', N'#111111', N'M', 50, 1),
(70, 23, N'Đen', N'#111111', N'L', 50, 1),
(71, 23, N'Đen', N'#111111', N'XL', 50, 1),
(72, 23, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(73, 23, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(74, 23, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(75, 24, N'Đen', N'#111111', N'M', 50, 1),
(76, 24, N'Đen', N'#111111', N'L', 50, 1),
(77, 24, N'Đen', N'#111111', N'XL', 50, 1),
(78, 24, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(79, 24, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(80, 24, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(81, 25, N'Đen', N'#111111', N'M', 50, 1),
(82, 25, N'Đen', N'#111111', N'L', 50, 1),
(83, 25, N'Đen', N'#111111', N'XL', 50, 1),
(84, 25, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(85, 25, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(86, 25, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(87, 26, N'Đen', N'#111111', N'M', 50, 1),
(88, 26, N'Đen', N'#111111', N'L', 50, 1),
(89, 26, N'Đen', N'#111111', N'XL', 50, 1),
(90, 26, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(91, 26, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(92, 26, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(93, 27, N'Đen', N'#111111', N'M', 50, 1),
(94, 27, N'Đen', N'#111111', N'L', 50, 1),
(95, 27, N'Đen', N'#111111', N'XL', 50, 1),
(96, 27, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(97, 27, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(98, 27, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(99, 28, N'Đen', N'#111111', N'M', 50, 1),
(100, 28, N'Đen', N'#111111', N'L', 50, 1);
GO
INSERT INTO [Variants] ([id], [product_id], [color_name], [color_code], [size], [stock], [is_active]) VALUES
(101, 28, N'Đen', N'#111111', N'XL', 50, 1),
(102, 28, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(103, 28, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(104, 28, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(105, 29, N'Đen', N'#111111', N'M', 50, 1),
(106, 29, N'Đen', N'#111111', N'L', 50, 1),
(107, 29, N'Đen', N'#111111', N'XL', 50, 1),
(108, 29, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(109, 29, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(110, 29, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(111, 30, N'Đen', N'#111111', N'M', 50, 1),
(112, 30, N'Đen', N'#111111', N'L', 50, 1),
(113, 30, N'Đen', N'#111111', N'XL', 50, 1),
(114, 30, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(115, 30, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(116, 30, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(117, 31, N'Đen', N'#111111', N'M', 50, 1),
(118, 31, N'Đen', N'#111111', N'L', 50, 1),
(119, 31, N'Đen', N'#111111', N'XL', 50, 1),
(120, 31, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(121, 31, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(122, 31, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(123, 32, N'Đen', N'#111111', N'M', 50, 1),
(124, 32, N'Đen', N'#111111', N'L', 50, 1),
(125, 32, N'Đen', N'#111111', N'XL', 50, 1),
(126, 32, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(127, 32, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(128, 32, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(129, 33, N'Đen', N'#111111', N'M', 50, 1),
(130, 33, N'Đen', N'#111111', N'L', 50, 1),
(131, 33, N'Đen', N'#111111', N'XL', 50, 1),
(132, 33, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(133, 33, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(134, 33, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(135, 34, N'Đen', N'#111111', N'M', 50, 1),
(136, 34, N'Đen', N'#111111', N'L', 50, 1),
(137, 34, N'Đen', N'#111111', N'XL', 50, 1),
(138, 34, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(139, 34, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(140, 34, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(141, 35, N'Đen', N'#111111', N'M', 50, 1),
(142, 35, N'Đen', N'#111111', N'L', 50, 1),
(143, 35, N'Đen', N'#111111', N'XL', 50, 1),
(144, 35, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(145, 35, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(146, 35, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(147, 36, N'Đen', N'#111111', N'M', 50, 1),
(148, 36, N'Đen', N'#111111', N'L', 50, 1),
(149, 36, N'Đen', N'#111111', N'XL', 50, 1),
(150, 36, N'Trắng', N'#F5F5F5', N'M', 50, 1);
GO
INSERT INTO [Variants] ([id], [product_id], [color_name], [color_code], [size], [stock], [is_active]) VALUES
(151, 36, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(152, 36, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(153, 37, N'Đen', N'#111111', N'M', 50, 1),
(154, 37, N'Đen', N'#111111', N'L', 50, 1),
(155, 37, N'Đen', N'#111111', N'XL', 50, 1),
(156, 37, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(157, 37, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(158, 37, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(159, 38, N'Đen', N'#111111', N'M', 50, 1),
(160, 38, N'Đen', N'#111111', N'L', 50, 1),
(161, 38, N'Đen', N'#111111', N'XL', 50, 1),
(162, 38, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(163, 38, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(164, 38, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(165, 39, N'Đen', N'#111111', N'M', 50, 1),
(166, 39, N'Đen', N'#111111', N'L', 50, 1),
(167, 39, N'Đen', N'#111111', N'XL', 50, 1),
(168, 39, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(169, 39, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(170, 39, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(171, 40, N'Đen', N'#111111', N'M', 50, 1),
(172, 40, N'Đen', N'#111111', N'L', 50, 1),
(173, 40, N'Đen', N'#111111', N'XL', 50, 1),
(174, 40, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(175, 40, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(176, 40, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(177, 41, N'Đen', N'#111111', N'M', 50, 1),
(178, 41, N'Đen', N'#111111', N'L', 50, 1),
(179, 41, N'Đen', N'#111111', N'XL', 50, 1),
(180, 41, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(181, 41, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(182, 41, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(183, 42, N'Đen', N'#111111', N'M', 50, 1),
(184, 42, N'Đen', N'#111111', N'L', 50, 1),
(185, 42, N'Đen', N'#111111', N'XL', 50, 1),
(186, 42, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(187, 42, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(188, 42, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(189, 43, N'Đen', N'#111111', N'M', 50, 1),
(190, 43, N'Đen', N'#111111', N'L', 50, 1),
(191, 43, N'Đen', N'#111111', N'XL', 50, 1),
(192, 43, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(193, 43, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(194, 43, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(195, 44, N'Đen', N'#111111', N'M', 50, 1),
(196, 44, N'Đen', N'#111111', N'L', 50, 1),
(197, 44, N'Đen', N'#111111', N'XL', 50, 1),
(198, 44, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(199, 44, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(200, 44, N'Trắng', N'#F5F5F5', N'XL', 50, 1);
GO
INSERT INTO [Variants] ([id], [product_id], [color_name], [color_code], [size], [stock], [is_active]) VALUES
(201, 45, N'Đen', N'#111111', N'M', 50, 1),
(202, 45, N'Đen', N'#111111', N'L', 50, 1),
(203, 45, N'Đen', N'#111111', N'XL', 50, 1),
(204, 45, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(205, 45, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(206, 45, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(207, 46, N'Đen', N'#111111', N'M', 50, 1),
(208, 46, N'Đen', N'#111111', N'L', 50, 1),
(209, 46, N'Đen', N'#111111', N'XL', 50, 1),
(210, 46, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(211, 46, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(212, 46, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(213, 47, N'Đen', N'#111111', N'M', 50, 1),
(214, 47, N'Đen', N'#111111', N'L', 50, 1),
(215, 47, N'Đen', N'#111111', N'XL', 50, 1),
(216, 47, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(217, 47, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(218, 47, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(219, 48, N'Đen', N'#111111', N'M', 50, 1),
(220, 48, N'Đen', N'#111111', N'L', 50, 1),
(221, 48, N'Đen', N'#111111', N'XL', 50, 1),
(222, 48, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(223, 48, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(224, 48, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(225, 49, N'Đen', N'#111111', N'M', 50, 1),
(226, 49, N'Đen', N'#111111', N'L', 50, 1),
(227, 49, N'Đen', N'#111111', N'XL', 50, 1),
(228, 49, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(229, 49, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(230, 49, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(231, 50, N'Đen', N'#111111', N'M', 50, 1),
(232, 50, N'Đen', N'#111111', N'L', 50, 1),
(233, 50, N'Đen', N'#111111', N'XL', 50, 1),
(234, 50, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(235, 50, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(236, 50, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(237, 51, N'Đen', N'#111111', N'M', 50, 1),
(238, 51, N'Đen', N'#111111', N'L', 50, 1),
(239, 51, N'Đen', N'#111111', N'XL', 50, 1),
(240, 51, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(241, 51, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(242, 51, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(243, 52, N'Đen', N'#111111', N'M', 50, 1),
(244, 52, N'Đen', N'#111111', N'L', 50, 1),
(245, 52, N'Đen', N'#111111', N'XL', 50, 1),
(246, 52, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(247, 52, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(248, 52, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(249, 53, N'Đen', N'#111111', N'M', 50, 1),
(250, 53, N'Đen', N'#111111', N'L', 50, 1);
GO
INSERT INTO [Variants] ([id], [product_id], [color_name], [color_code], [size], [stock], [is_active]) VALUES
(251, 53, N'Đen', N'#111111', N'XL', 50, 1),
(252, 53, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(253, 53, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(254, 53, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(255, 54, N'Đen', N'#111111', N'M', 50, 1),
(256, 54, N'Đen', N'#111111', N'L', 50, 1),
(257, 54, N'Đen', N'#111111', N'XL', 50, 1),
(258, 54, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(259, 54, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(260, 54, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(261, 55, N'Đen', N'#111111', N'M', 50, 1),
(262, 55, N'Đen', N'#111111', N'L', 50, 1),
(263, 55, N'Đen', N'#111111', N'XL', 50, 1),
(264, 55, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(265, 55, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(266, 55, N'Trắng', N'#F5F5F5', N'XL', 50, 1),
(267, 56, N'Đen', N'#111111', N'M', 50, 1),
(268, 56, N'Đen', N'#111111', N'L', 50, 1),
(269, 56, N'Đen', N'#111111', N'XL', 50, 1),
(270, 56, N'Trắng', N'#F5F5F5', N'M', 50, 1),
(271, 56, N'Trắng', N'#F5F5F5', N'L', 50, 1),
(272, 56, N'Trắng', N'#F5F5F5', N'XL', 50, 1);
GO
SET IDENTITY_INSERT [Variants] OFF;
GO

-- Mã giảm giá (5 rows)
SET IDENTITY_INSERT [Coupons] ON;
GO
INSERT INTO [Coupons] ([id], [code], [type], [value], [is_active], [min_amount], [max_amount], [max_uses], [used_count]) VALUES
(1, N'FREESHIP', N'freeship', 0, 1, 200000, NULL, NULL, 0),
(2, N'SALE10', N'percent', 10, 1, 100000, 50000, NULL, 0),
(3, N'GIAM50K', N'fixed', 50000, 1, 300000, NULL, NULL, 0),
(4, N'WELCOME', N'percent', 15, 1, 0, 100000, 100, 0),
(5, N'BLACKFRI', N'percent', 30, 0, 0, 200000, NULL, 0);
GO
SET IDENTITY_INSERT [Coupons] OFF;
GO

-- Đơn hàng (41 rows)
SET IDENTITY_INSERT [Orders] ON;
GO
INSERT INTO [Orders] ([id], [user_id], [customer_name], [phone], [shipping_address], [status], [total_amount], [is_paid], [payment_method], [discount_amount], [coupon], [created_at]) VALUES
(1, 2, N'codexstaff', N'0938527191', N'352 Đường Lê Lợi, Quận 1, TP.HCM', N'delivered', 1710000, 1, N'cod', 0, N'', N'2026-06-28 11:14:13.570638'),
(2, 2, N'codexstaff', N'0959634497', N'500 Đường Hai Bà Trưng, Quận 10, TP.HCM', N'cancelled', 2100000, 0, N'bank', 0, N'', N'2026-07-26 06:14:13.570638'),
(3, 2, N'codexstaff', N'0972247333', N'929 Đường Lý Thường Kiệt, Quận 6, TP.HCM', N'cancelled', 840000, 0, N'bank', 0, N'', N'2026-06-19 10:14:13.570638'),
(4, 2, N'codexstaff', N'0988730142', N'237 Đường Lê Lợi, Quận 8, TP.HCM', N'cancelled', 820000, 0, N'bank', 0, N'', N'2026-07-28 06:14:13.570638'),
(5, 2, N'codexstaff', N'0965977189', N'906 Đường Nguyễn Huệ, Quận 4, TP.HCM', N'shipping', 3235000, 1, N'bank', 0, N'', N'2026-06-28 15:14:13.570638'),
(6, 2, N'codexstaff', N'0946816445', N'847 Đường Nguyễn Huệ, Quận 2, TP.HCM', N'cancelled', 1215000, 0, N'cod', 0, N'', N'2026-07-22 21:14:13.570638'),
(7, 3, N'readmestaff', N'0911226597', N'108 Đường Hai Bà Trưng, Quận 6, TP.HCM', N'delivered', 880000, 1, N'bank', 0, N'', N'2026-06-16 05:14:13.570638'),
(8, 3, N'readmestaff', N'0976009952', N'405 Đường Võ Văn Tần, Quận 8, TP.HCM', N'delivered', 570000, 1, N'bank', 0, N'', N'2026-06-25 18:14:13.570638'),
(9, 3, N'readmestaff', N'0939702613', N'315 Đường Nguyễn Huệ, Quận 5, TP.HCM', N'pending', 1475000, 0, N'cod', 0, N'', N'2026-07-06 12:14:13.570638'),
(10, 3, N'readmestaff', N'0937342462', N'181 Đường Võ Văn Tần, Quận 3, TP.HCM', N'delivered', 3000000, 1, N'cod', 0, N'FREESHIP', N'2026-07-13 03:14:13.570638'),
(11, 3, N'readmestaff', N'0946403207', N'77 Đường Trần Hưng Đạo, Quận 4, TP.HCM', N'delivered', 2080000, 1, N'bank', 0, N'', N'2026-06-27 13:14:13.570638'),
(12, 3, N'readmestaff', N'0925962600', N'439 Đường Nguyễn Huệ, Quận 10, TP.HCM', N'cancelled', 2355000, 0, N'bank', 0, N'', N'2026-07-18 18:14:13.570638'),
(13, 4, N'nguyenvanA', N'0937003067', N'102 Đường Hai Bà Trưng, Quận 6, TP.HCM', N'pending', 365000, 0, N'cod', 0, N'', N'2026-06-17 18:14:13.570638'),
(14, 4, N'nguyenvanA', N'0980629076', N'910 Đường Trần Hưng Đạo, Quận 1, TP.HCM', N'delivered', 1015000, 1, N'cod', 50000, N'GIAM50K', N'2026-07-09 09:14:13.570638'),
(15, 4, N'nguyenvanA', N'0985714721', N'487 Đường Hai Bà Trưng, Quận 11, TP.HCM', N'delivered', 750000, 1, N'bank', 100000, N'WELCOME', N'2026-07-25 04:14:13.570638'),
(16, 4, N'nguyenvanA', N'0954048205', N'638 Đường Nguyễn Huệ, Quận 3, TP.HCM', N'shipping', 1805000, 1, N'bank', 0, N'', N'2026-07-09 19:14:13.570638'),
(17, 4, N'nguyenvanA', N'0926415594', N'767 Đường Nguyễn Huệ, Quận 5, TP.HCM', N'delivered', 315000, 1, N'cod', 0, N'', N'2026-07-27 10:14:13.570638'),
(18, 4, N'nguyenvanA', N'0923077265', N'954 Đường Hai Bà Trưng, Quận 5, TP.HCM', N'processing', 1695000, 0, N'bank', 0, N'', N'2026-06-15 14:14:13.570638'),
(19, 4, N'nguyenvanA', N'0996255426', N'786 Đường Trần Hưng Đạo, Quận 2, TP.HCM', N'delivered', 1645000, 1, N'cod', 50000, N'GIAM50K', N'2026-06-24 23:14:13.570638'),
(20, 5, N'tranthib', N'0925783215', N'661 Đường Lý Thường Kiệt, Quận 5, TP.HCM', N'processing', 2020000, 0, N'cod', 50000, N'GIAM50K', N'2026-07-01 17:14:13.570638'),
(21, 5, N'tranthib', N'0912871000', N'78 Đường Cách Mạng Tháng 8, Quận 1, TP.HCM', N'pending', 300000, 0, N'cod', 0, N'', N'2026-06-16 08:14:13.570638'),
(22, 5, N'tranthib', N'0910912808', N'560 Đường Võ Văn Tần, Quận 8, TP.HCM', N'cancelled', 1755000, 0, N'cod', 0, N'', N'2026-06-24 10:14:13.570638'),
(23, 5, N'tranthib', N'0971586160', N'230 Đường Lý Thường Kiệt, Quận 4, TP.HCM', N'delivered', 1150000, 1, N'cod', 0, N'', N'2026-07-02 03:14:13.570638'),
(24, 5, N'tranthib', N'0933652520', N'567 Đường Lý Thường Kiệt, Quận 8, TP.HCM', N'processing', 2015000, 0, N'bank', 50000, N'SALE10', N'2026-07-17 08:14:13.570638'),
(25, 5, N'tranthib', N'0969816650', N'662 Đường Cách Mạng Tháng 8, Quận 2, TP.HCM', N'cancelled', 1260000, 0, N'bank', 0, N'', N'2026-07-19 08:14:13.570638'),
(26, 5, N'tranthib', N'0937270704', N'935 Đường Hai Bà Trưng, Quận 11, TP.HCM', N'pending', 2240000, 0, N'cod', 0, N'', N'2026-07-04 00:14:13.570638'),
(27, 6, N'lethic', N'0956907072', N'691 Đường Trần Hưng Đạo, Quận 4, TP.HCM', N'shipping', 2490000, 1, N'cod', 0, N'', N'2026-07-02 14:14:13.570638'),
(28, 6, N'lethic', N'0950447994', N'837 Đường Võ Văn Tần, Quận 1, TP.HCM', N'cancelled', 620000, 0, N'cod', 0, N'', N'2026-07-09 15:14:13.570638'),
(29, 6, N'lethic', N'0993959209', N'86 Đường Phạm Ngũ Lão, Quận 4, TP.HCM', N'processing', 1560000, 0, N'cod', 0, N'FREESHIP', N'2026-06-15 06:14:13.570638'),
(30, 6, N'lethic', N'0958744981', N'241 Đường Võ Văn Tần, Quận 7, TP.HCM', N'processing', 390000, 0, N'cod', 0, N'FREESHIP', N'2026-06-18 06:14:13.570638'),
(31, 7, N'phamvand', N'0921416687', N'964 Đường Phạm Ngũ Lão, Quận 7, TP.HCM', N'processing', 3335000, 0, N'bank', 50000, N'SALE10', N'2026-07-19 14:14:13.570638'),
(32, 7, N'phamvand', N'0999910432', N'975 Đường Cách Mạng Tháng 8, Quận 8, TP.HCM', N'cancelled', 575000, 0, N'bank', 0, N'', N'2026-07-21 01:14:13.570638'),
(33, 7, N'phamvand', N'0923183536', N'869 Đường Lý Thường Kiệt, Quận 4, TP.HCM', N'delivered', 1425000, 1, N'cod', 0, N'', N'2026-06-27 05:14:13.570638'),
(34, 7, N'phamvand', N'0999612041', N'438 Đường Cách Mạng Tháng 8, Quận 7, TP.HCM', N'processing', 530000, 0, N'cod', 0, N'FREESHIP', N'2026-07-26 02:14:13.570638'),
(35, 7, N'phamvand', N'0933550676', N'683 Đường Hai Bà Trưng, Quận 3, TP.HCM', N'delivered', 405000, 1, N'bank', 50000, N'GIAM50K', N'2026-07-07 15:14:13.570638'),
(36, 7, N'phamvand', N'0919902974', N'13 Đường Cách Mạng Tháng 8, Quận 5, TP.HCM', N'processing', 297750, 0, N'bank', 47250, N'WELCOME', N'2026-07-12 08:14:13.570638'),
(37, 8, N'hoangthie', N'0968589984', N'643 Đường Trần Hưng Đạo, Quận 4, TP.HCM', N'delivered', 1050000, 1, N'bank', 50000, N'GIAM50K', N'2026-07-20 09:14:13.570638'),
(38, 8, N'hoangthie', N'0946777498', N'156 Đường Phạm Ngũ Lão, Quận 3, TP.HCM', N'shipping', 860000, 1, N'cod', 0, N'', N'2026-07-14 16:14:13.570638'),
(39, 8, N'hoangthie', N'0934846728', N'533 Đường Trần Hưng Đạo, Quận 10, TP.HCM', N'cancelled', 225000, 0, N'bank', 0, N'', N'2026-06-24 01:14:13.570638'),
(40, 8, N'hoangthie', N'0994281564', N'759 Đường Cách Mạng Tháng 8, Quận 7, TP.HCM', N'pending', 2700000, 0, N'cod', 0, N'', N'2026-06-23 05:14:13.570638'),
(41, 8, N'hoangthie', N'0916148050', N'35 Đường Lê Lợi, Quận 9, TP.HCM', N'processing', 1425000, 0, N'bank', 0, N'', N'2026-07-17 18:14:13.570638');
GO
SET IDENTITY_INSERT [Orders] OFF;
GO

-- Chi tiết đơn hàng (64 rows)
SET IDENTITY_INSERT [OrderItems] ON;
GO
INSERT INTO [OrderItems] ([id], [order_id], [product_id], [variant_id], [color], [size], [quantity], [price]) VALUES
(1, 1, 39, 169, N'Trắng', N'L', 3, 560000),
(2, 2, 35, 145, N'Trắng', N'L', 2, 450000),
(3, 2, 26, 91, N'Trắng', N'L', 2, 585000),
(4, 3, 16, 52, N'Trắng', N'FREE', 2, 210000),
(5, 3, 17, 54, N'Trắng', N'FREE', 2, 195000),
(6, 4, 50, 235, N'Trắng', N'L', 2, 395000),
(7, 5, 18, 56, N'Trắng', N'FREE', 3, 180000),
(8, 5, 22, 67, N'Trắng', N'L', 3, 645000),
(9, 5, 52, 247, N'Trắng', N'L', 2, 365000),
(10, 6, 50, 235, N'Trắng', N'L', 3, 395000),
(11, 7, 48, 223, N'Trắng', N'L', 2, 425000),
(12, 8, 29, 109, N'Trắng', N'L', 1, 540000),
(13, 9, 52, 247, N'Trắng', N'L', 1, 365000),
(14, 9, 29, 109, N'Trắng', N'L', 2, 540000),
(15, 10, 22, 67, N'Trắng', N'L', 3, 645000),
(16, 10, 7, 34, N'Trắng', N'FREE', 3, 345000),
(17, 11, 24, 79, N'Trắng', N'L', 2, 615000),
(18, 11, 49, 229, N'Trắng', N'L', 2, 410000),
(19, 12, 27, 97, N'Trắng', N'L', 2, 570000),
(20, 12, 50, 235, N'Trắng', N'L', 3, 395000),
(21, 13, 54, 259, N'Trắng', N'L', 1, 335000),
(22, 14, 34, 139, N'Trắng', N'L', 1, 465000),
(23, 14, 2, 8, N'Trắng', N'FREE', 3, 190000),
(24, 15, 49, 229, N'Trắng', N'L', 2, 410000),
(25, 16, 22, 67, N'Trắng', N'L', 2, 645000),
(26, 16, 44, 199, N'Trắng', N'L', 1, 485000),
(27, 17, 11, 42, N'Trắng', N'FREE', 1, 285000),
(28, 18, 28, 103, N'Trắng', N'L', 3, 555000),
(29, 19, 28, 103, N'Trắng', N'L', 3, 555000),
(30, 20, 30, 115, N'Trắng', N'L', 2, 525000),
(31, 20, 8, 36, N'Trắng', N'FREE', 3, 330000),
(32, 21, 21, 62, N'Trắng', N'FREE', 2, 135000),
(33, 22, 38, 163, N'Trắng', N'L', 3, 575000),
(34, 23, 4, 19, N'Trắng', N'L', 2, 560000),
(35, 24, 54, 259, N'Trắng', N'L', 3, 335000),
(36, 24, 42, 187, N'Trắng', N'L', 2, 515000),
(37, 25, 8, 36, N'Trắng', N'FREE', 2, 330000),
(38, 25, 2, 8, N'Trắng', N'FREE', 3, 190000),
(39, 26, 23, 73, N'Trắng', N'L', 1, 630000),
(40, 26, 41, 181, N'Trắng', N'L', 1, 530000),
(41, 26, 53, 253, N'Trắng', N'L', 3, 350000),
(42, 27, 1, 5, N'Trắng', N'L', 3, 490000),
(43, 27, 32, 127, N'Trắng', N'L', 2, 495000),
(44, 28, 3, 13, N'Trắng', N'L', 1, 590000),
(45, 29, 31, 121, N'Trắng', N'L', 3, 510000),
(46, 30, 18, 56, N'Trắng', N'FREE', 2, 180000),
(47, 31, 39, 169, N'Trắng', N'L', 2, 560000),
(48, 31, 24, 79, N'Trắng', N'L', 3, 615000),
(49, 31, 6, 31, N'Trắng', N'L', 1, 390000),
(50, 32, 40, 175, N'Trắng', N'L', 1, 545000);
GO
INSERT INTO [OrderItems] ([id], [order_id], [product_id], [variant_id], [color], [size], [quantity], [price]) VALUES
(51, 33, 34, 139, N'Trắng', N'L', 3, 465000),
(52, 34, 43, 193, N'Trắng', N'L', 1, 500000),
(53, 35, 48, 223, N'Trắng', N'L', 1, 425000),
(54, 36, 9, 38, N'Trắng', N'FREE', 1, 315000),
(55, 37, 33, 133, N'Trắng', N'L', 1, 480000),
(56, 37, 3, 13, N'Trắng', N'L', 1, 590000),
(57, 38, 15, 50, N'Trắng', N'FREE', 2, 225000),
(58, 38, 2, 8, N'Trắng', N'FREE', 2, 190000),
(59, 39, 17, 54, N'Trắng', N'FREE', 1, 195000),
(60, 40, 12, 44, N'Trắng', N'FREE', 3, 270000),
(61, 40, 32, 127, N'Trắng', N'L', 2, 495000),
(62, 40, 36, 151, N'Trắng', N'L', 2, 435000),
(63, 41, 9, 38, N'Trắng', N'FREE', 3, 315000),
(64, 41, 15, 50, N'Trắng', N'FREE', 2, 225000);
GO
SET IDENTITY_INSERT [OrderItems] OFF;
GO

-- Sản phẩm yêu thích (18 rows)
SET IDENTITY_INSERT [Wishlist] ON;
GO
INSERT INTO [Wishlist] ([id], [user_id], [product_id], [created]) VALUES
(1, 2, 23, N'2026-07-29 07:14:14.412789'),
(2, 2, 20, N'2026-07-29 07:14:14.418737'),
(3, 2, 13, N'2026-07-29 07:14:14.423634'),
(4, 3, 24, N'2026-07-29 07:14:14.428886'),
(5, 3, 20, N'2026-07-29 07:14:14.434199'),
(6, 3, 50, N'2026-07-29 07:14:14.444200'),
(7, 3, 49, N'2026-07-29 07:14:14.451635'),
(8, 4, 30, N'2026-07-29 07:14:14.457328'),
(9, 5, 35, N'2026-07-29 07:14:14.462671'),
(10, 5, 48, N'2026-07-29 07:14:14.470979'),
(11, 5, 49, N'2026-07-29 07:14:14.478414'),
(12, 5, 15, N'2026-07-29 07:14:14.483980'),
(13, 6, 15, N'2026-07-29 07:14:14.489318'),
(14, 7, 33, N'2026-07-29 07:14:14.495804'),
(15, 8, 2, N'2026-07-29 07:14:14.500785'),
(16, 8, 39, N'2026-07-29 07:14:14.506761'),
(17, 8, 18, N'2026-07-29 07:14:14.511646'),
(18, 8, 37, N'2026-07-29 07:14:14.516819');
GO
SET IDENTITY_INSERT [Wishlist] OFF;
GO

-- Câu hỏi thường gặp (9 rows)
SET IDENTITY_INSERT [FAQs] ON;
GO
INSERT INTO [FAQs] ([id], [question], [answer], [priority], [is_active]) VALUES
(1, N'Phi ship the nao?', N'Shop free ship toan quoc cho don tu 499K. Ban co the them san pham vao gio de xem phi ship truoc khi dat hang.', 10, 1),
(2, N'Co thanh toan chuyen khoan khong?', N'Shop ho tro thanh toan khi nhan hang va chuyen khoan ngan hang. O trang checkout ban co the chon phuong thuc phu hop.', 20, 1),
(3, N'Lam sao theo doi don?', N'Neu da dang nhap, ban vao muc Don hang de xem trang thai. Sau khi dat thanh cong, he thong cung hien trang xac nhan don ngay tren web.', 30, 1),
(4, N'Tu van size', N'Ban nen vao trang chi tiet san pham de chon mau va size. Neu can, hay gui them chieu cao, can nang va form mac mong muon de shop tu van nhanh hon.', 40, 1),
(5, N'Doi tra nhu the nao?', N'Ban hay lien he shop som nhat sau khi nhan hang neu can doi tra. Shop se can ma don, san pham va ly do doi tra de ho tro nhanh.', 50, 1),
(6, N'Tôi có thể đổi trả hàng không?', N'Chúng tôi hỗ trợ đổi trả trong vòng 7 ngày kể từ khi nhận hàng, với điều kiện sản phẩm còn nguyên tem mác và chưa qua sử dụng.', 10, 1),
(7, N'Thời gian giao hàng bao lâu?', N'Giao hàng nội thành TP.HCM: 1-2 ngày làm việc. Các tỉnh thành khác: 3-7 ngày làm việc.', 20, 1),
(8, N'Tôi có thể hủy đơn hàng không?', N'Bạn có thể hủy đơn hàng trong vòng 24h kể từ khi đặt hàng. Sau thời gian này, vui lòng liên hệ CSKH để được hỗ trợ.', 30, 1),
(9, N'Phương thức thanh toán nào được hỗ trợ?', N'Chúng tôi hỗ trợ thanh toán khi nhận hàng (COD) và chuyển khoản ngân hàng.', 40, 1);
GO
SET IDENTITY_INSERT [FAQs] OFF;
GO

-- Lịch sử hoạt động (51 rows)
SET IDENTITY_INSERT [Activities] ON;
GO
INSERT INTO [Activities] ([id], [user_id], [event], [path], [created_at]) VALUES
(1, 1, N'cart_add', N'/orders/', N'2026-07-29 07:14:14.529296'),
(2, 1, N'checkout', N'/checkout/', N'2026-07-29 07:14:14.539623'),
(3, 1, N'cart_add', N'/checkout/', N'2026-07-29 07:14:14.545798'),
(4, 1, N'page_view', N'/checkout/', N'2026-07-29 07:14:14.550653'),
(5, 1, N'page_view', N'/products/', N'2026-07-29 07:14:14.555423'),
(6, 1, N'page_view', N'/cart/', N'2026-07-29 07:14:14.561428'),
(7, 1, N'page_view', N'/products/', N'2026-07-29 07:14:14.566100'),
(8, 1, N'checkout', N'/products/', N'2026-07-29 07:14:14.571102'),
(9, 2, N'page_view', N'/checkout/', N'2026-07-29 07:14:14.581744'),
(10, 2, N'page_view', N'/checkout/', N'2026-07-29 07:14:14.586073'),
(11, 2, N'page_view', N'/orders/', N'2026-07-29 07:14:14.592023'),
(12, 2, N'page_view', N'/', N'2026-07-29 07:14:14.597137'),
(13, 2, N'page_view', N'/checkout/', N'2026-07-29 07:14:14.604378'),
(14, 2, N'page_view', N'/cart/', N'2026-07-29 07:14:14.608622'),
(15, 2, N'page_view', N'/', N'2026-07-29 07:14:14.613346'),
(16, 3, N'checkout', N'/', N'2026-07-29 07:14:14.621708'),
(17, 3, N'checkout', N'/orders/', N'2026-07-29 07:14:14.630852'),
(18, 3, N'action', N'/', N'2026-07-29 07:14:14.635190'),
(19, 3, N'page_view', N'/products/', N'2026-07-29 07:14:14.639362'),
(20, 3, N'action', N'/orders/', N'2026-07-29 07:14:14.643621'),
(21, 3, N'page_view', N'/cart/', N'2026-07-29 07:14:14.647859'),
(22, 4, N'page_view', N'/checkout/', N'2026-07-29 07:14:14.656512'),
(23, 4, N'page_view', N'/orders/', N'2026-07-29 07:14:14.661348'),
(24, 4, N'action', N'/', N'2026-07-29 07:14:14.664558'),
(25, 4, N'action', N'/products/', N'2026-07-29 07:14:14.668810'),
(26, 4, N'page_view', N'/products/', N'2026-07-29 07:14:14.672512'),
(27, 4, N'action', N'/products/', N'2026-07-29 07:14:14.676779'),
(28, 4, N'checkout', N'/checkout/', N'2026-07-29 07:14:14.681886'),
(29, 5, N'page_view', N'/orders/', N'2026-07-29 07:14:14.689090'),
(30, 5, N'action', N'/products/', N'2026-07-29 07:14:14.692994'),
(31, 5, N'cart_add', N'/cart/', N'2026-07-29 07:14:14.696703'),
(32, 5, N'action', N'/cart/', N'2026-07-29 07:14:14.705535'),
(33, 5, N'action', N'/checkout/', N'2026-07-29 07:14:14.714161'),
(34, 5, N'page_view', N'/checkout/', N'2026-07-29 07:14:14.718143'),
(35, 6, N'action', N'/', N'2026-07-29 07:14:14.725135'),
(36, 6, N'page_view', N'/products/', N'2026-07-29 07:14:14.730653'),
(37, 6, N'page_view', N'/checkout/', N'2026-07-29 07:14:14.734937'),
(38, 6, N'page_view', N'/cart/', N'2026-07-29 07:14:14.738577'),
(39, 6, N'page_view', N'/cart/', N'2026-07-29 07:14:14.743445'),
(40, 6, N'action', N'/orders/', N'2026-07-29 07:14:14.747198'),
(41, 7, N'page_view', N'/cart/', N'2026-07-29 07:14:14.754574'),
(42, 7, N'page_view', N'/cart/', N'2026-07-29 07:14:14.758280'),
(43, 7, N'checkout', N'/checkout/', N'2026-07-29 07:14:14.762627'),
(44, 7, N'page_view', N'/products/', N'2026-07-29 07:14:14.766386'),
(45, 7, N'page_view', N'/cart/', N'2026-07-29 07:14:14.770083'),
(46, 7, N'checkout', N'/', N'2026-07-29 07:14:14.773768'),
(47, 7, N'action', N'/checkout/', N'2026-07-29 07:14:14.776964'),
(48, 8, N'action', N'/orders/', N'2026-07-29 07:14:14.785587'),
(49, 8, N'checkout', N'/products/', N'2026-07-29 07:14:14.789966'),
(50, 8, N'action', N'/', N'2026-07-29 07:14:14.793835');
GO
INSERT INTO [Activities] ([id], [user_id], [event], [path], [created_at]) VALUES
(51, 8, N'page_view', N'/', N'2026-07-29 07:14:14.797574');
GO
SET IDENTITY_INSERT [Activities] OFF;
GO

-- ============================================================
-- Additional seed data: 10 users, 20 products, 59 orders
-- All new users password: user123
-- ============================================================
GO

-- 10 user accounts (password: user123)
SET IDENTITY_INSERT [Users] ON;
GO
INSERT INTO [Users] ([id],[username],[email],[password],[role],[is_active],[date_joined],[phone]) VALUES
(9, N'nguyenvanE', N'nguyenvane@email.com', N'pbkdf2_sha256$1200000$KQtzQK4Wwzk2NaNO24FXn9$0+eZ6ha6eoVblSk8qv6XOg2jscprdlkg1veeAALlrNA=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(10, N'phamthif', N'phamthif@email.com', N'pbkdf2_sha256$1200000$nEJO69pXugv88XGchrgKtX$prZqZz2rDYSuSGKl0iNBgSlT0DsCDdDgrXsd3lqa+Ec=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(11, N'hoangthig', N'hoangthig@email.com', N'pbkdf2_sha256$1200000$p4FBIVRmF6pkTdEIxnqAkP$mc+x18S0AHTZQY17wktiOoNrWBO2SWr3s9AY9CxRTbw=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(12, N'dothih', N'dothih@email.com', N'pbkdf2_sha256$1200000$3vKlnEy8IxxoXayWs6shvm$5pl2nrsXrnlnbEZF3+HIeTahRGlYL8nJIOg2YDLbzZk=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(13, N'buithii', N'buithii@email.com', N'pbkdf2_sha256$1200000$0P3KGbieRYWZyPHzakHGQ5$0DlryNLxs6Ghjxopk8XWjfsgrwIhvQfp1HhghFla0H0=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(14, N'dangthank', N'dangthank@email.com', N'pbkdf2_sha256$1200000$iAffsnahNyqOpChCH3RkIX$Mfh/gUfAjc85kRqawENqljkkvoLbwC8Cag+pqxrRtAU=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(15, N'ngothil', N'ngothil@email.com', N'pbkdf2_sha256$1200000$b5HIwfIJJwjrJmfTqaLwLs$xw7eZ+ChgcfWLZLzssVzMsfiWMwOHw8CJfNkgnN/2cY=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(16, N'lyvanm', N'lyvanm@email.com', N'pbkdf2_sha256$1200000$QcRD6Gk5VzAROSvKMMm80f$0Z8BvzS2D7Q062vQjJTI3+mMStmong9aiBl2awO5Pwo=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(17, N'tranvann', N'tranvann@email.com', N'pbkdf2_sha256$1200000$HjF5z1glcLmZpvSQaXGswl$xhE7Rz4EWF6S/q+yIacGk5Yn6KARd4S7LinxjXsJ8fk=', 2, 1, N'2026-07-30 07:14:07.174474', N''),
(18, N'vuongo', N'vuongo@email.com', N'pbkdf2_sha256$1200000$2dOp0Fd1jOOXnaB7gVnWkF$2uSu52dXH/C0RbXaU2y/8QCjXgTr2WeMDdssOfdGKg4=', 2, 1, N'2026-07-30 07:14:07.174474', N'');
GO
SET IDENTITY_INSERT [Users] OFF;
GO

-- 20 additional products
SET IDENTITY_INSERT [Products] ON;
GO
INSERT INTO [Products] ([id],[name],[slug],[category_id],[price],[stock],[available],[featured],[image_url],[created]) VALUES
(57,N'Áo khoác lông vũ Puffer',N'ao-khoac-long-vu-puffer',3,890000,200,1,1,N'',N'2026-07-30 07:14:05.039275'),
(58,N'Áo blazer Oversize',N'ao-blazer-oversize',3,750000,200,1,0,N'',N'2026-07-30 07:14:05.039275'),
(59,N'Quần jeans Skinny Black',N'quan-jeans-skinny-black',1,520000,300,1,0,N'',N'2026-07-30 07:14:05.039275'),
(60,N'Áo thun cổ trụ Basic',N'ao-thun-co-tru-basic',3,280000,300,1,1,N'',N'2026-07-30 07:14:05.039275'),
(61,N'Mũ snapback Logo',N'mu-snapback-logo',2,220000,100,1,0,N'',N'2026-07-30 07:14:05.039275'),
(62,N'Balo Urban Mini',N'balo-urban-mini',2,450000,100,1,0,N'',N'2026-07-30 07:14:05.039275'),
(63,N'Áo sơ mi linen Relax',N'ao-so-mi-linen-relax',3,380000,200,1,1,N'',N'2026-07-30 07:14:05.039275'),
(64,N'Quần short kaki Basic',N'quan-short-kaki-basic',1,350000,300,1,0,N'',N'2026-07-30 07:14:05.039275'),
(65,N'Dây chuyền bạc Minimal',N'day-chuyen-bac-minimal',2,180000,100,1,0,N'',N'2026-07-30 07:14:05.039275'),
(66,N'Vòng tay da Bracelet',N'vong-tay-da-bracelet',2,160000,100,1,0,N'',N'2026-07-30 07:14:05.039275'),
(67,N'Áo hoodie Zip Up',N'ao-hoodie-zip-up',3,650000,200,1,1,N'',N'2026-07-30 07:14:05.039275'),
(68,N'Quần tây ống côn Slim',N'quan-tay-ong-con-slim',1,480000,300,1,0,N'',N'2026-07-30 07:14:05.039275'),
(69,N'Áo khoác dạ Cashmere',N'ao-khoac-da-cashmere',3,1200000,100,1,0,N'',N'2026-07-30 07:14:05.039275'),
(70,N'Khăn choàng cổ Len',N'khan-choang-co-len',2,320000,100,1,0,N'',N'2026-07-30 07:14:05.039275'),
(71,N'Áo polo Pique Basic',N'ao-polo-pique-basic',3,340000,300,1,0,N'',N'2026-07-30 07:14:05.039275'),
(72,N'Quần baggy Denim Light',N'quan-baggy-denim-light',1,610000,300,1,1,N'',N'2026-07-30 07:14:05.039275'),
(73,N'Túi đeo hông Waist Bag',N'tui-deo-hong-waist-bag',2,280000,100,1,0,N'',N'2026-07-30 07:14:05.039275'),
(74,N'Áo len cổ lọ Tight',N'ao-len-co-lo-tight',3,420000,200,1,0,N'',N'2026-07-30 07:14:05.039275'),
(75,N'Giày sneaker Platform',N'giay-sneaker-platform',2,950000,100,1,1,N'',N'2026-07-30 07:14:05.039275'),
(76,N'Mũ beret Pháp',N'mu-beret-phap',2,140000,100,1,0,N'',N'2026-07-30 07:14:05.039275');
GO
SET IDENTITY_INSERT [Products] OFF;
GO

-- Variants for new products
SET IDENTITY_INSERT [Variants] ON;
GO
INSERT INTO [Variants] ([id],[product_id],[color_name],[color_code],[size],[stock],[is_active]) VALUES
(273,57,N'Đen',N'#111111',N'M',50,1),
(274,57,N'Đen',N'#111111',N'L',50,1),
(275,57,N'Đen',N'#111111',N'XL',50,1),
(276,57,N'Trắng',N'#F5F5F5',N'M',50,1),
(277,57,N'Trắng',N'#F5F5F5',N'L',50,1),
(278,57,N'Trắng',N'#F5F5F5',N'XL',50,1),
(279,58,N'Đen',N'#111111',N'M',50,1),
(280,58,N'Đen',N'#111111',N'L',50,1),
(281,58,N'Đen',N'#111111',N'XL',50,1),
(282,58,N'Trắng',N'#F5F5F5',N'M',50,1),
(283,58,N'Trắng',N'#F5F5F5',N'L',50,1),
(284,58,N'Trắng',N'#F5F5F5',N'XL',50,1),
(285,59,N'Đen',N'#111111',N'M',50,1),
(286,59,N'Đen',N'#111111',N'L',50,1),
(287,59,N'Đen',N'#111111',N'XL',50,1),
(288,59,N'Trắng',N'#F5F5F5',N'M',50,1),
(289,59,N'Trắng',N'#F5F5F5',N'L',50,1),
(290,59,N'Trắng',N'#F5F5F5',N'XL',50,1),
(291,60,N'Đen',N'#111111',N'M',50,1),
(292,60,N'Đen',N'#111111',N'L',50,1),
(293,60,N'Đen',N'#111111',N'XL',50,1),
(294,60,N'Trắng',N'#F5F5F5',N'M',50,1),
(295,60,N'Trắng',N'#F5F5F5',N'L',50,1),
(296,60,N'Trắng',N'#F5F5F5',N'XL',50,1),
(297,61,N'Đen',N'#111111',N'FREE',50,1),
(298,61,N'Trắng',N'#F5F5F5',N'FREE',50,1),
(299,62,N'Đen',N'#111111',N'FREE',50,1),
(300,62,N'Trắng',N'#F5F5F5',N'FREE',50,1),
(301,63,N'Đen',N'#111111',N'M',50,1),
(302,63,N'Đen',N'#111111',N'L',50,1),
(303,63,N'Đen',N'#111111',N'XL',50,1),
(304,63,N'Trắng',N'#F5F5F5',N'M',50,1),
(305,63,N'Trắng',N'#F5F5F5',N'L',50,1),
(306,63,N'Trắng',N'#F5F5F5',N'XL',50,1),
(307,64,N'Đen',N'#111111',N'M',50,1),
(308,64,N'Đen',N'#111111',N'L',50,1),
(309,64,N'Đen',N'#111111',N'XL',50,1),
(310,64,N'Trắng',N'#F5F5F5',N'M',50,1),
(311,64,N'Trắng',N'#F5F5F5',N'L',50,1),
(312,64,N'Trắng',N'#F5F5F5',N'XL',50,1),
(313,65,N'Đen',N'#111111',N'FREE',50,1),
(314,65,N'Trắng',N'#F5F5F5',N'FREE',50,1),
(315,66,N'Đen',N'#111111',N'FREE',50,1),
(316,66,N'Trắng',N'#F5F5F5',N'FREE',50,1),
(317,67,N'Đen',N'#111111',N'M',50,1),
(318,67,N'Đen',N'#111111',N'L',50,1),
(319,67,N'Đen',N'#111111',N'XL',50,1),
(320,67,N'Trắng',N'#F5F5F5',N'M',50,1),
(321,67,N'Trắng',N'#F5F5F5',N'L',50,1),
(322,67,N'Trắng',N'#F5F5F5',N'XL',50,1),
(323,68,N'Đen',N'#111111',N'M',50,1),
(324,68,N'Đen',N'#111111',N'L',50,1),
(325,68,N'Đen',N'#111111',N'XL',50,1),
(326,68,N'Trắng',N'#F5F5F5',N'M',50,1),
(327,68,N'Trắng',N'#F5F5F5',N'L',50,1),
(328,68,N'Trắng',N'#F5F5F5',N'XL',50,1),
(329,69,N'Đen',N'#111111',N'M',50,1),
(330,69,N'Đen',N'#111111',N'L',50,1),
(331,69,N'Đen',N'#111111',N'XL',50,1),
(332,69,N'Trắng',N'#F5F5F5',N'M',50,1),
(333,69,N'Trắng',N'#F5F5F5',N'L',50,1),
(334,69,N'Trắng',N'#F5F5F5',N'XL',50,1),
(335,70,N'Đen',N'#111111',N'FREE',50,1),
(336,70,N'Trắng',N'#F5F5F5',N'FREE',50,1),
(337,71,N'Đen',N'#111111',N'M',50,1),
(338,71,N'Đen',N'#111111',N'L',50,1),
(339,71,N'Đen',N'#111111',N'XL',50,1),
(340,71,N'Trắng',N'#F5F5F5',N'M',50,1),
(341,71,N'Trắng',N'#F5F5F5',N'L',50,1),
(342,71,N'Trắng',N'#F5F5F5',N'XL',50,1),
(343,72,N'Đen',N'#111111',N'M',50,1),
(344,72,N'Đen',N'#111111',N'L',50,1),
(345,72,N'Đen',N'#111111',N'XL',50,1),
(346,72,N'Trắng',N'#F5F5F5',N'M',50,1),
(347,72,N'Trắng',N'#F5F5F5',N'L',50,1),
(348,72,N'Trắng',N'#F5F5F5',N'XL',50,1),
(349,73,N'Đen',N'#111111',N'FREE',50,1),
(350,73,N'Trắng',N'#F5F5F5',N'FREE',50,1),
(351,74,N'Đen',N'#111111',N'M',50,1),
(352,74,N'Đen',N'#111111',N'L',50,1),
(353,74,N'Đen',N'#111111',N'XL',50,1),
(354,74,N'Trắng',N'#F5F5F5',N'M',50,1),
(355,74,N'Trắng',N'#F5F5F5',N'L',50,1),
(356,74,N'Trắng',N'#F5F5F5',N'XL',50,1),
(357,75,N'Đen',N'#111111',N'FREE',50,1),
(358,75,N'Trắng',N'#F5F5F5',N'FREE',50,1),
(359,76,N'Đen',N'#111111',N'FREE',50,1),
(360,76,N'Trắng',N'#F5F5F5',N'FREE',50,1);
GO
SET IDENTITY_INSERT [Variants] OFF;
GO

-- 59 orders (total 100)
SET IDENTITY_INSERT [Orders] ON;
GO
INSERT INTO [Orders] ([id],[user_id],[customer_name],[phone],[shipping_address],[status],[total_amount],[is_paid],[payment_method],[discount_amount],[coupon],[created_at]) VALUES
(42,4,N'nguyenvanA',N'0913356886',N'760 Đường Võ Văn Tần, Quận 4, TP.HCM',N'processing',3165000,0,N'cod',0,N'',N'2026-07-13 18:17:00'),
(43,1,N'admin',N'0931429110',N'715 Đường Cách Mạng Tháng 8, Quận 6, TP.HCM',N'shipping',2385000,1,N'cod',0,N'',N'2026-07-14 17:07:00'),
(44,13,N'buithii',N'0920576383',N'566 Đường Võ Văn Tần, Quận 11, TP.HCM',N'cancelled',525000,1,N'cod',0,N'',N'2026-06-29 03:24:00'),
(45,9,N'nguyenvanE',N'0970855700',N'651 Đường Trần Hưng Đạo, Quận 3, TP.HCM',N'shipping',3120000,1,N'bank',0,N'',N'2026-07-29 17:14:00'),
(46,11,N'hoangthig',N'0917507864',N'235 Đường Lê Lợi, Quận 6, TP.HCM',N'delivered',1330000,1,N'bank',0,N'',N'2026-07-14 04:16:00'),
(47,5,N'tranthib',N'0943101783',N'763 Đường Võ Văn Tần, Quận 12, TP.HCM',N'cancelled',475000,1,N'bank',50000,N'SALE10',N'2026-07-25 05:50:00'),
(48,14,N'dangthank',N'0990048665',N'66 Đường Cách Mạng Tháng 8, Quận 7, TP.HCM',N'cancelled',3600000,1,N'bank',0,N'',N'2026-07-06 03:18:00'),
(49,14,N'dangthank',N'0931227574',N'465 Đường Lê Lợi, Quận 12, TP.HCM',N'shipping',2895000,1,N'cod',0,N'',N'2026-07-05 15:01:00'),
(50,4,N'nguyenvanA',N'0958718453',N'900 Đường Võ Văn Tần, Quận 4, TP.HCM',N'pending',3380000,0,N'cod',0,N'',N'2026-07-29 06:45:00'),
(51,10,N'phamthif',N'0963551839',N'688 Đường Trần Hưng Đạo, Quận 8, TP.HCM',N'cancelled',735000,1,N'cod',0,N'',N'2026-06-29 00:04:00'),
(52,2,N'codexstaff',N'0940728046',N'70 Đường Lê Lợi, Quận 6, TP.HCM',N'pending',1700000,0,N'bank',100000,N'WELCOME',N'2026-06-30 15:51:00'),
(53,14,N'dangthank',N'0935556386',N'97 Đường Hai Bà Trưng, Quận 11, TP.HCM',N'delivered',3025000,1,N'bank',50000,N'GIAM50K',N'2026-07-13 04:27:00'),
(54,6,N'lethic',N'0947385696',N'474 Đường Nguyễn Huệ, Quận 2, TP.HCM',N'delivered',270000,1,N'cod',0,N'',N'2026-07-11 15:30:00'),
(55,7,N'phamvand',N'0963826716',N'925 Đường Lê Lợi, Quận 3, TP.HCM',N'delivered',3200000,1,N'cod',50000,N'GIAM50K',N'2026-07-03 06:03:00'),
(56,18,N'vuongo',N'0918181586',N'766 Đường Trần Hưng Đạo, Quận 1, TP.HCM',N'pending',1845000,1,N'cod',0,N'',N'2026-06-19 21:55:00'),
(57,8,N'hoangthie',N'0964193837',N'123 Đường Nguyễn Huệ, Quận 10, TP.HCM',N'cancelled',3545000,0,N'cod',50000,N'GIAM50K',N'2026-07-26 09:29:00'),
(58,11,N'hoangthig',N'0919736572',N'10 Đường Phạm Ngũ Lão, Quận 10, TP.HCM',N'cancelled',1590000,0,N'cod',0,N'',N'2026-07-30 09:39:00'),
(59,17,N'tranvann',N'0911049999',N'684 Đường Võ Văn Tần, Quận 11, TP.HCM',N'pending',680000,0,N'bank',0,N'',N'2026-07-03 19:13:00'),
(60,11,N'hoangthig',N'0937326368',N'704 Đường Võ Văn Tần, Quận 9, TP.HCM',N'delivered',320000,1,N'bank',0,N'',N'2026-06-15 10:49:00'),
(61,5,N'tranthib',N'0995511909',N'269 Đường Lý Thường Kiệt, Quận 12, TP.HCM',N'delivered',900000,1,N'bank',0,N'',N'2026-06-17 11:37:00'),
(62,18,N'vuongo',N'0929876811',N'441 Đường Lý Thường Kiệt, Quận 1, TP.HCM',N'shipping',2340000,1,N'bank',0,N'',N'2026-06-24 07:55:00'),
(63,6,N'lethic',N'0933763566',N'903 Đường Cách Mạng Tháng 8, Quận 1, TP.HCM',N'processing',2060000,1,N'bank',0,N'',N'2026-07-04 07:14:00'),
(64,1,N'admin',N'0998588154',N'198 Đường Cách Mạng Tháng 8, Quận 6, TP.HCM',N'shipping',1905000,1,N'cod',0,N'FREESHIP',N'2026-07-22 08:02:00'),
(65,4,N'nguyenvanA',N'0990070438',N'445 Đường Trần Hưng Đạo, Quận 12, TP.HCM',N'shipping',4260000,1,N'bank',0,N'',N'2026-06-19 21:58:00'),
(66,11,N'hoangthig',N'0993638503',N'322 Đường Hai Bà Trưng, Quận 12, TP.HCM',N'shipping',1690000,1,N'bank',50000,N'GIAM50K',N'2026-07-28 23:57:00'),
(67,6,N'lethic',N'0992613013',N'583 Đường Võ Văn Tần, Quận 7, TP.HCM',N'cancelled',1945000,0,N'bank',0,N'FREESHIP',N'2026-07-13 21:13:00'),
(68,17,N'tranvann',N'0973509974',N'813 Đường Lý Thường Kiệt, Quận 11, TP.HCM',N'pending',710000,1,N'bank',0,N'',N'2026-06-30 15:39:00'),
(69,3,N'readmestaff',N'0971124923',N'425 Đường Nguyễn Huệ, Quận 12, TP.HCM',N'delivered',435000,1,N'bank',50000,N'GIAM50K',N'2026-07-29 16:29:00'),
(70,2,N'codexstaff',N'0984813739',N'256 Đường Hai Bà Trưng, Quận 8, TP.HCM',N'processing',3620000,1,N'bank',100000,N'WELCOME',N'2026-06-30 08:28:00'),
(71,3,N'readmestaff',N'0948349783',N'241 Đường Võ Văn Tần, Quận 6, TP.HCM',N'shipping',1725000,1,N'cod',0,N'',N'2026-07-11 13:21:00'),
(72,18,N'vuongo',N'0972535301',N'426 Đường Lê Lợi, Quận 4, TP.HCM',N'delivered',6260000,1,N'bank',0,N'',N'2026-06-29 08:27:00'),
(73,16,N'lyvanm',N'0913895645',N'399 Đường Trần Hưng Đạo, Quận 11, TP.HCM',N'delivered',2440000,1,N'cod',100000,N'WELCOME',N'2026-07-26 13:08:00'),
(74,15,N'ngothil',N'0934391257',N'52 Đường Võ Văn Tần, Quận 7, TP.HCM',N'shipping',1865000,1,N'cod',100000,N'WELCOME',N'2026-07-19 01:22:00'),
(75,8,N'hoangthie',N'0997260863',N'71 Đường Lê Lợi, Quận 1, TP.HCM',N'processing',1035000,0,N'cod',0,N'',N'2026-07-29 08:49:00'),
(76,12,N'dothih',N'0932520277',N'621 Đường Hai Bà Trưng, Quận 3, TP.HCM',N'shipping',1520000,1,N'cod',0,N'',N'2026-07-29 09:54:00'),
(77,4,N'nguyenvanA',N'0985958181',N'802 Đường Lê Lợi, Quận 6, TP.HCM',N'cancelled',1380000,1,N'bank',0,N'',N'2026-07-12 05:46:00'),
(78,17,N'tranvann',N'0997302916',N'277 Đường Phạm Ngũ Lão, Quận 8, TP.HCM',N'delivered',1975000,1,N'bank',50000,N'SALE10',N'2026-07-24 21:24:00'),
(79,11,N'hoangthig',N'0913852048',N'507 Đường Trần Hưng Đạo, Quận 3, TP.HCM',N'delivered',2490000,1,N'cod',50000,N'SALE10',N'2026-06-30 23:26:00'),
(80,16,N'lyvanm',N'0984514489',N'777 Đường Nguyễn Huệ, Quận 12, TP.HCM',N'delivered',229500,1,N'bank',40500,N'WELCOME',N'2026-07-10 22:15:00'),
(81,10,N'phamthif',N'0999115205',N'596 Đường Trần Hưng Đạo, Quận 8, TP.HCM',N'cancelled',2070000,1,N'bank',50000,N'SALE10',N'2026-07-19 22:11:00'),
(82,7,N'phamvand',N'0939042654',N'757 Đường Phạm Ngũ Lão, Quận 5, TP.HCM',N'cancelled',4605000,1,N'cod',0,N'',N'2026-06-17 01:35:00'),
(83,10,N'phamthif',N'0926948946',N'654 Đường Phạm Ngũ Lão, Quận 2, TP.HCM',N'pending',1795000,1,N'bank',100000,N'WELCOME',N'2026-06-24 18:19:00'),
(84,3,N'readmestaff',N'0943311626',N'122 Đường Cách Mạng Tháng 8, Quận 10, TP.HCM',N'cancelled',4650000,0,N'bank',100000,N'WELCOME',N'2026-06-20 05:15:00'),
(85,6,N'lethic',N'0984087145',N'77 Đường Lý Thường Kiệt, Quận 1, TP.HCM',N'delivered',2920000,1,N'bank',100000,N'WELCOME',N'2026-07-25 18:42:00'),
(86,7,N'phamvand',N'0967061186',N'118 Đường Nguyễn Huệ, Quận 11, TP.HCM',N'processing',1935000,1,N'cod',0,N'',N'2026-07-21 09:28:00'),
(87,4,N'nguyenvanA',N'0972907576',N'706 Đường Võ Văn Tần, Quận 12, TP.HCM',N'delivered',2480000,1,N'bank',100000,N'WELCOME',N'2026-07-28 08:36:00'),
(88,2,N'codexstaff',N'0933513701',N'482 Đường Phạm Ngũ Lão, Quận 5, TP.HCM',N'processing',2775000,1,N'bank',0,N'',N'2026-07-10 17:02:00'),
(89,15,N'ngothil',N'0921819185',N'323 Đường Võ Văn Tần, Quận 6, TP.HCM',N'pending',3155000,1,N'cod',100000,N'WELCOME',N'2026-07-03 14:56:00'),
(90,16,N'lyvanm',N'0926297533',N'30 Đường Nguyễn Huệ, Quận 12, TP.HCM',N'processing',1030000,1,N'cod',50000,N'GIAM50K',N'2026-06-22 20:53:00'),
(91,5,N'tranthib',N'0976890827',N'956 Đường Võ Văn Tần, Quận 9, TP.HCM',N'shipping',2580000,1,N'bank',100000,N'WELCOME',N'2026-07-17 08:52:00'),
(92,1,N'admin',N'0947962005',N'744 Đường Võ Văn Tần, Quận 10, TP.HCM',N'cancelled',4515000,1,N'cod',100000,N'WELCOME',N'2026-06-29 13:02:00'),
(93,11,N'hoangthig',N'0973481797',N'723 Đường Cách Mạng Tháng 8, Quận 7, TP.HCM',N'processing',1230000,1,N'cod',0,N'',N'2026-06-24 02:30:00'),
(94,9,N'nguyenvanE',N'0955440919',N'639 Đường Cách Mạng Tháng 8, Quận 11, TP.HCM',N'pending',3895000,1,N'bank',50000,N'SALE10',N'2026-07-25 22:55:00'),
(95,4,N'nguyenvanA',N'0969549527',N'171 Đường Võ Văn Tần, Quận 1, TP.HCM',N'pending',1695000,1,N'cod',0,N'FREESHIP',N'2026-06-26 02:39:00'),
(96,13,N'buithii',N'0993176117',N'700 Đường Nguyễn Huệ, Quận 8, TP.HCM',N'cancelled',2160000,0,N'cod',100000,N'WELCOME',N'2026-07-13 11:37:00'),
(97,10,N'phamthif',N'0995756900',N'986 Đường Cách Mạng Tháng 8, Quận 12, TP.HCM',N'shipping',1925000,1,N'bank',0,N'FREESHIP',N'2026-07-07 18:18:00'),
(98,10,N'phamthif',N'0912944682',N'850 Đường Cách Mạng Tháng 8, Quận 5, TP.HCM',N'pending',2565000,0,N'bank',0,N'FREESHIP',N'2026-07-28 23:49:00'),
(99,5,N'tranthib',N'0994322033',N'100 Đường Lê Lợi, Quận 5, TP.HCM',N'delivered',825000,1,N'cod',50000,N'SALE10',N'2026-06-23 17:56:00'),
(100,12,N'dothih',N'0981249799',N'514 Đường Võ Văn Tần, Quận 3, TP.HCM',N'shipping',1480000,1,N'bank',0,N'FREESHIP',N'2026-06-20 12:00:00');
GO
SET IDENTITY_INSERT [Orders] OFF;
GO

-- Order items for new orders
SET IDENTITY_INSERT [OrderItems] ON;
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(65,42,5,21,N'Đen',N'M',1,620000),
(66,42,28,100,N'Đen',N'L',3,555000),
(67,42,4,19,N'Trắng',N'L',1,560000),
(68,42,70,336,N'Trắng',N'FREE',1,320000),
(69,43,14,47,N'Đen',N'FREE',2,240000),
(70,43,13,46,N'Trắng',N'FREE',2,255000),
(71,43,34,135,N'Đen',N'M',3,465000),
(72,44,30,113,N'Đen',N'XL',1,525000),
(73,45,10,39,N'Đen',N'FREE',3,300000),
(74,45,32,124,N'Đen',N'L',2,495000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(75,45,49,227,N'Đen',N'XL',3,410000),
(76,46,73,350,N'Trắng',N'FREE',1,280000),
(77,46,64,310,N'Trắng',N'M',3,350000),
(78,47,18,56,N'Trắng',N'FREE',1,180000),
(79,47,7,33,N'Đen',N'FREE',1,345000),
(80,48,69,331,N'Đen',N'XL',3,1200000),
(81,49,65,313,N'Đen',N'FREE',1,180000),
(82,49,48,220,N'Đen',N'L',3,425000),
(83,49,68,323,N'Đen',N'M',3,480000),
(84,50,9,37,N'Đen',N'FREE',1,315000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(85,50,61,297,N'Đen',N'FREE',2,220000),
(86,50,68,327,N'Trắng',N'L',2,480000),
(87,50,28,103,N'Trắng',N'L',3,555000),
(88,51,9,38,N'Trắng',N'FREE',1,315000),
(89,51,76,359,N'Đen',N'FREE',3,140000),
(90,52,70,335,N'Đen',N'FREE',3,320000),
(91,52,74,355,N'Trắng',N'L',2,420000),
(92,53,60,296,N'Trắng',N'XL',1,280000),
(93,53,13,45,N'Đen',N'FREE',2,255000),
(94,53,44,195,N'Đen',N'M',1,485000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(95,53,25,82,N'Đen',N'L',3,600000),
(96,54,12,43,N'Đen',N'FREE',1,270000),
(97,55,59,287,N'Đen',N'XL',2,520000),
(98,55,72,348,N'Trắng',N'XL',3,610000),
(99,55,63,302,N'Đen',N'L',1,380000),
(100,56,24,75,N'Đen',N'M',3,615000),
(101,57,34,136,N'Đen',N'L',3,465000),
(102,57,41,178,N'Đen',N'L',2,530000),
(103,57,51,238,N'Đen',N'L',3,380000),
(104,58,17,54,N'Trắng',N'FREE',1,195000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(105,58,32,125,N'Đen',N'XL',2,495000),
(106,58,21,62,N'Trắng',N'FREE',3,135000),
(107,59,71,338,N'Đen',N'L',2,340000),
(108,60,55,263,N'Đen',N'XL',1,320000),
(109,61,10,39,N'Đen',N'FREE',3,300000),
(110,62,27,98,N'Trắng',N'XL',1,570000),
(111,62,14,48,N'Trắng',N'FREE',3,240000),
(112,62,53,253,N'Trắng',N'L',3,350000),
(113,63,21,61,N'Đen',N'FREE',2,135000),
(114,63,5,24,N'Trắng',N'M',1,620000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(115,63,26,90,N'Trắng',N'M',2,585000),
(116,64,66,316,N'Trắng',N'FREE',3,160000),
(117,64,69,331,N'Đen',N'XL',1,1200000),
(118,64,15,50,N'Trắng',N'FREE',1,225000),
(119,65,74,352,N'Đen',N'L',2,420000),
(120,65,6,32,N'Trắng',N'XL',2,390000),
(121,65,1,5,N'Trắng',N'L',3,490000),
(122,65,26,89,N'Đen',N'XL',2,585000),
(123,66,52,248,N'Trắng',N'XL',2,365000),
(124,66,71,338,N'Đen',N'L',1,340000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(125,66,54,260,N'Trắng',N'XL',2,335000),
(126,67,56,271,N'Trắng',N'L',3,305000),
(127,67,42,186,N'Trắng',N'M',2,515000),
(128,68,40,172,N'Đen',N'L',1,545000),
(129,68,19,57,N'Đen',N'FREE',1,165000),
(130,69,19,57,N'Đen',N'FREE',1,165000),
(131,69,55,262,N'Đen',N'L',1,320000),
(132,70,71,340,N'Trắng',N'M',1,340000),
(133,70,61,298,N'Trắng',N'FREE',2,220000),
(134,70,32,128,N'Trắng',N'XL',2,495000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(135,70,67,320,N'Trắng',N'M',3,650000),
(136,71,30,114,N'Trắng',N'M',3,525000),
(137,71,20,59,N'Đen',N'FREE',1,150000),
(138,72,62,299,N'Đen',N'FREE',2,450000),
(139,72,39,168,N'Trắng',N'M',2,560000),
(140,72,69,334,N'Trắng',N'XL',3,1200000),
(141,72,70,335,N'Đen',N'FREE',2,320000),
(142,73,69,329,N'Đen',N'M',2,1200000),
(143,73,76,359,N'Đen',N'FREE',1,140000),
(144,74,44,198,N'Trắng',N'M',2,485000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(145,74,54,257,N'Đen',N'XL',1,335000),
(146,74,61,297,N'Đen',N'FREE',3,220000),
(147,75,17,54,N'Trắng',N'FREE',3,195000),
(148,75,15,49,N'Đen',N'FREE',2,225000),
(149,76,74,356,N'Trắng',N'XL',2,420000),
(150,76,51,242,N'Trắng',N'XL',1,380000),
(151,76,10,39,N'Đen',N'FREE',1,300000),
(152,77,2,8,N'Trắng',N'FREE',2,190000),
(153,77,14,48,N'Trắng',N'FREE',2,240000),
(154,77,59,290,N'Trắng',N'XL',1,520000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(155,78,12,44,N'Trắng',N'FREE',2,270000),
(156,78,32,126,N'Trắng',N'M',3,495000),
(157,79,44,197,N'Đen',N'XL',3,485000),
(158,79,36,151,N'Trắng',N'L',1,435000),
(159,79,67,318,N'Đen',N'L',1,650000),
(160,80,12,44,N'Trắng',N'FREE',1,270000),
(161,81,59,287,N'Đen',N'XL',2,520000),
(162,81,33,130,N'Đen',N'L',1,480000),
(163,81,25,83,N'Đen',N'XL',1,600000),
(164,82,30,113,N'Đen',N'XL',1,525000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(165,82,39,165,N'Đen',N'M',3,560000),
(166,82,69,330,N'Đen',N'L',2,1200000),
(167,83,44,196,N'Đen',N'L',1,485000),
(168,83,33,132,N'Trắng',N'M',1,480000),
(169,83,9,38,N'Trắng',N'FREE',2,315000),
(170,83,10,39,N'Đen',N'FREE',1,300000),
(171,84,39,169,N'Trắng',N'L',2,560000),
(172,84,40,175,N'Trắng',N'L',3,545000),
(173,84,8,35,N'Đen',N'FREE',1,330000),
(174,84,28,101,N'Đen',N'XL',3,555000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(175,85,5,22,N'Đen',N'L',2,620000),
(176,85,37,158,N'Trắng',N'XL',2,590000),
(177,85,10,39,N'Đen',N'FREE',2,300000),
(178,86,22,65,N'Đen',N'XL',3,645000),
(179,87,11,41,N'Đen',N'FREE',2,285000),
(180,87,42,187,N'Trắng',N'L',2,515000),
(181,87,4,15,N'Đen',N'M',1,560000),
(182,87,74,355,N'Trắng',N'L',1,420000),
(183,88,45,204,N'Trắng',N'M',2,470000),
(184,88,42,188,N'Trắng',N'XL',1,515000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(185,88,21,62,N'Trắng',N'FREE',2,135000),
(186,88,64,309,N'Đen',N'XL',3,350000),
(187,89,7,33,N'Đen',N'FREE',3,345000),
(188,89,47,217,N'Trắng',N'L',2,440000),
(189,89,57,273,N'Đen',N'M',1,890000),
(190,89,35,145,N'Trắng',N'L',1,450000),
(191,90,29,105,N'Đen',N'M',2,540000),
(192,91,32,126,N'Trắng',N'M',3,495000),
(193,91,19,58,N'Trắng',N'FREE',1,165000),
(194,91,66,315,N'Đen',N'FREE',1,160000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(195,91,36,150,N'Trắng',N'M',2,435000),
(196,92,45,203,N'Đen',N'XL',3,470000),
(197,92,70,336,N'Trắng',N'FREE',2,320000),
(198,92,42,184,N'Đen',N'L',3,515000),
(199,92,31,121,N'Trắng',N'L',2,510000),
(200,93,13,46,N'Trắng',N'FREE',1,255000),
(201,93,68,326,N'Trắng',N'M',1,480000),
(202,93,19,58,N'Trắng',N'FREE',3,165000),
(203,94,70,335,N'Đen',N'FREE',3,320000),
(204,94,9,37,N'Đen',N'FREE',3,315000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(205,94,37,154,N'Đen',N'L',3,590000),
(206,94,12,44,N'Trắng',N'FREE',1,270000),
(207,95,48,222,N'Trắng',N'M',1,425000),
(208,95,32,127,N'Trắng',N'L',2,495000),
(209,95,73,349,N'Đen',N'FREE',1,280000),
(210,96,59,287,N'Đen',N'XL',3,520000),
(211,96,2,8,N'Trắng',N'FREE',2,190000),
(212,96,70,335,N'Đen',N'FREE',1,320000),
(213,97,50,234,N'Trắng',N'M',1,395000),
(214,97,31,120,N'Trắng',N'M',3,510000);
GO
INSERT INTO [OrderItems] ([id],[order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES
(215,98,46,208,N'Đen',N'L',3,455000),
(216,98,25,85,N'Trắng',N'L',2,600000),
(217,99,12,44,N'Trắng',N'FREE',2,270000),
(218,99,54,256,N'Đen',N'L',1,335000),
(219,100,15,50,N'Trắng',N'FREE',1,225000),
(220,100,19,57,N'Đen',N'FREE',3,165000),
(221,100,51,241,N'Trắng',N'L',2,380000);
GO
SET IDENTITY_INSERT [OrderItems] OFF;
GO

-- Wishlist items for new users
SET IDENTITY_INSERT [Wishlist] ON;
GO
INSERT INTO [Wishlist] ([id],[user_id],[product_id],[created]) VALUES
(19,9,69,N'2026-07-08 00:00:00'),
(20,9,16,N'2026-07-28 00:00:00'),
(21,9,59,N'2026-07-28 00:00:00'),
(22,10,75,N'2026-06-21 00:00:00'),
(23,10,49,N'2026-07-28 00:00:00'),
(24,10,48,N'2026-06-29 00:00:00'),
(25,11,4,N'2026-07-26 00:00:00'),
(26,11,72,N'2026-06-19 00:00:00'),
(27,11,42,N'2026-07-25 00:00:00'),
(28,11,29,N'2026-07-14 00:00:00'),
(29,12,53,N'2026-06-17 00:00:00'),
(30,12,15,N'2026-06-17 00:00:00'),
(31,12,18,N'2026-07-04 00:00:00'),
(32,13,15,N'2026-06-23 00:00:00'),
(33,13,13,N'2026-07-09 00:00:00'),
(34,13,31,N'2026-07-14 00:00:00'),
(35,13,69,N'2026-07-08 00:00:00'),
(36,14,76,N'2026-07-16 00:00:00'),
(37,14,20,N'2026-07-24 00:00:00'),
(38,14,54,N'2026-07-11 00:00:00'),
(39,14,13,N'2026-07-02 00:00:00'),
(40,15,48,N'2026-06-28 00:00:00'),
(41,16,57,N'2026-07-28 00:00:00'),
(42,16,31,N'2026-07-08 00:00:00'),
(43,16,47,N'2026-07-19 00:00:00'),
(44,16,13,N'2026-07-26 00:00:00'),
(45,17,8,N'2026-06-27 00:00:00'),
(46,17,51,N'2026-06-22 00:00:00'),
(47,17,36,N'2026-07-14 00:00:00'),
(48,18,28,N'2026-07-26 00:00:00');
GO
SET IDENTITY_INSERT [Wishlist] OFF;
GO

-- Activities
SET IDENTITY_INSERT [Activities] ON;
GO
INSERT INTO [Activities] ([id],[user_id],[event],[path],[created_at]) VALUES
(52,1,N'checkout',N'/products/',N'2026-06-18 00:00:00'),
(53,1,N'cart_add',N'/',N'2026-06-23 00:00:00'),
(54,2,N'cart_add',N'/products/',N'2026-07-22 00:00:00'),
(55,2,N'cart_add',N'/orders/',N'2026-07-06 00:00:00'),
(56,2,N'checkout',N'/products/',N'2026-06-15 00:00:00'),
(57,3,N'checkout',N'/products/',N'2026-07-19 00:00:00'),
(58,3,N'page_view',N'/products/',N'2026-06-22 00:00:00'),
(59,3,N'checkout',N'/products/',N'2026-06-15 00:00:00'),
(60,4,N'cart_add',N'/cart/',N'2026-06-16 00:00:00'),
(61,4,N'cart_add',N'/checkout/',N'2026-06-18 00:00:00');
GO
INSERT INTO [Activities] ([id],[user_id],[event],[path],[created_at]) VALUES
(62,4,N'page_view',N'/',N'2026-07-18 00:00:00'),
(63,4,N'action',N'/cart/',N'2026-07-15 00:00:00'),
(64,5,N'cart_add',N'/orders/',N'2026-07-13 00:00:00'),
(65,5,N'checkout',N'/checkout/',N'2026-06-17 00:00:00'),
(66,6,N'action',N'/checkout/',N'2026-06-18 00:00:00'),
(67,6,N'page_view',N'/checkout/',N'2026-07-12 00:00:00'),
(68,7,N'page_view',N'/cart/',N'2026-06-19 00:00:00'),
(69,7,N'cart_add',N'/',N'2026-07-23 00:00:00'),
(70,7,N'checkout',N'/orders/',N'2026-06-23 00:00:00'),
(71,7,N'checkout',N'/checkout/',N'2026-07-25 00:00:00');
GO
INSERT INTO [Activities] ([id],[user_id],[event],[path],[created_at]) VALUES
(72,7,N'checkout',N'/checkout/',N'2026-07-23 00:00:00'),
(73,8,N'page_view',N'/orders/',N'2026-06-21 00:00:00'),
(74,8,N'action',N'/checkout/',N'2026-06-28 00:00:00'),
(75,8,N'action',N'/cart/',N'2026-06-29 00:00:00'),
(76,8,N'action',N'/checkout/',N'2026-07-14 00:00:00'),
(77,8,N'checkout',N'/checkout/',N'2026-06-21 00:00:00'),
(78,9,N'checkout',N'/cart/',N'2026-07-27 00:00:00'),
(79,9,N'action',N'/',N'2026-06-24 00:00:00'),
(80,9,N'page_view',N'/',N'2026-06-20 00:00:00'),
(81,9,N'page_view',N'/cart/',N'2026-07-12 00:00:00');
GO
INSERT INTO [Activities] ([id],[user_id],[event],[path],[created_at]) VALUES
(82,10,N'page_view',N'/orders/',N'2026-07-20 00:00:00'),
(83,10,N'checkout',N'/',N'2026-07-20 00:00:00'),
(84,10,N'checkout',N'/checkout/',N'2026-07-11 00:00:00'),
(85,11,N'checkout',N'/cart/',N'2026-07-03 00:00:00'),
(86,11,N'cart_add',N'/products/',N'2026-06-21 00:00:00'),
(87,12,N'page_view',N'/cart/',N'2026-06-29 00:00:00'),
(88,12,N'checkout',N'/',N'2026-07-20 00:00:00'),
(89,12,N'cart_add',N'/checkout/',N'2026-07-02 00:00:00'),
(90,12,N'page_view',N'/orders/',N'2026-07-20 00:00:00'),
(91,12,N'checkout',N'/',N'2026-07-27 00:00:00');
GO
INSERT INTO [Activities] ([id],[user_id],[event],[path],[created_at]) VALUES
(92,13,N'checkout',N'/cart/',N'2026-07-02 00:00:00'),
(93,13,N'page_view',N'/products/',N'2026-07-07 00:00:00'),
(94,13,N'action',N'/',N'2026-06-24 00:00:00'),
(95,14,N'page_view',N'/',N'2026-07-25 00:00:00'),
(96,14,N'cart_add',N'/checkout/',N'2026-07-18 00:00:00'),
(97,14,N'action',N'/cart/',N'2026-07-11 00:00:00'),
(98,15,N'checkout',N'/cart/',N'2026-07-08 00:00:00'),
(99,15,N'page_view',N'/',N'2026-07-21 00:00:00'),
(100,15,N'cart_add',N'/orders/',N'2026-06-24 00:00:00'),
(101,16,N'page_view',N'/cart/',N'2026-07-28 00:00:00');
GO
INSERT INTO [Activities] ([id],[user_id],[event],[path],[created_at]) VALUES
(102,16,N'action',N'/checkout/',N'2026-07-13 00:00:00'),
(103,17,N'checkout',N'/products/',N'2026-07-11 00:00:00'),
(104,17,N'page_view',N'/cart/',N'2026-07-17 00:00:00'),
(105,17,N'page_view',N'/cart/',N'2026-07-12 00:00:00'),
(106,17,N'action',N'/orders/',N'2026-07-28 00:00:00'),
(107,17,N'checkout',N'/',N'2026-07-27 00:00:00'),
(108,18,N'page_view',N'/',N'2026-07-10 00:00:00'),
(109,18,N'checkout',N'/products/',N'2026-06-28 00:00:00'),
(110,18,N'checkout',N'/cart/',N'2026-06-23 00:00:00');
GO
SET IDENTITY_INSERT [Activities] OFF;
GO
