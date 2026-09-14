-- ============================================================
-- HUUGIAU Fashion - DEMO DATA
-- Must be run after 01_CREATE_TABLES.sql in SQL Server.
-- Seeds the legacy schema used by import_legacy.
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
 (N'Áo',N'ao'),(N'Quần',N'quan'),(N'Áo khoác',N'ao-khoac'),(N'Váy',N'vay'),(N'Giày',N'giay'),(N'Phụ kiện',N'phu-kien');

DECLARE @product INT = 1;
WHILE @product <= 24 BEGIN
    INSERT INTO [Products] ([name],[slug],[category_id],[price],[stock],[available],[featured],[image_url],[created])
    VALUES (CONCAT(N'Sản phẩm demo ',RIGHT(CONCAT(N'0',@product),2)),CONCAT(N'san-pham-demo-',@product),((@product-1)%6)+1,199000+((@product-1)%8)*50000,120+(@product%40),1,CASE WHEN @product<=8 THEN 1 ELSE 0 END,CONCAT(N'https://placehold.co/900x1125/f4eee8/35251d?text=HUUGIAU+',@product),DATEADD(day,-@product,GETDATE()));
    SET @product += 1;
END;

DECLARE @pid INT = 1;
DECLARE @size NVARCHAR(20);
WHILE @pid <= 24 BEGIN
    SET @size=N'S';
    WHILE @size IS NOT NULL BEGIN
        INSERT INTO [Variants] ([product_id],[color_name],[color_code],[size],[stock],[is_active]) VALUES (@pid,CASE WHEN @pid%2=0 THEN N'Đen' ELSE N'Nâu' END,CASE WHEN @pid%2=0 THEN N'#111111' ELSE N'#8A4A2A' END,@size,30+(@pid%15),1);
        SET @size=CASE @size WHEN N'S' THEN N'M' WHEN N'M' THEN N'L' WHEN N'L' THEN N'XL' ELSE NULL END;
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
    INSERT INTO [OrderItems] ([order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES (@order,((@order-1)%24)+1,(((@order-1)%24)*4)+1,CASE WHEN @order%2=0 THEN N'Đen' ELSE N'Nâu' END,N'S',1+(@order%2),199000+(((@order-1)%8)*50000));
    IF @order%3=0 INSERT INTO [OrderItems] ([order_id],[product_id],[variant_id],[color],[size],[quantity],[price]) VALUES (@order,(@order%24)+1,((@order%24)*4)+2,N'Đen',N'M',1,249000);
    SET @order += 1;
END;

SET @i=5;
WHILE @i <= 19 BEGIN INSERT INTO [Wishlist] ([user_id],[product_id],[created]) VALUES (@i,((@i-5)%24)+1,DATEADD(day,-@i,GETDATE())); SET @i += 1; END;
INSERT INTO [FAQs] ([question],[answer],[priority],[is_active]) VALUES
 (N'Đổi trả trong bao lâu?',N'HUUGIAU hỗ trợ đổi trả trong 7 ngày theo chính sách cửa hàng.',1,1),(N'Bao lâu nhận được hàng?',N'Đơn nội thành thường giao trong 1-2 ngày làm việc.',2,1),(N'Có thanh toán khi nhận hàng không?',N'Có, cửa hàng hỗ trợ COD và thanh toán online.',3,1),(N'Làm sao kiểm tra tồn kho?',N'Tồn kho theo màu và size hiển thị trên trang chi tiết sản phẩm.',4,1);
INSERT INTO [Activities] ([user_id],[event],[path],[created_at]) SELECT id,N'login',N'/dang-nhap/',DATEADD(day,-(id%30),GETDATE()) FROM [Users] WHERE id>=5;
PRINT N'DEMO DATA OK: users=19, categories=6, products=24, variants=96, coupons=6, orders=5000, order_items=6666';
