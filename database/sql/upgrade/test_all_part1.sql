-- Part 1: Test setup and Triggers 1-3
USE [HUUGIAU_Fashion];
GO SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON; GO
SET NOCOUNT ON;
PRINT N'=== FASHION-WEBSITE T-SQL TEST SUITE ===';

DECLARE @TestCount INT=0, @PassCount INT=0, @FailCount INT=0, @Result BIT, @TestName NVARCHAR(200);

-- TEST 1: Trigger chặn đặt quá tồn kho
SET @TestName=N'Trigger: Chặn đặt quá tồn kho';
BEGIN TRY BEGIN TRANSACTION;
    DECLARE @OID BIGINT;
    INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,payment_method,status,total_amount,created_at,updated_at)
    VALUES ('TEST-001',N'Test','test@test.com','0123456789',N'Addr','cod','pending',100000,SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @OID=SCOPE_IDENTITY();
    INSERT INTO dbo.orders_orderitem (order_id,product_id,variant_id,product_name,quantity,price,created_at)
    VALUES (@OID,999999,999999,N'Test',10,10000,SYSUTCDATETIME());
    SET @Result=0; ROLLBACK TRANSACTION;
END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION;
    IF ERROR_MESSAGE() LIKE N'%Lỗi tồn kho%' SET @Result=1 ELSE SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 2: Trigger trừ tồn kho khi đủ hàng
SET @TestName=N'Trigger: Trừ tồn kho khi đủ hàng';
BEGIN TRY BEGIN TRANSACTION;
    DECLARE @VID BIGINT;
    INSERT INTO dbo.products_productvariant (product_id,color_name,size,stock,is_active) VALUES (999999,N'Test',N'M',100,1);
    SET @VID=SCOPE_IDENTITY();
    DECLARE @OID2 BIGINT;
    INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,payment_method,status,total_amount,created_at,updated_at)
    VALUES ('TEST-002',N'Test2','test2@test.com','0123456789',N'Addr','cod','pending',100000,SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @OID2=SCOPE_IDENTITY();
    INSERT INTO dbo.orders_orderitem (order_id,product_id,variant_id,product_name,selected_size,quantity,price,created_at)
    VALUES (@OID2,999999,@VID,N'Test',N'M',5,10000,SYSUTCDATETIME());
    DECLARE @StockAfter INT; SELECT @StockAfter=stock FROM dbo.products_productvariant WHERE id=@VID;
    IF @StockAfter=95 SET @Result=1 ELSE SET @Result=0; COMMIT TRANSACTION;
END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION; SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 3: Trigger hoàn kho khi hủy đơn
SET @TestName=N'Trigger: Hoàn kho khi hủy đơn';
BEGIN TRY BEGIN TRANSACTION;
    DECLARE @VID2 BIGINT;
    INSERT INTO dbo.products_productvariant (product_id,color_name,size,stock,is_active) VALUES (999998,N'Test2',N'L',50,1);
    SET @VID2=SCOPE_IDENTITY();
    DECLARE @OID3 BIGINT;
    INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,payment_method,status,total_amount,created_at,updated_at)
    VALUES ('TEST-003',N'Test3','test3@test.com','0123456789',N'Addr','cod','confirmed',100000,SYSUTCDATETIME(),SYSUTCDATETIME());
    SET @OID3=SCOPE_IDENTITY();
    INSERT INTO dbo.orders_orderitem (order_id,product_id,variant_id,product_name,selected_size,quantity,price,created_at)
    VALUES (@OID3,999998,@VID2,N'Test2',N'L',10,10000,SYSUTCDATETIME());
    UPDATE dbo.orders_order SET status='cancelled' WHERE id=@OID3;
    DECLARE @StockAfter2 INT; SELECT @StockAfter2=stock FROM dbo.products_productvariant WHERE id=@VID2;
    IF @StockAfter2=50 SET @Result=1 ELSE SET @Result=0; COMMIT TRANSACTION;
END TRY BEGIN CATCH IF XACT_STATE()<>0 ROLLBACK TRANSACTION; SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;