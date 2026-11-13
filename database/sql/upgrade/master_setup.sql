-- ============================================================================
-- FASHION-WEBSITE - MASTER SETUP SCRIPT
-- File: master_setup.sql
-- Chạy tất cả các file SQL theo thứ tự để cài đặt T-SQL Suite hoàn chỉnh
-- Usage: sqlcmd -S localhost -U sa -P "YourPassword" -d HUUGIAU_Fashion -i master_setup.sql
-- ============================================================================

USE [HUUGIAU_Fashion];
GO

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

PRINT N'============================================================';
PRINT N'=== FASHION-WEBSITE T-SQL SUITE MASTER SETUP ===';
PRINT N'============================================================';
PRINT N'Start time: ' + CONVERT(NVARCHAR, SYSUTCDATETIME(), 121);
PRINT N'';

-- 1. Core Tables
PRINT N'[1/8] Creating core tables...';
:r .\01_ddl_core_tables.sql
:r .\01b_orders_order.sql
:r .\01c_orders_orderitem.sql
:r .\01d_refund_history_indexes.sql
GO

-- 2. Rules & Defaults (if needed - placeholder)
PRINT N'[2/8] Rules & Defaults (placeholder)...';
-- :r .\02_rules_defaults.sql
GO

-- 3. Triggers
PRINT N'[3/8] Installing triggers...';
:r .\03a_trigger_stock.sql
:r .\03b_trigger_restore.sql
:r .\03c_trigger_protect.sql
:r .\03d_trigger_refund_sync.sql
GO

-- 4. Stored Procedures
PRINT N'[4/8] Creating stored procedures...';
:r .\04a_sp_create_order.sql
:r .\04b_sp_cancel_refund.sql
:r .\04c_sp_reports.sql
GO

-- 5. Cursors
PRINT N'[5/8] Creating cursors...';
:r .\05_cursors.sql
GO

-- 6. Views & Functions
PRINT N'[6/8] Creating views & functions...';
:r .\06_views_functions.sql
GO

-- 7. Transactions & Concurrency Demos
PRINT N'[7/8] Installing transaction demos...';
:r .\07_transactions_concurrency.sql
GO

-- 8. Seed Data
PRINT N'[8/8] Seeding initial data...';
:r .\08_seed_data.sql
GO

PRINT N'';
PRINT N'============================================================';
PRINT N'=== MASTER SETUP COMPLETED SUCCESSFULLY ===';
PRINT N'End time: ' + CONVERT(NVARCHAR, SYSUTCDATETIME(), 121);
PRINT N'============================================================';
PRINT N'';
PRINT N'Next step: Run test suite with test_all.sql';