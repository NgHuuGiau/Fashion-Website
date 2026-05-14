(function () {
    var dataNode = document.getElementById("variant-data");
    var picker = document.getElementById("variant-picker");
    var colorSelect = document.getElementById("color-select");
    var sizeSelect = document.getElementById("size-select");
    var variantInput = document.getElementById("variant-id-input");
    var stockText = document.getElementById("variant-stock-text");

    if (!dataNode || !picker || !colorSelect || !sizeSelect || !variantInput) {
        return;
    }

    var variants = [];
    try {
        variants = JSON.parse(dataNode.textContent || "[]");
    } catch (e) {
        variants = [];
    }

    if (!variants.length) {
        return;
    }

    function uniqueSizesByColor(color) {
        var map = {};
        variants.forEach(function (item) {
            if (item.color_name === color) {
                map[item.size] = true;
            }
        });
        return Object.keys(map);
    }

    function findVariant(color, size) {
        for (var i = 0; i < variants.length; i++) {
            var item = variants[i];
            if (item.color_name === color && item.size === size) {
                return item;
            }
        }
        return null;
    }

    function renderSizeOptions(color, preferredSize) {
        var sizes = uniqueSizesByColor(color);
        sizeSelect.innerHTML = "";

        sizes.forEach(function (size) {
            var option = document.createElement("option");
            option.value = size;
            option.textContent = size;
            if (size === preferredSize) {
                option.selected = true;
            }
            sizeSelect.appendChild(option);
        });

        if (!sizeSelect.value && sizes.length) {
            sizeSelect.value = sizes[0];
        }
    }

    function applyVariant() {
        var color = colorSelect.value;
        var size = sizeSelect.value;
        var variant = findVariant(color, size);

        if (!variant) {
            variantInput.value = "";
            stockText.textContent = "Biến thể này hiện không khả dụng.";
            return;
        }

        variantInput.value = variant.id;
        stockText.textContent = "Tồn kho: " + variant.stock;
    }

    var defaultVariantId = parseInt(picker.getAttribute("data-default-variant") || "0", 10);
    var defaultVariant = variants.find(function (item) {
        return item.id === defaultVariantId;
    }) || variants[0];

    colorSelect.value = defaultVariant.color_name;
    renderSizeOptions(defaultVariant.color_name, defaultVariant.size);
    applyVariant();

    colorSelect.addEventListener("change", function () {
        renderSizeOptions(colorSelect.value, "");
        applyVariant();
    });

    sizeSelect.addEventListener("change", applyVariant);
})();

(function () {
    var mainImage = document.getElementById("detail-main-image");
    var thumbs = Array.prototype.slice.call(document.querySelectorAll("[data-detail-image]"));
    var prevButton = document.getElementById("detail-prev-image");
    var nextButton = document.getElementById("detail-next-image");
    var switchTimer = null;

    if (!mainImage || !thumbs.length) {
        return;
    }

    var currentIndex = thumbs.findIndex(function (thumb) {
        return thumb.classList.contains("active");
    });
    if (currentIndex < 0) {
        currentIndex = 0;
    }

    function showImageAt(index) {
        if (!thumbs.length) {
            return;
        }

        var normalizedIndex = index;
        if (normalizedIndex < 0) {
            normalizedIndex = thumbs.length - 1;
        }
        if (normalizedIndex >= thumbs.length) {
            normalizedIndex = 0;
        }

        var activeThumb = thumbs[normalizedIndex];
        var url = activeThumb.getAttribute("data-detail-image");
        var thumbPreview = activeThumb.querySelector("img");
        if (!url) {
            return;
        }

        currentIndex = normalizedIndex;
        thumbs.forEach(function (item) {
            item.classList.remove("active");
        });
        activeThumb.classList.add("active");

        if (mainImage.src === url) {
            if (thumbPreview && thumbPreview.alt) {
                mainImage.alt = thumbPreview.alt;
            }
            return;
        }

        if (switchTimer) {
            window.clearTimeout(switchTimer);
        }

        mainImage.classList.add("is-switching");
        switchTimer = window.setTimeout(function () {
            mainImage.src = url;
            if (thumbPreview && thumbPreview.alt) {
                mainImage.alt = thumbPreview.alt;
            }
            switchTimer = null;
        }, 120);
    }

    thumbs.forEach(function (thumb, index) {
        thumb.addEventListener("click", function () {
            showImageAt(index);
        });
    });

    if (prevButton) {
        prevButton.addEventListener("click", function () {
            showImageAt(currentIndex - 1);
        });
    }

    if (nextButton) {
        nextButton.addEventListener("click", function () {
            showImageAt(currentIndex + 1);
        });
    }

    mainImage.addEventListener("load", function () {
        mainImage.classList.remove("is-switching");
    });
})();

