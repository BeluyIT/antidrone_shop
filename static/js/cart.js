(() => {
    const CART_KEY = 'antidrone_cart_v1';

    const safeParse = (value) => {
        if (!value) return null;
        try {
            return JSON.parse(value);
        } catch (err) {
            return null;
        }
    };

    const getCart = () => {
        const data = safeParse(localStorage.getItem(CART_KEY)) || {};
        if (!data.items || typeof data.items !== 'object') {
            data.items = {};
        }
        return data;
    };

    const saveCart = (cart) => {
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
        updateBadge();
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
        saveCart(cart);
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

        if (!items.length) {
            container.innerHTML = '<div class="cart-empty">Кошик порожній.</div>';
            summary.innerHTML = '<div class="cart-total">Разом: 0 UAH</div>';
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
        summary.innerHTML = `<div class="cart-total">Разом: ${formatPrice(total)} UAH</div>`;
    };

    document.addEventListener('click', (event) => {
        const addButton = event.target.closest('.js-add-to-cart');
        if (addButton) {
            const item = {
                id: String(addButton.dataset.id || ''),
                name: addButton.dataset.name || 'Товар',
                sku: addButton.dataset.sku || '',
                price: Number(addButton.dataset.price) || 0,
                qty: 1,
            };
            if (item.id) {
                addItem(item);
            }
            return;
        }

        const actionButton = event.target.closest('[data-cart-action]');
        if (!actionButton) return;

        const action = actionButton.dataset.cartAction;
        const id = String(actionButton.dataset.cartId || '');
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
