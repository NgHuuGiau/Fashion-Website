PRAGMA foreign_keys = ON;

----- | DANH MỤC SẢN PHẨM | -----
INSERT INTO products_category (name, slug)
SELECT 'Áo Thun', 'ao-thun' WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug='ao-thun');

INSERT INTO products_category (name, slug)
SELECT 'Áo Sơ Mi', 'ao-so-mi' WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug='ao-so-mi');

INSERT INTO products_category (name, slug)
SELECT 'Áo Khoác', 'ao-khoac' WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug='ao-khoac');

INSERT INTO products_category (name, slug)
SELECT 'Quần Tây & Kaki', 'quan-tay-kaki' WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug='quan-tay-kaki');

INSERT INTO products_category (name, slug)
SELECT 'Quần Jeans', 'quan-jeans' WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug='quan-jeans');

INSERT INTO products_category (name, slug)
SELECT 'Giày Dép', 'giay-dep' WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug='giay-dep');

INSERT INTO products_category (name, slug)
SELECT 'Phụ Kiện', 'phu-kien' WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug='phu-kien');


----- | SẢN PHẨM CHÍNH | -----
INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='ao-thun'), 'Áo Thun Basic Cotton 100%', 'ao-thun-basic-cotton', '', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80', 'Áo thun cotton thoáng mát, form regular fit chuẩn thời trang dạo phố. Vải nhẹ, thấm hút cực tốt.', 250000, 100, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='ao-thun-basic-cotton');

INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='ao-thun'), 'Áo Thun Oversize Local Brand', 'ao-thun-oversize-local', '', 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500&q=80', 'Phong cách đường phố Oversize cá tính, hoạ tiết in lụa chìm sắc nét cao cấp.', 350000, 80, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='ao-thun-oversize-local');

INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='ao-so-mi'), 'Sơ Mi Lụa Cổ Vest Cuban', 'so-mi-lua-cuban', '', 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&q=80', 'Sơ mi tay ngắn cổ Cuban trẻ trung, chất liệu lụa mỏng nhẹ phù hợp mặc đi biển hoặc đi chơi.', 420000, 50, 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='so-mi-lua-cuban');

INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='ao-so-mi'), 'Sơ Mi Oxford Cổ Điển', 'so-mi-oxford', '', 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&q=80', 'Sơ mi dài tay form slimfit ôm nhẹ, dành cho những ngày làm việc công sở thanh lịch.', 490000, 60, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='so-mi-oxford');

INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='quan-jeans'), 'Quần Jeans Xanh Vintage Wash', 'jeans-xanh-vintage-wash', '', 'https://images.unsplash.com/photo-1542272604-78027ee2cc64?w=500&q=80', 'Jeans denim với kỹ thuật wash mài độc đáo, có độ co giãn nhẹ.', 550000, 70, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='jeans-xanh-vintage-wash');

INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='quan-jeans'), 'Quần Jeans Đen Ống Rộng Baggy', 'jeans-den-ong-rong', '', 'https://images.unsplash.com/photo-1604176352968-3e4210aa39e4?w=500&q=80', 'Form ống rộng chuẩn style Gen Z, mang lại cảm giác thoải mái khi di chuyển.', 590000, 40, 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='jeans-den-ong-rong');

INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='ao-khoac'), 'Jacket Denim Xước Bụi', 'jacket-denim-xuoc', '', 'https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=500&q=80', 'Khoác bò denim cực ngầu, thiết kế unisex phù hợp cả nam và nữ.', 750000, 30, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='jacket-denim-xuoc');

INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='ao-khoac'), 'Áo Khoác Nỉ Hoodie Zip', 'hoodie-zip-ni', '', 'https://images.unsplash.com/photo-1556821840-b6a655845cca?w=500&q=80', 'Áo khoác dây kéo khóa nỉ bông ấm áp, must-have item cho mùa lạnh.', 650000, 50, 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='hoodie-zip-ni');

INSERT INTO products_product (category_id, name, slug, image, image_url, description, price, stock, available, featured, created, updated)
SELECT (SELECT id FROM products_category WHERE slug='phu-kien'), 'Kính Râm Thời Trang Mắt Mèo', 'kinh-ram-mat-meo', '', 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500&q=80', 'Bảo vệ mắt khỏi tia UV với tròng kính tráng gương siêu đỉnh.', 320000, 120, 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_product WHERE slug='kinh-ram-mat-meo');


----- | BIẾN THỂ SẢN PHẨM | -----
INSERT INTO products_productvariant (product_id, color_name, color_code, size, stock, is_active)
SELECT p.id, color, code, size, 20, 1
FROM products_product p
JOIN (SELECT 'Trắng' as color, '#FFFFFF' as code UNION SELECT 'Đen' as color, '#000000' as code) c
JOIN (SELECT 'S' as size UNION SELECT 'M' as size UNION SELECT 'L' as size UNION SELECT 'XL' as size) s
WHERE p.slug = 'ao-thun-basic-cotton'
AND NOT EXISTS (
    SELECT 1 FROM products_productvariant v 
    WHERE v.product_id = p.id AND v.color_name = color AND v.size = size
);

