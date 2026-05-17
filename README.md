# Fashion Website

Website ban hang cho local brand thoi trang, xay dung bang Django va Django Templates. Du an tap trung vao luong mua hang co ban: xem catalog, xem chi tiet san pham, chon mau/size, them vao gio, checkout, dang nhap va quan tri san pham/don hang.

## Thanh phan chinh

- `backend/`: source Django, model, view, url va business logic
- `frontend/`: template HTML, CSS, JavaScript va static assets
- `database/`: SQLite database, file seed va du lieu dong bo san pham
- `scripts/`: script chay local va smoke test

## Cong nghe

- Python
- Django
- SQLite
- HTML, CSS, JavaScript

## Cai dat

Yeu cau:

- Python 3
- `pip`

Tao moi truong ao va cai dependency:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Chay du an

Cach nhanh nhat:

```powershell
.\scripts\run_local.ps1
```

Script nay se:

1. Kiem tra cau hinh Django
2. Chay `migrate`
3. Dong bo du lieu san pham bang `python manage.py seed_products --sync`
4. Mo trinh duyet tai `http://localhost:8000/`
5. Chay Django development server

Neu muon bo qua migrate hoac seed:

```powershell
.\scripts\run_local.ps1 -SkipMigrate
.\scripts\run_local.ps1 -SkipSeed
```

Neu muon doi cong:

```powershell
.\scripts\run_local.ps1 -Port 9000
```

## Chay thu cong

Neu khong dung script:

```powershell
.venv\Scripts\Activate.ps1
cd backend
python manage.py migrate
python manage.py seed_products --sync
python manage.py runserver
```

## Du lieu anh san pham

- Anh cover va anh chi tiet local nam trong `frontend/static/images/products/`
- Gallery chi tiet tren trang san pham uu tien anh detail (`detail-1`, `detail-2`)
- Neu can tao lai artwork local cho toan bo san pham:

```powershell
cd backend
python manage.py generate_product_artwork
```

## Tai khoan va tinh nang

- Khach co the xem danh sach san pham, loc, tim kiem va xem chi tiet
- San pham ao/quan co chon mau, size va ton kho theo bien the
- Co wishlist, gio hang, checkout, theo doi don hang
- Staff co trang dashboard de them/sua/xoa san pham va quan ly don

## Test

Chay test Django:

```powershell
cd backend
python manage.py test
```
