// App State
let menuItems = [];
let cart = [];
let activeCategory = 'all';
let selectedOrderType = 'dine-in';
let currentUser = null;
let currentOrderId = null;
let statusPollInterval = null;

// DOM Elements
const logo = document.getElementById('logo');
const menuToggle = document.getElementById('menu-toggle');
const navLinks = document.getElementById('nav-links');
const cartTrigger = document.getElementById('cart-trigger');
const cartBadge = document.getElementById('cart-badge');
const cartDrawer = document.getElementById('cart-drawer');
const cartBackdrop = document.getElementById('cart-backdrop');
const closeCart = document.getElementById('close-cart');
const cartItemsContainer = document.getElementById('cart-items-container');
const cartTotal = document.getElementById('cart-total');
const btnProceedCheckout = document.getElementById('btn-proceed-checkout');

const modalBackdrop = document.getElementById('modal-backdrop');
const checkoutModal = document.getElementById('checkout-modal');
const closeModal = document.getElementById('close-modal');
const modalTitle = document.getElementById('modal-title');
const checkoutForm = document.getElementById('checkout-form');
const paymentSpinner = document.getElementById('payment-spinner');
const spTitle = document.getElementById('sp-title');
const spSubtext = document.getElementById('sp-subtext');

// Auth and Payment Verify Elements
const authHeaderWrapper = document.getElementById('auth-header-wrapper');
const authBackdrop = document.getElementById('auth-backdrop');
const authModal = document.getElementById('auth-modal');
const closeAuthModal = document.getElementById('close-auth-modal');

// Profile Elements
const profileBackdrop = document.getElementById('profile-backdrop');
const profileModal = document.getElementById('profile-modal');
const closeProfileModal = document.getElementById('close-profile-modal');
const profileOrdersFeed = document.getElementById('profile-orders-feed');

const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const panelLogin = document.getElementById('panel-login');
const panelRegister = document.getElementById('panel-register');

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginErrorMsg = document.getElementById('login-error-msg');
const registerErrorMsg = document.getElementById('register-error-msg');

// OTP registration wrapper elements
const registerFieldsWrapper = document.getElementById('register-fields-wrapper');
const registerOtpWrapper = document.getElementById('register-otp-wrapper');
const otpCodeInput = document.getElementById('otp-code');
const otpErrorMsg = document.getElementById('otp-error-msg');
const btnVerifyOtp = document.getElementById('btn-verify-otp');
const btnCancelOtp = document.getElementById('btn-cancel-otp');

const paymentPendingVerification = document.getElementById('payment-pending-verification');
const paymentSuccess = document.getElementById('payment-success');
const paymentFailed = document.getElementById('payment-failed');
const paymentUtrForm = document.getElementById('payment-utr-form');
const upiUtrInput = document.getElementById('upi-utr-input');
const utrErrorMsg = document.getElementById('utr-error-msg');

const btnSimSuccess = document.getElementById('btn-sim-success');
const btnSimFail = document.getElementById('btn-sim-fail');
const btnRetryPayment = document.getElementById('btn-retry-payment');

const orderTypeBtns = document.querySelectorAll('.order-type-btn');
const tableNumberGroup = document.getElementById('table-number-group');
const tableNumInput = document.getElementById('table-num');
const btnCloseSuccess = document.getElementById('btn-close-success');

// Page Load Initializer
window.addEventListener('DOMContentLoaded', () => {
  checkUserSession();
  fetchMenuItems();
  setupEventListeners();
  initGoogleSignIn();
});

// Check if user session is active on startup
async function checkUserSession() {
  try {
    const response = await fetch('/api/session');
    if (!response.ok) throw new Error('Session fetch failed');
    const result = await response.json();
    if (result.logged_in) {
      currentUser = result.user;
      renderAuthHeader(true);
    } else {
      currentUser = null;
      renderAuthHeader(false);
    }
  } catch (err) {
    console.error('Session check error:', err);
    renderAuthHeader(false);
  }
}

