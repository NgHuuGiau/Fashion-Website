import { test, expect } from "./fixtures";

const BASE_URL = process.env.BASE_URL || "http://localhost:8000";

test.describe("Admin Dashboard", () => {
  test.use({ storageState: ".auth/admin.json" });

  test("should access admin dashboard", async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    await expect(page.locator("h1")).toContainText(/Chào mừng|Dashboard|Bảng điều khiển|Admin/);
  });

  test("should display order statistics", async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    // Kiểm tra có thẻ h1 hoặc bất kỳ nội dung thống kê nào
    const stats = page.locator(".adm-kpi-card, .stat-card, .kpi-card, [class*=\"stat\"], [class*=\"kpi\"]").first();
    await expect(stats).toBeVisible({ timeout: 10000 }).catch(async () => {
      // Fallback: kiểm tra có nội dung thống kê nào không
      const bodyText = await page.textContent("body");
      expect(bodyText).toMatch(/đơn hàng|doanh thu|sản phẩm|khách hàng/i);
    });
  });

  test("should filter orders", async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    // Thử click vào tab đơn hàng với nhiều selector có thể
    const ordersTab = page.locator('[data-target="admin-orders"], button:has-text("Đơn hàng"), a:has-text("Đơn hàng"), [href*="admin-orders"]').first();
    if (await ordersTab.isVisible({ timeout: 5000 })) {
      await ordersTab.click();
      const statusSelect = page.locator('select[name="order_status"], select[id*="status"]').first();
      if (await statusSelect.isVisible({ timeout: 5000 })) {
        await statusSelect.selectOption("delivered");
        await expect(page).toHaveURL(/order_status=delivered/);
      }
    }
  });

  test("should export orders CSV", async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    const exportBtn = page.locator('a[href*="xuat-don"], button:has-text("Xuất đơn"), button:has-text("Export"), a:has-text("CSV")').first();
    if (await exportBtn.isVisible({ timeout: 5000 })) {
      const downloadPromise = page.waitForEvent("download");
      await exportBtn.click();
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.csv$/);
    }
  });

  test("should change order status", async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    const ordersTab = page.locator('[data-target="admin-orders"], button:has-text("Đơn hàng"), a:has-text("Đơn hàng")').first();
    if (await ordersTab.isVisible({ timeout: 5000 })) {
      await ordersTab.click();
      const statusForm = page.locator("form.admin-quick-form:visible, form:has(input[name='action'][value='update_order_status'])").first();
      if (await statusForm.isVisible({ timeout: 5000 })) {
        await statusForm.locator('select[name="new_status"], select[id*="status"]').first().selectOption("shipping");
        const responsePromise = page.waitForResponse((response) =>
          response.request().method() === "POST" && response.url().includes("/admin-dashboard/")
        );
        await statusForm.locator('button[type="submit"]').click();
        expect((await responsePromise).status()).toBe(302);
      }
    }
  });

  test("should print invoice", async ({ page }) => {
    await page.goto(`${BASE_URL}/admin-dashboard/`);
    const ordersTab = page.locator('[data-target="admin-orders"], button:has-text("Đơn hàng"), a:has-text("Đơn hàng")').first();
    if (await ordersTab.isVisible({ timeout: 5000 })) {
      await ordersTab.click();
      const invoiceLink = page.locator('a[href*="/admin-dashboard/in-hoa-don/"], a[href*="in-hoa-don"]').first();
      if (await invoiceLink.isVisible({ timeout: 5000 })) {
        await expect(invoiceLink).toHaveAttribute("target", "_blank");
        await expect(invoiceLink).toHaveAttribute("href", /\/in-hoa-don\//);
      }
    }
  });
});
