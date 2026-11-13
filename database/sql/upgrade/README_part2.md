## Tính năng chính

| Thành phần | Mô tả | File |
|------------|-------|------|
| **Trigger tồn kho** | Tự động kiểm tra & trừ stock khi insert order_item | `03a_trigger_stock.sql` |
| **Trigger hoàn kho** | Tự động hoàn stock/voucher khi hủy/hoàn đơn | `03b_trigger_restore.sql` |
| **Trigger bảo vệ** | Chặn xóa/sửa đơn `done/shipping/cancelled/refunded` | `03c_trigger_protect.sql` |
| **Trigger refund** | Đồng bộ order `refunded` khi duyệt hoàn tiền | `03d_trigger_refund_sync.sql` |
| **SP tạo đơn atomic** | Transaction an toàn với Savepoint, TRY/CATCH | `04a_sp_create_order.sql` |
| **SP hủy/hoàn tiền** | Xử lý nghiệp vụ an toàn | `04b_sp_cancel_refund.sql` |
| **SP báo cáo** | Doanh thu tháng, top sản phẩm | `04c_sp_reports.sql` |
| **Cursor VIP** | Phân hạng khách hàng, tặng voucher tự động | `05_cursors.sql` |
| **Cursor quét đơn** | Tự động hủy đơn pending quá hạn | `05_cursors.sql` |
| **Views báo cáo** | Doanh thu tháng, sản phẩm, khách hàng | `06_views_functions.sql` |
| **UDF giảm giá** | Tính voucher percent/fixed/free_shipping | `06_views_functions.sql` |

## Tích hợp với Django

### 1. Sequence cho order_code
```python
# Trong Django model OrdersOrder.save()
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT NEXT VALUE FOR dbo.seq_order_code")
    seq = cursor.fetchone()[0]
    self.order_code = f"ORD-{timezone.now().strftime('%Y%m%d')}{seq:05d}"
```

### 2. Gọi SP tạo đơn hàng
```python
from django.db import connection

def create_order_atomic(...):
    with connection.cursor() as cursor:
        cursor.execute("""
            DECLARE @OrderCode NVARCHAR(32), @OrderID BIGINT;
            EXEC dbo.sp_TaoDonHangAnToan
                @UserID = %s, @CustomerName = %s, @Email = %s, @Phone = %s,
                @Address = %s, @PaymentMethod = %s, @Items = %s,
                @OrderCode = @OrderCode OUTPUT, @OrderID = @OrderID OUTPUT;
            SELECT @OrderCode, @OrderID;
        """, [user_id, name, email, phone, address, payment_method, items_json])
        return cursor.fetchone()
```

### 3. Sử dụng Views cho báo cáo
```python
from django.db import connection


def get_monthly_revenue():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM dbo.v_BaoCaoDoanhThuTheoThang")
        return cursor.fetchall()
```

### 4. Function tính voucher
```python
def calculate_discount(coupon_code, subtotal):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT dbo.fn_TinhGiamGiaVoucher(%s, %s)", [coupon_code, subtotal]
        )
        return cursor.fetchone()[0]
```

## Lưu ý quan trọng

1. **Backup database trước khi chạy** master_setup.sql
2. **Test trên staging** trước khi deploy production
3. **Trigger sẽ override Django logic** cho:
   - Trừ tồn kho (trigger tự xử lý, Django không cần trừ)
   - Hoàn kho khi hủy (trigger tự xử lý)
   - Bảo vệ đơn closed (trigger chặn ở DB level)
4. **Voucher usage** được trigger quản lý tự động qua `orders_couponredemption`
5. **Sequence** `seq_order_code` cần tạo trước khi dùng

## Test Coverage

Test suite kiểm tra:
- Trigger chặn đặt quá tồn kho
- Trigger trừ tồn kho khi đủ hàng
- Trigger hoàn kho/voucher khi hủy/hoàn
- Trigger chặn xóa/sửa đơn closed
- Trigger đồng bộ refund
- SP tạo đơn atomic
- SP hủy đơn, duyệt hoàn tiền
- Views báo cáo trả về dữ liệu
- Function tính voucher
- Cursor quét đơn quá hạn