(function () {
    var toggle = document.getElementById("menu-toggle");
    var closeBtn = document.getElementById("menu-close");
    var menu = document.getElementById("side-menu");
    var overlay = document.getElementById("menu-overlay");

    if (!toggle || !closeBtn || !menu || !overlay) {
        return;
    }

    function openMenu() {
        menu.classList.add("open");
        overlay.classList.add("show");
        document.body.style.overflow = "hidden";
    }

    function closeMenu() {
        menu.classList.remove("open");
        overlay.classList.remove("show");
        document.body.style.overflow = "";
    }

    toggle.addEventListener("click", openMenu);
    closeBtn.addEventListener("click", closeMenu);
    overlay.addEventListener("click", closeMenu);
})();

(function () {
    var launcher = document.getElementById("chat-launcher");
    var chatbox = document.getElementById("support-chatbox");
    var backdrop = document.getElementById("chatbox-backdrop");
    var closeBtn = document.getElementById("chatbox-close");
    var form = document.getElementById("chatbox-form");
    var input = document.getElementById("chatbox-input");
    var messages = document.getElementById("chatbox-messages");
    var suggestions = document.querySelectorAll(".chat-suggestion");
    var endpoint = chatbox ? chatbox.getAttribute("data-chat-endpoint") : "";

    if (!launcher || !chatbox || !closeBtn || !form || !input || !messages || !backdrop) {
        return;
    }

    function scrollMessagesToBottom() {
        window.requestAnimationFrame(function () {
            messages.scrollTop = messages.scrollHeight;
        });
    }

    function appendMessage(role, text) {
        var item = document.createElement("article");
        var bubble = document.createElement("p");

        item.className = "chat-message " + role;
        bubble.textContent = text;
        item.appendChild(bubble);
        messages.appendChild(item);
        scrollMessagesToBottom();
        return item;
    }

    function openChatbox() {
        chatbox.classList.remove("hidden");
        backdrop.classList.remove("hidden");
        launcher.classList.add("hidden");
        document.body.style.overflow = "hidden";
        setTimeout(function () {
            input.focus();
            scrollMessagesToBottom();
        }, 50);
    }

    function closeChatbox() {
        chatbox.classList.add("hidden");
        backdrop.classList.add("hidden");
        launcher.classList.remove("hidden");
        document.body.style.overflow = "";
    }

    function getFallbackReply(message) {
        var text = (message || "").toLowerCase();

        if (text.indexOf("ship") !== -1 || text.indexOf("giao") !== -1 || text.indexOf("van chuyen") !== -1) {
            return "Shop có free ship toàn quốc cho đơn từ 499K. Bạn có thể thêm sản phẩm vào giỏ để xem phí ship cụ thể trước khi đặt hàng.";
        }

        if (text.indexOf("thanh toan") !== -1 || text.indexOf("chuyen khoan") !== -1 || text.indexOf("cod") !== -1) {
            return "Hiện shop hỗ trợ thanh toán khi nhận hàng và chuyển khoản ngân hàng. Ở trang checkout bạn có thể chọn phương thức phù hợp.";
        }

        if (text.indexOf("size") !== -1 || text.indexOf("kich co") !== -1 || text.indexOf("rong") !== -1) {
            return "Bạn nên vào trang chi tiết sản phẩm để chọn màu và size. Nếu đang phân vân, hãy gửi thêm chiều cao, cân nặng và form mặc mong muốn để shop tư vấn nhanh hơn.";
        }

        if (text.indexOf("don") !== -1 || text.indexOf("theo doi") !== -1 || text.indexOf("trang thai") !== -1) {
            return "Nếu đã đăng nhập, bạn vào mục Đơn hàng để xem trạng thái. Sau khi đặt thành công, hệ thống cũng hiện trang xác nhận đơn ngay trên web.";
        }

        if (text.indexOf("doi") !== -1 || text.indexOf("tra") !== -1 || text.indexOf("hoan") !== -1) {
            return "Bạn hãy liên hệ shop sớm nhất sau khi nhận hàng nếu cần đổi trả. Khi nhận hỗ trợ thủ công, shop cần mã đơn, sản phẩm và lý do đổi trả.";
        }

        if (text.indexOf("gio") !== -1 || text.indexOf("cart") !== -1 || text.indexOf("mua") !== -1) {
            return "Bạn có thể thêm sản phẩm vào giỏ hàng ngay tại trang chi tiết. Sau đó vào Giỏ hàng, kiểm tra số lượng và tiếp tục sang Checkout để đặt đơn.";
        }

        return "Mình có thể hỗ trợ các câu hỏi về size, ship, thanh toán, đổi trả và theo dõi đơn hàng. Bạn thử hỏi cụ thể hơn một chút nhé.";
    }

    function fetchReply(message) {
        if (!endpoint) {
            return Promise.resolve(getFallbackReply(message));
        }

        return fetch(endpoint + "?q=" + encodeURIComponent(message), {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("chat_request_failed");
                }
                return response.json();
            })
            .then(function (payload) {
                return payload.reply || getFallbackReply(message);
            })
            .catch(function () {
                return getFallbackReply(message);
            });
    }

    function sendMessage(text) {
        var cleanText = (text || "").trim();
        if (!cleanText) {
            return;
        }

        appendMessage("user", cleanText);
        input.value = "";
        input.disabled = true;
        var loadingMessage = appendMessage("bot", "Shop đang trả lời...");

        window.setTimeout(function () {
            fetchReply(cleanText).then(function (reply) {
                if (loadingMessage && loadingMessage.parentNode) {
                    loadingMessage.remove();
                }
                appendMessage("bot", reply);
                input.disabled = false;
                input.focus();
            });
        }, 180);
    }

    launcher.addEventListener("click", openChatbox);
    closeBtn.addEventListener("click", closeChatbox);
    backdrop.addEventListener("click", closeChatbox);
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !chatbox.classList.contains("hidden")) {
            closeChatbox();
        }
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        sendMessage(input.value);
    });

    suggestions.forEach(function (button) {
        button.addEventListener("click", function () {
            sendMessage(button.textContent || "");
        });
    });
})();

