(() => {
    const CART_KEY = 'antidrone_cart';
    const LEGACY_KEYS = ['antidrone_cart_v1'];
    const log = (...args) => console.log('[cart]', ...args);
    log('cart.js loaded');

    const safeParse = (value) => {
        if (!value) return null;
        try {
            return JSON.parse(value);
        } catch (err) {
            return null;
        }
    };

    const loadStoredCart = () => {
        let raw = localStorage.getItem(CART_KEY);
        if (!raw) {
            for (const key of LEGACY_KEYS) {
                raw = localStorage.getItem(key);
                if (raw) {
                    localStorage.setItem(CART_KEY, raw);
                    localStorage.removeItem(key);
                    log('migrated cart key', key, '->', CART_KEY);
                    break;
                }
            }
        }
        log('load cart raw', raw);
        return safeParse(raw) || {};
    };

    const getCart = () => {
        const data = loadStoredCart();
        if (!data.items || typeof data.items !== 'object') {
            data.items = {};
        }
        return data;
    };

    const saveCart = (cart) => {
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
        log('save cart', cart);
        updateBadge();
    };

    const clearCart = () => {
        const cart = { items: {} };
        saveCart(cart);
        renderCartPage();
    };

    const getTotalQty = (cart) => {
        return Object.values(cart.items).reduce((sum, item) => sum + (Number(item.qty) || 0), 0);
    };

    const formatPrice = (value) => {
        const amount = Number(value) || 0;
        return new Intl.NumberFormat('uk-UA', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount);
    };

    const buildTelegramMessage = (item) => {
        const priceValue = Number(item.price) || 0;
        const priceText = priceValue > 0 ? `${formatPrice(priceValue)} UAH` : 'ціна за запитом';
        const lines = [
            'Запит на товар:',
            item.name ? `Назва: ${item.name}` : null,
            item.sku ? `SKU: ${item.sku}` : null,
            `Ціна: ${priceText}`,
        ].filter(Boolean);
        return lines.join('\n');
    };

    const openTelegramOrder = (button) => {
        const handle = button.dataset.telegram || 'antidrone_ukraine';
        const item = {
            name: button.dataset.name || 'Товар',
            sku: button.dataset.sku || '',
            price: Number(button.dataset.price) || 0,
        };
        const message = buildTelegramMessage(item);
        const url = `https://t.me/${handle}?text=${encodeURIComponent(message)}`;
        window.open(url, '_blank', 'noopener');
    };

    const updateBadge = () => {
        const badges = document.querySelectorAll('.js-cart-badge');
        if (!badges.length) return;
        const qty = getTotalQty(getCart());
        badges.forEach((badge) => {
            badge.textContent = String(qty);
        });
    };

    const addItem = (item) => {
        const cart = getCart();
        const existing = cart.items[item.id];
        if (existing) {
            existing.qty = (Number(existing.qty) || 0) + (Number(item.qty) || 1);
        } else {
            cart.items[item.id] = { ...item, qty: Number(item.qty) || 1 };
        }
        log('before save', cart);
        log('add item', item);
        saveCart(cart);
        log('after save', localStorage.getItem(CART_KEY));
    };

    const extractItemFromElement = (element) => ({
        id: String(element.dataset.productId || element.dataset.id || ''),
        name: element.dataset.name || 'Товар',
        sku: element.dataset.sku || '',
        price: Number(element.dataset.price) || 0,
        qty: 1,
    });

    window.addToCart = (payload) => {
        if (!payload) return;
        const element = payload instanceof HTMLElement ? payload : null;
        const item = element ? extractItemFromElement(element) : {
            id: String(payload.id || payload.productId || ''),
            name: payload.name || 'Товар',
            sku: payload.sku || '',
            price: Number(payload.price) || 0,
            qty: Number(payload.qty) || 1,
        };
        log('addToCart called', item);
        if (item.id) {
            addItem(item);
        }
    };

    const updateItemQty = (id, delta) => {
        const cart = getCart();
        const item = cart.items[id];
        if (!item) return;
        const nextQty = (Number(item.qty) || 0) + delta;
        if (nextQty <= 0) {
            delete cart.items[id];
        } else {
            item.qty = nextQty;
        }
        saveCart(cart);
        renderCartPage();
    };

    const removeItem = (id) => {
        const cart = getCart();
        if (cart.items[id]) {
            delete cart.items[id];
            saveCart(cart);
            renderCartPage();
        }
    };

    const renderCartPage = () => {
        const container = document.getElementById('cart-items');
        const summary = document.getElementById('cart-summary');
        if (!container || !summary) return;

        const cart = getCart();
        const items = Object.values(cart.items);
        log('render cart items', items.length);

        if (!items.length) {
            const catalogUrl = container.dataset.catalogUrl || '/catalog/';
            container.innerHTML = `\n                <div class="cart-empty">\n                    <div class="cart-empty-text">Кошик порожній.</div>\n                    <a class="btn btn-primary btn-ghost" href="${catalogUrl}">Перейти до каталогу</a>\n                </div>\n            `;\n            summary.innerHTML = '<div class="cart-total">Разом: 0 UAH</div>';
            return;
        }

        let total = 0;
        const rows = items.map((item) => {
            const price = Number(item.price) || 0;
            const qty = Number(item.qty) || 0;
            const lineTotal = price * qty;
            total += lineTotal;
            return `
                <div class="cart-row">
                    <div class="cart-cell">
                        <div class="cart-title">${item.name || 'Товар'}</div>
                        ${item.sku ? `<div class="cart-sku">SKU: ${item.sku}</div>` : ''}
                    </div>
                    <div class="cart-cell cart-price">${formatPrice(price)} UAH</div>
                    <div class="cart-cell cart-qty">
                        <button class="btn btn-primary btn-qty" data-cart-action="dec" data-cart-id="${item.id}">−</button>
                        <span class="cart-qty-value">${qty}</span>
                        <button class="btn btn-primary btn-qty" data-cart-action="inc" data-cart-id="${item.id}">+</button>
                    </div>
                    <div class="cart-cell cart-line-total">${formatPrice(lineTotal)} UAH</div>
                    <div class="cart-cell cart-actions">
                        <button class="btn btn-primary btn-remove" data-cart-action="remove" data-cart-id="${item.id}">Видалити</button>
                    </div>
                </div>
            `;
        });

        container.innerHTML = rows.join('');
        summary.innerHTML = `\n            <div class="cart-total">Разом: ${formatPrice(total)} UAH</div>\n            <button class="btn btn-primary btn-clear-cart" data-cart-action="clear">Очистити кошик</button>\n        `;
    };

    document.addEventListener('click', (event) => {
        const addButton = event.target.closest('.js-add-to-cart');
        if (addButton) {
            if (addButton.dataset.addMode !== 'direct') {
                log('add button click', addButton.dataset);
                window.addToCart(addButton);
            }
            return;
        }

        const telegramButton = event.target.closest('.js-telegram-order');
        if (telegramButton) {
            event.preventDefault();
            openTelegramOrder(telegramButton);
            return;
        }

        const actionButton = event.target.closest('[data-cart-action]');
        if (!actionButton) return;

        const action = actionButton.dataset.cartAction;
        const id = String(actionButton.dataset.cartId || '');

        if (action === 'clear') {
            clearCart();
            return;
        }

        if (!id) return;

        if (action === 'inc') {
            updateItemQty(id, 1);
        } else if (action === 'dec') {
            updateItemQty(id, -1);
        } else if (action === 'remove') {
            removeItem(id);
        }
    });

    document.addEventListener('DOMContentLoaded', () => {
        updateBadge();
        renderCartPage();
    });
})();
