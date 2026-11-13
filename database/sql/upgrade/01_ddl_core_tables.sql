-- ============================================================================
-- FASHION-WEBSITE - HỆ QUẢN TRỊ CƠ SỞ DỮ LIỆU (SQL SERVER 2022)
-- File: 01_ddl_core_tables.sql
-- Mục đích: Cấu trúc bảng nghiệp vụ cốt lõi, PK, FK, Constraints, Index
-- ============================================================================

USE [HUUGIAU_Fashion];
GO

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

PRINT N'=== BẮT ĐẦU TẠO BẢNG NGHIỆP VỤ ===';

-- -----------------------------------------------------------------------------
-- BẢNG: products_product (Sản phẩm)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'products_product' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.products_product (
        id                  BIGINT IDENTITY(1,1) NOT NULL,
        name                NVARCHAR(255) NOT NULL,
        slug                NVARCHAR(255) NOT NULL,
        description         NVARCHAR(MAX) NULL,
        short_description   NVARCHAR(MAX) NULL,
        base_price          DECIMAL(12,2) NOT NULL DEFAULT 0,
        sale_price          DECIMAL(12,2) NULL,
        sku                 NVARCHAR(64) NOT NULL,
        barcode             NVARCHAR(64) NULL,
        is_active           BIT NOT NULL DEFAULT 1,
        is_featured         BIT NOT NULL DEFAULT 0,
        category_id         BIGINT NULL,
        brand_id            BIGINT NULL,
        collection_id       BIGINT NULL,
        weight              DECIMAL(8,2) NULL,
        length              DECIMAL(8,2) NULL,
        width               DECIMAL(8,2) NULL,
        height              DECIMAL(8,2) NULL,
        meta_title          NVARCHAR(255) NULL,
        meta_description    NVARCHAR(512) NULL,
        meta_keywords       NVARCHAR(512) NULL,
        created_at          DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at          DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        deleted_at          DATETIME2(3) NULL,
        CONSTRAINT PK_products_product PRIMARY KEY CLUSTERED (id),
        CONSTRAINT UQ_products_product_slug UNIQUE (slug),
        CONSTRAINT UQ_products_product_sku UNIQUE (sku),
        CONSTRAINT CK_products_product_base_price CHECK (base_price >= 0),
        CONSTRAINT CK_products_product_sale_price CHECK (sale_price IS NULL OR sale_price >= 0),
        CONSTRAINT CK_products_product_sale_lt_base CHECK (sale_price IS NULL OR sale_price <= base_price)
    );
    PRINT N'Created: products_product';
END
GO

-- -----------------------------------------------------------------------------
-- BẢNG: products_productvariant (Biến thể sản phẩm - Màu/Size)
-- -----------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'products_productvariant' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.products_productvariant (
        id              BIGINT IDENTITY(1,1) NOT NULL,
        product_id      BIGINT NOT NULL,
        color_name      NVARCHAR(50) NOT NULL,
        color_code      NVARCHAR(20) NULL,
        size            NVARCHAR(20) NOT NULL,
        stock           INT NOT NULL DEFAULT 0,
        is_active       BIT NOT NULL DEFAULT 1,
        height          INT NOT NULL DEFAULT 0,
        length          INT NOT NULL DEFAULT 0,
        weight          INT NOT NULL DEFAULT 0,
        width           INT NOT NULL DEFAULT 0,
        created_at      DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at      DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_products_productvariant PRIMARY KEY CLUSTERED (id),
        CONSTRAINT FK_products_productvariant_product FOREIGN KEY (product_id)
            REFERENCES dbo.products_product (id) ON DELETE CASCADE,
        CONSTRAINT UQ_products_productvariant_product_color_size UNIQUE (product_id, color_name, size),
        CONSTRAINT CK_products_productvariant_stock CHECK (stock >= 0)
    );
    PRINT N'Created: products_productvariant';
END
GO