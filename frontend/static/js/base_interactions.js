(function() {
    'use strict';
    document.addEventListener('DOMContentLoaded', function() {
        // ─── Search autocomplete ───
        (function(){
            var input = document.getElementById('header-search-input');
            var box = document.getElementById('search-suggest');
            var form = document.getElementById('header-search-form');
            if (!input || !box || !form) return;
            var suggestUrl = form.getAttribute('data-suggest-url');
            var timer, selected = -1;
            input.addEventListener('input', function(){
                clearTimeout(timer);
                var q = this.value.trim();
                if (q.length < 1) { box.innerHTML = ''; box.classList.remove('is-active'); return; }
                timer = setTimeout(function(){
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', suggestUrl + '?q=' + encodeURIComponent(q), true);
                    xhr.onload = function(){
                        if (xhr.status !== 200) return;
                        var data = JSON.parse(xhr.responseText);
                        if (!data.length) { box.innerHTML = ''; box.classList.remove('is-active'); return; }
                        var html = '';
                        data.forEach(function(item){
                            html += '<a href="/san-pham/' + item.id + '/' + item.slug + '/" class="suggest-item">';
                            if (item.image) html += '<img src="' + item.image + '" alt="" class="suggest-img">';
                            html += '<div class="suggest-info"><span class="suggest-name">' + escapeHtml(item.name) + '</span>';
                            html += '<span class="suggest-price">' + Number(item.price).toLocaleString('vi-VN') + '₫</span></div></a>';
                        });
                        box.innerHTML = html;
                        box.classList.add('is-active');
                        selected = -1;
                    };
                    xhr.send();
                }, 250);
            });
            input.addEventListener('keydown', function(e){
                var items = box.querySelectorAll('.suggest-item');
                if (!items.length) return;
                if (e.key === 'ArrowDown') { e.preventDefault(); selected = Math.min(selected + 1, items.length - 1); highlight(items, selected); }
                else if (e.key === 'ArrowUp') { e.preventDefault(); selected = Math.max(selected - 1, -1); highlight(items, selected); }
                else if (e.key === 'Enter' && selected >= 0) { e.preventDefault(); items[selected].click(); }
            });
            document.addEventListener('click', function(e){
                if (!input.contains(e.target) && !box.contains(e.target)) { box.classList.remove('is-active'); }
            });
            function highlight(items, idx) {
                items.forEach(function(item, i){ item.classList.toggle('is-highlight', i === idx); });
            }
            function escapeHtml(text) {
                var d = document.createElement('div');
                d.textContent = text;
                return d.innerHTML;
            }
        })();

        // ─── Sidebar menu (toggle on hamburger) ───
        var hamburger = document.getElementById('hamburger-btn');
        var closeMenu = document.getElementById('close-menu');
        var siteNav = document.getElementById('site-nav');

        function toggleMenu(open) {
            var isOpen = open !== undefined ? open : !siteNav.classList.contains('is-open');
            if (isOpen) {
                siteNav.classList.add('is-open');
                document.body.style.overflow = 'hidden';
            } else {
                siteNav.classList.remove('is-open');
                document.body.style.overflow = '';
            }
        }

        if (hamburger && siteNav) {
            hamburger.addEventListener('click', function(e) { e.stopPropagation(); toggleMenu(); });
        }
        if (closeMenu && siteNav) {
            closeMenu.addEventListener('click', function() { toggleMenu(false); });
        }
        document.addEventListener('click', function(e) {
            if (siteNav && siteNav.classList.contains('is-open') && !siteNav.contains(e.target) && e.target !== hamburger) {
                toggleMenu(false);
            }
        });
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && siteNav && siteNav.classList.contains('is-open')) {
                toggleMenu(false);
            }
        });
        siteNav.addEventListener('click', function(e) {
            if (e.target.closest('a') && siteNav.classList.contains('is-open')) {
                toggleMenu(false);
            }
        });

        // ─── Auto-dismiss messages ───
        document.querySelectorAll('.message-stack .message').forEach(function(msg) {
            msg.addEventListener('click', function() {
                this.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                this.style.opacity = '0';
                this.style.transform = 'translateY(-8px)';
                setTimeout(function() { if (msg && msg.parentNode) msg.remove(); }, 300);
            });
        });

        // ─── Scroll reveal animation ───
        if ('IntersectionObserver' in window) {
            var revealElements = document.querySelectorAll('.lookbook-shell, .hero-shell, .detail-layout, .checkout-layout, .cart-layout, .auth-layout, .account-layout, .admin-hero-shell');
            var revealObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        revealObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
            revealElements.forEach(function(el) {
                el.classList.add('reveal');
                revealObserver.observe(el);
            });
        }

        // ─── Cart quantity bump animation ───
        var cartCount = document.querySelector('.icon-count');
        if (cartCount) {
            var originalText = cartCount.textContent;
            var observer = new MutationObserver(function() {
                if (cartCount.textContent !== originalText) {
                    originalText = cartCount.textContent;
                    cartCount.classList.remove('bump');
                    void cartCount.offsetWidth;
                    cartCount.classList.add('bump');
                }
            });
            observer.observe(cartCount, { childList: true, characterData: true, subtree: true });
        }

        // ─── Toast notifications ───
        (function(){
            var dataEl = document.getElementById('messages-data');
            if (!dataEl) return;
            var raw = dataEl.textContent.trim();
            if (!raw || raw === '[]') return;
            var messages;
            try { messages = JSON.parse(raw); } catch(e) { return; }
            var container = document.getElementById('toast-container');
            if (!container) return;
            messages.forEach(function(msg, idx){
                var toast = document.createElement('div');
                toast.className = 'toast toast-' + (msg.tags || 'info');
                toast.textContent = msg.text;
                toast.style.animationDelay = (idx * 0.15) + 's';
                container.appendChild(toast);
                setTimeout(function(){ toast.classList.add('toast-hide'); }, 3000 + idx * 150);
                setTimeout(function(){ if (toast.parentNode) toast.remove(); }, 3500 + idx * 150);
            });
        })();
    });
})();
