(function() {
    'use strict';

    // ─── Variant picker (button-based) ───
    const dataNode = document.getElementById('variant-data');
    const picker = document.getElementById('variant-picker');
    const variantInput = document.getElementById('variant-id-input');
    const stockText = document.getElementById('variant-stock-text');

    if (dataNode && picker && variantInput) {
        let variants = [];
        try { variants = JSON.parse(dataNode.textContent || '[]'); } catch (_) {}
        const colorOptions = picker.querySelectorAll('[data-variant-color]');
        const sizeOptions = picker.querySelectorAll('[data-variant-size]');

        function getSelectedColor() {
            const active = picker.querySelector('[data-variant-color].is-active');
            return active ? active.dataset.variantColor : '';
        }

        function getSelectedSize() {
            const active = picker.querySelector('[data-variant-size].is-active');
            return active ? active.dataset.variantSize : '';
        }

        function findVariant(color, size) {
            return variants.find(v => v.color_name === color && v.size === size) || null;
        }

        function updateAvailableSizes(color) {
            const available = new Set();
            variants.forEach(v => { if (v.color_name === color) available.add(v.size); });
            sizeOptions.forEach(btn => {
                const size = btn.dataset.variantSize;
                if (available.has(size)) {
                    btn.disabled = false;
                    btn.classList.remove('disabled');
                } else {
                    btn.disabled = true;
                    btn.classList.add('disabled');
                }
            });
        }

        function applyVariant() {
            const color = getSelectedColor();
            const size = getSelectedSize();
            if (!color || !size) {
                variantInput.value = '';
                if (stockText) stockText.textContent = 'Vui lòng chọn màu và size.';
                return;
            }
            const variant = findVariant(color, size);
            if (variant) {
                variantInput.value = variant.id;
                if (stockText) stockText.textContent = 'Tồn kho: ' + variant.stock;
            } else {
                variantInput.value = '';
                if (stockText) stockText.textContent = 'Biến thể này hiện không khả dụng.';
            }
        }

        colorOptions.forEach(btn => {
            btn.addEventListener('click', function() {
                colorOptions.forEach(b => b.classList.remove('is-active'));
                this.classList.add('is-active');
                updateAvailableSizes(this.dataset.variantColor);
                const currentSize = getSelectedSize();
                if (currentSize) {
                    const sizesForColor = new Set();
                    variants.forEach(v => { if (v.color_name === this.dataset.variantColor) sizesForColor.add(v.size); });
                    if (!sizesForColor.has(currentSize)) {
                        const firstAvailable = sizeOptions.find(s => !s.disabled);
                        if (firstAvailable) {
                            sizeOptions.forEach(b => b.classList.remove('is-active'));
                            firstAvailable.classList.add('is-active');
                        }
                    }
                }
                applyVariant();
            });
        });

        sizeOptions.forEach(btn => {
            btn.addEventListener('click', function() {
                if (this.disabled) return;
                sizeOptions.forEach(b => b.classList.remove('is-active'));
                this.classList.add('is-active');
                applyVariant();
            });
        });

        const defaultVariantId = parseInt(picker.dataset.defaultVariant || '0', 10);
        const defaultVariant = variants.find(v => v.id === defaultVariantId) || variants[0];
        if (defaultVariant && colorOptions.length && sizeOptions.length) {
            colorOptions.forEach(b => {
                b.classList.toggle('is-active', b.dataset.variantColor === defaultVariant.color_name);
            });
            updateAvailableSizes(defaultVariant.color_name);
            sizeOptions.forEach(b => {
                b.classList.toggle('is-active', b.dataset.variantSize === defaultVariant.size);
                b.disabled = false;
                b.classList.remove('disabled');
            });
            applyVariant();
        }
    }

    // ─── Image gallery (thumb clicks via delegation) ───
    document.addEventListener('click', function(e) {
        var thumb = e.target.closest('[data-detail-image]');
        if (!thumb) return;
        var url = thumb.dataset.detailImage;
        if (!url) return;
        var main = document.getElementById('detail-main-image');
        if (!main) return;
        main.style.opacity = '0';
        setTimeout(function() { main.src = url; main.alt = thumb.dataset.detailAlt || main.alt; main.style.opacity = '1'; }, 120);
        document.querySelectorAll('[data-detail-image]').forEach(function(t) { t.classList.remove('active'); });
        thumb.classList.add('active');
    });

    // ─── Quantity stepper (delegation) ───
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('[data-qty-step]');
        if (!btn) return;
        var step = parseInt(btn.dataset.qtyStep || '0', 10);
        var wrap = btn.closest('.qty-stepper');
        var input = wrap ? wrap.querySelector('[data-qty-input]') : null;
        if (!input) return;
        var min = parseInt(input.min || '1', 10);
        var max = parseInt(input.max || '9999', 10);
        var cur = parseInt(input.value || String(min), 10);
        var next = Math.max(min, Math.min(max, (isNaN(cur) ? min : cur) + step));
        input.value = String(next);
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        var form = wrap.closest('form');
        if (form && form.action && form.action.indexOf('cart_update') !== -1) {
            form.requestSubmit ? form.requestSubmit() : form.submit();
        }
    });

    // ─── Support chat ───
    const launcher = document.getElementById('chat-launcher');
    const chatbox = document.getElementById('support-chatbox');
    const backdrop = document.getElementById('chatbox-backdrop');
    const closeBtn = document.getElementById('chatbox-close');
    const chatForm = document.getElementById('chatbox-form');
    const chatInput = document.getElementById('chatbox-input');
    const chatMessages = document.getElementById('chatbox-messages');
    const chatSuggestions = document.querySelectorAll('.chat-suggestion');
    const endpoint = chatbox ? chatbox.dataset.chatEndpoint : '';

    if (launcher && chatbox && closeBtn && chatForm && chatInput && chatMessages && backdrop) {
        function scrollToBottom() {
            requestAnimationFrame(() => { chatMessages.scrollTop = chatMessages.scrollHeight; });
        }

        function appendMessage(role, text) {
            const article = document.createElement('article');
            const bubble = document.createElement('p');
            article.className = 'chat-message ' + role;
            bubble.textContent = text;
            article.appendChild(bubble);
            chatMessages.appendChild(article);
            scrollToBottom();
            return article;
        }

        function getFallbackReply(message) {
            var text = (message || '').toLowerCase();
            if (/ship|giao|v[\s\S]*chuy[\s\S]n|free ship|ph[\s\S]*ship/i.test(text)) {
                if (/bao nhi[uê]|m[\s\S]*n|ph[\s\S]*\.?.?.?\s*ship/i.test(text)) return 'Phí ship tiêu chuẩn là 30K nội thành HCM và 50K toàn quốc. Freeship cho đơn từ 499K. Bạn thử add sản phẩm vào giỏ để xem phí ship chính xác nhé.';
                return 'Shop có free ship toàn quốc cho đơn từ 499K. Freeship tự động áp dụng, không cần nhập mã.';
            }
            if (/thanh[\s\S]*to[\s\S]*n|chuy[\s\S]*n[\s\S]*kho[\s\S]*n|cod|qr/i.test(text)) {
                if (/qr|m[\s\S]*\s*qr/i.test(text)) return 'Khi chọn chuyển khoản, trang thanh toán sẽ hiển thị mã QR để bạn quét. Bạn cũng có thể chuyển thủ công theo thông tin tài khoản hiển thị trên màn hình. Sau khi chuyển, bấm "Đã chuyển khoản" để shop xác nhận.';
                return 'Hiện shop hỗ trợ thanh toán khi nhận hàng (COD) và chuyển khoản ngân hàng (QR). COD được khuyến khích vì tiện lợi, không cần chờ xác nhận thanh toán.';
            }
            if (/size|kích[\s\S]*c[oồ]|vừa|m[\s\S]*c|1m|m[\s\S]*t|cao.*cân|chi[eê]u cao/i.test(text)) {
                var match = text.match(/(\d{1,2})\s*m[\s\S]*?(\d{1,3})\s*kg/i);
                if (match) {
                    var h = parseInt(match[1], 10) * 100 + parseInt(match[2], 10);
                    var w = parseInt(match[3], 10);
                    if (h >= 175 || w >= 80) return 'Với số đo của bạn, shop gợi ý size L hoặc XL cho áo, M hoặc L cho quần. Tuy nhiên tùy form mặc ôm hay rộng nữa — nếu thích mặc ôm thì chọn size nhỏ hơn 1 size.';
                    if (h >= 165 || w >= 65) return 'Với số đo của bạn, shop gợi ý size M cho áo và M cho quần. Nếu thích mặc rộng hoặc có chất riêng, shop có thể tư vấn thêm nếu bạn nói rõ sản phẩm.';
                    return 'Theo số đo bạn cung cấp, size S hoặc M sẽ phù hợp. Bạn vào trang sản phẩm để xem bảng size chi tiết nhé.';
                }
                return 'Bạn vào trang chi tiết sản phẩm để chọn màu và size. Nếu phân vân, gửi shop chiều cao, cân nặng và form mặc mong muốn (ôm/rộng) để shop tư vấn nhanh hơn.';
            }
            if (/đơn|theo[\s\S]*d[oõ]i|trạng[\s\S]*th[iá]i|order|don/i.test(text)) return 'Bạn vào mục "Đơn hàng của tôi" để theo dõi trạng thái. Nếu đơn đang "Chờ xử lý" nghĩa là shop chưa xác nhận, "Đang xử lý" là đã xác nhận và chuẩn bị giao.';
            if (/đ[oô]i|tr[ảa]|hoà[n]|hủy/i.test(text)) return 'Bạn có thể đổi size trong 7 ngày nếu sản phẩm còn nguyên tag và chưa qua sử dụng. Liên hệ shop qua chat hoặc gửi email kèm mã đơn và lý do để được hỗ trợ nhanh nhất.';
            if (/giỏ|cart|mua|thêm|checkout/i.test(text)) return 'Bạn thêm sản phẩm vào giỏ ở trang chi tiết, sau đó vào Giỏ hàng để kiểm tra rồi bấm Thanh toán. Nếu chưa có tài khoản, bạn vẫn có thể đặt hàng và tạo tài khoản sau.';
            if (/kho|tồn|còn h|hết|hàng/i.test(text)) return 'Tồn kho được cập nhật theo thời gian thực. Nếu sản phẩm hiện "Hết hàng", bạn có thể để lại email để shop báo khi có lại.';
            if (/m[\s\S]*u|gi[\s\S]|sale|gi[ảa]m|khuy[\s\S]*n m[\s\S]*i/i.test(text)) return 'Các chương trình giảm giá được cập nhật trên trang chủ. Freeship cho đơn từ 499K luôn áp dụng. Bạn cũng có thể dùng mã giảm giá (nếu có) ở bước checkout.';
            return 'Shop có thể hỗ trợ bạn về: size — phí ship — thanh toán — đổi trả — theo dõi đơn hàng. Bạn thử hỏi cụ thể hơn một chút (vd: "1m72 68kg mặc size gì?", "còn màu đen không?", "ship bao nhiêu?") nhé.';
        }

        function fetchReply(message) {
            if (!endpoint) return Promise.resolve(getFallbackReply(message));
            return fetch(endpoint + '?q=' + encodeURIComponent(message), {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            }).then(r => {
                if (!r.ok) throw new Error('fail');
                return r.json();
            }).then(payload => payload.reply || getFallbackReply(message))
              .catch(() => getFallbackReply(message));
        }

        function sendMessage(text) {
            const cleanText = (text || '').trim();
            if (!cleanText) return;
            appendMessage('user', cleanText);
            chatInput.value = '';
            chatInput.disabled = true;
            const loadingMsg = appendMessage('bot', 'Shop đang trả lời...');
            setTimeout(() => {
                fetchReply(cleanText).then(reply => {
                    if (loadingMsg && loadingMsg.parentNode) loadingMsg.remove();
                    appendMessage('bot', reply);
                    chatInput.disabled = false;
                    chatInput.focus();
                });
            }, 180);
        }

        launcher.addEventListener('click', () => {
            chatbox.classList.remove('hidden');
            backdrop.classList.remove('hidden');
            launcher.classList.add('hidden');
            document.body.style.overflow = 'hidden';
            setTimeout(() => { chatInput.focus(); scrollToBottom(); }, 50);
        });

        function closeChat() {
            chatbox.classList.add('hidden');
            backdrop.classList.add('hidden');
            launcher.classList.remove('hidden');
            document.body.style.overflow = '';
        }

        closeBtn.addEventListener('click', closeChat);
        backdrop.addEventListener('click', closeChat);
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape' && !chatbox.classList.contains('hidden')) closeChat();
        });
        chatForm.addEventListener('submit', e => { e.preventDefault(); sendMessage(chatInput.value); });
        chatSuggestions.forEach(btn => {
            btn.addEventListener('click', () => sendMessage(btn.textContent || ''));
        });
    }

    // ─── Add variant row (admin) ───
    const addRowBtn = document.getElementById('add-variant-row');
    const variantTableBody = document.getElementById('variant-table-body');
    if (addRowBtn && variantTableBody) {
        function makeRowKey() { return 'row-' + Date.now() + '-' + Math.floor(Math.random() * 1000); }
        function buildRow() {
            const rowKey = makeRowKey();
            const row = document.createElement('tr');
            row.className = 'variant-row';
            row.innerHTML = [
                '<td><input type="hidden" name="variant_row_key[]" value="' + rowKey + '"><input type="text" name="variant_color_name[]" placeholder="Đen"></td>',
                '<td><input type="text" name="variant_color_code[]" value="#111111" placeholder="#111111"></td>',
                '<td><input type="text" name="variant_size[]" placeholder="M"></td>',
                '<td><input type="number" name="variant_stock[]" min="0" step="1" value="0" placeholder="0"></td>',
                '<td class="variant-check"><input type="checkbox" name="variant_is_active[]" value="' + rowKey + '" checked></td>',
                '<td><button type="button" class="btn danger small variant-remove">Xóa</button></td>'
            ].join('');
            return row;
        }
        addRowBtn.addEventListener('click', () => variantTableBody.appendChild(buildRow()));
        variantTableBody.addEventListener('click', e => {
            const target = e.target;
            if (!target.classList.contains('variant-remove')) return;
            const rows = variantTableBody.querySelectorAll('.variant-row');
            if (rows.length <= 1) {
                const inputs = rows[0].querySelectorAll('input');
                inputs.forEach(inp => {
                    if (inp.type === 'checkbox') inp.checked = true;
                    else if (inp.type === 'number') inp.value = '0';
                    else if (inp.name === 'variant_color_code[]') inp.value = '#111111';
                    else inp.value = '';
                });
                return;
            }
            const row = target.closest('.variant-row');
            if (row) row.remove();
        });
    }

    // ─── Smooth scroll for anchor links ───
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ─── Back to top ───
    const backToTop = document.createElement('button');
    backToTop.className = 'back-to-top hidden';
    backToTop.innerHTML = '<i class="fa-solid fa-arrow-up" aria-hidden="true"></i>';
    backToTop.setAttribute('aria-label', 'Lên đầu trang');
    document.body.appendChild(backToTop);

    window.addEventListener('scroll', () => {
        backToTop.classList.toggle('hidden', window.scrollY < 400);
    }, { passive: true });

    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // ─── Toast notification system ───
    window.showToast = function(message, type) {
        type = type || 'success';
        const container = document.getElementById('toast-container');
        if (!container) {
            const c = document.createElement('div');
            c.id = 'toast-container';
            c.className = 'toast-container';
            document.body.appendChild(c);
        }
        const toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        toast.textContent = message;
        const container2 = document.getElementById('toast-container');
        container2.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('toast-visible'));
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            setTimeout(() => { if (toast.parentNode) toast.remove(); }, 300);
        }, 3500);
    };

    // ─── Image lazy loading ───
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        }, { rootMargin: '200px' });
        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // ─── Keyboard shortcut: close modals with Escape ───
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            const openDropdown = document.querySelector('.account-menu[open]');
            if (openDropdown) openDropdown.removeAttribute('open');
        }
    });

})();
