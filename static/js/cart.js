const CART_KEY = 'antidrone_cart';
const LEGACY_KEYS = ['antidrone_cart_v1'];

window.updateCartBadge = () => {
    console.log('[cart] updateCartBadge called');
    let cart = {};
    try {
        cart = JSON.parse(localStorage.getItem(CART_KEY) || '{}') || {};
    } catch (err) {
        console.error('[cart] Failed to parse cart:', err);
        cart = {};
    }
    if (!cart.items || typeof cart.items !== 'object') {
        cart.items = {};
    }
    const qty = Object.values(cart.items).reduce((sum, item) => sum + (Number(item.qty) || 0), 0);
    console.log('[cart] Total quantity:', qty);

    const badges = [];
    const badge = document.getElementById('cartBadge');
    if (badge) {
        badges.push(badge);
        console.log('[cart] Found badge by ID: cartBadge');
    } else {
        console.warn('[cart] Badge element #cartBadge NOT FOUND');
    }
    document.querySelectorAll('.js-cart-badge').forEach((node) => badges.push(node));

    console.log('[cart] Total badges found:', badges.length);
    if (!badges.length) {
        console.warn('[cart] No badge elements found!');
        return;
    }

    badges.forEach((node, index) => {
        node.textContent = String(qty);
        if (qty > 0) {
            node.removeAttribute('hidden');
            console.log(`[cart] Badge ${index}: showing with qty=${qty}`);
        } else {
            node.setAttribute('hidden', '');
            console.log(`[cart] Badge ${index}: hidden (qty=0)`);
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
    if (window.updateCartBadge) {
        window.updateCartBadge();
    }
    if (window.__cartRenderPage) {
        window.__cartRenderPage();
    }
}

window.addToCart = addToCart;
console.log('[cart] cart.js loaded; window.addToCart =', typeof window.addToCart);

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

    // Auto-cleanup: Set order timestamp
    const setOrderTimestamp = () => {
        localStorage.setItem('order_timestamp', Date.now());
        log('Order timestamp set');
    };

    // Auto-cleanup: Check if cart should be cleared (20 minutes after order)
    const checkAutoCleanCart = () => {
        const orderTime = localStorage.getItem('order_timestamp');
        if (!orderTime) return;

        const elapsed = Date.now() - parseInt(orderTime);
        const TWENTY_MINUTES = 20 * 60 * 1000; // 20 minutes in milliseconds

        if (elapsed > TWENTY_MINUTES) {
            clearCart();
            localStorage.removeItem('order_timestamp');
            log('Auto-cleaned cart after 20 minutes');
        }
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
            `Ціна: ${priceText}`,
        ].filter(Boolean);
        return lines.join('\n');
    };

    const openTelegramOrder = (button) => {
        const handle = button.dataset.telegram || 'antidrone_ukraine';
        const item = {
            name: button.dataset.name || 'Товар',
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
        const productCard = event.target.closest('.product-card[data-product-url]');
        if (productCard) {
            const isAction = event.target.closest('a, button');
            if (!isAction) {
                const url = productCard.dataset.productUrl;
                if (url) {
                    window.location.href = url;
                    return;
                }
            }
        }

        const addButton = event.target.closest('.js-add-to-cart');
        if (addButton) {
            if (addButton.dataset.addMode !== 'direct') {
                log('add button click', addButton.dataset);
                window.addToCart(addButton);

                // Animation: Button "Added!" feedback
                const originalText = addButton.textContent;
                addButton.textContent = '✓ Додано!';
                addButton.classList.add('btn-added');
                setTimeout(() => {
                    addButton.textContent = originalText;
                    addButton.classList.remove('btn-added');
                }, 1500);

                // Animation: Cart icon pulse
                const cartIcon = document.querySelector('.header-cart i, .header-action i.bi-cart3');
                if (cartIcon) {
                    cartIcon.classList.add('pulse');
                    setTimeout(() => cartIcon.classList.remove('pulse'), 500);
                }

                // Animation: Badge bounce
                const badge = document.getElementById('cartBadge');
                if (badge) {
                    badge.classList.add('bounce');
                    setTimeout(() => badge.classList.remove('bounce'), 300);
                }
            }
            return;
        }

        const telegramButton = event.target.closest('.js-telegram-order');
        if (telegramButton) {
            event.preventDefault();
            openTelegramOrder(telegramButton);
            return;
        }

        const checkoutTrigger = event.target.closest('[data-checkout-start]');
        if (checkoutTrigger) {
            event.preventDefault();
            startCheckout();
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
        console.log('[cart] DOMContentLoaded fired');
        checkAutoCleanCart();
        if (window.updateCartBadge) {
            window.updateCartBadge();
            console.log('[cart] Badge updated on DOMContentLoaded');
        }
        renderCartPage();
    });

    const checkoutState = {
        items: [],
        total: 0,
    };

    const getCookie = (name) => {
        const match = document.cookie.match(new RegExp(`(?:^|; )${name.replace(/([$?*|{}\]\\^])/g, '\\$1')}=([^;]*)`));
        return match ? decodeURIComponent(match[1]) : '';
    };

    const showToast = (message, tone = 'error') => {
        const toast = document.getElementById('checkout-toast');
        if (!toast) {
            alert(message);
            return;
        }
        toast.textContent = message;
        toast.classList.toggle('is-error', tone === 'error');
        toast.classList.add('is-visible');
        toast.removeAttribute('hidden');
        clearTimeout(toast.__hideTimer);
        toast.__hideTimer = setTimeout(() => {
            toast.classList.remove('is-visible');
            toast.setAttribute('hidden', '');
        }, 4200);
    };

    const renderCheckoutPreview = () => {
        const itemsContainer = document.getElementById('checkout-modal-items');
        const totalContainer = document.getElementById('checkout-modal-total');
        if (!itemsContainer || !totalContainer) return;

        if (!checkoutState.items.length) {
            itemsContainer.innerHTML = '<div class="checkout-modal-empty">Кошик порожній.</div>';
            totalContainer.textContent = '';
            return;
        }

        const rows = checkoutState.items.map((item) => {
            const name = item.name || 'Товар';
            const qty = Number(item.qty) || 1;
            return `
                <div class="checkout-modal-row">
                    <span class="checkout-modal-name">${name}</span>
                    <span class="checkout-modal-qty">× ${qty}</span>
                </div>
            `;
        });

        itemsContainer.innerHTML = rows.join('');
        totalContainer.textContent = `Разом: ${formatPrice(checkoutState.total)} грн`;
    };

    const openCheckoutModal = () => {
        const modal = document.getElementById('checkout-modal');
        if (!modal) {
            showToast('Не вдалося відкрити вікно підтвердження.');
            return;
        }
        const errorBox = document.getElementById('checkout-modal-error');
        if (errorBox) {
            errorBox.textContent = '';
            errorBox.setAttribute('hidden', '');
        }
        renderCheckoutPreview();
        modal.removeAttribute('hidden');
        modal.classList.add('is-open');
        document.body.classList.add('modal-open');
    };

    const closeCheckoutModal = () => {
        const modal = document.getElementById('checkout-modal');
        if (!modal) return;
        modal.classList.remove('is-open');
        modal.setAttribute('hidden', '');
        document.body.classList.remove('modal-open');
    };

    const buildOrderPayload = () => ({
        items: checkoutState.items.map((item) => ({
            sku: String(item.sku || '').trim(),
            name: String(item.name || 'Товар').trim(),
            price: Math.round(Number(item.price) || 0),
            qty: Math.max(1, Math.round(Number(item.qty) || 1)),
        })),
        total: Math.round(Number(checkoutState.total) || 0),
        currency: 'UAH',
        source: 'site',
        page: window.location.href,
        ts: Date.now(),
    });

    const createOrder = async () => {
        const csrfToken = getCookie('csrftoken');
        if (!csrfToken) {
            throw new Error('Не вдалося отримати CSRF токен.');
        }

        const response = await fetch('/api/create-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(buildOrderPayload()),
        });

        if (!response.ok) {
            let errorMessage = 'Помилка при створенні замовлення.';
            try {
                const data = await response.json();
                if (data && data.error) {
                    errorMessage = data.error;
                }
            } catch (err) {
                // ignore parsing errors
            }
            throw new Error(errorMessage);
        }

        return response.json();
    };

    const startCheckout = () => {
        const cart = getCart();
        const items = Object.values(cart.items || {});
        if (!items.length) {
            showToast('Кошик порожній.');
            return;
        }
        checkoutState.items = items;
        checkoutState.total = items.reduce(
            (sum, item) => sum + (Number(item.price) || 0) * (Number(item.qty) || 1),
            0
        );
        openCheckoutModal();
    };

    const bindCheckoutModal = () => {
        const modal = document.getElementById('checkout-modal');
        if (!modal) return;

        modal.addEventListener('click', (event) => {
            const closeTarget = event.target.closest('[data-checkout-close]');
            if (closeTarget) {
                closeCheckoutModal();
            }
        });

        const cancelButton = modal.querySelector('[data-checkout-cancel]');
        if (cancelButton) {
            cancelButton.addEventListener('click', () => closeCheckoutModal());
        }

        const confirmButton = modal.querySelector('[data-checkout-confirm]');
        if (confirmButton) {
            confirmButton.addEventListener('click', async () => {
                if (!checkoutState.items.length) {
                    const errorBox = document.getElementById('checkout-modal-error');
                    if (errorBox) {
                        errorBox.textContent = 'Кошик порожній.';
                        errorBox.removeAttribute('hidden');
                    } else {
                        showToast('Кошик порожній.');
                    }
                    return;
                }
                confirmButton.disabled = true;
                confirmButton.setAttribute('aria-busy', 'true');
                const originalLabel = confirmButton.textContent;
                confirmButton.textContent = 'Відправляємо...';
                try {
                    const result = await createOrder();
                    if (!result || !result.order_id) {
                        throw new Error('Сервер не повернув номер замовлення.');
                    }
                    setOrderTimestamp();
                    closeCheckoutModal();
                    window.location.href = `https://t.me/antidrone_order_bot?start=${result.order_id}`;
                } catch (err) {
                    const errorBox = document.getElementById('checkout-modal-error');
                    if (errorBox) {
                        errorBox.textContent = err.message || 'Сталася помилка. Спробуйте ще раз.';
                        errorBox.removeAttribute('hidden');
                    } else {
                        showToast(err.message || 'Сталася помилка. Спробуйте ще раз.');
                    }
                } finally {
                    confirmButton.disabled = false;
                    confirmButton.removeAttribute('aria-busy');
                    confirmButton.textContent = originalLabel;
                }
            });
        }
    };

    window.__checkoutStart = startCheckout;
    bindCheckoutModal();

    // Mobile menu toggle
    const initMobileMenu = () => {
        console.log('[Mobile Menu] Initializing...');
        const toggle = document.querySelector('.mobile-toggle');
        const mobileNav = document.getElementById('mobile-nav');
        console.log('[Mobile Menu] Elements:', { toggle, mobileNav });

        if (!toggle || !mobileNav) {
            console.error('[Mobile Menu] Elements not found!');
            return;
        }

        toggle.addEventListener('click', () => {
            console.log('[Mobile Menu] Toggle clicked!');
            const isOpen = mobileNav.classList.toggle('is-open');
            console.log('[Mobile Menu] Is open:', isOpen);
            toggle.classList.toggle('is-active', isOpen);
            toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');

            const icon = toggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-list', !isOpen);
                icon.classList.toggle('bi-x-lg', isOpen);
            }
        });

        // Close menu when clicking on a link
        mobileNav.addEventListener('click', (e) => {
            if (e.target.closest('a')) {
                mobileNav.classList.remove('is-open');
                toggle.classList.remove('is-active');
                toggle.setAttribute('aria-expanded', 'false');
                const icon = toggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('bi-x-lg');
                    icon.classList.add('bi-list');
                }
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (mobileNav.classList.contains('is-open') &&
                !mobileNav.contains(e.target) &&
                !toggle.contains(e.target)) {
                console.log('[Mobile Menu] Closing (clicked outside)');
                mobileNav.classList.remove('is-open');
                toggle.classList.remove('is-active');
                toggle.setAttribute('aria-expanded', 'false');
                const icon = toggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('bi-x-lg');
                    icon.classList.add('bi-list');
                }
            }
        });
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileMenu);
    } else {
        initMobileMenu();
    }

    // Also update badge immediately if DOM is already ready
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        console.log('[cart] DOM already ready, updating badge immediately');
        setTimeout(() => {
            if (window.updateCartBadge) {
                window.updateCartBadge();
            }
        }, 0);
    }

    window.__cartUpdateBadge = window.updateCartBadge;
    window.__cartRenderPage = renderCartPage;
})();
