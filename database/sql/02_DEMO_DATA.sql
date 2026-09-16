-- ============================================================
-- HUUGIAU Fashion - DEMO DATA
-- Must be run after 01_CREATE_TABLES.sql in SQL Server.
-- Seeds the legacy schema used by import_legacy.
-- DEMO ONLY: this inserts sample users, orders, reviews and addresses; never run on production.
-- ============================================================
SET NOCOUNT ON;
USE [HUUGIAU_Fashion];

INSERT INTO [Users] ([username], [email], [password], [role], [is_active], [date_joined], [phone]) VALUES
 (N'admin', N'admin@example.com', N'pbkdf2_sha256$1200000$JNTOX81AkUEuRlFmJC7tyl$7LJe81bmTZ9BTA1WK592OWWN97YZ1QbaKLtKAY1XG64=', 0, 1, DATEADD(day,-365,GETDATE()), N'0900000001'),
 (N'staff1', N'staff1@example.com', N'pbkdf2_sha256$1200000$gGeaTKPPhLCOt4dtI0xort$o+3nLZynWZ1ICm1uVVCQ2pI+jHc85QRb0D7z+kJZcII=', 1, 1, DATEADD(day,-300,GETDATE()), N'0900000002'),
 (N'staff2', N'staff2@example.com', N'pbkdf2_sha256$1200000$gGeaTKPPhLCOt4dtI0xort$o+3nLZynWZ1ICm1uVVCQ2pI+jHc85QRb0D7z+kJZcII=', 1, 1, DATEADD(day,-280,GETDATE()), N'0900000003'),
 (N'staff3', N'staff3@example.com', N'pbkdf2_sha256$1200000$gGeaTKPPhLCOt4dtI0xort$o+3nLZynWZ1ICm1uVVCQ2pI+jHc85QRb0D7z+kJZcII=', 1, 1, DATEADD(day,-260,GETDATE()), N'0900000004');
DECLARE @i INT = 1;
WHILE @i <= 15 BEGIN
    INSERT INTO [Users] ([username], [email], [password], [role], [is_active], [date_joined], [phone])
    VALUES (CONCAT(N'user',RIGHT(CONCAT(N'0',@i),2)), CONCAT(N'user',RIGHT(CONCAT(N'0',@i),2),N'@example.com'), N'pbkdf2_sha256$1200000$uTDqiEq47w8ngceQ2jHDJc$sxP9SgtOsnNh5OyEuBPdKHmNNQSREDAxqUfxu1GsbTU=', 2, 1, DATEADD(day,-@i*10,GETDATE()), CONCAT(N'09',RIGHT(CONCAT(N'0000000',@i),8)));
    SET @i += 1;
END;

INSERT INTO [Categories] ([name], [slug]) VALUES
 (N'Áo',N'ao'),(N'Quần',N'quan'),(N'Phụ Kiện',N'phu-kien');

