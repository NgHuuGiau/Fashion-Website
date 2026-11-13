-- ============================================================================
-- FASHION-WEBSITE - SEED DATA
-- File: 08_seed_data.sql
-- Mục đích: Dữ liệu mẫu sản phẩm, voucher, đơn hàng demo
-- ============================================================================

USE [HUUGIAU_Fashion];
GO SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON; GO
PRINT N'=== BẮT ĐẦU NẠP DỮ LIỆU MẪU ===';

-- -----------------------------------------------------------------------------
-- Voucher mẫu
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM dbo.orders_coupon WHERE code = 'WELCOME10')
    INSERT INTO dbo.orders_coupon (code, name, discount_type, value, min_order_amount, is_active, usage_limit, max_uses_per_user, trigger_type)
    VALUES ('WELCOME10', N'Chào mừng thành viên mới', 'percent', 10, 100000, 1, NULL, 1, 'cart');

IF NOT EXISTS (SELECT 1 FROM dbo.orders_coupon WHERE code = 'FREESHIP')
    INSERT INTO dbo.orders_coupon (code, name, discount_type, value, min_order_amount, is_active, usage_limit, max_uses_per_user, trigger_type)
    VALUES ('FREESHIP', N'Miễn phí ship đơn từ 300k', 'free_shipping', 0, 300000, 1, NULL, 1, 'cart');

IF NOT EXISTS (SELECT 1 FROM dbo.orders_coupon WHERE code = 'SALE200K')
    INSERT INTO dbo.orders_coupon (code, name, discount_type, value, min_order_amount, max_discount_amount, is_active, usage_limit, max_uses_per_user, trigger_type)
    VALUES ('SALE200K', N'Giảm 200k đơn từ 1tr', 'fixed', 200000, 1000000, 200000, 1, 100, 1, 'cart');

-- -----------------------------------------------------------------------------
-- Sequence cho order_code (nếu chưa có)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM sys.sequences WHERE name = 'seq_order_code')
    CREATE SEQUENCE dbo.seq_order_code AS INT START WITH 1 INCREMENT BY 1;

-- -----------------------------------------------------------------------------
-- Sản phẩm mẫu (chạy qua Django seed_products command thay vì raw SQL)
-- Dữ liệu demo này chỉ để tham khảo cấu trúc
-- -----------------------------------------------------------------------------
/*
INSERT INTO dbo.products_product (name, slug, description, base_price, sale_price, sku, is_active, category_id, created_at, updated_at)
VALUES
(N'Áo sơ mi nam cao cấp', N'ao-so-mi-nam-cao-cap', N'Chất liệu cotton 100%', 350000, 299000, 'SM-NAM-001', 1, 1, SYSUTCDATETIME(), SYSUTCDATETIME()),
(N'Váy đầm nữ xinh xắn', N'vay-dam-nu-xinh-xan', N'Thiết kế hiện đại', 450000, 399000, 'VD-NU-001', 1, 2, SYSUTCDATETIME(), SYSUTCDATETIME()),
(N'Quần jeans unisex', N'quan-jeans-unisex', N'Form rộng thoải mái', 400000, 350000, 'QJ-UNI-001', 1, 3, SYSUTCDATETIME(), SYSUTCDATETIME());

INSERT INTO dbo.products_productvariant (product_id, color_name, color_code, size, stock, is_active)
VALUES
(1, N'Trắng', '#FFFFFF', N'S', 50, 1), (1, N'Trắng', '#FFFFFF', N'M', 50, 1), (1, N'Trắng', '#FFFFFF', N'L', 50, 1),
(1, N'Đen', '#000000', N'S', 30, 1), (1, N'Đen', '#000000', N'M', 30, 1), (1, N'Đen', '#000000', N'L', 30, 1),
(2, N'Hồng', '#FFC0CB', N'S', 20, 1), (2, N'Hồng', '#FFC0CB', N'M', 20, 1),
(3, N'Xanh navy', '#000080', N'29', 40, 1), (3, N'Xanh navy', '#000080', N'30', 40, 1), (3, N'Xanh navy', '#000080', N'31', 40, 1);
*/

PRINT N'=== HOÀN TẤT SEED DATA (Chỉ voucher, sản phẩm seed qua Django) ===';