(function () {
    var addRowButton = document.getElementById("add-variant-row");
    var tableBody = document.getElementById("variant-table-body");

    if (!addRowButton || !tableBody) {
        return;
    }

    function makeRowKey() {
        return "row-" + Date.now() + "-" + Math.floor(Math.random() * 1000);
    }

    function buildRow() {
        var rowKey = makeRowKey();
        var row = document.createElement("tr");
        row.className = "variant-row";
        row.innerHTML = [
            '<td><input type="hidden" name="variant_row_key[]" value="' + rowKey + '"><input type="text" name="variant_color_name[]" placeholder="Đen"></td>',
            '<td><input type="text" name="variant_color_code[]" value="#111111" placeholder="#111111"></td>',
            '<td><input type="text" name="variant_size[]" placeholder="M"></td>',
            '<td><input type="number" name="variant_stock[]" min="0" step="1" value="0" placeholder="0"></td>',
            '<td class="variant-check"><input type="checkbox" name="variant_is_active[]" value="' + rowKey + '" checked></td>',
            '<td><button type="button" class="btn danger small variant-remove">Xóa</button></td>'
        ].join("");
        return row;
    }

    addRowButton.addEventListener("click", function () {
        tableBody.appendChild(buildRow());
    });

    tableBody.addEventListener("click", function (event) {
        var target = event.target;
        if (!target.classList.contains("variant-remove")) {
            return;
        }

        var rows = tableBody.querySelectorAll(".variant-row");
        if (rows.length <= 1) {
            var inputs = rows[0].querySelectorAll("input");
            inputs.forEach(function (input) {
                if (input.type === "checkbox") {
                    input.checked = true;
                } else if (input.type === "number") {
                    input.value = "0";
                } else if (input.name === "variant_color_code[]") {
                    input.value = "#111111";
                } else {
                    input.value = "";
                }
            });
            return;
        }

        var row = target.closest(".variant-row");
        if (row) {
            row.remove();
        }
    });
})();

(function () {
    var priceInputs = Array.prototype.slice.call(document.querySelectorAll("[data-price-input]"));

    if (!priceInputs.length) {
        return;
    }

    function formatPriceInputValue(value) {
        var digits = String(value || "").replace(/\D/g, "");
        if (!digits) {
            return "";
        }

        return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    priceInputs.forEach(function (input) {
        input.value = formatPriceInputValue(input.value);

        input.addEventListener("input", function () {
            input.value = formatPriceInputValue(input.value);
        });

        input.addEventListener("blur", function () {
            input.value = formatPriceInputValue(input.value);
        });
    });
})();