INSERT INTO products_productvariant (product_id, color_name, color_code, size, stock, is_active)
SELECT p.id, color, code, size, 15, 1
FROM products_product p
JOIN (SELECT 'Đen' as color, '#000000' as code) c
JOIN (SELECT '28' as size UNION SELECT '30' as size UNION SELECT '32' as size UNION SELECT '34' as size) s
WHERE p.slug = 'jeans-den-ong-rong'
AND NOT EXISTS (
    SELECT 1 FROM products_productvariant v 
    WHERE v.product_id = p.id AND v.color_name = color AND v.size = size
);

INSERT INTO products_productvariant (product_id, color_name, color_code, size, stock, is_active)
SELECT p.id, color, code, size, 15, 1
FROM products_product p
JOIN (SELECT 'Xanh Nhạt' as color, '#4b7cb6' as code UNION SELECT 'Xanh Đậm' as color, '#1e3a8a' as code) c
JOIN (SELECT '29' as size UNION SELECT '31' as size UNION SELECT '33' as size) s
WHERE p.slug = 'jeans-xanh-vintage-wash'
AND NOT EXISTS (
    SELECT 1 FROM products_productvariant v 
    WHERE v.product_id = p.id AND v.color_name = color AND v.size = size
);

UPDATE products_product
SET stock = COALESCE((
    SELECT SUM(v.stock)
    FROM products_productvariant v
    WHERE v.product_id = products_product.id AND v.is_active = 1
), stock),
updated = CURRENT_TIMESTAMP;


----- | MÃ GIẢM GIÁ | -----
INSERT INTO orders_coupon (code, discount_type, value, min_order_amount, max_discount_amount, is_active, usage_limit, used_count, created_at, updated_at)
SELECT 'WELCOME10', 'percent', 10, 200000, 50000, 1, 1000, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM orders_coupon WHERE code='WELCOME10');

INSERT INTO orders_coupon (code, discount_type, value, min_order_amount, is_active, usage_limit, used_count, created_at, updated_at)
SELECT 'FREESHIP', 'freeship', 0, 300000, 1, 500, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM orders_coupon WHERE code='FREESHIP');

INSERT INTO orders_coupon (code, discount_type, value, min_order_amount, is_active, usage_limit, used_count, created_at, updated_at)
SELECT 'GIAM50K', 'fixed', 50000, 500000, 1, 200, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM orders_coupon WHERE code='GIAM50K');


----- | TÀI KHOẢN NGƯỜI DÙNG | -----
INSERT INTO auth_user (password, is_superuser, username, email, is_staff, is_active, date_joined, first_name, last_name)
SELECT 'pbkdf2_sha256$1200000$PEB4CousFV7rTzzBWs8XeM$BWcXkyNZKHeXGENUiS0i5H5KaDTIxrBvTBn6ngD1lPE=', 1, 'admin', 'admin@local.test', 1, 1, CURRENT_TIMESTAMP, 'Admin', ''
WHERE NOT EXISTS (SELECT 1 FROM auth_user WHERE username='admin');

INSERT INTO auth_user (password, is_superuser, username, email, is_staff, is_active, date_joined, first_name, last_name)
SELECT 'pbkdf2_sha256$1200000$XYm3mxbjYp7zx3STzVkifk$cB93MBOWi7eaGdiDWDIG1mg78p9pl+TtzQ5E7F9Ii8I=', 0, 'user', 'user@local.test', 0, 1, CURRENT_TIMESTAMP, 'User', ''
WHERE NOT EXISTS (SELECT 1 FROM auth_user WHERE username='user');

INSERT INTO users_userprofile (user_id, phone_number)
SELECT (SELECT id FROM auth_user WHERE username='user'), '0901234567'
WHERE NOT EXISTS (SELECT 1 FROM users_userprofile WHERE user_id=(SELECT id FROM auth_user WHERE username='user'));


----- | WISHLIST - YÊU THÍCH | -----
INSERT INTO products_wishlistitem (user_id, product_id, created)
SELECT (SELECT id FROM auth_user WHERE username='user'), (SELECT id FROM products_product WHERE slug='ao-thun-basic-cotton'), CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM products_wishlistitem WHERE user_id=(SELECT id FROM auth_user WHERE username='user') AND product_id=(SELECT id FROM products_product WHERE slug='ao-thun-basic-cotton'));


----- | ĐƠN HÀNG MẪU | -----
INSERT INTO orders_order (user_id, customer_name, customer_email, phone, shipping_address, payment_method, status, subtotal_amount, shipping_fee, discount_amount, total_amount, created_at, updated_at, is_paid, note, bank_code, coupon_code)
SELECT (SELECT id FROM auth_user WHERE username='user'), 'User Demo', 'user@local.test', '0901234567', 'Quận 1, TP. HCM', 'cod', 'delivered', 800000, 30000, 50000, 780000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, '', '', ''
WHERE NOT EXISTS (SELECT 1 FROM orders_order WHERE customer_email='user@local.test');

INSERT INTO orders_orderitem (order_id, product_id, variant_id, selected_color, selected_size, quantity, price)
SELECT 
    (SELECT id FROM orders_order WHERE customer_email='user@local.test' LIMIT 1),
    (SELECT id FROM products_product WHERE slug='ao-thun-basic-cotton'),
    NULL, 'Trắng', 'M', 2, 250000
WHERE NOT EXISTS (SELECT 1 FROM orders_orderitem WHERE order_id=(SELECT id FROM orders_order WHERE customer_email='user@local.test' LIMIT 1));