-- Đồng bộ 76 sản phẩm với database/seed/products_to_sync.json.
DECLARE @product_seed TABLE (
    [id] INT, [name] NVARCHAR(200), [slug] NVARCHAR(200),
    [category_id] INT, [price] INT, [featured] BIT
);
INSERT INTO @product_seed VALUES
(1,N'Áo thun Oversize Core Logo',N'ao-thun-oversize-core-logo',1,305000,0),
(2,N'Áo thun Boxy Signature',N'ao-thun-boxy-signature',1,320000,0),
(3,N'Áo thun Faded Wash',N'ao-thun-faded-wash',1,335000,0),
(4,N'Áo polo Dệt Urban',N'ao-polo-knit-urban',1,350000,1),
(5,N'Áo hoodie khóa kéo Raw Edge',N'ao-hoodie-zip-raw-edge',1,365000,0),
(6,N'Áo hoodie Boxy Blackout',N'ao-hoodie-boxy-blackout',1,380000,0),
(7,N'Áo sweatshirt Varsity',N'ao-sweatshirt-varsity',1,395000,1),
(8,N'Áo sơ mi Flannel Street Check',N'ao-so-mi-flannel-street-check',1,410000,0),
(9,N'Áo khoác gió Wind Layer',N'ao-khoac-gio-wind-layer',1,425000,1),
(10,N'Áo khoác bomber Mono',N'ao-khoac-bomber-mono',1,440000,0),
(11,N'Áo jersey Sport Line',N'ao-jersey-sportline',1,455000,0),
(12,N'Áo tank top Base Layer',N'ao-tanktop-base-layer',1,470000,0),
(13,N'Áo thun cổ cao Mock Neck',N'ao-thun-co-cao-mock-neck',1,485000,0),
(14,N'Áo cardigan Knit Loose',N'ao-cardigan-knit-loose',1,500000,0),
(15,N'Áo khoác denim Blue Stone',N'ao-denim-jacket-blue-stone',1,515000,0),
(16,N'Áo khoác coach Track Unit',N'ao-coach-jacket-track-unit',1,530000,0),
(17,N'Áo thun Graphic No.01',N'ao-thun-graphic-no01',1,545000,1),
(18,N'Áo thun Graphic No.02',N'ao-thun-graphic-no02',1,560000,0),
(19,N'Áo hoodie Washed Ink',N'ao-hoodie-washed-ink',1,575000,0),
(20,N'Áo sơ mi Cuban Camp',N'ao-so-mi-cuban-camp',1,590000,0),
(21,N'Quần cargo Multi Pocket',N'quan-cargo-multi-pocket',2,435000,0),
(22,N'Quần jogger Tech Cuff',N'quan-jogger-cuff-tech',2,450000,0),
(23,N'Quần jeans Straight 90s',N'quan-jeans-straight-90s',2,465000,1),
(24,N'Quần jeans Baggy Fade',N'quan-jeans-baggy-fade',2,480000,0),
(25,N'Quần short Utility',N'quan-short-utility',2,495000,0),
(26,N'Quần short nỉ Basic',N'quan-short-sweat-basic',2,510000,1),
(27,N'Quần tây Relax Fit',N'quan-tay-relax-fit',2,525000,0),
(28,N'Quần dù Parachute',N'quan-du-parachute',2,540000,0),
(29,N'Quần track pants Side Line',N'quan-track-pant-side-line',2,555000,0),
(30,N'Quần nỉ Daily',N'quan-ni-daily',2,570000,1),
(31,N'Quần cargo Ripstop',N'quan-cargo-ripstop',2,585000,0),
(32,N'Quần denim Raw Hem',N'quan-denim-raw-hem',2,600000,0),
(33,N'Quần short denim Washed',N'quan-shorts-denim-washed',2,615000,0),
(34,N'Quần chino Loose Fit',N'quan-chinos-loose',2,630000,0),
(35,N'Quần ống rộng Pleated',N'quan-ong-rong-pleated',2,645000,0),
(36,N'Nón lưỡi trai Basic',N'non-luoi-trai-swe',3,135000,0),
(37,N'Mũ len Beanie Ribbed',N'beanie-ribbed',3,150000,0),
(38,N'Túi đeo chéo Mini Pack',N'tui-deo-cheo-mini-pack',3,165000,0),
(39,N'Túi tote Canvas Heavy',N'tui-tote-canvas-heavy',3,180000,0),
(40,N'Vớ cổ cao Logo',N'vo-co-cao-logo',3,195000,0),
(41,N'Thắt lưng Webbing',N'that-lung-webbing',3,210000,0),
(42,N'Ví mini Reflect',N'vi-mini-reflect',3,225000,1),
(43,N'Khăn bandana Mono',N'khan-bandana-mono',3,240000,0),
(44,N'Móc khóa Carabiner',N'moc-khoa-carabiner',3,255000,1),
(45,N'Mũ bucket Nylon',N'mu-bucket-nylon',3,270000,0),
(46,N'Bình nước thép 500ml',N'binh-nuoc-steel-500ml',3,285000,0),
(47,N'Dây đeo điện thoại',N'day-deo-dien-thoai',3,300000,1),
(48,N'Kính mát gọng vuông',N'kinh-mat-frame-vuong',3,315000,0),
(49,N'Găng tay ngón cụt',N'gang-tay-ngon-cut',3,330000,0),
(50,N'Khẩu trang 3 lớp',N'khau-trang-3-lop-swe',3,345000,1),
(51,N'Áo thun Oversize Core Black',N'ao-thun-oversize-core-black',1,390000,0),
(52,N'Áo hoodie Boxy Ash',N'hoodie-boxy-ash',1,620000,0),
(53,N'Quần cargo Street Fit',N'cargo-pants-street-fit',2,560000,0),
(54,N'Quần jeans Baggy Fade Blue',N'jeans-baggy-fade-blue',2,590000,1),
(55,N'Mũ lưỡi trai Logo Minimal',N'cap-logo-minimal',3,190000,0),
(56,N'Quần jogger Tech Cuff',N'jogger-cuff-tech',2,490000,0),
(57,N'Áo khoác lông vũ Puffer',N'ao-khoac-long-vu-puffer',1,890000,1),
(58,N'Áo blazer Oversize',N'ao-blazer-oversize',1,750000,0),
(59,N'Quần jeans Skinny Black',N'quan-jeans-skinny-black',2,520000,0),
(60,N'Áo thun cổ trụ Basic',N'ao-thun-co-tru-basic',1,280000,1),
(61,N'Mũ snapback Logo',N'mu-snapback-logo',3,220000,0),
(62,N'Balo Urban Mini',N'balo-urban-mini',3,450000,0),
(63,N'Áo sơ mi linen Relax',N'ao-so-mi-linen-relax',1,380000,1),
(64,N'Quần short kaki Basic',N'quan-short-kaki-basic',2,350000,0),
(65,N'Dây chuyền bạc Minimal',N'day-chuyen-bac-minimal',3,180000,0),
(66,N'Vòng tay da Bracelet',N'vong-tay-da-bracelet',3,160000,0),
(67,N'Áo hoodie Zip Up',N'ao-hoodie-zip-up',1,650000,1),
(68,N'Quần tây ống côn Slim',N'quan-tay-ong-con-slim',2,480000,0),
(69,N'Áo khoác dạ Cashmere',N'ao-khoac-da-cashmere',1,1200000,0),
(70,N'Khăn choàng cổ Len',N'khan-choang-co-len',3,320000,0),
(71,N'Áo polo Pique Basic',N'ao-polo-pique-basic',1,340000,0),
(72,N'Quần baggy Denim Light',N'quan-baggy-denim-light',2,610000,1),
(73,N'Túi đeo hông Waist Bag',N'tui-deo-hong-waist-bag',3,280000,0),
(74,N'Áo len cổ lọ Tight',N'ao-len-co-lo-tight',1,420000,0),
(75,N'Giày sneaker Platform',N'giay-sneaker-platform',3,950000,1),
(76,N'Mũ beret Pháp',N'mu-beret-phap',3,140000,0);

