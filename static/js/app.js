/**
 * Personal Finance Advisor Bot - Core Application Orchestrator
 * Adheres strictly to: Non-vibe UI, no purple gradients, crisp non-pill buttons,
 * Indian Rupee (INR / ₹) standard formatting, and deterministic modular structure.
 */

const AppState = {
  currentView: 'dashboard',
  currentMonth: new Date().toISOString().slice(0, 7), // YYYY-MM
  categories: [
    'Food',
    'Rent',
    'Transport',
    'Education',
    'Healthcare',
    'Entertainment',
    'Shopping',
    'Utilities',
    'Other'
  ]
};

// Indian Rupee (INR) Formatter
function formatINR(val) {
  if (val === null || val === undefined || isNaN(val)) return '₹0.00';
  const num = Number(val);
  const isNegative = num < 0;
  const abs = Math.abs(num);

  const parts = abs.toFixed(2).split('.');
  let whole = parts[0];
  const decimal = parts[1];

  let lastThree = whole.substring(whole.length - 3);
  let otherNumbers = whole.substring(0, whole.length - 3);
  if (otherNumbers !== '') {
    lastThree = ',' + lastThree;
  }
  const formattedWhole = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + lastThree;
  const prefix = isNegative ? '-₹' : '₹';
  return `${prefix}${formattedWhole}.${decimal}`;
}

// Toast Notification Manager
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button style="background:none;border:none;cursor:pointer;color:inherit;" onclick="this.parentElement.remove()">&times;</button>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 4000);
}

// Modal Handlers
function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('open');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('open');
}

// View Routing & Navigation
function switchView(viewName) {
  AppState.currentView = viewName;

  // Update navigation styling
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    if (item.getAttribute('data-view') === viewName) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Update view visibility
  document.querySelectorAll('.app-view').forEach(view => {
    view.classList.remove('active');
  });

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) targetView.classList.add('active');

  // Update top bar title
  const titles = {
    'dashboard': 'Dashboard Overview',
    'income': 'Income Streams & Payroll',
    'expenses': 'Expense Ledger',
    'budgets': 'Budget Planner & Limits',
    'goals': 'Capital & Savings Goals',
    'ai-advisor': 'AI Financial Diagnostic Advisor',
    'settings': 'Workspace Configuration & Compliance'
  };
  const titleEl = document.getElementById('active-view-title');
  if (titleEl) titleEl.innerText = titles[viewName] || 'Personal Finance';

  // Load data corresponding to the view
  if (viewName === 'dashboard') loadDashboardData();
  else if (viewName === 'income') loadIncomeData();
  else if (viewName === 'expenses') loadExpensesData();
  else if (viewName === 'budgets') loadBudgetsData();
  else if (viewName === 'goals') loadGoalsData();
  else if (viewName === 'ai-advisor') checkAIStatus();
  else if (viewName === 'settings') loadSettingsView();
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  // Set default month in month picker
  const monthPicker = document.getElementById('global-month-picker');
  if (monthPicker) {
    monthPicker.value = AppState.currentMonth;
    monthPicker.addEventListener('change', (e) => {
      AppState.currentMonth = e.target.value;
      switchView(AppState.currentView);
    });
  }

  // Sidebar link clicks
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const view = item.getAttribute('data-view');
      if (view) switchView(view);
    });
  });

  // Jump to AI Advisor button
  const jumpBtn = document.getElementById('jump-to-ai-btn');
  if (jumpBtn) {
    jumpBtn.addEventListener('click', () => switchView('ai-advisor'));
  }

  // Logout handlers
  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.href = '/login';
    } catch {
      window.location.href = '/login';
    }
  };

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);

  const settingsLogoutBtn = document.getElementById('settings-logout-btn');
  if (settingsLogoutBtn) settingsLogoutBtn.addEventListener('click', handleLogout);

  // Initialize categories in selects
  initCategorySelects();

  // Load initial view
  switchView('dashboard');
});

// Category Dropdowns Populator
function initCategorySelects() {
  const expenseCatSelect = document.getElementById('expense-category-input');
  const budgetCatSelect = document.getElementById('budget-category-input');
  const expenseFilterSelect = document.getElementById('expense-category-filter');

  if (expenseCatSelect) {
    expenseCatSelect.innerHTML = AppState.categories
      .map(c => `<option value="${c}">${c}</option>`)
      .join('');
  }

  if (budgetCatSelect) {
    budgetCatSelect.innerHTML = AppState.categories
      .map(c => `<option value="${c}">${c}</option>`)
      .join('');
  }

  if (expenseFilterSelect) {
    expenseFilterSelect.innerHTML = '<option value="All">All Categories</option>' +
      AppState.categories.map(c => `<option value="${c}">${c}</option>`).join('');
  }
}

// Settings View Loader
async function loadSettingsView() {
  const statusEl = document.getElementById('settings-gemini-status');
  if (!statusEl) return;

  try {
    const res = await fetch('/api/ai/status');
    const data = await res.json();
    if (data.is_configured) {
      statusEl.innerHTML = '<span class="badge badge-success">Configured & Operational</span> (Google Gemini Active)';
    } else {
      statusEl.innerHTML = '<span class="badge badge-warning">Key Not Configured</span> (Add GEMINI_API_KEY in .env)';
    }
  } catch {
    statusEl.innerHTML = '<span class="badge badge-neutral">Unavailable</span>';
  }
}
