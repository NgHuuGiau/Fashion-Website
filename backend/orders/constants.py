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
    "VIB": {"name": "VIB", "bin": "970441"},
    "HDB": {"name": "HDBank", "bin": "970437"},
    "OCB": {"name": "OCB", "bin": "970448"},
    "MSB": {"name": "MSB", "bin": "970426"},
    "TPB": {"name": "TPBank", "bin": "970423"},
    "SCB": {"name": "SCB", "bin": "970429"},
    "SHB": {"name": "SHB", "bin": "970443"},
    "LPB": {"name": "LPBank", "bin": "970449"},
    "NAB": {"name": "Nam A Bank", "bin": "970428"},
    "SSB": {"name": "SeABank", "bin": "970440"},
    "EIB": {"name": "Eximbank", "bin": "970431"},
    "STB": {"name": "Sacombank", "bin": "970403"},
    "DAB": {"name": "DongABank", "bin": "970406"},
    "PGB": {"name": "PG Bank", "bin": "970430"},
    "BVB": {"name": "BaoVietBank", "bin": "970438"},
    "ABB": {"name": "ABBANK", "bin": "970425"},
    "KLB": {"name": "KienLongBank", "bin": "970452"},
}

BANK_CHOICES = [("", "-- Chọn ngân hàng --")] + [(code, meta["name"]) for code, meta in BANKS.items()]
