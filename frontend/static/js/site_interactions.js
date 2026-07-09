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
    var thumbs = document.querySelectorAll("[data-detail-image]");
    var prevBtn = document.getElementById("detail-prev-image");
    var nextBtn = document.getElementById("detail-next-image");

    if (!mainImage || !thumbs.length) {
        return;
    }

    var thumbList = Array.prototype.slice.call(thumbs);

    function setActiveByIndex(index) {
        if (!thumbList.length) {
            return;
        }
        var targetIndex = (index + thumbList.length) % thumbList.length;
        var target = thumbList[targetIndex];
        var url = target.getAttribute("data-detail-image");
        var alt = target.getAttribute("data-detail-alt") || mainImage.alt;
        if (!url) {
            return;
        }
        mainImage.src = url;
        mainImage.alt = alt;
        thumbList.forEach(function (item) {
            item.classList.remove("active");
        });
        target.classList.add("active");
    }

    thumbs.forEach(function (thumb) {
        thumb.addEventListener("click", function () {
            var url = thumb.getAttribute("data-detail-image");
            if (!url) {
                return;
            }

            mainImage.src = url;
            thumbList.forEach(function (item) {
                item.classList.remove("active");
            });
            thumb.classList.add("active");
        });
    });

    if (prevBtn) {
        prevBtn.addEventListener("click", function () {
            var activeIndex = -1;
            for (var i = 0; i < thumbList.length; i++) {
                if (thumbList[i].classList.contains("active")) {
                    activeIndex = i;
                    break;
                }
            }
            setActiveByIndex(activeIndex <= 0 ? thumbList.length - 1 : activeIndex - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", function () {
            var activeIndex = -1;
            for (var i = 0; i < thumbList.length; i++) {
                if (thumbList[i].classList.contains("active")) {
                    activeIndex = i;
                    break;
                }
            }
            setActiveByIndex(activeIndex < 0 ? 0 : activeIndex + 1);
        });
    }
})();

(function () {
    var steppers = document.querySelectorAll("[data-qty-step]");

    if (!steppers.length) {
        return;
    }

    steppers.forEach(function (button) {
        button.addEventListener("click", function () {
            var step = parseInt(button.getAttribute("data-qty-step") || "0", 10);
            var wrap = button.closest(".qty-stepper");
            var input = wrap ? wrap.querySelector("[data-qty-input]") : null;

            if (!input) {
                return;
            }

            var min = parseInt(input.getAttribute("min") || "1", 10);
            var max = parseInt(input.getAttribute("max") || "9999", 10);
            var current = parseInt(input.value || String(min), 10);
            var next = current + step;

            if (isNaN(next)) {
                next = min;
            }

            if (next < min) {
                next = min;
            }

            if (next > max) {
                next = max;
            }

            input.value = String(next);
            input.dispatchEvent(new Event("input", { bubbles: true }));
            input.dispatchEvent(new Event("change", { bubbles: true }));

            var form = wrap.closest("form");
            if (form && form.action && form.action.indexOf("cart_update") !== -1) {
                if (typeof form.requestSubmit === "function") {
                    form.requestSubmit();
                } else {
                    form.submit();
                }
            }
        });
    });
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