// Renders either Sign In or User Tag in Header
function renderAuthHeader(isLoggedIn) {
  if (isLoggedIn && currentUser) {
    authHeaderWrapper.innerHTML = `
      <div class="user-header-profile" id="btn-show-profile" style="cursor: pointer;">
        <i class="fa-regular fa-circle-user" style="color: var(--primary); font-size: 16px;"></i>
        <span>Hi, ${currentUser.name.split(' ')[0]}</span>
      </div>
      <button class="btn-logout-header" id="btn-logout" title="Log Out">
        <i class="fa-solid fa-arrow-right-from-bracket"></i>
      </button>
    `;
    document.getElementById('btn-logout').addEventListener('click', handleLogout);
    document.getElementById('btn-show-profile').addEventListener('click', showProfileModalView);
  } else {
    authHeaderWrapper.innerHTML = `
      <button class="cart-trigger" id="btn-show-auth" style="border: 1px solid var(--primary); color: var(--primary);">
        <i class="fa-regular fa-user"></i>
        <span>Sign In</span>
      </button>
    `;
    document.getElementById('btn-show-auth').addEventListener('click', showAuthModalView);
  }
}

// Show/Hide Auth Modals
function showAuthModalView() {
  resetAuthForms();
  authModal.classList.add('open');
  authBackdrop.classList.add('open');
}

function hideAuthModalView() {
  authModal.classList.remove('open');
  authBackdrop.classList.remove('open');
}

// User Profile Modal Functions
async function showProfileModalView() {
  if (!currentUser) return;
  
  // Populate details
  document.getElementById('profile-display-name').innerText = currentUser.name;
  document.getElementById('profile-display-phone').innerText = currentUser.phone;
  document.getElementById('profile-display-email').innerText = currentUser.email;
  
  // Open modal
  profileModal.classList.add('open');
  profileBackdrop.classList.add('open');
  
  // Load order history
  profileOrdersFeed.innerHTML = `
    <div style="text-align: center; padding: 30px; color: var(--text-muted);">
      <i class="fa-solid fa-spinner fa-spin" style="font-size: 24px; margin-bottom: 8px; display: block; color: var(--primary);"></i>
      Loading order history...
    </div>
  `;
  
  try {
    const response = await fetch('/api/user/orders');
    if (!response.ok) throw new Error('Failed to retrieve order history');
    const orders = await response.json();
    renderProfileOrders(orders);
  } catch (err) {
    console.error('Error fetching user orders:', err);
    profileOrdersFeed.innerHTML = `
      <div style="text-align: center; padding: 30px; color: #b33939;">
        <i class="fa-solid fa-triangle-exclamation" style="font-size: 24px; margin-bottom: 8px; display: block;"></i>
        Failed to load orders. Please try again.
      </div>
    `;
  }
}

function hideProfileModalView() {
  profileModal.classList.remove('open');
  profileBackdrop.classList.remove('open');
}

