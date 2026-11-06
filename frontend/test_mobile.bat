@echo off
cd /d D:\Project\Fashion-Website\frontend
npx playwright test tests/admin.spec.ts --project="Mobile Chrome" --workers=1 --timeout=180000