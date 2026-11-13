-- Part 3: Reporting SPs
CREATE OR ALTER PROCEDURE dbo.sp_BaoCaoDoanhThuTheoThang
    @FromDate DATE = NULL, @ToDate DATE = NULL
AS BEGIN SET NOCOUNT ON;
    IF @FromDate IS NULL SET @FromDate = DATEADD(MONTH,-12,CAST(SYSUTCDATETIME() AS DATE));
    IF @ToDate IS NULL SET @ToDate = CAST(SYSUTCDATETIME() AS DATE);
    SELECT FORMAT(o.created_at,'yyyy-MM') AS Thang,
        COUNT(DISTINCT o.id) AS SoDonHang,
        SUM(CASE WHEN o.status='done' THEN 1 ELSE 0 END) AS DonHoanTat,
        SUM(CASE WHEN o.status='cancelled' THEN 1 ELSE 0 END) AS DonHuy,
        SUM(CASE WHEN o.status='refunded' THEN 1 ELSE 0 END) AS DonHoan,
        SUM(o.subtotal_amount) AS TongTienHang, SUM(o.discount_amount) AS TongGiamGia,
        SUM(o.shipping_fee) AS TongPhiShip, SUM(o.vat_amount) AS TongVAT,
        SUM(o.total_amount) AS TongDoanhThu, SUM(o.points_earned) AS TongDiemTich
    FROM dbo.orders_order o
    WHERE o.created_at>=@FromDate AND o.created_at<=@ToDate AND o.deleted_at IS NULL
    GROUP BY FORMAT(o.created_at,'yyyy-MM') ORDER BY Thang; END; GO

CREATE OR ALTER PROCEDURE dbo.sp_BaoCaoSanPhamBanChay
    @FromDate DATE = NULL, @ToDate DATE = NULL, @TopN INT = 20
AS BEGIN SET NOCOUNT ON;
    IF @FromDate IS NULL SET @FromDate = DATEADD(MONTH,-3,CAST(SYSUTCDATETIME() AS DATE));
    IF @ToDate IS NULL SET @ToDate = CAST(SYSUTCDATETIME() AS DATE);
    SELECT TOP (@TopN) p.id,p.name,p.sku,p.base_price,p.sale_price,
        SUM(oi.quantity) AS TongSoLuongBan, SUM(oi.quantity*oi.price) AS TongDoanhThu,
        COUNT(DISTINCT oi.order_id) AS SoDonHang
    FROM dbo.orders_orderitem oi JOIN dbo.orders_order o ON oi.order_id=o.id
    JOIN dbo.products_product p ON oi.product_id=p.id
    WHERE o.status IN ('confirmed','shipping','done')
      AND o.created_at>=@FromDate AND o.created_at<=@ToDate AND o.deleted_at IS NULL
    GROUP BY p.id,p.name,p.sku,p.base_price,p.sale_price ORDER BY TongSoLuongBan DESC; END; GO

PRINT N'=== HOÀN TẤT STORED PROCEDURES ===';