function renderProfileOrders(orders) {
  if (orders.length === 0) {
    profileOrdersFeed.innerHTML = `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <i class="fa-solid fa-clipboard-list" style="font-size: 32px; color: var(--border); margin-bottom: 8px; display: block;"></i>
        No orders placed yet.
      </div>
    `;
    return;
  }

  profileOrdersFeed.innerHTML = '';
  orders.forEach(order => {
    const orderCard = document.createElement('div');
    orderCard.style.cssText = 'background: #FAF9F6; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 16px; display: flex; flex-direction: column; gap: 12px;';
    
    const isPaid = order.payment_status === 'paid';
    const statusText = isPaid ? 'Paid' : (order.payment_status === 'failed' ? 'Failed' : 'Pending');
    const statusColor = isPaid ? 'var(--secondary)' : (order.payment_status === 'failed' ? '#b33939' : '#b8860b');
    
    let itemsListHtml = '';
    order.items.forEach(item => {
      itemsListHtml += `
        <div style="display: flex; justify-content: space-between; font-size: 13px; color: var(--text-main); margin-bottom: 4px;">
          <span><strong>${item.quantity}x</strong> ${item.item_name}</span>
          <span style="color: var(--text-muted);">&#8377;${(item.price * item.quantity).toFixed(2)}</span>
        </div>
      `;
    });

    orderCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px dashed var(--border); padding-bottom: 8px;">
        <div>
          <span style="font-weight: 700; color: var(--text-main); font-size: 14px;">${order.id}</span>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${order.created_at}</div>
        </div>
        <span style="font-size: 11px; font-weight: 700; color: ${statusColor}; text-transform: uppercase; background: rgba(0,0,0,0.03); padding: 2px 6px; border-radius: 4px;">
          ${statusText}
        </span>
      </div>
      <div>
        ${itemsListHtml}
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed var(--border); padding-top: 8px; font-size: 13px;">
        <span style="font-weight: 700; color: var(--text-main); font-size: 15px;">&#8377;${order.total_amount.toFixed(2)}</span>
        <span style="font-size: 11px; color: var(--text-muted);">${capitalize(order.order_type)} ${order.order_type === 'dine-in' ? `(Table ${order.table_number})` : ''}</span>
      </div>
    `;
    profileOrdersFeed.appendChild(orderCard);
  });
}

// Switch Login/Register Tabs
function switchAuthTab(tab) {
  if (tab === 'login') {
    tabLogin.classList.add('active');
    tabLogin.style.color = 'var(--primary)';
    tabLogin.style.borderBottomColor = 'var(--primary)';
    
    tabRegister.classList.remove('active');
    tabRegister.style.color = 'var(--text-muted)';
    tabRegister.style.borderBottomColor = 'transparent';
    
    panelLogin.style.display = 'block';
    panelRegister.style.display = 'none';
  } else {
    tabRegister.classList.add('active');
    tabRegister.style.color = 'var(--primary)';
    tabRegister.style.borderBottomColor = 'var(--primary)';
    
    tabLogin.classList.remove('active');
    tabLogin.style.color = 'var(--text-muted)';
    tabLogin.style.borderBottomColor = 'transparent';
    
    panelRegister.style.display = 'block';
    panelLogin.style.display = 'none';
  }
  loginErrorMsg.style.display = 'none';
  registerErrorMsg.style.display = 'none';
  resetRegisterOtpView();
}

function resetAuthForms() {
  loginForm.reset();
  registerForm.reset();
  loginErrorMsg.style.display = 'none';
  registerErrorMsg.style.display = 'none';
  switchAuthTab('login');
}

function resetRegisterOtpView() {
  registerFieldsWrapper.style.display = 'block';
  registerOtpWrapper.style.display = 'none';
  otpCodeInput.value = '';
  otpErrorMsg.style.display = 'none';
}

// Auth API Calls
async function handleLoginSubmit(e) {
  e.preventDefault();
  loginErrorMsg.style.display = 'none';
  
  const loginId = document.getElementById('login-id').value;
  const password = document.getElementById('login-password').value;

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login_id: loginId, password: password })
    });
    const result = await response.json();
    
    if (!response.ok) throw new Error(result.error || 'Login failed');
    
    currentUser = result.user;
    renderAuthHeader(true);
    hideAuthModalView();
    alert(`Signed in successfully! Welcome, ${currentUser.name}.`);
  } catch (err) {
    loginErrorMsg.innerText = err.message;
    loginErrorMsg.style.display = 'block';
  }
}

// Step 1 of registration: validate fields, complexity, confirm password, and request OTP
async function handleRegisterRequestOtp(e) {
  e.preventDefault();
  registerErrorMsg.style.display = 'none';
  
  const name = document.getElementById('reg-name').value.trim();
  const phone = document.getElementById('reg-phone').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const confirmPassword = document.getElementById('reg-confirm-password').value;

  // Confirm passwords match
  if (password !== confirmPassword) {
    registerErrorMsg.innerText = "Passwords do not match. Please re-enter.";
    registerErrorMsg.style.display = 'block';
    return;
  }

  // Password complexity regex (Capital, Small, Number, Special Char, Min 8 chars)
  const pwdRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  if (!pwdRegex.test(password)) {
    registerErrorMsg.innerText = "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character (e.g. @$!%*?&).";
    registerErrorMsg.style.display = 'block';
    return;
  }

  try {
    const response = await fetch('/api/register/request-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone, email, password, confirm_password: confirmPassword })
    });
    const result = await response.json();
    
    if (!response.ok) throw new Error(result.error || 'Failed to request OTP');
    
    // Transition registration form to single OTP verification state
    registerFieldsWrapper.style.display = 'none';
    registerOtpWrapper.style.display = 'block';
    
    alert('Verification code sent! Check your mobile number (SMS) or email.');
  } catch (err) {
    registerErrorMsg.innerText = err.message;
    registerErrorMsg.style.display = 'block';
  }
}

// Step 2 of registration: verify single code and create account
async function handleRegisterVerifyOtp() {
  otpErrorMsg.style.display = 'none';
  const code = otpCodeInput.value.trim();

  if (code.length !== 6 || isNaN(code)) {
    otpErrorMsg.innerText = 'Verification code must be exactly a 6-digit number.';
    otpErrorMsg.style.display = 'block';
    return;
  }

  try {
    const response = await fetch('/api/register/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reg_otp: code })
    });
    const result = await response.json();
    
    if (!response.ok) throw new Error(result.error || 'OTP verification failed');
    
    currentUser = result.user;
    renderAuthHeader(true);
    hideAuthModalView();
    alert(`Account created and verified successfully! Welcome, ${currentUser.name}.`);
  } catch (err) {
    otpErrorMsg.innerText = err.message;
    otpErrorMsg.style.display = 'block';
  }
}

async function handleLogout() {
  try {
    const response = await fetch('/api/logout', { method: 'POST' });
    if (response.ok) {
      currentUser = null;
      renderAuthHeader(false);
      alert('Logged out successfully.');
    }
  } catch (err) {
    console.error('Logout error:', err);
  }
}

// Fetch menu items from backend API
async function fetchMenuItems() {
  try {
    const response = await fetch('/api/menu');
    if (!response.ok) throw new Error('Failed to fetch menu');
    menuItems = await response.json();
    renderMenu(menuItems);
  } catch (error) {
    console.error('Error fetching menu:', error);
    document.getElementById('menu-grid').innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
        <i class="fa-solid fa-circle-exclamation" style="font-size: 32px; color: var(--primary); margin-bottom: 12px;"></i>
        <p>Sorry, we couldn't load the menu. Please check your connection or reload.</p>
      </div>
    `;
  }
}

// Render menu cards to the grid
function renderMenu(items) {
  const grid = document.getElementById('menu-grid');
  grid.innerHTML = '';

  const filtered = activeCategory === 'all' 
    ? items 
    : items.filter(item => item.category === activeCategory);

  if (filtered.length === 0) {
    grid.innerHTML = `<p style="grid-column:1/-1; text-align:center; color:var(--text-muted);">No items available in this category.</p>`;
    return;
  }

  filtered.forEach(item => {
    const card = document.createElement('div');
    card.className = 'menu-card';
    
    const imagePath = item.image ? item.image : 'images/cafe_interior.jpg';
    
    card.innerHTML = `
      <div class="menu-card-img-wrapper">
        <img class="menu-card-img" src="${imagePath}" alt="${item.name}" loading="lazy">
        <span class="menu-card-category">${capitalize(item.category)}</span>
      </div>
      <div class="menu-card-content">
        <div class="menu-card-header">
          <h3 class="menu-card-title">${item.name}</h3>
          <span class="menu-card-price">&#8377;${item.price}</span>
        </div>
        <p class="menu-card-desc">${item.description}</p>
        <div class="menu-card-footer">
          <button class="btn-add-cart" data-id="${item.id}">
            <i class="fa-solid fa-plus"></i> Add to Cart
          </button>
        </div>
      </div>
    `;
    
    card.querySelector('.btn-add-cart').addEventListener('click', () => {
      addToCart(item.id);
    });

    grid.appendChild(card);
  });
}

// Cart functions
function addToCart(itemId) {
  const item = menuItems.find(i => i.id === itemId);
  if (!item) return;

  const existing = cart.find(c => c.id === itemId);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({
      id: item.id,
      name: item.name,
      price: item.price,
      image: item.image,
      quantity: 1
    });
  }

  updateCart();
  animateCartBadge();
}

