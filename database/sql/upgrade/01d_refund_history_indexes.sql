-- Part 4: Refund, Status History, Indexes
-- BẢNG: orders_refundrecord
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'orders_refundrecord' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.orders_refundrecord (
        id BIGINT IDENTITY(1,1) NOT NULL,
        request_id NVARCHAR(32) NOT NULL,
        order_id BIGINT NOT NULL,
        requested_by_id BIGINT NULL,
        amount DECIMAL(12,2) NOT NULL,
        reason NVARCHAR(255) NOT NULL,
        status NVARCHAR(12) NOT NULL DEFAULT 'pending',
        gateway_code NVARCHAR(20) NULL,
        gateway_response NVARCHAR(MAX) NULL,
        created_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_orders_refundrecord PRIMARY KEY CLUSTERED (id),
        CONSTRAINT UQ_orders_refundrecord_request_id UNIQUE (request_id),
        CONSTRAINT FK_orders_refundrecord_order FOREIGN KEY (order_id) REFERENCES dbo.orders_order (id) ON DELETE CASCADE,
        CONSTRAINT FK_orders_refundrecord_user FOREIGN KEY (requested_by_id) REFERENCES dbo.auth_user (id) ON DELETE SET NULL,
        CONSTRAINT CK_orders_refundrecord_amount CHECK (amount > 0),
        CONSTRAINT CK_orders_refundrecord_status CHECK (status IN ('pending','approved','rejected','succeeded','failed'))
    );
END
GO

-- BẢNG: orders_orderstatushistory
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'orders_orderstatushistory' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.orders_orderstatushistory (
        id BIGINT IDENTITY(1,1) NOT NULL,
        order_id BIGINT NOT NULL,
        from_status NVARCHAR(20) NULL,
        to_status NVARCHAR(20) NOT NULL,
        source NVARCHAR(32) NOT NULL DEFAULT 'system',
        actor_id BIGINT NULL,
        transaction_id NVARCHAR(64) NULL,
        note NVARCHAR(255) NULL,
        created_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_orders_orderstatushistory PRIMARY KEY CLUSTERED (id),
        CONSTRAINT FK_orders_orderstatushistory_order FOREIGN KEY (order_id) REFERENCES dbo.orders_order (id) ON DELETE CASCADE,
        CONSTRAINT FK_orders_orderstatushistory_actor FOREIGN KEY (actor_id) REFERENCES dbo.auth_user (id) ON DELETE SET NULL
    );
END
GO

-- INDEXES
CREATE NONCLUSTERED INDEX IX_orders_order_user_created ON dbo.orders_order (user_id, created_at DESC);
CREATE NONCLUSTERED INDEX IX_orders_order_status_created ON dbo.orders_order (status, created_at DESC);
CREATE NONCLUSTERED INDEX IX_orders_order_payment_method ON dbo.orders_order (payment_method);
CREATE NONCLUSTERED INDEX IX_orders_orderitem_order ON dbo.orders_orderitem (order_id);
CREATE NONCLUSTERED INDEX IX_orders_orderitem_variant ON dbo.orders_orderitem (variant_id);
CREATE NONCLUSTERED INDEX IX_products_productvariant_product ON dbo.products_productvariant (product_id);
CREATE NONCLUSTERED INDEX IX_orders_coupon_code_active ON dbo.orders_coupon (code) WHERE is_active = 1;
CREATE NONCLUSTERED INDEX IX_orders_refundrecord_order ON dbo.orders_refundrecord (order_id);
CREATE NONCLUSTERED INDEX IX_orders_refundrecord_status ON dbo.orders_refundrecord (status);

PRINT N'=== HOÀN TẤT TẠO BẢNG VÀ INDEX ===';