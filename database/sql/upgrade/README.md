# Fashion-Website T-SQL Suite Upgrade

Bộ nâng cấp T-SQL chuyên sâu cho Fashion-Website, chuyển từ application-level logic sang database-level guarantees (ACID).

## Cấu trúc file

```
database/sql/upgrade/
├── master_setup.sql                 # Script chính chạy tất cả
├── 01_ddl_core_tables.sql           # Core tables
├── 01b_orders_order.sql             # Orders table
├── 01c_orders_orderitem.sql         # Order items, coupons, refunds
├── 01d_refund_history_indexes.sql   # Refund, status history, indexes
├── 03a_trigger_stock.sql            # Trigger: Kiểm tra & trừ tồn kho
├── 03b_trigger_restore.sql          # Trigger: Hoàn kho khi hủy/hoàn
├── 03c_trigger_protect.sql          # Trigger: Chặn sửa/xóa đơn closed
├── 03d_trigger_refund_sync.sql      # Trigger: Đồng bộ refund + lịch sử
├── 04a_sp_create_order.sql          # SP: Tạo đơn hàng atomic
├── 04b_sp_cancel_refund.sql         # SP: Hủy đơn, xử lý hoàn tiền
├── 04c_sp_reports.sql               # SP: Báo cáo doanh thu, top SP
├── 05_cursors.sql                   # Cursor: VIP tier, quét đơn quá hạn
├── 06_views_functions.sql           # Views & UDFs báo cáo
├── 07_transactions_concurrency.sql  # Demo: Savepoint, Lock hints
├── 08_seed_data.sql                 # Voucher mẫu, sequence
├── test_all_part1.sql               # Test triggers 1-3
├── test_all_part2.sql               # Test triggers 4-6, SPs
├── test_all_part3.sql               # Test views, functions, cursor
└── README.md                        # File này
```

## Cách cài đặt

### Yêu cầu
- SQL Server 2022 (hoặc 2019+)
- Database `HUUGIAU_Fashion` đã tồn tại
- Quyền `db_owner` hoặc `sysadmin`

### Chạy master setup
```bash
sqlcmd -S localhost -U sa -P "YourStrongPassword" -d HUUGIAU_Fashion -i database\sql\upgrade\master_setup.sql
```

### Chạy test suite
```bash
sqlcmd -S localhost -U sa -P "YourStrongPassword" -d HUUGIAU_Fashion -i database\sql\upgrade\test_all_part1.sql
sqlcmd -S localhost -U sa -P "YourStrongPassword" -d HUUGIAU_Fashion -i database\sql\upgrade\test_all_part2.sql
sqlcmd -S localhost -U sa -P "YourStrongPassword" -d HUUGIAU_Fashion -i database\sql\upgrade\test_all_part3.sql
```