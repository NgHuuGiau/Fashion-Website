@echo off
cd /d D:\Project\Fashion-Website\frontend
npx playwright test tests/cart-checkout.spec.ts --project="Mobile Chrome" --workers=1 --timeout=300000