function updateCart() {
  renderCartItems();
  
  const totalCount = cart.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  
  cartBadge.innerText = totalCount;
  cartTotal.innerHTML = `&#8377;${totalPrice.toFixed(2)}`;
  btnProceedCheckout.disabled = cart.length === 0;
}

function renderCartItems() {
  if (cart.length === 0) {
    cartItemsContainer.innerHTML = `
      <div class="cart-empty-message">
        <i class="fa-solid fa-bag-shopping" style="font-size: 36px; margin-bottom: 12px; color: var(--border);"></i>
        <p>Your bag is empty.</p>
        <p style="font-size: 13px; margin-top: 4px;">Add delicious tiffins to get started!</p>
      </div>
    `;
    return;
  }

  cartItemsContainer.innerHTML = '';
  cart.forEach(item => {
    const itemEl = document.createElement('div');
    itemEl.className = 'cart-item';
    itemEl.innerHTML = `
      <img src="${item.image || 'images/cafe_interior.jpg'}" class="cart-item-img" alt="${item.name}">
      <div class="cart-item-info">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-price">&#8377;${item.price}</div>
      </div>
      <div class="cart-item-controls">
        <button class="cart-qty-btn decrease-btn" data-id="${item.id}"><i class="fa-solid fa-minus"></i></button>
        <span class="cart-qty-val">${item.quantity}</span>
        <button class="cart-qty-btn increase-btn" data-id="${item.id}"><i class="fa-solid fa-plus"></i></button>
        <button class="cart-item-remove remove-btn" data-id="${item.id}" aria-label="Remove item"><i class="fa-regular fa-trash-can"></i></button>
      </div>
    `;

    itemEl.querySelector('.decrease-btn').addEventListener('click', () => changeQuantity(item.id, -1));
    itemEl.querySelector('.increase-btn').addEventListener('click', () => changeQuantity(item.id, 1));
    itemEl.querySelector('.remove-btn').addEventListener('click', () => removeFromCart(item.id));

    cartItemsContainer.appendChild(itemEl);
  });
}

