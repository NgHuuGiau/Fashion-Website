-- ============================================================================
-- FASHION-WEBSITE - CURSORS
-- File: 05_cursors.sql
-- Mục đích: Cursors quét đơn quá hạn, phân hạng VIP tặng voucher
-- ============================================================================

USE [HUUGIAU_Fashion];
GO SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON; GO
PRINT N'=== BẮT ĐẦU CÀI ĐẶT CURSORS ===';

-- -----------------------------------------------------------------------------
-- CURSOR 1: sp_Cursor_PhanHangVaTangVoucherKhachHang
-- Duyệt lịch sử chi tiêu, xếp hạng VIP và tặng voucher tri ân
-- -----------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.sp_Cursor_PhanHangVaTangVoucherKhachHang
AS BEGIN SET NOCOUNT ON;
    DECLARE @UserID BIGINT, @TotalSpent DECIMAL(12,2), @Tier NVARCHAR(20), @VoucherCode NVARCHAR(30), @VoucherValue DECIMAL(12,2);
    DECLARE @VoucherID BIGINT;

    -- Cursor qua các khách hàng có đơn hoàn tất
    DECLARE cur_vip CURSOR LOCAL FAST_FORWARD READ_ONLY FOR
    SELECT o.user_id, SUM(o.total_amount)
    FROM dbo.orders_order o
    WHERE o.status = 'done' AND o.user_id IS NOT NULL AND o.deleted_at IS NULL
    GROUP BY o.user_id
    HAVING SUM(o.total_amount) > 0;

    OPEN cur_vip;
    FETCH NEXT FROM cur_vip INTO @UserID, @TotalSpent;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Xếp hạng dựa trên tổng chi tiêu
        IF @TotalSpent >= 50000000 SET @Tier = 'DIAMOND', @VoucherCode = 'VIP_DIAMOND_' + CAST(@UserID AS NVARCHAR), @VoucherValue = 500000;
        ELSE IF @TotalSpent >= 20000000 SET @Tier = 'PLATINUM', @VoucherCode = 'VIP_PLATINUM_' + CAST(@UserID AS NVARCHAR), @VoucherValue = 200000;
        ELSE IF @TotalSpent >= 10000000 SET @Tier = 'GOLD', @VoucherCode = 'VIP_GOLD_' + CAST(@UserID AS NVARCHAR), @VoucherValue = 100000;
        ELSE IF @TotalSpent >= 5000000 SET @Tier = 'SILVER', @VoucherCode = 'VIP_SILVER_' + CAST(@UserID AS NVARCHAR), @VoucherValue = 50000;
        ELSE SET @Tier = 'BRONZE', @VoucherCode = 'VIP_BRONZE_' + CAST(@UserID AS NVARCHAR), @VoucherValue = 20000;

        -- Kiểm tra đã cấp voucher tier này chưa
        IF NOT EXISTS (SELECT 1 FROM dbo.orders_coupon WHERE code = @VoucherCode)
        BEGIN
            INSERT INTO dbo.orders_coupon (code, name, discount_type, value, min_order_amount, max_discount_amount, is_active, usage_limit, max_uses_per_user, trigger_type, created_at, updated_at)
            VALUES (@VoucherCode, N'Voucher tri ân ' + @Tier, 'fixed', @VoucherValue, 0, @VoucherValue, 1, 1, 1, 'cart', SYSUTCDATETIME(), SYSUTCDATETIME());
        END

        FETCH NEXT FROM cur_vip INTO @UserID, @TotalSpent;
    END

    CLOSE cur_vip; DEALLOCATE cur_vip;
    PRINT N'Cursor sp_Cursor_PhanHangVaTangVoucherKhachHang: Đã xử lý xong.';
END; GO

-- -----------------------------------------------------------------------------
-- CURSOR 2: sp_Cursor_QuetDonQuocHan - Quét đơn quá hạn tự động hủy
-- -----------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.sp_Cursor_QuetDonQuocHan
    @TimeoutHours INT = 24 -- Hủy đơn pending quá 24h chưa thanh toán
AS BEGIN SET NOCOUNT ON;
    DECLARE @OrderID BIGINT, @OrderCode NVARCHAR(32);
    DECLARE @Cutoff DATETIME2(3) = DATEADD(HOUR, -@TimeoutHours, SYSUTCDATETIME());

    DECLARE cur_expired CURSOR LOCAL FAST_FORWARD READ_ONLY FOR
    SELECT id, order_code FROM dbo.orders_order
    WHERE status = 'pending' AND is_paid = 0 AND created_at < @Cutoff AND deleted_at IS NULL;

    OPEN cur_expired;
    FETCH NEXT FROM cur_expired INTO @OrderID, @OrderCode;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Hủy đơn qua SP (sẽ trigger hoàn kho)
        EXEC dbo.sp_HuyDonHang @OrderID, NULL, N'Tự động hủy do quá hạn thanh toán';
        FETCH NEXT FROM cur_expired INTO @OrderID, @OrderCode;
    END

    CLOSE cur_expired; DEALLOCATE cur_expired;
    PRINT N'Cursor sp_Cursor_QuetDonQuocHan: Đã quét xong.';
END; GO

PRINT N'=== HOÀN TẤT CURSORS ===';