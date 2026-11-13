-- Part 2: sp_HuyDonHang, sp_XuLyHoanTien
CREATE OR ALTER PROCEDURE dbo.sp_HuyDonHang
    @OrderID BIGINT, @ActorID BIGINT = NULL, @Reason NVARCHAR(255) = NULL
AS BEGIN SET NOCOUNT ON; BEGIN TRY
    UPDATE dbo.orders_order SET status='cancelled', updated_at=SYSUTCDATETIME()
    WHERE id=@OrderID AND status IN ('pending','confirmed');
    IF @@ROWCOUNT=0 THROW 50003, N'Không thể hủy đơn ở trạng thái này.', 1;
    INSERT INTO dbo.orders_orderstatushistory (order_id,from_status,to_status,source,actor_id,note,created_at)
    SELECT id,status,'cancelled','customer',@ActorID,@Reason,SYSUTCDATETIME()
    FROM dbo.orders_order WHERE id=@OrderID; RETURN 0;
END TRY BEGIN CATCH DECLARE @Msg NVARCHAR(4000)=ERROR_MESSAGE(); RAISERROR(@Msg,16,1); RETURN -1; END CATCH END; GO

CREATE OR ALTER PROCEDURE dbo.sp_XuLyHoanTien
    @RequestID NVARCHAR(32), @Action NVARCHAR(10), @ActorID BIGINT, @Note NVARCHAR(255) = NULL
AS BEGIN SET NOCOUNT ON; DECLARE @OrderID BIGINT, @Amt DECIMAL(12,2), @CurStatus NVARCHAR(12); BEGIN TRY
    SELECT @OrderID=order_id, @Amt=amount, @CurStatus=status FROM dbo.orders_refundrecord WHERE request_id=@RequestID;
    IF @CurStatus<>'pending' THROW 50004, N'Yêu cầu đã xử lý.', 1;
    IF @Action='approve' UPDATE dbo.orders_refundrecord SET status='approved', updated_at=SYSUTCDATETIME() WHERE request_id=@RequestID;
    ELSE IF @Action='reject' UPDATE dbo.orders_refundrecord SET status='rejected', updated_at=SYSUTCDATETIME() WHERE request_id=@RequestID;
    ELSE THROW 50005, N'Hành động không hợp lệ.', 1;
    INSERT INTO dbo.orders_orderstatushistory (order_id,from_status,to_status,source,actor_id,note,created_at)
    VALUES (@OrderID,'refunded',@Action,'staff',@ActorID,@Note,SYSUTCDATETIME()); RETURN 0;
END TRY BEGIN CATCH DECLARE @Msg NVARCHAR(4000)=ERROR_MESSAGE(); RAISERROR(@Msg,16,1); RETURN -1; END CATCH END; GO