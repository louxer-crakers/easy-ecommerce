// E-Commerce Application - Main JavaScript

// ========================================
// Utility Functions
// ========================================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = toast.querySelector('.toast-message');
    const toastIcon = toast.querySelector('.toast-icon');

    toast.classList.remove('success', 'error', 'show');
    toastMessage.textContent = message;

    if (type === 'success') {
        toastIcon.className = 'toast-icon fas fa-check-circle';
        toast.classList.add('success');
    } else {
        toastIcon.className = 'toast-icon fas fa-exclamation-circle';
        toast.classList.add('error');
    }

    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Set Auth state
function updateAuthUI() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    const authLink = document.getElementById('auth-link');
    const userMenu = document.getElementById('user-menu');
    const userNameDisplay = document.getElementById('user-name-display');
    const ordersLink = document.getElementById('orders-link');
    const adminLink = document.getElementById('admin-link');

    if (token && user.name) {
        // Logged in
        authLink.style.display = 'none';
        userMenu.style.display = 'block';
        if (userNameDisplay) userNameDisplay.textContent = user.name;
        if (ordersLink) ordersLink.style.display = 'flex';
        if (adminLink) adminLink.style.display = 'flex';
    } else {
        // Not logged in
        authLink.style.display = 'flex';
        userMenu.style.display = 'none';
        if (ordersLink) ordersLink.style.display = 'none';
        if (adminLink) adminLink.style.display = 'none';
    }
}

// User dropdown toggle
document.addEventListener('DOMContentLoaded', () => {
    const userBtn = document.getElementById('user-btn');
    const userDropdown = document.getElementById('user-dropdown');

    if (userBtn && userDropdown) {
        userBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            userDropdown.classList.remove('show');
        });
    }

    // Logout from dropdown
    const logoutBtnDropdown = document.getElementById('logout-btn-dropdown');
    if (logoutBtnDropdown) {
        logoutBtnDropdown.addEventListener('click', () => {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            showToast('Logged out successfully', 'success');
            setTimeout(() => window.location.href = '/', 1000);
        });
    }

    updateAuthUI();
    updateCartCount();
});

// Update cart count
function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const badge = document.getElementById('cart-count');
    if (badge) {
        badge.textContent = totalItems;
        badge.style.display = totalItems > 0 ? 'inline-block' : 'none';
    }
}

// Auth check for protected routes
function requireAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        sessionStorage.setItem('returnUrl', window.location.pathname);
        window.location.href = '/auth';
        return false;
    }
    return true;
}

// API request with auth
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('token');

    if (!token) {
        throw new Error('Not authenticated');
    }

    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, options);

    // Handle 401 - token expired
    if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        sessionStorage.setItem('returnUrl', window.location.pathname);
        window.location.href = '/auth';
        throw new Error('Session expired');
    }

    return response;
}
