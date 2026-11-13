-- ============================================================================
-- FASHION-WEBSITE - VIEWS & FUNCTIONS
-- File: 06_views_functions.sql
-- Mục đích: Views báo cáo, Scalar UDF, Table-Valued UDF
-- ============================================================================

USE [HUUGIAU_Fashion];
GO SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON; GO
PRINT N'=== BẮT ĐẦU TẠO VIEWS & FUNCTIONS ===';

-- -----------------------------------------------------------------------------
-- VIEW 1: v_ThongKeSanPhamVaDoanhSo - Thống kê sản phẩm và doanh số
-- -----------------------------------------------------------------------------
CREATE OR ALTER VIEW dbo.v_ThongKeSanPhamVaDoanhSo
WITH SCHEMABINDING
AS
SELECT
    p.id AS ProductID,
    p.name AS ProductName,
    p.sku AS SKU,
    p.base_price AS GiaGoc,
    p.sale_price AS GiaGiam,
    ISNULL(SUM(oi.quantity), 0) AS TongSoLuongBan,
    ISNULL(SUM(oi.quantity * oi.price), 0) AS TongDoanhThu,
    COUNT(DISTINCT oi.order_id) AS SoDonHang,
    COUNT(DISTINCT o.user_id) AS SoKhachHang
FROM dbo.products_product p
LEFT JOIN dbo.orders_orderitem oi ON p.id = oi.product_id
LEFT JOIN dbo.orders_order o ON oi.order_id = o.id AND o.status IN ('confirmed','shipping','done') AND o.deleted_at IS NULL
WHERE p.deleted_at IS NULL
GROUP BY p.id, p.name, p.sku, p.base_price, p.sale_price;
GO

-- -----------------------------------------------------------------------------
-- VIEW 2: v_BaoCaoDoanhThuTheoThang - Báo cáo doanh thu theo tháng
-- -----------------------------------------------------------------------------
CREATE OR ALTER VIEW dbo.v_BaoCaoDoanhThuTheoThang
WITH SCHEMABINDING
AS
SELECT
    FORMAT(o.created_at, 'yyyy-MM') AS Thang,
    YEAR(o.created_at) AS Nam,
    MONTH(o.created_at) AS ThangSo,
    COUNT(DISTINCT o.id) AS TongSoDon,
    SUM(CASE WHEN o.status = 'done' THEN 1 ELSE 0 END) AS DonHoanTat,
    SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS DonHuy,
    SUM(CASE WHEN o.status = 'refunded' THEN 1 ELSE 0 END) AS DonHoan,
    SUM(o.subtotal_amount) AS TongTienHang,
    SUM(o.discount_amount) AS TongGiamGia,
    SUM(o.shipping_fee) AS TongPhiShip,
    SUM(o.vat_amount) AS TongVAT,
    SUM(o.total_amount) AS TongDoanhThu
FROM dbo.orders_order o
WHERE o.deleted_at IS NULL
GROUP BY FORMAT(o.created_at, 'yyyy-MM'), YEAR(o.created_at), MONTH(o.created_at);
GO

-- -----------------------------------------------------------------------------
-- VIEW 3: v_KhachHangChiTieu - Thống kê chi tiêu khách hàng
-- -----------------------------------------------------------------------------
CREATE OR ALTER VIEW dbo.v_KhachHangChiTieu
WITH SCHEMABINDING
AS
SELECT
    u.id AS UserID,
    u.username AS Username,
    u.email AS Email,
    up.phone_number AS Phone,
    COUNT(DISTINCT o.id) AS TongSoDon,
    SUM(CASE WHEN o.status = 'done' THEN o.total_amount ELSE 0 END) AS TongChiTieu,
    MAX(o.created_at) AS LanCuoiMua,
    up.points AS DiemHienTai
FROM dbo.auth_user u
LEFT JOIN dbo.users_userprofile up ON u.id = up.user_id
LEFT JOIN dbo.orders_order o ON u.id = o.user_id AND o.deleted_at IS NULL
WHERE u.is_active = 1
GROUP BY u.id, u.username, u.email, up.phone_number, up.points;
GO

-- -----------------------------------------------------------------------------
-- SCALAR UDF: fn_TinhGiamGiaVoucher - Tính giảm giá voucher
-- -----------------------------------------------------------------------------
CREATE OR ALTER FUNCTION dbo.fn_TinhGiamGiaVoucher
(
    @CouponCode NVARCHAR(30),
    @Subtotal DECIMAL(12,2)
)
RETURNS DECIMAL(12,2)
WITH SCHEMABINDING
AS
BEGIN
    DECLARE @Result DECIMAL(12,2) = 0;
    DECLARE @CType NVARCHAR(20), @CVal DECIMAL(12,2), @CMax DECIMAL(12,2);

    SELECT @CType = discount_type, @CVal = value, @CMax = ISNULL(max_discount_amount, 0)
    FROM dbo.orders_coupon
    WHERE code = @CouponCode AND is_active = 1
      AND (starts_at IS NULL OR starts_at <= SYSUTCDATETIME())
      AND (ends_at IS NULL OR ends_at >= SYSUTCDATETIME())
      AND (usage_limit IS NULL OR used_count < usage_limit);

    IF @CType IS NOT NULL
    BEGIN
        IF @CType = 'percent' SET @Result = ROUND(@Subtotal * @CVal / 100, 2);
        ELSE IF @CType = 'fixed' SET @Result = @CVal;
        IF @CMax > 0 AND @Result > @CMax SET @Result = @CMax;
        IF @Result > @Subtotal SET @Result = @Subtotal;
    END
    RETURN @Result;
END;
GO

-- -----------------------------------------------------------------------------
-- TABLE-VALUED UDF: fn_LayChiTietDonHang - Lấy chi tiết đơn hàng
-- -----------------------------------------------------------------------------
CREATE OR ALTER FUNCTION dbo.fn_LayChiTietDonHang
(
    @OrderID BIGINT
)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
(
    SELECT
        oi.id AS OrderItemID,
        oi.product_id AS ProductID,
        p.name AS ProductName,
        p.sku AS SKU,
        oi.variant_id AS VariantID,
        oi.selected_color AS Color,
        oi.selected_size AS Size,
        oi.quantity AS Quantity,
        oi.price AS UnitPrice,
        (oi.quantity * oi.price) AS LineTotal
    FROM dbo.orders_orderitem oi
    JOIN dbo.products_product p ON oi.product_id = p.id
    WHERE oi.order_id = @OrderID
);
GO

PRINT N'=== HOÀN TẤT VIEWS & FUNCTIONS ===';