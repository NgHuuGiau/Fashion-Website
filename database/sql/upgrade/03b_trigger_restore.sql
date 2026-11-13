-- Part 2: Cancel/Refund Restore Stock
CREATE OR ALTER TRIGGER dbo.trg_HoanKhoKhiHuyDonHang
ON dbo.orders_order
AFTER UPDATE
AS
BEGIN SET NOCOUNT ON;
    IF UPDATE(status) AND EXISTS (
        SELECT 1 FROM inserted i JOIN deleted d ON i.id=d.id
        WHERE i.status IN ('cancelled','refunded') AND d.status NOT IN ('cancelled','refunded')
    )
    BEGIN
        UPDATE pv SET pv.stock = pv.stock + oi.quantity, pv.updated_at = SYSUTCDATETIME()
        FROM dbo.products_productvariant pv
        JOIN dbo.orders_orderitem oi ON pv.id = oi.variant_id
        JOIN inserted i ON oi.order_id = i.id JOIN deleted d ON i.id = d.id
        WHERE i.status IN ('cancelled','refunded') AND d.status NOT IN ('cancelled','refunded')
          AND oi.variant_id IS NOT NULL;

        UPDATE c SET c.used_count = c.used_count - 1, c.updated_at = SYSUTCDATETIME()
        FROM dbo.orders_coupon c JOIN inserted i ON c.id = i.coupon_id JOIN deleted d ON i.id = d.id
        WHERE i.status IN ('cancelled','refunded') AND d.status NOT IN ('cancelled','refunded')
          AND i.coupon_id IS NOT NULL AND c.used_count > 0;

        DELETE cr FROM dbo.orders_couponredemption cr
        JOIN inserted i ON cr.order_id = i.id JOIN deleted d ON i.id = d.id
        WHERE i.status IN ('cancelled','refunded') AND d.status NOT IN ('cancelled','refunded');

        PRINT N'Trigger trg_HoanKhoKhiHuyDonHang: Đã hoàn kho/voucher.';
    END
END;
GO