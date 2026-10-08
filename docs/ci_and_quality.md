# CI pipeline và quality gate

Workflow chính: `.github/workflows/ci.yml` (chạy trên mọi push/PR vào `main`, `develop`).

## Các job (phải xanh hết mới merge)

| Job | Công cụ | Ghi chú |
|---|---|---|
| Lint | Ruff check + format | `backend/`, fail khi vi phạm |
| Type check | Mypy | Fail khi lỗi type |
| Security | Bandit (SAST) + pip-audit (deps) | Fail khi có findings |
| Tests | pytest `-n auto` trên PostgreSQL, Python 3.10–3.13, Django 5.2 | Bỏ `tests/stress`, `tests/performance` |
| Frontend lint | ESLint + Stylelint | `frontend/` |
| Frontend E2E | Playwright chromium + Mobile Chrome | Seed demo + user `testuser` |
| Build | `check --deploy`, collectstatic, compress offline | Bắt lỗi cấu hình prod |
| CodeQL | Workflow riêng (`codeql.yml`) | Python + JavaScript |
| Release | Workflow riêng (`release.yml`) | Đóng gói bản phát hành, chạy trên `main` |
| Auto-assign PR | Workflow riêng (`auto-assign.yml`) | Gán reviewer tự động |

## Chạy local tương đương CI

```powershell
cd backend
python -m ruff check .; python -m ruff format --check .
python -m pytest -n 4 --ignore=tests/stress --ignore=tests/performance
cd ../frontend
npx eslint "static/js/*.js"; npx stylelint "static/css/*.css"
```

Local dùng `-n 4` thay vì `-n auto` của CI: SQL Server nghẽn khi worker tăng. `pytest` đọc
`--ds=core.settings` trong `backend/pyproject.toml`, nên local chạy trên SQL Server thật;
muốn chạy SQLite in-memory thì dùng `python manage.py test` với `core.test_settings_sqlite`
(xem README).

## Lưu ý đã biết

- CI dùng PostgreSQL; local/prod dùng SQL Server — vẫn cần chạy suite trên đúng
  SQL Server triển khai trước khi mở bán.
- Test nào phụ thuộc `.env` máy local phải dùng `@override_settings`
  (bài học từ `test_faq_payment_reply`).
- Số liệu test trong README là số test collect được, phải cập nhật khi thêm test
  (hiện 515).
