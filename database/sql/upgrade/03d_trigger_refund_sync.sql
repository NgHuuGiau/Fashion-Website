-- Part 4: Refund sync + Status history
CREATE OR ALTER TRIGGER dbo.trg_DongBoThanhToanKhiHoanTien
ON dbo.orders_refundrecord
AFTER UPDATE
AS BEGIN SET NOCOUNT ON;
    IF UPDATE(status)
    BEGIN
        UPDATE o SET o.status='refunded', o.is_paid=0, o.refunded_amount=i.amount, o.updated_at=SYSUTCDATETIME()
        FROM dbo.orders_order o JOIN inserted i ON o.id=i.order_id JOIN deleted d ON i.id=d.id
        WHERE i.status='succeeded' AND d.status<>'succeeded';
        PRINT N'Trigger trg_DongBoThanhToanKhiHoanTien: Đồng bộ refunded.';
    END
END;
GO

CREATE OR ALTER TRIGGER dbo.trg_GhiLichSuTrangThaiDonHang
ON dbo.orders_order
AFTER UPDATE
AS BEGIN SET NOCOUNT ON;
    IF UPDATE(status)
    BEGIN
        INSERT INTO dbo.orders_orderstatushistory (order_id,from_status,to_status,source,actor_id,transaction_id,note,created_at)
        SELECT i.id, d.status, i.status,
            CASE WHEN i.status='cancelled' THEN 'customer' WHEN i.status='refunded' THEN 'system'
                 WHEN i.status IN ('confirmed','shipping','done') THEN 'staff' ELSE 'system' END,
            NULL, i.gateway_transaction_id,
            CASE WHEN i.status='cancelled' THEN N'Khách hủy' WHEN i.status='refunded' THEN N'Hoàn tiền'
                 ELSE N'Cập nhật trạng thái' END,
            SYSUTCDATETIME()
        FROM inserted i JOIN deleted d ON i.id=d.id WHERE i.status<>d.status;
    END
END;
GO

PRINT N'=== HOÀN TẤT TẤT CẢ TRIGGERS ===';