function changeQuantity(itemId, amount) {
  const item = cart.find(c => c.id === itemId);
  if (!item) return;
  
  item.quantity += amount;
  if (item.quantity <= 0) {
    removeFromCart(itemId);
  } else {
    updateCart();
  }
}

function removeFromCart(itemId) {
  cart = cart.filter(c => c.id !== itemId);
  updateCart();
}

function animateCartBadge() {
  cartBadge.style.transform = 'scale(1.4)';
  setTimeout(() => {
    cartBadge.style.transform = 'scale(1)';
  }, 200);
}

// Real-time status polling for payment confirmation
function startPaymentStatusPolling(orderId) {
  if (statusPollInterval) clearInterval(statusPollInterval);
  
  statusPollInterval = setInterval(async () => {
    try {
      const response = await fetch(`/api/payment/status/${orderId}`);
      const result = await response.json();
      
      if (result.success) {
        if (result.paid) {
          stopPaymentStatusPolling();
          showSuccessScreen(orderId, result.total_amount);
        } else if (result.failed) {
          stopPaymentStatusPolling();
          showFailureScreen(orderId);
        }
      }
    } catch (err) {
      console.error('Error polling status:', err);
    }
  }, 3000);
}

function stopPaymentStatusPolling() {
  if (statusPollInterval) {
    clearInterval(statusPollInterval);
    statusPollInterval = null;
  }
}