SET IDENTITY_INSERT [Products] ON;

INSERT INTO [Products] ([id],[name],[slug],[category_id],[price],[stock],[available],[featured],[image_url],[created])
SELECT [id],[name],[slug],[category_id], [price],
    CASE WHEN [category_id] IN (1,2) THEN 450 ELSE 100 END,
    1,[featured],CONCAT(N'https://placehold.co/900x1125/f4eee8/35251d?text=HUUGIAU+', [id]),
    DATEADD(day,-[id],GETDATE())
FROM @product_seed;

SET IDENTITY_INSERT [Products] OFF;

-- Hai màu cho từng sản phẩm; size khớp seed Django: M/L/XL hoặc FREE.
DECLARE @pid INT = 1;
DECLARE @color NVARCHAR(20);
DECLARE @color_code NVARCHAR(20);
WHILE @pid <= 76 BEGIN
    SET @color = N'Đen';
    SET @color_code = N'#111111';
    WHILE @color IS NOT NULL BEGIN
        IF EXISTS (SELECT 1 FROM [Products] WHERE [id]=@pid AND [category_id] IN (1,2))
        BEGIN
            INSERT INTO [Variants] ([product_id],[color_name],[color_code],[size],[stock],[is_active]) VALUES
                (@pid,@color,@color_code,N'M',50,1),(@pid,@color,@color_code,N'L',50,1),(@pid,@color,@color_code,N'XL',50,1);
        END
        ELSE
            INSERT INTO [Variants] ([product_id],[color_name],[color_code],[size],[stock],[is_active]) VALUES
                (@pid,@color,@color_code,N'FREE',50,1);
        SET @color = CASE @color WHEN N'Đen' THEN N'Trắng' ELSE NULL END;
        SET @color_code = CASE @color WHEN N'Trắng' THEN N'#F5F5F5' ELSE NULL END;
    END;
    SET @pid += 1;
END;

INSERT INTO [Coupons] ([code],[type],[value],[is_active],[min_amount],[max_amount],[max_uses],[used_count]) VALUES
 (N'WELCOME',N'percent',15,1,0,100000,1000,0),(N'SALE10',N'percent',10,1,200000,50000,5000,0),(N'GIAM50K',N'fixed',50000,1,300000,NULL,500,0),(N'FREESHIP',N'freeship',0,1,200000,NULL,5000,0),(N'VIP20',N'percent',20,1,500000,200000,200,0),(N'BLACKFRI',N'percent',30,0,0,300000,NULL,0);

