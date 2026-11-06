/* global gtag */
(function () {
  const STORAGE_KEY = "huugiau_cookie_consent";
  const BANNER_HTML = `
    <div class="cookie-consent" id="cookie-consent" role="dialog" aria-live="polite" hidden>
      <div class="cookie-consent__inner">
        <div class="cookie-consent__text">
          <strong>Chúng tôi sử dụng cookie</strong>
          Website dùng cookie để cải thiện trải nghiệm, phân tích truy cập và cá nhân hóa quảng cáo.
          Bấm "Chấp nhận" để đồng ý hoặc "Tùy chỉnh" để chọn loại cookie.
        </div>
        <div class="cookie-consent__actions">
          <button type="button" class="btn ghost" data-action="customize">Tùy chỉnh</button>
          <button type="button" class="btn" data-action="accept">Chấp nhận tất cả</button>
        </div>
      </div>
    </div>
  `;

  function getConsent () {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)); } catch { return null; }
  }

  function setConsent (consent) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(consent));
  }

  function showBanner () {
    const el = document.getElementById("cookie-consent");
    if (el) {
      el.hidden = false;
      requestAnimationFrame(() => el.classList.add("visible"));
    }
  }

  function hideBanner () {
    const el = document.getElementById("cookie-consent");
    if (el) {
      el.classList.remove("visible");
      setTimeout(() => { el.hidden = true; }, 300);
    }
  }

  function init () {
    const consent = getConsent();
    if (consent) {
      // đã chọn trước đó: áp lại vào gtag ( consent mode mặc định là denied)
      if (window.gtag) {
        gtag("consent", "update", {
          analytics_storage: consent.analytics ? "granted" : "denied",
          ad_storage: consent.marketing ? "granted" : "denied"
        });
      }
      return;
    }

    const wrapper = document.createElement("div");
    wrapper.innerHTML = BANNER_HTML;
    document.body.appendChild(wrapper.firstElementChild);

    if (!document.querySelector('link[href*="cookie_consent.css"]')) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = "/static/css/cookie_consent.css";
      document.head.appendChild(link);
    }

    const banner = document.getElementById("cookie-consent");
    banner.querySelector('[data-action="accept"]').addEventListener("click", () => {
      setConsent({ necessary: true, analytics: true, marketing: true, timestamp: Date.now() });
      hideBanner();
      if (window.gtag) {
        gtag("consent", "update", { analytics_storage: "granted", ad_storage: "granted" });
      }
    });

    banner.querySelector('[data-action="customize"]').addEventListener("click", () => {
      const analytics = confirm("Cho phép cookie phân tích (Google Analytics)?");
      const marketing = confirm("Cho phép cookie quảng cáo/đánh giá lại?");
      setConsent({
        necessary: true,
        analytics,
        marketing,
        timestamp: Date.now()
      });
      hideBanner();
      if (window.gtag) {
        gtag("consent", "update", {
          analytics_storage: analytics ? "granted" : "denied",
          ad_storage: marketing ? "granted" : "denied"
        });
      }
    });

    showBanner();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
