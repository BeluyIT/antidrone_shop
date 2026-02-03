const CART_KEY = 'antidrone_cart';
const LEGACY_KEYS = ['antidrone_cart_v1'];

window.updateCartBadge = () => {
    let cart = {};
    try {
        cart = JSON.parse(localStorage.getItem(CART_KEY) || '{}') || {};
    } catch (err) {
        cart = {};
    }
    if (!cart.items || typeof cart.items !== 'object') {
        cart.items = {};
    }
    const qty = Object.values(cart.items).reduce((sum, item) => sum + (Number(item.qty) || 0), 0);
    const badges = [];
    const badge = document.getElementById('cartBadge');
    if (badge) {
        badges.push(badge);
    }
    document.querySelectorAll('.js-cart-badge').forEach((node) => badges.push(node));
    if (!badges.length) return;
    badges.forEach((node) => {
        node.textContent = String(qty);
        if (qty > 0) {
            node.removeAttribute('hidden');
        } else {
            node.setAttribute('hidden', '');
        }
    });
};

function addToCart(button) {
    console.log('[cart] addToCart called', button);
    if (!window.__cartAddItem) {
        console.log('[cart] addToCart called before cart init, fallback to direct save');
    }
    if (!button || !button.dataset) {
        return;
    }
    const item = {
        id: String(button.dataset.productId || button.dataset.id || ''),
        name: button.dataset.name || 'Товар',
        sku: button.dataset.sku || '',
        price: Number(button.dataset.price) || 0,
        image: button.dataset.image || '',
        qty: 1,
    };
    if (!item.id) return;
    if (window.__cartAddItem) {
        window.__cartAddItem(item);
        return;
    }
    let cart = {};
    try {
        cart = JSON.parse(localStorage.getItem(CART_KEY) || '{}') || {};
    } catch (err) {
        cart = {};
    }
    if (!cart.items || typeof cart.items !== 'object') {
        cart.items = {};
    }
    const existing = cart.items[item.id];
    if (existing) {
        existing.qty = (Number(existing.qty) || 0) + 1;
        if (!existing.image && item.image) {
            existing.image = item.image;
        }
    } else {
        cart.items[item.id] = item;
    }
    console.log('[cart] before save', cart);
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    console.log('[cart] after save', localStorage.getItem(CART_KEY));
    if (window.__cartUpdateBadge) {
        window.__cartUpdateBadge();
    }
    if (window.__cartRenderPage) {
        window.__cartRenderPage();
    }
}

window.addToCart = addToCart;
console.log('[cart] cart.js loaded; window.addToCart =', typeof window.addToCart);

window.checkoutToTelegram = (event) => {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    }

    let cart = {};
    try {
        cart = JSON.parse(localStorage.getItem(CART_KEY) || '{}') || {};
    } catch (err) {
        cart = {};
    }
    if (!cart.items || typeof cart.items !== 'object') {
        cart.items = {};
    }
    const items = Object.values(cart.items);
    if (!items.length) {
        alert('Кошик порожній!');
        return false;
    }

    // Prepare data for Telegram bot deep link
    const orderData = items.map((item) => ({
        id: String(item.id || ''),
        name: item.name || 'Товар',
        sku: item.sku || '',
        price: Number(item.price) || 0,
        qty: Number(item.qty) || 1,
    }));

    // Encode to base64 for deep link (URL-safe)
    const jsonData = JSON.stringify(orderData);
    const encoded = btoa(unescape(encodeURIComponent(jsonData)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');

    // Open Telegram bot with order data
    const botUsername = 'antidrone_order_bot';
    const url = `https://t.me/${botUsername}?start=${encoded}`;

    console.log('[cart] Opening Telegram bot:', url);
    window.open(url, '_blank', 'noopener');
    return false;
};

(() => {
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
        if (window.updateCartBadge) {
            window.updateCartBadge();
        }
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

    const addItem = (item) => {
        const cart = getCart();
        const existing = cart.items[item.id];
        if (existing) {
            existing.qty = (Number(existing.qty) || 0) + (Number(item.qty) || 1);
            if (!existing.image && item.image) {
                existing.image = item.image;
            }
        } else {
            cart.items[item.id] = { ...item, qty: Number(item.qty) || 1 };
        }
        log('before save', cart);
        log('add item', item);
        saveCart(cart);
        log('after save', localStorage.getItem(CART_KEY));
    };

    window.__cartAddItem = addItem;

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

        const totalEl = summary.querySelector('#cart-total');
        const checkoutButton = summary.querySelector('.btn-checkout');
        const clearButton = summary.querySelector('.btn-clear-cart');

        if (!items.length) {
            const catalogUrl = container.dataset.catalogUrl || '/catalog/';
            container.innerHTML = `<div class="cart-empty"><div class="cart-empty-text">Кошик порожній.</div><a class="btn btn-primary btn-ghost" href="${catalogUrl}">Перейти до каталогу</a></div>`;
            if (totalEl) {
                totalEl.textContent = 'Разом: 0 грн';
            }
            if (checkoutButton) {
                checkoutButton.setAttribute('aria-disabled', 'true');
                checkoutButton.dataset.cartEmpty = 'true';
            }
            if (clearButton) {
                clearButton.disabled = true;
            }
            return;
        }

        let total = 0;
        const rows = items.map((item) => {
            const price = Number(item.price) || 0;
            const qty = Number(item.qty) || 0;
            const lineTotal = price * qty;
            total += lineTotal;
            const thumb = item.image
                ? `<img src="${item.image}" alt="${item.name || 'Товар'}">`
                : `<div class="cart-thumb-placeholder"></div>`;
            return `
                <div class="cart-row">
                    <div class="cart-cell cart-thumb">${thumb}</div>
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
        if (totalEl) {
            totalEl.textContent = `Разом: ${formatPrice(total)} грн`;
        }
        if (checkoutButton) {
            checkoutButton.removeAttribute('aria-disabled');
            checkoutButton.dataset.cartEmpty = 'false';
        }
        if (clearButton) {
            clearButton.disabled = false;
        }
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
        if (window.updateCartBadge) {
            window.updateCartBadge();
        }
        renderCartPage();
    });

    window.__cartUpdateBadge = window.updateCartBadge;
    window.__cartRenderPage = renderCartPage;
})();