DECLARE @order INT=1;
DECLARE @uid INT;
DECLARE @status NVARCHAR(20);
DECLARE @payment NVARCHAR(20);
DECLARE @subtotal INT;
DECLARE @shipping INT;
DECLARE @discount INT;
WHILE @order <= 5000 BEGIN
    SET @uid=((@order-1)%15)+5;
    SET @status=CASE @order%7 WHEN 0 THEN N'cancelled' WHEN 1 THEN N'pending' WHEN 2 THEN N'processing' WHEN 3 THEN N'processing' WHEN 4 THEN N'shipping' ELSE N'delivered' END;
    SET @payment=CASE @order%3 WHEN 0 THEN N'cod' WHEN 1 THEN N'bank' ELSE N'vnpay' END;
    SET @subtotal=199000+((@order-1)%8)*50000;
    SET @shipping=CASE WHEN @order%4=0 THEN 0 ELSE 30000 END;
    SET @discount=CASE WHEN @order%5=0 THEN 50000 ELSE 0 END;
    INSERT INTO [Orders] ([user_id],[customer_name],[phone],[shipping_address],[status],[total_amount],[is_paid],[payment_method],[discount_amount],[coupon],[created_at])
    SELECT @uid,CONCAT(u.username,N' Demo'),u.phone,CONCAT(N'Số ',((@order-1)%99)+1,N' Nguyễn Huệ, Quận ',((@order-1)%12)+1,N', TP.HCM'),@status,@subtotal+@shipping-@discount,CASE WHEN @status IN (N'processing',N'shipping',N'delivered') THEN 1 ELSE 0 END,@payment,@discount,CASE WHEN @discount>0 THEN N'GIAM50K' ELSE N'' END,DATEADD(day,-(@order%365),GETDATE()) FROM [Users] u WHERE u.id=@uid;
    SET @order += 1;
END;

SET @order=1;
WHILE @order <= 5000 BEGIN
    INSERT INTO [OrderItems] ([order_id],[product_id],[variant_id],[color],[size],[quantity],[price])
    VALUES (@order,((@order-1)%76)+1,
        (SELECT TOP 1 [id] FROM [Variants] WHERE [product_id]=((@order-1)%76)+1 AND [color_name]=CASE WHEN @order%2=0 THEN N'Đen' ELSE N'Trắng' END AND [size]=CASE WHEN [product_id] <= 35 OR [product_id] BETWEEN 51 AND 54 OR [product_id] BETWEEN 57 AND 60 OR [product_id] BETWEEN 63 AND 64 OR [product_id] BETWEEN 67 AND 69 OR [product_id] BETWEEN 71 AND 72 OR [product_id]=74 THEN N'M' ELSE N'FREE' END),
        CASE WHEN @order%2=0 THEN N'Đen' ELSE N'Trắng' END,
        CASE WHEN ((@order-1)%76)+1 <= 35 OR ((@order-1)%76)+1 BETWEEN 51 AND 54 OR ((@order-1)%76)+1 BETWEEN 57 AND 60 OR ((@order-1)%76)+1 BETWEEN 63 AND 64 OR ((@order-1)%76)+1 BETWEEN 67 AND 69 OR ((@order-1)%76)+1 BETWEEN 71 AND 72 OR ((@order-1)%76)+1=74 THEN N'M' ELSE N'FREE' END,
        1+(@order%2),199000+(((@order-1)%8)*50000));
    IF @order%3=0 INSERT INTO [OrderItems] ([order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES (@order,(@order%76)+1,(SELECT TOP 1 [id] FROM [Variants] WHERE [product_id]=(@order%76)+1 AND [color_name]=N'Đen'),N'Đen',CASE WHEN (@order%76)+1 <= 35 OR (@order%76)+1 BETWEEN 51 AND 54 OR (@order%76)+1 BETWEEN 57 AND 60 OR (@order%76)+1 BETWEEN 63 AND 64 OR (@order%76)+1 BETWEEN 67 AND 69 OR (@order%76)+1 BETWEEN 71 AND 72 OR (@order%76)+1=74 THEN N'M' ELSE N'FREE' END,1,249000);
    SET @order += 1;
END;

SET @i=5;
WHILE @i <= 19 BEGIN INSERT INTO [Wishlist] ([user_id],[product_id],[created]) VALUES (@i,((@i-5)%76)+1,DATEADD(day,-@i,GETDATE())); SET @i += 1; END;
INSERT INTO [FAQs] ([question],[answer],[priority],[is_active]) VALUES
 (N'Đổi trả trong bao lâu?',N'HUUGIAU hỗ trợ đổi trả trong 7 ngày theo chính sách cửa hàng.',1,1),(N'Bao lâu nhận được hàng?',N'Đơn nội thành thường giao trong 1-2 ngày làm việc.',2,1),(N'Có thanh toán khi nhận hàng không?',N'Có, cửa hàng hỗ trợ COD và thanh toán online.',3,1),(N'Làm sao kiểm tra tồn kho?',N'Tồn kho theo màu và size hiển thị trên trang chi tiết sản phẩm.',4,1);
INSERT INTO [Activities] ([user_id],[event],[path],[created_at]) SELECT id,N'login',N'/dang-nhap/',DATEADD(day,-(id%30),GETDATE()) FROM [Users] WHERE id>=5;
PRINT N'DEMO DATA OK: users=19, categories=3, products=76, variants=360, coupons=6, orders=5000, order_items=6666';
