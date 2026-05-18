from decimal import Decimal


SHOP_BANK_ACCOUNT = "1234567890"
SHOP_ACCOUNT_NAME = "HUUGIAU LOCAL BRAND"
PAYMENT_TIMEOUT_MINUTES = 15
STANDARD_SHIPPING_FEE = Decimal("30000")
FREESHIP_THRESHOLD = Decimal("499000")

BANKS = {
    "VCB": {"name": "Vietcombank", "bin": "970436"},
    "TCB": {"name": "Techcombank", "bin": "970407"},
    "MB": {"name": "MBBank", "bin": "970422"},
    "ACB": {"name": "ACB", "bin": "970416"},
    "BIDV": {"name": "BIDV", "bin": "970418"},
    "VPB": {"name": "VPBank", "bin": "970432"},
}

BANK_CHOICES = [("", "-- Chọn ngân hàng --")] + [(code, meta["name"]) for code, meta in BANKS.items()]
