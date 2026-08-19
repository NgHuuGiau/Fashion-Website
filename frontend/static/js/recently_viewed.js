// Recently Viewed Products - localStorage
const RECENTLY_VIEWED_KEY = 'huugiau_recently_viewed';
const MAX_RECENT = 10;

function getRecentlyViewed() {
  try {
    return JSON.parse(localStorage.getItem(RECENTLY_VIEWED_KEY)) || [];
  } catch {
    return [];
  }
}

function saveRecentlyViewed(list) {
  localStorage.setItem(RECENTLY_VIEWED_KEY, JSON.stringify(list.slice(0, MAX_RECENT)));
  // sync to cookie for server-side reading
  document.cookie = `${RECENTLY_VIEWED_KEY}=${encodeURIComponent(JSON.stringify(list.slice(0, MAX_RECENT)))};path=/;max-age=${60*60*24*30};SameSite=Lax`;
}

function addRecentlyViewed(product) {
  // product: { id, name, slug, price, image_url, discount_percent }
  const list = getRecentlyViewed();
  const filtered = list.filter(p => p.id !== product.id);
  filtered.unshift(product);
  saveRecentlyViewed(filtered);
}

function renderRecentlyViewed(containerSelector) {
  const list = getRecentlyViewed();
  if (!list.length) return;

  const container = document.querySelector(containerSelector);
  if (!container) return;

  container.innerHTML = list.map(p => `
    <a href="/san-pham/${p.id}/${p.slug}/" class="recent-item">
      <img src="${p.image_url}" alt="${p.name}" loading="lazy">
      <span class="recent-name">${p.name}</span>
      <span class="recent-price">
        ${p.discount_percent
          ? `<s>${Number(p.price).toLocaleString('vi-VN')}đ</s> ${Number(p.price * (1 - p.discount_percent / 100)).toLocaleString('vi-VN')}đ`
          : `${Number(p.price).toLocaleString('vi-VN')}đ`}
      </span>
    </a>
  `).join('');
}

// Auto-track on product detail pages
if (document.body.classList.contains('product-detail-page')) {
  const productData = window.PRODUCT_DATA; // set in template
  if (productData) addRecentlyViewed(productData);
}

// Expose for manual use
window.RecentlyViewed = { add: addRecentlyViewed, get: getRecentlyViewed, render: renderRecentlyViewed };