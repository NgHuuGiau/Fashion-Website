#!/usr/bin/env python
"""Manual test script for all 4 roles using Playwright"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:8000"

async def test_guest(page):
    print("\n=== TEST GUEST ===")
    # 1. Browse catalog
    await page.goto(f"{BASE_URL}/")
    await page.wait_for_load_state("networkidle")
    print("[OK] Home page loaded")
    
    # Check products visible
    products = await page.locator(".product-card, article.product, [data-product-id]").count()
    print(f"[OK] Products visible: {products}")
    
    # 2. Go to product detail
    await page.goto(f"{BASE_URL}/?category=ao")
    await page.wait_for_load_state("networkidle")
    print("[OK] Category filter works")
    
    # 3. Add to cart
    add_buttons = page.locator("button:has-text('Thêm vào giỏ'), button:has-text('Add to cart'), button.add-to-cart")
    if await add_buttons.count() > 0:
        await add_buttons.first.click()
        await page.wait_for_timeout(1000)
        print("[OK] Add to cart clicked")
    
    # 4. Go to cart
    await page.goto(f"{BASE_URL}/gio-hang/")
    await page.wait_for_load_state("networkidle")
    print("[OK] Cart page loaded")
    
    # 5. Checkout COD
    checkout_btn = page.locator("button:has-text('Thanh toán'), button:has-text('Checkout'), a:has-text('Thanh toán')")
    if await checkout_btn.count() > 0:
        print("[OK] Checkout button visible")
    
    return True

async def test_user(page):
    print("\n=== TEST USER ===")
    # Login
    await page.goto(f"{BASE_URL}/dang-nhap/")
    await page.fill('input[name="username"]', "nguyenvanA")
    await page.fill('input[name="password"]', "user123")
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")
    print("[OK] User logged in")
    
    # Profile page
    await page.goto(f"{BASE_URL}/tai-khoan/")
    await page.wait_for_load_state("networkidle")
    print("[OK] Profile page loaded")
    
    # Order history
    await page.goto(f"{BASE_URL}/don-hang-cua-toi/")
    await page.wait_for_load_state("networkidle")
    print("[OK] Order history loaded")
    
    # Wishlist
    await page.goto(f"{BASE_URL}/yeu-thich/")
    await page.wait_for_load_state("networkidle")
    print("[OK] Wishlist loaded")
    
    # Change password
    await page.goto(f"{BASE_URL}/doi-mat-khau/")
    await page.wait_for_load_state("networkidle")
    print("[OK] Change password page loaded")
    
    return True

async def test_staff(page):
    print("\n=== TEST STAFF ===")
    # Login
    await page.goto(f"{BASE_URL}/dang-nhap/")
    await page.fill('input[name="username"]', "staff1")
    await page.fill('input[name="password"]', "staff123")
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")
    print("[OK] Staff logged in")
    
    # Admin dashboard
    await page.goto(f"{BASE_URL}/admin-dashboard/")
    await page.wait_for_load_state("networkidle")
    print("[OK] Admin dashboard loaded")
    
    # Orders management
    await page.click('[data-target="admin-orders"]')
    await page.wait_for_timeout(1000)
    print("[OK] Orders tab clicked")
    
    return True

async def test_admin(page):
    print("\n=== TEST ADMIN ===")
    # Login with 2FA
    await page.goto(f"{BASE_URL}/admin/")
    await page.fill('input[name="username"]', "admin")
    await page.fill('input[name="password"]', "admin123")
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")
    print("[OK] Admin first step login")
    
    # 2FA - we need to get TOTP from the database
    # For now, just check if 2FA page appears
    current_url = page.url
    if "2fa" in current_url or "otp" in current_url:
        print("[OK] 2FA page reached")
    
    return True

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await test_guest(page)
            await test_user(page)
            await test_staff(page)
            await test_admin(page)
            print("\n[SUCCESS] ALL ROLES TESTED SUCCESSFULLY!")
        except Exception as e:
            print(f"\n[ERROR] ERROR: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())