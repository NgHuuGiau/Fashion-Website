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
| CodeQL | Workflow riêng | Python + JavaScript |

## Chạy local tương đương CI

```powershell
cd backend
python -m ruff check .; python -m ruff format --check .
python -m pytest -n auto --ignore=tests/stress --ignore=tests/performance
cd ../frontend
npx eslint "static/js/*.js"; npx stylelint "static/css/*.css"
```

## Lưu ý đã biết

- CI dùng PostgreSQL; local/prod dùng SQL Server — vẫn cần chạy suite trên đúng
  SQL Server triển khai trước khi mở bán (đã chạy: 486 Django pass).
- Test nào phụ thuộc `.env` máy local phải dùng `@override_settings`
  (bài học từ `test_faq_payment_reply`).
- Không commit số liệu test cứng vào README — lấy kết quả lần chạy hiện tại làm chuẩn.