// Stage 1: Checkout Form Submit
async function handleCheckoutSubmit(e) {
  e.preventDefault();
  
  const name = document.getElementById('cust-name').value;
  const phone = document.getElementById('cust-phone').value;
  const table = selectedOrderType === 'dine-in' ? tableNumInput.value : 'N/A';

  checkoutForm.style.display = 'none';
  paymentSpinner.style.display = 'flex';
  spTitle.innerText = 'Creating Order';
  spSubtext.innerText = 'Saving order details to database...';
  modalTitle.innerText = 'Processing Order';
  
  try {
    const response = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        items: cart,
        name: name,
        phone: phone,
        order_type: selectedOrderType,
        table_number: table
      })
    });

    const result = await response.json();
    if (!result.success) throw new Error(result.error || 'Server rejected checkout');

    currentOrderId = result.order_id;

    // Transition to UPI Scan & Pay panel
    paymentSpinner.style.display = 'none';
    paymentPendingVerification.style.display = 'flex';
    modalTitle.innerText = 'UPI Payment';

    // Populate QR screen details
    document.getElementById('display-order-id').innerText = result.order_id;
    document.getElementById('display-payment-amount').innerHTML = `&#8377;${result.total_amount.toFixed(2)}`;
    
    // Generate UPI QR Code image
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=170x170&margin=5&data=${encodeURIComponent(result.upi_uri)}`;
    document.getElementById('upi-qr-image').src = qrUrl;

    // Mobile deep link
    document.getElementById('upi-deep-link').href = result.upi_uri;

    // Reset UTR form and start polling for status check
    paymentUtrForm.reset();
    utrErrorMsg.style.display = 'none';
    
    startPaymentStatusPolling(currentOrderId);

  } catch (error) {
    console.error('Checkout failed:', error);
    paymentSpinner.style.display = 'none';
    checkoutForm.style.display = 'block';
    modalTitle.innerText = 'Checkout';
    alert(error.message || 'Something went wrong during checkout. Please try again.');
  }
}

// Stage 2: UTR Payment Verification Form Submit (Fallback if auto-redirect takes long)
async function handlePaymentUtrSubmit(e) {
  e.preventDefault();
  utrErrorMsg.style.display = 'none';
  
  const utr = upiUtrInput.value.trim();
  if (utr.length !== 12 || isNaN(utr)) {
    utrErrorMsg.innerText = 'UTR must be exactly a 12-digit number.';
    utrErrorMsg.style.display = 'block';
    return;
  }

  stopPaymentStatusPolling();

  paymentPendingVerification.style.display = 'none';
  paymentSpinner.style.display = 'flex';
  spTitle.innerText = 'Verifying UPI Payment';
  spSubtext.innerText = 'Matching transaction reference in network settlement...';
  modalTitle.innerText = 'Payment Verification';

  try {
    const response = await fetch('/api/payment/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_id: currentOrderId,
        upi_utr: utr
      })
    });
    
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.error || 'Payment verification failed');

    showSuccessScreen(result.order_id, result.total_amount);

  } catch (error) {
    console.error('Verification failed:', error);
    paymentSpinner.style.display = 'none';
    paymentPendingVerification.style.display = 'flex';
    modalTitle.innerText = 'UPI Payment';
    utrErrorMsg.innerText = error.message || 'Verification failed. Please check UTR and re-submit.';
    utrErrorMsg.style.display = 'block';
    
    startPaymentStatusPolling(currentOrderId);
  }
}

// Shared helper to transition modal into confirmation screen
function showSuccessScreen(orderId, totalAmount) {
  paymentSpinner.style.display = 'none';
  paymentPendingVerification.style.display = 'none';
  paymentFailed.style.display = 'none';
  paymentSuccess.style.display = 'flex';
  modalTitle.innerText = 'Confirmed';

  document.getElementById('display-success-order-id').innerText = orderId;
  document.getElementById('display-success-amount').innerHTML = `&#8377;${totalAmount.toFixed(2)}`;

  // Clear the cart
  cart = [];
  updateCart();
}

// Shared helper to transition modal into failure screen
function showFailureScreen(orderId) {
  paymentSpinner.style.display = 'none';
  paymentPendingVerification.style.display = 'none';
  paymentSuccess.style.display = 'none';
  paymentFailed.style.display = 'flex';
  modalTitle.innerText = 'Payment Failed';

  document.getElementById('display-failed-order-id').innerText = orderId;
}

