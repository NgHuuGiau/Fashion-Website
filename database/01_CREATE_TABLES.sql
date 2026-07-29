-- ============================================================
-- HUUGIAU Fashion - CREATE TABLES (10 bang don gian)
-- Open in SSMS and press F5
-- ============================================================

IF DB_ID('HUUGIAU_Fashion') IS NULL
    CREATE DATABASE [HUUGIAU_Fashion];
GO

USE [HUUGIAU_Fashion];
GO

-- Tài khoản người dùng
DROP TABLE IF EXISTS [Users];
CREATE TABLE [Users] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [username] NVARCHAR(150) NOT NULL,
    [email] NVARCHAR(254) NOT NULL,
    [password] NVARCHAR(128) NOT NULL,
    [role] INT NOT NULL DEFAULT 2,  -- 0=admin, 1=staff, 2=user
    [is_active] BIT NOT NULL DEFAULT 1,
    [date_joined] DATETIME2 NOT NULL,
    [phone] NVARCHAR(20) NOT NULL DEFAULT ''
);
GO

-- Danh mục sản phẩm
DROP TABLE IF EXISTS [Categories];
CREATE TABLE [Categories] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [name] NVARCHAR(100) NOT NULL,
    [slug] NVARCHAR(100) NOT NULL
);
GO

-- Sản phẩm
DROP TABLE IF EXISTS [Products];
CREATE TABLE [Products] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [name] NVARCHAR(200) NOT NULL,
    [slug] NVARCHAR(200) NOT NULL,
    [category_id] INT REFERENCES Categories(id),
    [price] INT NOT NULL,
    [stock] INT NOT NULL DEFAULT 0,
    [available] BIT NOT NULL DEFAULT 1,
    [featured] BIT NOT NULL DEFAULT 0,
    [image_url] NVARCHAR(500) NOT NULL DEFAULT '',
    [created] DATETIME2 NOT NULL
);
GO

-- Biến thể sản phẩm (màu sắc, kích cỡ)
DROP TABLE IF EXISTS [Variants];
CREATE TABLE [Variants] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [product_id] INT NOT NULL REFERENCES Products(id),
    [color_name] NVARCHAR(50) NOT NULL DEFAULT '',
    [color_code] NVARCHAR(20) NOT NULL DEFAULT '#111111',
    [size] NVARCHAR(20) NOT NULL DEFAULT '',
    [stock] INT NOT NULL DEFAULT 0,
    [is_active] BIT NOT NULL DEFAULT 1
);
GO

-- Mã giảm giá
DROP TABLE IF EXISTS [Coupons];
CREATE TABLE [Coupons] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [code] NVARCHAR(30) NOT NULL,
    [type] NVARCHAR(20) NOT NULL DEFAULT 'percent',
    [value] INT NOT NULL DEFAULT 0,
    [is_active] BIT NOT NULL DEFAULT 1,
    [min_amount] INT NOT NULL DEFAULT 0,
    [max_amount] INT NULL,
    [max_uses] INT NULL,
    [used_count] INT NOT NULL DEFAULT 0
);
GO

-- Đơn hàng
DROP TABLE IF EXISTS [Orders];
CREATE TABLE [Orders] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NULL REFERENCES Users(id),
    [customer_name] NVARCHAR(150) NOT NULL,
    [phone] NVARCHAR(20) NOT NULL,
    [shipping_address] NVARCHAR(MAX) NOT NULL,
    [status] NVARCHAR(20) NOT NULL DEFAULT 'pending',
    [total_amount] INT NOT NULL DEFAULT 0,
    [is_paid] BIT NOT NULL DEFAULT 0,
    [payment_method] NVARCHAR(20) NOT NULL DEFAULT 'cod',
    [discount_amount] INT NOT NULL DEFAULT 0,
    [coupon] NVARCHAR(30) NOT NULL DEFAULT '',
    [created_at] DATETIME2 NOT NULL
);
GO

-- Chi tiết đơn hàng
DROP TABLE IF EXISTS [OrderItems];
CREATE TABLE [OrderItems] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [order_id] INT NOT NULL REFERENCES Orders(id),
    [product_id] INT NOT NULL REFERENCES Products(id),
    [variant_id] INT NULL REFERENCES Variants(id),
    [color] NVARCHAR(50) NOT NULL DEFAULT '',
    [size] NVARCHAR(20) NOT NULL DEFAULT '',
    [quantity] INT NOT NULL DEFAULT 1,
    [price] INT NOT NULL
);
GO

-- Sản phẩm yêu thích
DROP TABLE IF EXISTS [Wishlist];
CREATE TABLE [Wishlist] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NOT NULL REFERENCES Users(id),
    [product_id] INT NOT NULL REFERENCES Products(id),
    [created] DATETIME2 NOT NULL
);
GO

-- Câu hỏi thường gặp
DROP TABLE IF EXISTS [FAQs];
CREATE TABLE [FAQs] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [question] NVARCHAR(255) NOT NULL,
    [answer] NVARCHAR(MAX) NOT NULL,
    [priority] INT NOT NULL DEFAULT 100,
    [is_active] BIT NOT NULL DEFAULT 1
);
GO

-- Lịch sử hoạt động
DROP TABLE IF EXISTS [Activities];
CREATE TABLE [Activities] (
    [id] INT IDENTITY(1,1) PRIMARY KEY,
    [user_id] INT NULL REFERENCES Users(id),
    [event] NVARCHAR(20) NOT NULL DEFAULT 'page_view',
    [path] NVARCHAR(255) NOT NULL DEFAULT '',
    [created_at] DATETIME2 NOT NULL
);
GO

