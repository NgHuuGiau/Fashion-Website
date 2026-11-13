-- Part 3: OrderItem, Coupon, Refund
-- BẢNG: orders_orderitem
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'orders_orderitem' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.orders_orderitem (
        id BIGINT IDENTITY(1,1) NOT NULL,
        order_id BIGINT NOT NULL,
        product_id BIGINT NOT NULL,
        variant_id BIGINT NULL,
        product_name NVARCHAR(255) NOT NULL,
        selected_color NVARCHAR(50) NULL,
        selected_size NVARCHAR(20) NULL,
        quantity INT NOT NULL,
        price DECIMAL(12,2) NOT NULL,
        created_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_orders_orderitem PRIMARY KEY CLUSTERED (id),
        CONSTRAINT FK_orders_orderitem_order FOREIGN KEY (order_id) REFERENCES dbo.orders_order (id) ON DELETE CASCADE,
        CONSTRAINT FK_orders_orderitem_product FOREIGN KEY (product_id) REFERENCES dbo.products_product (id) ON DELETE NO ACTION,
        CONSTRAINT FK_orders_orderitem_variant FOREIGN KEY (variant_id) REFERENCES dbo.products_productvariant (id) ON DELETE SET NULL,
        CONSTRAINT CK_orders_orderitem_quantity CHECK (quantity > 0),
        CONSTRAINT CK_orders_orderitem_price CHECK (price >= 0)
    );
END
GO

-- BẢNG: orders_coupon
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'orders_coupon' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.orders_coupon (
        id BIGINT IDENTITY(1,1) NOT NULL,
        code NVARCHAR(30) NOT NULL,
        name NVARCHAR(100) NULL,
        discount_type NVARCHAR(20) NOT NULL,
        value DECIMAL(12,2) NOT NULL DEFAULT 0,
        min_order_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
        max_discount_amount DECIMAL(12,2) NULL,
        is_active BIT NOT NULL DEFAULT 1,
        starts_at DATETIME2(3) NULL,
        ends_at DATETIME2(3) NULL,
        usage_limit INT NULL,
        used_count INT NOT NULL DEFAULT 0,
        max_uses_per_user INT NULL,
        stackable BIT NOT NULL DEFAULT 0,
        trigger_type NVARCHAR(20) NOT NULL DEFAULT 'cart',
        gift_product_id BIGINT NULL,
        created_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        deleted_at DATETIME2(3) NULL,
        CONSTRAINT PK_orders_coupon PRIMARY KEY CLUSTERED (id),
        CONSTRAINT UQ_orders_coupon_code UNIQUE (code),
        CONSTRAINT FK_orders_coupon_gift_product FOREIGN KEY (gift_product_id) REFERENCES dbo.products_product (id) ON DELETE SET NULL,
        CONSTRAINT CK_orders_coupon_value CHECK (value >= 0),
        CONSTRAINT CK_orders_coupon_discount_type CHECK (discount_type IN ('percent','fixed','free_shipping','gift')),
        CONSTRAINT CK_orders_coupon_trigger CHECK (trigger_type IN ('cart','checkout','product'))
    );
END
GO

-- BẢNG: orders_couponredemption
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'orders_couponredemption' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.orders_couponredemption (
        id BIGINT IDENTITY(1,1) NOT NULL,
        coupon_id BIGINT NOT NULL,
        order_id BIGINT NULL,
        user_id BIGINT NULL,
        used_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_orders_couponredemption PRIMARY KEY CLUSTERED (id),
        CONSTRAINT FK_orders_couponredemption_coupon FOREIGN KEY (coupon_id) REFERENCES dbo.orders_coupon (id) ON DELETE CASCADE,
        CONSTRAINT FK_orders_couponredemption_order FOREIGN KEY (order_id) REFERENCES dbo.orders_order (id) ON DELETE SET NULL,
        CONSTRAINT FK_orders_couponredemption_user FOREIGN KEY (user_id) REFERENCES dbo.auth_user (id) ON DELETE SET NULL
    );
END
GO