// Dev Simulator Actions
async function simulateOutcome(outcome) {
  if (!currentOrderId) return;
  try {
    const response = await fetch(`/api/payment/simulate/${currentOrderId}/${outcome}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const result = await response.json();
    console.log(`Simulation [${outcome}] outcome triggered:`, result);
  } catch (err) {
    console.error('Simulation triggering error:', err);
  }
}

// ================= GOOGLE AUTHENTICATION INTEGRATION =================

// Initializes the Google Identity Services Client dynamically
async function initGoogleSignIn() {
  try {
    const response = await fetch('/api/auth/google/client-id');
    const data = await response.json();
    if (data.client_id) {
      google.accounts.id.initialize({
        client_id: data.client_id,
        callback: handleCredentialResponse
      });
      
      const loginBtnEl = document.getElementById("google-login-btn");
      if (loginBtnEl) {
        google.accounts.id.renderButton(loginBtnEl, {
          theme: "outline",
          size: "large",
          width: 280,
          text: "signin_with"
        });
      }
      
      const signupBtnEl = document.getElementById("google-signup-btn");
      if (signupBtnEl) {
        google.accounts.id.renderButton(signupBtnEl, {
          theme: "outline",
          size: "large",
          width: 280,
          text: "signup_with"
        });
      }
    }
  } catch (err) {
    console.error('Failed to init Google Sign-in:', err);
  }
}

// Callback invoked when Google OAuth returns the ID token
async function handleCredentialResponse(response) {
  try {
    const idToken = response.credential;
    const res = await fetch('/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken })
    });
    const result = await res.json();
    
    if (!res.ok) throw new Error(result.error || 'Google login failed');
    
    currentUser = result.user;
    renderAuthHeader(true);
    hideAuthModalView();
    alert(`Google Authentication Successful! Welcome, ${currentUser.name}.`);
  } catch (err) {
    alert(err.message || 'Google authentication failed.');
  }
}

// Setup Event Listeners
function setupEventListeners() {
  // Mobile nav toggler
  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    const icon = menuToggle.querySelector('i');
    icon.className = navLinks.classList.contains('open') ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
  });

  // Nav click handlers
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      menuToggle.querySelector('i').className = 'fa-solid fa-bars';
      navLinks.querySelectorAll('a').forEach(a => a.classList.remove('active'));
      link.classList.add('active');
    });
  });

  logo.addEventListener('click', () => {
    navLinks.querySelectorAll('a').forEach(a => a.classList.remove('active'));
    navLinks.querySelector('[data-section="home"]').classList.add('active');
  });

  // Open/Close Cart Drawer
  cartTrigger.addEventListener('click', () => {
    cartDrawer.classList.add('open');
    cartBackdrop.classList.add('open');
  });

  const hideCart = () => {
    cartDrawer.classList.remove('open');
    cartBackdrop.classList.remove('open');
  };
  closeCart.addEventListener('click', hideCart);
  cartBackdrop.addEventListener('click', hideCart);

  // Filter Categories
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.getAttribute('data-category');
      renderMenu(menuItems);
    });
  });

  // Auth modal handlers
  tabLogin.addEventListener('click', () => switchAuthTab('login'));
  tabRegister.addEventListener('click', () => switchAuthTab('register'));
  closeAuthModal.addEventListener('click', hideAuthModalView);
  authBackdrop.addEventListener('click', hideAuthModalView);

  loginForm.addEventListener('submit', handleLoginSubmit);
  registerForm.addEventListener('submit', handleRegisterRequestOtp);

  // OTP Signup button listeners
  btnVerifyOtp.addEventListener('click', handleRegisterVerifyOtp);
  btnCancelOtp.addEventListener('click', resetRegisterOtpView);

  // Profile modal event listeners
  closeProfileModal.addEventListener('click', hideProfileModalView);
  profileBackdrop.addEventListener('click', hideProfileModalView);

  // Open Checkout Modal
  btnProceedCheckout.addEventListener('click', () => {
    hideCart();
    
    checkoutForm.style.display = 'block';
    paymentSpinner.style.display = 'none';
    paymentPendingVerification.style.display = 'none';
    paymentSuccess.style.display = 'none';
    paymentFailed.style.display = 'none';
    modalTitle.innerText = 'Checkout';
    
    checkoutForm.reset();
    
    if (currentUser) {
      document.getElementById('cust-name').value = currentUser.name;
      document.getElementById('cust-phone').value = currentUser.phone;
    }

    selectedOrderType = 'dine-in';
    orderTypeBtns.forEach(b => b.classList.remove('active'));
    document.querySelector('[data-type="dine-in"]').classList.add('active');
    tableNumberGroup.style.display = 'block';
    tableNumInput.required = true;

    checkoutModal.classList.add('open');
    modalBackdrop.classList.add('open');
  });

  // Close Checkout Modal
  const hideModal = () => {
    stopPaymentStatusPolling();
    checkoutModal.classList.remove('open');
    modalBackdrop.classList.remove('open');
  };
  closeModal.addEventListener('click', hideModal);
  modalBackdrop.addEventListener('click', hideModal);

  // Form Order Type Selection
  orderTypeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      orderTypeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedOrderType = btn.getAttribute('data-type');
      
      if (selectedOrderType === 'dine-in') {
        tableNumberGroup.style.display = 'block';
        tableNumInput.required = true;
      } else {
        tableNumberGroup.style.display = 'none';
        tableNumInput.required = false;
        tableNumInput.value = '';
      }
    });
  });

  // Submit handlers
  checkoutForm.addEventListener('submit', handleCheckoutSubmit);
  paymentUtrForm.addEventListener('submit', handlePaymentUtrSubmit);
  
  // Dev Simulator outcomes
  btnSimSuccess.addEventListener('click', () => simulateOutcome('success'));
  btnSimFail.addEventListener('click', () => simulateOutcome('failed'));

  // Retry Verification flow
  btnRetryPayment.addEventListener('click', () => {
    paymentFailed.style.display = 'none';
    paymentPendingVerification.style.display = 'flex';
    modalTitle.innerText = 'UPI Payment';
    startPaymentStatusPolling(currentOrderId);
  });

  btnCloseSuccess.addEventListener('click', hideModal);
}

// Helpers
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
