(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", () => {
    (function () {
      const input = document.getElementById("header-search-input");
      const box = document.getElementById("search-suggest");
      const form = document.getElementById("header-search-form");
      if (!input || !box || !form) return;
      const suggestUrl = form.getAttribute("data-suggest-url");
      let timer; let selected = -1;
      input.addEventListener("input", function () {
        clearTimeout(timer);
        const q = this.value.trim();
        if (q.length < 1) { box.innerHTML = ""; box.classList.remove("is-active"); return; }
        timer = setTimeout(() => {
          const xhr = new XMLHttpRequest();
          xhr.open("GET", `${suggestUrl}?q=${encodeURIComponent(q)}`, true);
          xhr.onload = function () {
            if (xhr.status !== 200) return;
            let data;
            try { data = JSON.parse(xhr.responseText); } catch (e) { return; }
            if (!data.length) { box.innerHTML = ""; box.classList.remove("is-active"); return; }
            let html = "";
            data.forEach((item) => {
              html += `<a href="/san-pham/${item.id}/${item.slug}/" class="suggest-item">`;
              if (item.image) html += `<img src="${item.image}" alt="" class="suggest-img">`;
              html += `<div class="suggest-info"><span class="suggest-name">${escapeHtml(item.name)}</span>`;
              html += `<span class="suggest-price">${Number(item.price).toLocaleString("vi-VN")}₫</span></div></a>`;
            });
            box.innerHTML = html;
            box.classList.add("is-active");
            selected = -1;
          };
          xhr.send();
        }, 250);
      });
      input.addEventListener("keydown", (e) => {
        const items = box.querySelectorAll(".suggest-item");
        if (!items.length) return;
        if (e.key === "ArrowDown") { e.preventDefault(); selected = Math.min(selected + 1, items.length - 1); highlight(items, selected); } else if (e.key === "ArrowUp") { e.preventDefault(); selected = Math.max(selected - 1, -1); highlight(items, selected); } else if (e.key === "Enter" && selected >= 0) { e.preventDefault(); items[selected].click(); }
      });
      document.addEventListener("click", (e) => {
        if (!input.contains(e.target) && !box.contains(e.target)) { box.classList.remove("is-active"); }
      });
      function highlight (items, idx) {
        items.forEach((item, i) => { item.classList.toggle("is-highlight", i === idx); });
      }
      function escapeHtml (text) {
        const d = document.createElement("div");
        d.textContent = text;
        return d.innerHTML;
      }
    })();

    const hamburger = document.getElementById("hamburger-btn");
    const closeMenu = document.getElementById("close-menu");
    const siteNav = document.getElementById("site-nav");

    function toggleMenu (open) {
      const isOpen = open !== undefined ? open : !siteNav.classList.contains("is-open");
      if (isOpen) {
        siteNav.classList.add("is-open");
        document.body.dataset.navOpen = "1";
        document.body.style.overflow = "hidden";
      } else {
        siteNav.classList.remove("is-open");
        delete document.body.dataset.navOpen;
        if (!document.getElementById("gallery-zoom")?.classList.contains("is-open") &&
                    !document.querySelector(".chatbox:not(.hidden)")) {
          document.body.style.overflow = "";
        }
      }
    }

    if (hamburger && siteNav) {
      hamburger.addEventListener("click", (e) => { e.stopPropagation(); toggleMenu(); });
    }
    if (closeMenu && siteNav) {
      closeMenu.addEventListener("click", () => { toggleMenu(false); });
    }
    document.addEventListener("click", (e) => {
      if (siteNav && siteNav.classList.contains("is-open") && !siteNav.contains(e.target) && e.target !== hamburger) {
        toggleMenu(false);
      }
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && siteNav && siteNav.classList.contains("is-open")) {
        toggleMenu(false);
      }
    });
    if (siteNav) {
      siteNav.addEventListener("click", (e) => {
        if (e.target.closest("a") && siteNav.classList.contains("is-open")) {
          toggleMenu(false);
        }
      });
    }

    document.querySelectorAll(".message-stack .message").forEach((msg) => {
      msg.addEventListener("click", function () {
        this.style.transition = "opacity 0.3s ease, transform 0.3s ease";
        this.style.opacity = "0";
        this.style.transform = "translateY(-8px)";
        setTimeout(() => { if (msg && msg.parentNode) msg.remove(); }, 300);
      });
    });

    if ("IntersectionObserver" in window) {
      const revealElements = document.querySelectorAll(".lookbook-shell, .hero-shell, .detail-layout, .checkout-layout, .cart-layout, .auth-layout, .account-layout, .admin-hero-shell");
      const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
      revealElements.forEach((el) => {
        el.classList.add("reveal");
        revealObserver.observe(el);
      });
    }

    const cartCount = document.querySelector(".icon-count");
    if (cartCount) {
      let originalText = cartCount.textContent;
      const observer = new MutationObserver(() => {
        if (cartCount.textContent !== originalText) {
          originalText = cartCount.textContent;
          cartCount.classList.remove("bump");
          cartCount.getBoundingClientRect();
          cartCount.classList.add("bump");
        }
      });
      observer.observe(cartCount, { childList: true, characterData: true, subtree: true });
    }

    (function () {
      const dataEl = document.getElementById("messages-data");
      if (!dataEl) return;
      const raw = dataEl.textContent.trim();
      if (!raw || raw === "[]") return;
      let messages;
      try { messages = JSON.parse(raw); } catch (e) { return; }
      const container = document.getElementById("toast-container");
      if (!container) return;
      messages.forEach((msg, idx) => {
        const toast = document.createElement("div");
        toast.className = `toast toast-${msg.tags || "info"}`;
        toast.textContent = msg.text;
        toast.style.animationDelay = `${idx * 0.15}s`;
        container.appendChild(toast);
        setTimeout(() => { toast.classList.add("toast-hide"); }, 3000 + idx * 150);
        setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3500 + idx * 150);
      });
    })();
  });

  (function () {
    const popup = document.getElementById("buy-popup");
    const nameEl = document.getElementById("buy-popup-name");
    const metaEl = document.getElementById("buy-popup-meta");
    const thumbEl = document.getElementById("buy-popup-thumb");
    const closeBtn = document.getElementById("buy-popup-close");
    if (!popup || !nameEl || !metaEl || !thumbEl || !closeBtn) return;

    const items = [
      { name: "Áo Tee Oversize Essential", thumb: "TEE", price: "250.000", city: "Hà Nội" },
      { name: "Quần Jeans Baggy Fade Blue", thumb: "QUẦN", price: "520.000", city: "TP. Hồ Chí Minh" },
      { name: "Hoodie Nỉ Cotton Local", thumb: "ÁO", price: "590.000", city: "Đà Nẵng" },
      { name: "Nón Bucket Côn Sơn", thumb: "PHỤ KIỆN", price: "280.000", city: "Hải Phòng" },
      { name: "Áo Polo Cotton Pique", thumb: "ÁO", price: "320.000", city: "Cần Thơ" },
      { name: "Quần Short Denim Cargo", thumb: "QUẦN", price: "340.000", city: "Huế" },
      { name: "Áo Khoác Denim Varsity", thumb: "ÁO", price: "780.000", city: "Biên Hòa" },
      { name: "Áo Sơ Mi Oversize Canvas", thumb: "ÁO", price: "390.000", city: "Vũng Tàu" },
      { name: "Quần Jogger 2-Tone", thumb: "QUẦN", price: "430.000", city: "Long Xuyên" },
      { name: "Áo Thun Graphic No.01", thumb: "ÁO", price: "290.000", city: "Đà Lạt" },
      { name: "Váy Denim Cargo Mini", thumb: "VÁY", price: "460.000", city: "Hà Nội" },
      { name: "Áo Hoodie Zip Local", thumb: "ÁO", price: "620.000", city: "TP. Hồ Chí Minh" },
      { name: "Quần Ống Rộng Wide Denim", thumb: "QUẦN", price: "550.000", city: "Nha Trang" },
      { name: "Túi Tote Canvas Local", thumb: "TÚI", price: "210.000", city: "Bắc Ninh" },
      { name: "Áo Cardigan Len Loose", thumb: "ÁO", price: "680.000", city: "Buôn Ma Thuột" },
      { name: "Nón Lưỡi Trai Embroidery", thumb: "NÓN", price: "180.000", city: "Thanh Hóa" }
    ];
    let hiding = false;
    let timer = null;

    function show (item) {
      if (hiding) return;
      const mins = 2 + Math.floor(Math.random() * 38);
      nameEl.textContent = item.name;
      metaEl.textContent = `Ai đó ở ${item.city} vừa đặt ${item.price}đ · ${mins} phút trước`;
      thumbEl.textContent = item.thumb;
      popup.classList.remove("hidden");
      popup.classList.add("show");
      timer = setTimeout(() => {
        popup.classList.remove("show");
        popup.classList.add("hidden");
      }, 4000 + Math.floor(Math.random() * 2500));
    }

    function pick () {
      show(items[Math.floor(Math.random() * items.length)]);
    }

    function schedule () {
      timer = setTimeout(() => {
        if (!hiding) pick();
        schedule();
      }, 22000 + Math.floor(Math.random() * 26000));
    }

    setTimeout(() => {
      if (hiding) return;
      pick();
      schedule();
    }, 4000 + Math.floor(Math.random() * 5000));

    closeBtn.addEventListener("click", () => {
      hiding = true;
      if (timer) clearTimeout(timer);
      popup.classList.remove("show");
      popup.classList.add("hidden");
    });
  })();

  (function () {
    const popup = document.getElementById("exit-popup");
    if (!popup) return;
    try { if (localStorage.getItem("exit_popup_seen")) return; } catch (e) {}

    let dismissed = false;
    function show () {
      if (dismissed) return;
      popup.classList.remove("hidden");
      popup.classList.add("show");
      document.body.dataset.exitOpen = "1";
      document.body.style.overflow = "hidden";
    }
    function hide () {
      dismissed = true;
      popup.classList.remove("show");
      popup.classList.add("hidden");
      delete document.body.dataset.exitOpen;
      if (!document.getElementById("gallery-zoom")?.classList.contains("is-open") &&
                !document.querySelector(".chatbox:not(.hidden)")) {
        document.body.style.overflow = "";
      }
      try { localStorage.setItem("exit_popup_seen", "1"); } catch (e) {}
    }

    document.addEventListener("mouseout", (e) => {
      if (e.relatedTarget !== null || e.clientY > 20) return;
      show();
    });

    const close = document.getElementById("exit-popup-close");
    if (close) close.addEventListener("click", hide);
    popup.addEventListener("click", (e) => { if (e.target === popup) hide(); });

    const form = document.getElementById("exit-popup-form");
    if (form) {
      form.addEventListener("submit", () => {
        try { localStorage.setItem("exit_popup_seen", "1"); } catch (e) {}
        dismissed = true;
        popup.classList.remove("show");
        popup.classList.add("hidden");
        delete document.body.dataset.exitOpen;
        if (!document.getElementById("gallery-zoom")?.classList.contains("is-open") &&
                    !document.querySelector(".chatbox:not(.hidden)")) {
          document.body.style.overflow = "";
        }
      });
    }
  })();

  (function () {
    const drawer = document.getElementById("cart-drawer");
    const overlay = document.getElementById("cart-drawer-overlay");
    const itemsEl = document.getElementById("cart-drawer-items");
    const countEl = document.getElementById("cart-drawer-count");
    const subtotalEl = document.getElementById("cart-drawer-subtotal");
    if (!drawer || !overlay) return;

    function fmt (n) {
      return `${Number(n).toLocaleString("vi-VN")}đ`;
    }

    function refreshCartBadges (count) {
      const badges = document.querySelectorAll(".site-nav-cart-count, .icon-count");
      Array.prototype.forEach.call(badges, (b) => { b.textContent = count; b.hidden = count <= 0; });
    }

    function render (data) {
      if (countEl) countEl.textContent = data.count;
      if (subtotalEl) subtotalEl.textContent = fmt(data.subtotal);
      refreshCartBadges(data.count);
      if (!itemsEl) return;
      itemsEl.innerHTML = "";
      if (!data.items || !data.items.length) {
        itemsEl.innerHTML = '<p class="cart-drawer-empty">Giỏ hàng đang trống.</p>';
        return;
      }
      data.items.forEach((it) => {
        const row = document.createElement("div");
        row.className = "cart-drawer-item";
        const img = document.createElement("img");
        img.src = it.image;
        img.alt = "";
        img.loading = "lazy";
        const info = document.createElement("div");
        const link = document.createElement("a");
        link.href = it.url;
        link.textContent = it.name;
        info.appendChild(link);
        if (it.variant_label) {
          const v = document.createElement("span");
          v.className = "cart-drawer-variant";
          v.textContent = it.variant_label;
          info.appendChild(v);
        }
        const q = document.createElement("span");
        q.textContent = `${it.quantity} × ${fmt(it.price)}`;
        info.appendChild(q);
        const total = document.createElement("strong");
        total.textContent = fmt(it.line_total);
        row.appendChild(img);
        row.appendChild(info);
        row.appendChild(total);
        itemsEl.appendChild(row);
      });
    }

    window.openCartDrawer = function () {
      fetch("/gio-hang/tom-tat/", { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then((r) => { return r.json(); })
        .then((data) => {
          render(data);
          drawer.classList.add("is-open");
          overlay.hidden = false;
          document.body.classList.add("drawer-open");
          drawer.setAttribute("aria-hidden", "false");
          return data;
        })
        .catch(() => {});
    };

    function closeDrawer () {
      drawer.classList.remove("is-open");
      overlay.hidden = true;
      document.body.classList.remove("drawer-open");
      drawer.setAttribute("aria-hidden", "true");
    }

    const closeBtn = document.getElementById("cart-drawer-close");
    if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
    overlay.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && drawer.classList.contains("is-open")) closeDrawer();
    });
  })();

  (function () {
    const form = document.getElementById("detail-buy-form");
    if (!form) return;
    form.addEventListener("submit", (e) => {
      const btn = document.activeElement;
      if (!btn || !btn.hasAttribute("data-ajax-add")) return;
      e.preventDefault();
      const spinner = document.createElement("span");
      spinner.className = "detail-buy-spinner";
      btn.appendChild(spinner);
      btn.disabled = true;
      (async () => {
        try {
          const response = await fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: { "X-Requested-With": "XMLHttpRequest" }
          });
          const data = await response.json();
          if (!data || !data.ok) {
            window.location.href = btn.value;
            return;
          }
          if (window.openCartDrawer) window.openCartDrawer();
        } catch (_) {
          window.location.href = btn.value;
        } finally {
          btn.disabled = false;
          if (spinner.parentNode) spinner.parentNode.removeChild(spinner);
        }
      })();
    });
  })();
})();
