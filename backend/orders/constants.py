import os
from decimal import Decimal


SHOP_BANK_ACCOUNT = os.getenv("SHOP_BANK_ACCOUNT", "1234567890")
SHOP_ACCOUNT_NAME = os.getenv("SHOP_ACCOUNT_NAME", "HUUGIAU LOCAL BRAND")
PAYMENT_TIMEOUT_MINUTES = 15
STANDARD_SHIPPING_FEE = Decimal("30000")
FREESHIP_THRESHOLD = Decimal("499000")

# Phí giao nội thành (HCM + vùng phụ cận) rẻ hơn, miền Bắc xa hơn.
SHIPPING_FEE_ZONES = {
    "near": Decimal("25000"),
    "standard": Decimal("30000"),
    "north": Decimal("35000"),
}
TIER_DISCOUNTS = {
    "VIP": 5,
    "Thân thiết": 3,
    "Thành viên": 0,
}

HCMC_KEYWORDS = (
    "ho chi minh",
    "hcm",
    "tp hcm",
    "tphcm",
    "sai gon",
    "quan 1",
    "quan 2",
    "quan 3",
    "quan 4",
    "quan 5",
    "quan 6",
    "quan 7",
    "quan 8",
    "quan 9",
    "quan 10",
    "quan 11",
    "quan 12",
    "thu duc",
    "go vap",
    "binh thanh",
    "tan binh",
    "tan phu",
    "phu nhuan",
    "binh tan",
)
NEAR_HCMC_KEYWORDS = (
    "binh duong",
    "dong nai",
    "tay ninh",
    "ba ria",
    "vung tau",
    "long an",
    "tien giang",
    "ben tre",
)
NORTHERN_KEYWORDS = (
    "ha noi",
    "hanoi",
    "hai phong",
    "bac ninh",
    "hung yen",
    "hai duong",
    "vinh phuc",
    "bac giang",
    "thai nguyen",
    "quang ninh",
    "son la",
    "hue",
    "da nang",
    "nha trang",
    "viet tri",
    "thai binh",
    "nam dinh",
    "ninh binh",
    "thanh hoa",
    "nghe an",
    "ha tinh",
)

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

BANK_CHOICES = [("", "-- Chọn ngân hàng --")] + [
    (code, meta["name"]) for code, meta in BANKS.items()
]
