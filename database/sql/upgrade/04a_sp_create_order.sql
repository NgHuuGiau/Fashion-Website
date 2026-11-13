-- Part 1: sp_TaoDonHangAnToan
CREATE OR ALTER PROCEDURE dbo.sp_TaoDonHangAnToan
    @UserID BIGINT = NULL, @CustomerName NVARCHAR(150), @Email NVARCHAR(254),
    @Phone NVARCHAR(20), @Address NVARCHAR(MAX), @WardName NVARCHAR(150) = NULL,
    @Note NVARCHAR(MAX) = NULL, @PaymentMethod NVARCHAR(20), @CouponCode NVARCHAR(30) = NULL,
    @PointsUsed INT = 0, @BankCode NVARCHAR(20) = NULL, @GiftWrap BIT = 0, @GiftNote NVARCHAR(255) = NULL,
    @Items NVARCHAR(MAX), @OrderCode NVARCHAR(32) OUTPUT, @OrderID BIGINT OUTPUT
AS BEGIN SET NOCOUNT ON;
    DECLARE @TranName NVARCHAR(32) = N'TaoDonHang_' + CAST(NEWID() AS NVARCHAR(36));
    DECLARE @Subtotal DECIMAL(12,2)=0, @Discount DECIMAL(12,2)=0, @Shipping DECIMAL(12,2)=30000;
    DECLARE @VAT DECIMAL(12,2)=0, @Total DECIMAL(12,2)=0, @CouponID BIGINT=NULL, @PointsEarned INT=0;
    SAVE TRANSACTION @TranName;
    BEGIN TRY
        IF @PaymentMethod NOT IN ('cod','bank_transfer','vnpay','paypal','wallet')
            THROW 50001, N'Phương thức TT không hợp lệ.', 1;
        SET @OrderCode = N'ORD-' + FORMAT(SYSUTCDATETIME(), N'yyyyMMdd') + RIGHT(N'00000'+CAST(NEXT VALUE FOR dbo.seq_order_code AS NVARCHAR(5)),5);
        IF @CouponCode IS NOT NULL AND @CouponCode <> ''
        BEGIN
            SELECT @CouponID=id FROM dbo.orders_coupon WHERE code=@CouponCode AND is_active=1
                AND (starts_at IS NULL OR starts_at<=SYSUTCDATETIME()) AND (ends_at IS NULL OR ends_at>=SYSUTCDATETIME())
                AND (usage_limit IS NULL OR used_count<usage_limit);
            IF @CouponID IS NULL THROW 50002, N'Mã giảm giá không hợp lệ.', 1;
        END
        INSERT INTO dbo.orders_order (order_code,customer_name,customer_email,phone,shipping_address,shipping_ward_name,note,
            payment_method,status,user_id,coupon_id,coupon_code,points_used,bank_code,gift_wrap,gift_note,
            subtotal_amount,discount_amount,shipping_fee,vat_amount,total_amount,created_at,updated_at)
        VALUES (@OrderCode,@CustomerName,@Email,@Phone,@Address,@WardName,@Note,
            @PaymentMethod,'pending',@UserID,@CouponID,@CouponCode,@PointsUsed,@BankCode,@GiftWrap,@GiftNote,
            0,0,@Shipping,0,0,SYSUTCDATETIME(),SYSUTCDATETIME());
        SET @OrderID = SCOPE_IDENTITY();
        -- Insert items from JSON (use OPENJSON in production)
        -- INSERT INTO dbo.orders_orderitem ... FROM OPENJSON(@Items) ...
        SELECT @Subtotal=SUM(quantity*price) FROM dbo.orders_orderitem WHERE order_id=@OrderID;
        IF @CouponID IS NOT NULL BEGIN
            DECLARE @CType NVARCHAR(20), @CVal DECIMAL(12,2), @CMax DECIMAL(12,2);
            SELECT @CType=discount_type, @CVal=value, @CMax=ISNULL(max_discount_amount,0) FROM dbo.orders_coupon WHERE id=@CouponID;
            IF @CType='percent' SET @Discount=ROUND(@Subtotal*@CVal/100,2);
            ELSE IF @CType='fixed' SET @Discount=@CVal;
            IF @CMax>0 AND @Discount>@CMax SET @Discount=@CMax;
            IF @Discount>@Subtotal SET @Discount=@Subtotal;
            UPDATE dbo.orders_coupon SET used_count=used_count+1 WHERE id=@CouponID;
            INSERT INTO dbo.orders_couponredemption (coupon_id,order_id,user_id) VALUES (@CouponID,@OrderID,@UserID);
        END
        SET @VAT=ROUND((@Subtotal-@Discount)*0.10,2); SET @Total=@Subtotal-@Discount+@Shipping+@VAT;
        SET @PointsEarned=FLOOR(@Total/10000);
        UPDATE dbo.orders_order SET subtotal_amount=@Subtotal, discount_amount=@Discount, vat_amount=@VAT,
            total_amount=@Total, points_earned=@PointsEarned, updated_at=SYSUTCDATETIME() WHERE id=@OrderID;
        COMMIT TRANSACTION; RETURN 0;
    END TRY BEGIN CATCH
        ROLLBACK TRANSACTION @TranName; DECLARE @Msg NVARCHAR(4000)=ERROR_MESSAGE();
        RAISERROR(@Msg,16,1); RETURN -1;
    END CATCH
END; GO