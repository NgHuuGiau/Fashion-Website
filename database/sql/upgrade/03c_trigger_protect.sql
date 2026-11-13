-- Part 3: Protect closed orders
CREATE OR ALTER TRIGGER dbo.trg_ChongSuaXoaDonHangDaDong
ON dbo.orders_order
INSTEAD OF DELETE, UPDATE
AS
BEGIN SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM inserted) AND EXISTS (SELECT 1 FROM deleted)
    BEGIN
        IF EXISTS (SELECT 1 FROM deleted WHERE status IN ('done','shipping','cancelled','refunded'))
        BEGIN
            RAISERROR(N'Không thể xóa đơn hàng đã giao/đang giao/đã hủy/đã hoàn.', 16, 1);
            ROLLBACK TRANSACTION; RETURN;
        END
        DELETE FROM dbo.orders_order WHERE id IN (SELECT id FROM deleted); RETURN;
    END

    IF EXISTS (SELECT 1 FROM inserted) AND EXISTS (SELECT 1 FROM deleted)
    BEGIN
        IF EXISTS (
            SELECT 1 FROM inserted i JOIN deleted d ON i.id=d.id
            WHERE d.status IN ('done','shipping','cancelled','refunded') AND i.status <> d.status
        )
        BEGIN
            RAISERROR(N'Đơn hàng ở trạng thái kết thúc, không thể đổi trạng thái.', 16, 1);
            ROLLBACK TRANSACTION; RETURN;
        END

        UPDATE o SET o.status=i.status, o.is_paid=i.is_paid, o.tracking_code=i.tracking_code,
            o.carrier=i.carrier, o.delivered_at=i.delivered_at, o.refunded_amount=i.refunded_amount,
            o.gateway_transaction_id=i.gateway_transaction_id, o.vnpay_transaction_id=i.vnpay_transaction_id,
            o.updated_at=SYSUTCDATETIME()
        FROM dbo.orders_order o JOIN inserted i ON o.id=i.id;
    END
END;
GO