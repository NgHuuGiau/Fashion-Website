-- ============================================================================
-- FASHION-WEBSITE - TRIGGERS (Part 1): Stock Management
-- File: 03a_trigger_stock.sql
-- ============================================================================

USE [HUUGIAU_Fashion];
GO
SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON; GO

PRINT N'=== BẮT ĐẦU CÀI ĐẶT TRIGGERS (Part 1) ===';

-- -----------------------------------------------------------------------------
-- TRIGGER 1: trg_KiemTraVaTruTonKho
-- AFTER INSERT trên orders_orderitem
-- Kiểm tra và trừ tồn kho biến thể
-- -----------------------------------------------------------------------------
CREATE OR ALTER TRIGGER dbo.trg_KiemTraVaTruTonKho
ON dbo.orders_orderitem
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1 FROM inserted i
        JOIN dbo.products_productvariant pv ON i.variant_id = pv.id
        WHERE pv.stock < i.quantity
    )
    BEGIN
        DECLARE @TenSP NVARCHAR(255), @Mau NVARCHAR(50), @Size NVARCHAR(20);
        DECLARE @TonKho INT, @SoLuongDat INT;

        SELECT TOP 1 @TenSP=i.product_name, @Mau=i.selected_color, @Size=i.selected_size,
               @TonKho=pv.stock, @SoLuongDat=i.quantity
        FROM inserted i JOIN dbo.products_productvariant pv ON i.variant_id=pv.id
        WHERE pv.stock < i.quantity;

        DECLARE @Msg NVARCHAR(500) = FORMATMESSAGE(
            N'Lỗi tồn kho: Sản phẩm "%s" (Màu: %s, Size: %s) chỉ còn %d, không đủ đặt %d.',
            @TenSP, @Mau, @Size, @TonKho, @SoLuongDat
        );
        RAISERROR(@Msg, 16, 1); ROLLBACK TRANSACTION; RETURN;
    END

    UPDATE pv SET pv.stock = pv.stock - i.quantity, pv.updated_at = SYSUTCDATETIME()
    FROM dbo.products_productvariant pv JOIN inserted i ON pv.id = i.variant_id
    WHERE i.variant_id IS NOT NULL;

    PRINT N'Trigger trg_KiemTraVaTruTonKho: Đã trừ tồn kho.';
END;
GO