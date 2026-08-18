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
                variantInput.setAttribute('data-variant-label', variant.color_name + ' / ' + variant.size);
                if (stockText) stockText.textContent = 'Tồn kho: ' + variant.stock;
            } else {
                variantInput.value = '';
                variantInput.removeAttribute('data-variant-label');
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

    // ─── Gallery zoom (click ảnh chính mở lightbox) ───
    document.addEventListener('click', function(e) {
        var main = document.getElementById('detail-main-image');
        if (!main || e.target !== main) return;
        var src = main.currentSrc || main.src;
        var overlay = document.getElementById('gallery-zoom');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'gallery-zoom';
            overlay.className = 'gallery-zoom-overlay';
            overlay.setAttribute('role', 'dialog');
            overlay.setAttribute('aria-modal', 'true');
            overlay.setAttribute('aria-label', 'Xem ảnh phóng to');
            overlay.innerHTML = '<button type="button" class="gallery-zoom-close" aria-label="Đóng">&times;</button><img alt="" loading="lazy">';
            document.body.appendChild(overlay);
        }
        overlay.querySelector('img').src = src;
        overlay.classList.add('is-open');
        document.body.style.overflow = 'hidden';
    });
    document.addEventListener('click', function(e) {
        var overlay = document.getElementById('gallery-zoom');
        if (!overlay || !overlay.classList.contains('is-open')) return;
        if (e.target === overlay || e.target.closest('.gallery-zoom-close')) {
            overlay.classList.remove('is-open');
            document.body.style.overflow = '';
        }
    });
    document.addEventListener('keydown', function(e) {
        if (e.key !== 'Escape') return;
        var overlay = document.getElementById('gallery-zoom');
        if (overlay && overlay.classList.contains('is-open')) {
            overlay.classList.remove('is-open');
            document.body.style.overflow = '';
        }
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

        function appendSuggestions(suggestions) {
            if (!suggestions || !suggestions.length) return;
            const holder = document.createElement('div');
            holder.className = 'chat-suggestion-row';
            suggestions.forEach(text => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'chat-suggestion';
                btn.textContent = text;
                btn.addEventListener('click', () => sendMessage(btn.textContent || ''));
                holder.appendChild(btn);
            });
            chatMessages.appendChild(holder);
            scrollToBottom();
        }

        function fetchReply(message) {
            if (!endpoint) return Promise.resolve({ reply: getFallbackReply(message), suggestions: [] });
            return fetch(endpoint + '?q=' + encodeURIComponent(message), {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            }).then(r => {
                if (!r.ok) throw new Error('fail');
                return r.json();
            }).then(payload => ({
                reply: payload.reply || getFallbackReply(message),
                suggestions: payload.suggestions || []
            })).catch(() => ({ reply: getFallbackReply(message), suggestions: [] }));
        }

        function sendMessage(text) {
            const cleanText = (text || '').trim();
            if (!cleanText) return;
            appendMessage('user', cleanText);
            chatInput.value = '';
            chatInput.disabled = true;
            const loadingMsg = appendMessage('bot', 'Shop đang trả lời...');
            setTimeout(() => {
                fetchReply(cleanText).then(result => {
                    if (loadingMsg && loadingMsg.parentNode) loadingMsg.remove();
                    appendMessage('bot', result.reply);
                    appendSuggestions(result.suggestions);
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

    // ─── Variant matrix editor (admin) ───
    const matrixBody = document.getElementById('variant-matrix-body');
    const matrixHead = document.getElementById('variant-matrix-head');
    const matrixSizesBox = document.getElementById('variant-matrix-sizes');
    const matrixStockTotal = document.querySelector('.admin-product-form input[name="stock"]');

    function matrixToken(size) {
        return String(size).trim().toUpperCase().replace(/[^A-Za-z0-9]+/g, '_') || 'size';
    }
    function matrixExistingSizes() {
        const set = new Set();
        if (matrixSizesBox) {
            matrixSizesBox.querySelectorAll('input[name="matrix_sizes"]').forEach(inp => set.add(inp.value.trim().toUpperCase()));
        }
        matrixBody.querySelectorAll('.matrix-size-cell').forEach(cell => set.add(cell.dataset.size.toUpperCase()));
        return set;
    }
    function matrixNextColorIndex() {
        let max = -1;
        matrixBody.querySelectorAll('.variant-color-row').forEach(row => {
            const idx = parseInt(row.dataset.colorIndex, 10);
            if (!isNaN(idx) && idx > max) max = idx;
        });
        return max + 1;
    }
    function matrixBuildColorRow(index, sizes) {
        const tr = document.createElement('tr');
        tr.className = 'variant-color-row';
        tr.dataset.colorIndex = String(index);
        const cells = [
            '<td><div class="matrix-color-inputs">' +
            '<input type="text" name="matrix_color_name[]" placeholder="Đen">' +
            '<input type="color" name="matrix_color_code[]" value="#111111" title="Mã màu">' +
            '</div></td>',
            '<td class="variant-check"><input type="checkbox" name="matrix_color_active[]" value="' + index + '" checked></td>'
        ];
        sizes.forEach(size => {
            cells.push('<td class="matrix-size-cell" data-size="' + size + '"><input type="number" name="matrix_stock_' + index + '_' + matrixToken(size) + '" min="0" step="1" value="0" placeholder="0"></td>');
        });
        cells.push('<td><button type="button" class="btn danger small variant-color-remove">Xóa</button></td>');
        tr.innerHTML = cells.join('');
        return tr;
    }
    function matrixAddSizeColumn(size) {
        size = String(size).trim().toUpperCase();
        if (!size || matrixExistingSizes().has(size)) return;
        const token = matrixToken(size);
        if (matrixHead) {
            const th = document.createElement('th');
            th.className = 'matrix-size-col';
            th.textContent = size;
            matrixHead.insertBefore(th, matrixHead.querySelector('.matrix-corner-end'));
        }
        matrixBody.querySelectorAll('.variant-color-row').forEach(row => {
            const idx = row.dataset.colorIndex;
            const td = document.createElement('td');
            td.className = 'matrix-size-cell';
            td.dataset.size = size;
            td.innerHTML = '<input type="number" name="matrix_stock_' + idx + '_' + token + '" min="0" step="1" value="0" placeholder="0">';
            row.insertBefore(td, row.querySelector('.variant-color-remove').closest('td'));
        });
        if (matrixSizesBox) {
            const hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = 'matrix_sizes';
            hidden.value = size;
            matrixSizesBox.appendChild(hidden);
        }
        matrixUpdateStockTotal();
    }
    function matrixUpdateStockTotal() {
        if (!matrixStockTotal) return;
        let total = 0;
        matrixBody.querySelectorAll('.variant-color-row').forEach(row => {
            const active = row.querySelector('input[name="matrix_color_active[]"]');
            if (active && !active.checked) return;
            row.querySelectorAll('input[type="number"]').forEach(inp => {
                const value = parseInt(inp.value, 10);
                if (!isNaN(value) && value > 0) total += value;
            });
        });
        matrixStockTotal.value = total;
    }
    if (matrixBody && matrixHead) {
        const addColorBtn = document.getElementById('add-variant-color');
        if (addColorBtn) {
            addColorBtn.addEventListener('click', () => {
                matrixBody.appendChild(matrixBuildColorRow(matrixNextColorIndex(), matrixExistingSizes()));
            });
        }
        matrixBody.addEventListener('click', e => {
            const removeBtn = e.target.closest('.variant-color-remove');
            if (!removeBtn) return;
            const rows = matrixBody.querySelectorAll('.variant-color-row');
            if (rows.length <= 1) {
                rows[0].querySelectorAll('input[type="text"]').forEach(inp => { inp.value = ''; });
                rows[0].querySelectorAll('input[type="number"]').forEach(inp => { inp.value = '0'; });
                rows[0].querySelector('input[type="checkbox"]').checked = true;
                return;
            }
            removeBtn.closest('tr').remove();
            matrixUpdateStockTotal();
        });
        matrixBody.addEventListener('input', e => {
            if (e.target && e.target.type === 'number') matrixUpdateStockTotal();
        });
        matrixBody.addEventListener('change', e => {
            if (e.target && e.target.matches('input[name="matrix_color_active[]"]')) matrixUpdateStockTotal();
        });
        document.querySelectorAll('.add-size-quick').forEach(btn => {
            btn.addEventListener('click', () => matrixAddSizeColumn(btn.dataset.size));
        });
        const customSizeInput = document.getElementById('variant-custom-size');
        const addCustomSizeBtn = document.getElementById('add-variant-custom-size');
        function matrixAddCustomSize() {
            if (!customSizeInput) return;
            matrixAddSizeColumn(customSizeInput.value);
            customSizeInput.value = '';
            customSizeInput.focus();
        }
        if (addCustomSizeBtn) addCustomSizeBtn.addEventListener('click', matrixAddCustomSize);
        if (customSizeInput) {
            customSizeInput.addEventListener('keydown', e => {
                if (e.key === 'Enter') { e.preventDefault(); matrixAddCustomSize(); }
            });
        }
        matrixUpdateStockTotal();
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

    // ─── Gallery arrow navigation (data-gallery-dir) ───
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('[data-gallery-dir]');
        if (!btn) return;
        var dir = parseInt(btn.dataset.galleryDir, 10);
        var thumbs = document.querySelectorAll('[data-detail-image]');
        if (!thumbs.length) return;
        var arr = Array.from(thumbs);
        var idx = arr.findIndex(function(x) { return x.classList.contains('active'); });
        var next = dir === 1
            ? (idx < 0 ? 0 : (idx + 1) % arr.length)
            : (idx <= 0 ? arr.length - 1 : idx - 1);
        var target = arr[next];
        if (!target) return;
        var main = document.getElementById('detail-main-image');
        if (!main) return;
        main.style.opacity = '0';
        setTimeout(function() {
            main.src = target.dataset.detailImage;
            main.alt = target.dataset.detailAlt || main.alt;
            main.style.opacity = '1';
        }, 120);
        arr.forEach(function(x) { x.classList.remove('active'); });
        target.classList.add('active');
    });

    // ─── Size guide modal (data-modal) ───
    document.addEventListener('click', function(e) {
        var trigger = e.target.closest('[data-modal]');
        if (!trigger) return;
        var modalId = trigger.dataset.modal;
        var modal = document.getElementById(modalId);
        if (!modal) return;
        // A trigger inside an accordion <summary> must not toggle the accordion.
        if (trigger.closest('summary')) {
            e.preventDefault();
            e.stopPropagation();
        }
        var action = trigger.dataset.modalAction || 'open';
        if (action === 'open') {
            modal.classList.add('is-open');
        } else {
            modal.classList.remove('is-open');
        }
    });
    document.addEventListener('click', function(e) {
        var overlay = e.target.closest('.size-guide-overlay');
        if (overlay && e.target === overlay) {
            overlay.classList.remove('is-open');
        }
    });

    // ─── Order filter auto-submit (onchange) ───
    document.addEventListener('change', function(e) {
        var select = e.target.closest('[data-auto-submit]');
        if (select && select.form) select.form.submit();
    });

    // ─── Order card clickable ───
    document.addEventListener('click', function(e) {
        var card = e.target.closest('.order-card-clickable');
        if (!card) return;
        if (e.target.closest('a, button, input, textarea, select, form')) return;
        var link = card.querySelector('a[href]');
        if (link) window.location.href = link.href;
    });

    // ─── Admin tab switching (data-target) ───
    (function() {
        var tabs = document.querySelectorAll('.admin-tab[data-target]');
        var contents = {};
        tabs.forEach(function(tab) {
            var id = tab.dataset.target;
            contents[id] = document.getElementById(id);
        });
        function showTab(targetId) {
            tabs.forEach(function(t) { t.classList.remove('active'); });
            Object.keys(contents).forEach(function(id) {
                if (contents[id]) contents[id].classList.remove('active');
            });
            var targetTab = document.querySelector('.admin-tab[data-target="' + targetId + '"]');
            if (targetTab) targetTab.classList.add('active');
            if (contents[targetId]) contents[targetId].classList.add('active');
        }
        tabs.forEach(function(tab) {
            tab.addEventListener('click', function() {
                showTab(this.dataset.target);
            });
        });
        var hash = window.location.hash.replace('#', '');
        if (hash && contents[hash]) showTab(hash);
    })();

    // ─── Admin product search ───
    (function() {
        var searchInput = document.getElementById('admin-product-search');
        if (!searchInput) return;
        var table = document.querySelector('.admin-product-table tbody');
        if (!table) return;
        searchInput.addEventListener('input', function() {
            var q = this.value.trim().toLowerCase();
            table.querySelectorAll('tr').forEach(function(row) {
                if (row.classList.contains('admin-empty-row')) return;
                row.style.display = q && row.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
            });
        });
    })();

    // ─── Admin coupon edit/reset ───
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('[data-edit-coupon]');
        if (!btn) return;
        var el = function(id) { return document.getElementById(id); };
        el('coupon-id-input').value = btn.dataset.editCoupon;
        el('coupon-code-input').value = btn.dataset.couponCode;
        el('coupon-type-select').value = btn.dataset.couponType;
        el('coupon-value-input').value = btn.dataset.couponValue;
        el('coupon-min-input').value = btn.dataset.couponMin;
        el('coupon-max-input').value = btn.dataset.couponMax || '';
        el('coupon-active-input').checked = btn.dataset.couponActive === 'True';
        el('coupon-form-title').textContent = 'Chỉnh sửa mã';
        el('coupon-cancel-btn').style.display = '';
        var target = document.getElementById('admin-coupons');
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#coupon-cancel-btn')) return;
        var el = function(id) { return document.getElementById(id); };
        el('coupon-id-input').value = '';
        el('coupon-code-input').value = '';
        el('coupon-type-select').value = 'percent';
        el('coupon-value-input').value = '';
        el('coupon-min-input').value = '0';
        el('coupon-max-input').value = '';
        el('coupon-active-input').checked = true;
        el('coupon-form-title').textContent = 'Thêm mã mới';
        el('coupon-cancel-btn').style.display = 'none';
    });

    // ─── Admin bulk select ───
    (function() {
        var headerCheck = document.getElementById('admin-select-all-header');
        var footerCheck = document.getElementById('admin-select-all');
        if (!headerCheck) return;
        var checks = document.querySelectorAll('.admin-product-check');
        var bulkIds = document.getElementById('admin-bulk-ids');
        var bulkIdsShow = document.getElementById('admin-bulk-ids-show');
        var hideBtn = document.getElementById('admin-bulk-hide-btn');
        var showBtn = document.getElementById('admin-bulk-show-btn');
        function updateBulk() {
            var selected = [];
            checks.forEach(function(c) { if (c.checked) selected.push(c.value); });
            var ids = selected.join(',');
            if (bulkIds) bulkIds.innerHTML = ids ? '<input type="hidden" name="product_ids" value="' + ids + '"><input type="hidden" name="make_available" value="0">' : '';
            if (bulkIdsShow) bulkIdsShow.innerHTML = ids ? '<input type="hidden" name="product_ids" value="' + ids + '"><input type="hidden" name="make_available" value="1">' : '';
            if (hideBtn) hideBtn.disabled = !selected.length;
            if (showBtn) showBtn.disabled = !selected.length;
        }
        headerCheck.addEventListener('change', function() {
            checks.forEach(function(c) { c.checked = headerCheck.checked; });
            if (footerCheck) footerCheck.checked = headerCheck.checked;
            updateBulk();
        });
        if (footerCheck) {
            footerCheck.addEventListener('change', function() {
                checks.forEach(function(c) { c.checked = footerCheck.checked; });
                if (headerCheck) headerCheck.checked = footerCheck.checked;
                updateBulk();
            });
        }
        checks.forEach(function(c) { c.addEventListener('change', updateBulk); });
    })();

    // ─── Table scroll hint ───
    document.querySelectorAll('.table-wrap').forEach(function(wrap) {
        if (wrap.scrollWidth > wrap.clientWidth) {
            var hint = document.createElement('small');
            hint.textContent = '← Vuốt để xem thêm →';
            hint.style.cssText = 'display:block;text-align:center;font-size:0.7rem;color:var(--muted);padding:0.25rem 0 0';
            wrap.parentNode.insertBefore(hint, wrap.nextSibling);
        }
    });

    // ─── Keyboard shortcut: close modals with Escape ───
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            const openDropdown = document.querySelector('.account-menu[open]');
            if (openDropdown) openDropdown.removeAttribute('open');
        }
    });

    // ─── Star rating picker ───
    document.querySelectorAll('[data-star-rating]').forEach(group => {
        const input = group.querySelector('input[name="rating"]');
        group.querySelectorAll('.star').forEach(btn => {
            btn.addEventListener('click', () => {
                const value = parseInt(btn.dataset.starValue, 10);
                group.querySelectorAll('.star').forEach((s, i) => {
                    s.classList.toggle('active', i < value);
                    const icon = s.querySelector('i');
                    if (icon) icon.className = i < value ? 'fa-solid fa-star' : 'fa-regular fa-star';
                });
                if (input) input.value = value;
            });
        });
    });

    // ─── Static star display (summary + review items) ───
    document.querySelectorAll('[data-static-stars]').forEach(el => {
        const value = parseFloat(el.dataset.staticStars || '0');
        const whole = Math.floor(value);
        const frac = value - whole;
        el.querySelectorAll('[data-star-index]').forEach(icon => {
            const idx = parseInt(icon.dataset.starIndex, 10);
            if (idx <= whole) {
                icon.className = 'fa-solid fa-star is-fill';
            } else if (idx === whole + 1 && frac >= 0.3 && frac < 0.8) {
                icon.className = 'fa-solid fa-star-half-stroke is-half';
            } else if (idx === whole + 1 && frac >= 0.8) {
                icon.className = 'fa-solid fa-star is-fill';
            } else {
                icon.className = 'fa-regular fa-star';
            }
        });
    });

    // ─── Sticky buy bar (mobile) ───
    (function() {
        var sticky = document.getElementById('sticky-buy');
        var mainForm = document.getElementById('detail-buy-form');
        if (!sticky || !mainForm) return;
        var qtyInput = mainForm.querySelector('[data-qty-input]');
        var variantId = document.getElementById('variant-id-input');

        var shown = false;
        function maybeShow() {
            var nearBottom = window.innerHeight + window.scrollY >= document.body.scrollHeight - 480;
            var shouldShow = window.innerWidth <= 900 && window.scrollY > 420 && !nearBottom;
            if (shouldShow && !shown) { sticky.classList.add('is-visible'); sticky.setAttribute('aria-hidden', 'false'); shown = true; }
            else if (!shouldShow && shown) { sticky.classList.remove('is-visible'); sticky.setAttribute('aria-hidden', 'true'); shown = false; }
        }
        window.addEventListener('scroll', maybeShow, { passive: true });
        window.addEventListener('resize', maybeShow);
        maybeShow();

        function syncToSticky() {
            if (variantId && variantId.value) {
                var label = variantId.getAttribute('data-variant-label');
                var text = sticky.querySelector('.sticky-buy-info span');
                if (label && text) text.textContent = label;
            }
        }

        sticky.querySelectorAll('[data-detail-buy-submit]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var next = btn.dataset.stickyNext || '';
                mainForm.querySelectorAll('input[name="next"]').forEach(function(n) { n.remove(); });
                if (next) {
                    var nextInput = document.createElement('input');
                    nextInput.type = 'hidden';
                    nextInput.name = 'next';
                    nextInput.value = next;
                    mainForm.appendChild(nextInput);
                }
                if (variantId && variantId.value) {
                    var existing = mainForm.querySelector('input[name="variant_id"]');
                    if (existing) existing.value = variantId.value;
                    else {
                        var copy = document.createElement('input');
                        copy.type = 'hidden';
                        copy.name = 'variant_id';
                        copy.value = variantId.value;
                        mainForm.appendChild(copy);
                    }
                }
                if (qtyInput) {
                    var qtyCopy = mainForm.querySelector('[data-qty-input]');
                    if (qtyCopy) qtyCopy.value = qtyInput.value;
                }
                mainForm.submit();
            });
        });

        var picker = document.getElementById('variant-picker');
        if (picker && variantId) {
            picker.addEventListener('click', function() {
                setTimeout(syncToSticky, 0);
            });
        }
    })();

    // ─── Social proof: "người đang xem" (detail) ───
    (function() {
        var el = document.querySelector('[data-viewers-count]');
        if (!el) return;
        var base = 9 + Math.floor(Math.random() * 14);
        el.textContent = base;
        setInterval(function() {
            var drift = Math.floor(Math.random() * 3) - 1;
            base = Math.max(6, Math.min(28, base + drift));
            el.textContent = base;
        }, 9000);
    })();

    // ─── Flash sale countdown (home) ───
    (function() {
        var timer = document.querySelector('[data-flash-sale]');
        if (!timer) return;
        var hEl = timer.querySelector('[data-flash-h]');
        var mEl = timer.querySelector('[data-flash-m]');
        var sEl = timer.querySelector('[data-flash-s]');
        if (!hEl || !mEl || !sEl) return;
        // ponytail: countdown đến cuối ngày — đơn giản, không cần cấu hình
        function tick() {
            var now = new Date();
            var end = new Date(now);
            end.setHours(23, 59, 59, 999);
            var diff = Math.max(0, end - now);
            var h = Math.floor(diff / 3600000);
            var m = Math.floor((diff % 3600000) / 60000);
            var s = Math.floor((diff % 60000) / 1000);
            hEl.textContent = String(h).padStart(2, '0');
            mEl.textContent = String(m).padStart(2, '0');
            sEl.textContent = String(s).padStart(2, '0');
        }
        tick();
        setInterval(tick, 1000);
    })();

})();
