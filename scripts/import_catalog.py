#!/usr/bin/env python3
"""
Import catalog from CSV/Excel to local_products_to_sync.json format.
Usage: python scripts/import_catalog.py --input catalog.xlsx --output database/seed/local_products_to_sync.json
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Cần cài pandas: pip install pandas openpyxl")
    sys.exit(1)

REQUIRED_COLUMNS = {
    'name': 'Tên sản phẩm',
    'slug': 'Slug (URL friendly)',
    'category': 'Danh mục (Áo/Quần/Phụ kiện...)',
    'price': 'Giá bán (VNĐ)',
    'color': 'Màu sắc',
    'size': 'Kích cỡ (S/M/L/XL...)',
    'stock': 'Tồn kho',
    'description': 'Mô tả',
    'is_active': 'Active (True/False)',
}

OPTIONAL_COLUMNS = {
    'compare_at_price': 'Giá so sánh (giá cũ)',
    'sku': 'SKU/Mã sản phẩm',
    'brand': 'Thương hiệu',
    'tags': 'Tags (phân cách bằng dấu phẩy)',
    'image_url': 'URL ảnh chính',
    'gallery_urls': 'URL ảnh gallery (phân cách bằng dấu phẩy)',
}