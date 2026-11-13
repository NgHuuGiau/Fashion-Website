-- ============================================================================
-- FASHION-WEBSITE - TRANSACTIONS & CONCURRENCY DEMO
-- File: 07_transactions_concurrency.sql
-- Mục đích: Demo Savepoint, Lock hints (UPDLOCK, ROWLOCK), Isolation Levels
-- ============================================================================

USE [HUUGIAU_Fashion];
GO SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON; GO
PRINT N'=== BẮT ĐẦU DEMO TRANSACTIONS & CONCURRENCY ===';

-- -----------------------------------------------------------------------------
-- DEMO 1: Savepoint trong SP tạo đơn hàng (đã có trong sp_TaoDonHangAnToan)
-- Minh họa cách rollback phần nếu có lỗi
-- -----------------------------------------------------------------------------
/*
BEGIN TRANSACTION;
SAVE TRANSACTION SavePoint_BeforeCoupon;
    -- Apply coupon logic
    IF @CouponInvalid = 1
        ROLLBACK TRANSACTION SavePoint_BeforeCoupon; -- Chỉ rollback phần coupon
COMMIT TRANSACTION;
*/

-- -----------------------------------------------------------------------------
-- DEMO 2: SELECT với UPDLOCK, ROWLOCK để tránh deadlock khi trừ tồn kho
-- -----------------------------------------------------------------------------
/*
-- Trong trigger hoặc SP, khi cần lock hàng trước khi update:
SELECT pv.stock FROM dbo.products_productvariant pv WITH (UPDLOCK, ROWLOCK)
WHERE pv.id = @VariantID;
-- Sau đó UPDATE an toàn
*/

-- -----------------------------------------------------------------------------
-- DEMO 3: Isolation Level READ COMMITTED SNAPSHOT (khuyên dùng cho production)
-- -----------------------------------------------------------------------------
/*
-- Bật RCSI cho database (chạy 1 lần):
ALTER DATABASE [HUUGIAU_Fashion] SET READ_COMMITTED_SNAPSHOT ON;
-- Hoặc set cho session:
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
*/

-- -----------------------------------------------------------------------------
-- DEMO 4: Xử lý deadlock với retry logic
-- -----------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.sp_UpdateStockWithRetry
    @VariantID BIGINT, @QuantityChange INT, @MaxRetries INT = 3
AS BEGIN SET NOCOUNT ON;
    DECLARE @RetryCount INT = 0, @Success BIT = 0;
    WHILE @RetryCount < @MaxRetries AND @Success = 0
    BEGIN
        BEGIN TRY
            BEGIN TRANSACTION;
            UPDATE dbo.products_productvariant
            SET stock = stock + @QuantityChange, updated_at = SYSUTCDATETIME()
            WHERE id = @VariantID AND stock + @QuantityChange >= 0;
            IF @@ROWCOUNT = 0
                THROW 50006, N'Tồn kho không đủ hoặc biến thể không tồn tại.', 1;
            COMMIT TRANSACTION;
            SET @Success = 1;
        END TRY
        BEGIN CATCH
            IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
            SET @RetryCount += 1;
            IF @RetryCount >= @MaxRetries
            BEGIN
                DECLARE @Msg NVARCHAR(4000) = ERROR_MESSAGE();
                RAISERROR(@Msg, 16, 1); RETURN -1;
            END
            WAITFOR DELAY '00:00:00.1'; -- Wait 100ms before retry
        END CATCH
    END
    RETURN 0;
END; GO

-- -----------------------------------------------------------------------------
-- DEMO 5: Pessimistic locking cho voucher usage (tránh race condition)
-- -----------------------------------------------------------------------------
/*
BEGIN TRANSACTION;
SELECT used_count, usage_limit FROM dbo.orders_coupon WITH (UPDLOCK, ROWLOCK) WHERE id = @CouponID;
IF used_count < usage_limit
    UPDATE dbo.orders_coupon SET used_count = used_count + 1 WHERE id = @CouponID;
COMMIT TRANSACTION;
*/

PRINT N'=== HOÀN TẤT DEMO TRANSACTIONS ===';