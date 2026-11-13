@echo off
cd /d D:\Project\Fashion-Website\frontend
set BASE_URL=http://127.0.0.1:8000
npx playwright test --project=chromium --project="Mobile Chrome"