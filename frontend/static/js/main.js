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
            stockText.textContent = "Bien the nay hien khong kha dung.";
            return;
        }

        variantInput.value = variant.id;
        stockText.textContent = "Ton kho: " + variant.stock;
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
