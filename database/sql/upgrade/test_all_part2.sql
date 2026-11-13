-- Part 2: Triggers 4-6, SPs
DECLARE @OID4 BIGINT, @OID5 BIGINT, @OID6 BIGINT, @RefundID BIGINT, @OrderStatus NVARCHAR(20), @IsPaid BIT, @St NVARCHAR(20), @Rs NVARCHAR(12), @RowCount INT, @Disc DECIMAL(12,2);

-- TEST 4: Trigger chặn xóa đơn done
SET @TestName=N'Trigger: Chặn xóa đơn done';
BEGIN TRY BEGIN TRANSACTION;
    INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,payment_method,status,total_amount,created_at,updated_at)
    VALUES ('TEST-004',N'Test4','test4@test.com','0123456789',N'Addr','cod','done',100000,SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @OID4=SCOPE_IDENTITY(); DELETE FROM dbo.orders_order WHERE id=@OID4;
    SET @Result=0; COMMIT TRANSACTION;
END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION;
    IF ERROR_MESSAGE() LIKE N'%Không thể xóa%' SET @Result=1 ELSE SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 5: Trigger chặn đổi trạng thái done
SET @TestName=N'Trigger: Chặn đổi trạng thái done';
BEGIN TRY BEGIN TRANSACTION;
    INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,payment_method,status,total_amount,created_at,updated_at)
    VALUES ('TEST-005',N'Test5','test5@test.com','0123456789',N'Addr','cod','done',100000,SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @OID5=SCOPE_IDENTITY(); UPDATE dbo.orders_order SET status='shipping' WHERE id=@OID5;
    SET @Result=0; COMMIT TRANSACTION;
END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION;
    IF ERROR_MESSAGE() LIKE N'%không thể thay đổi trạng thái%' SET @Result=1 ELSE SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 6: Trigger đồng bộ refund
SET @TestName=N'Trigger: Đồng bộ refunded khi duyệt hoàn tiền';
BEGIN TRY BEGIN TRANSACTION;
    INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,payment_method,status,is_paid,total_amount,created_at,updated_at)
    VALUES ('TEST-006',N'Test6','test6@test.com','0123456789',N'Addr','vnpay','done',1,100000,SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @OID6=SCOPE_IDENTITY();
    INSERT INTO dbo.orders_refundrecord (request_id,order_id,amount,reason,status,created_at,updated_at)
    VALUES ('REF-TEST-001',@OID6,100000,N'Test refund','pending',SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @RefundID=SCOPE_IDENTITY();
    UPDATE dbo.orders_refundrecord SET status='succeeded' WHERE id=@RefundID;
    SELECT @OrderStatus=status,@IsPaid=is_paid FROM dbo.orders_order WHERE id=@OID6;
    IF @OrderStatus='refunded' AND @IsPaid=0 SET @Result=1 ELSE SET @Result=0; COMMIT TRANSACTION;
END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION; SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 7: SP sp_TaoDonHangAnToan
SET @TestName=N'SP: sp_TaoDonHangAnToan';
DECLARE @OutCode NVARCHAR(32), @OutID BIGINT;
BEGIN TRY
    EXEC @Result = dbo.sp_TaoDonHangAnToan @UserID=NULL,@CustomerName=N'SP Test',@Email='sp@test.com',@Phone='0987654321',
        @Address=N'SP Address',@PaymentMethod='cod',@Items=N'[]',@OrderCode=@OutCode OUTPUT,@OrderID=@OutID OUTPUT;
    IF @Result=0 AND @OutID IS NOT NULL SET @Result=1 ELSE SET @Result=0;
END TRY BEGIN CATCH SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 8: SP sp_HuyDonHang
SET @TestName=N'SP: sp_HuyDonHang';
DECLARE @OID7 BIGINT;
BEGIN TRY
    INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,payment_method,status,total_amount,created_at,updated_at)
    VALUES ('TEST-007',N'SP Cancel',N'sp@cancel.com','0111111111',N'Addr','cod','pending',50000,SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @OID7=SCOPE_IDENTITY(); EXEC @Result = dbo.sp_HuyDonHang @OrderID=@OID7,@Reason=N'Test cancel';
    SELECT @St=status FROM dbo.orders_order WHERE id=@OID7;
    IF @Result=0 AND @St='cancelled' SET @Result=1 ELSE SET @Result=0;
END TRY BEGIN CATCH SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 9: SP sp_XuLyHoanTien
SET @TestName=N'SP: sp_XuLyHoanTien duyệt refund';
DECLARE @OID8 BIGINT;
BEGIN TRY
    INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,payment_method,status,is_paid,total_amount,created_at,updated_at)
    VALUES ('TEST-008',N'SP Refund',N'sp@refund.com','0222222222',N'Addr','vnpay','done',1,200000,SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @OID8=SCOPE_IDENTITY();
    INSERT INTO dbo.orders_refundrecord (request_id,order_id,amount,reason,status,created_at,updated_at)
    VALUES ('REF-TEST-002',@OID8,200000,N'SP test','pending',SYSUTCDATETIME(),SYSUTCDATETIME());
    EXEC @Result = dbo.sp_XuLyHoanTien @RequestID='REF-TEST-002',@Action='approve',@ActorID=1;
    SELECT @Rs=status FROM dbo.orders_refundrecord WHERE request_id='REF-TEST-002';
    IF @Result=0 AND @Rs='approved' SET @Result=1 ELSE SET @Result=0;
END TRY BEGIN CATCH SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;