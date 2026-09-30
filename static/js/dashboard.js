/**
 * Dashboard View Controller
 * Manages metric indicators, recent transactions table, and Chart.js instances.
 */

let trendChartInstance = null;
let categoryChartInstance = null;

// Clean institutional fintech palette (NO purple gradients)
const FINTECH_PALETTE = [
  '#0f172a', // Slate 900
  '#1d4ed8', // Blue 700
  '#059669', // Emerald 600
  '#d97706', // Amber 600
  '#dc2626', // Red 600
  '#0891b2', // Cyan 600
  '#475569', // Slate 600
  '#2563eb', // Blue 600
  '#10b981'  // Emerald 500
];

async function loadDashboardData() {
  try {
    const res = await fetch(`/api/dashboard?month=${AppState.currentMonth}`);
    const result = await res.json();

    if (!res.ok || result.status !== 'success') {
      showToast(result.message || 'Failed to fetch dashboard metrics.', 'error');
      return;
    }

    const data = result.data;

    // Demo banner toggle
    const demoBanner = document.getElementById('demo-banner');
    if (demoBanner) {
      demoBanner.style.display = data.is_demo_baseline ? 'flex' : 'none';
    }

    // Populate Key Metrics
    document.getElementById('metric-income').innerText = data.total_income_formatted || formatINR(data.total_income);
    document.getElementById('metric-expense').innerText = data.total_expense_formatted || formatINR(data.total_expense);
    document.getElementById('metric-savings').innerText = data.savings_formatted || formatINR(data.savings);
    document.getElementById('metric-savings-pct').innerText = `Savings Ratio: ${data.savings_percentage}%`;
    document.getElementById('metric-budget-remaining').innerText = data.remaining_budget_formatted || formatINR(data.remaining_budget);
    document.getElementById('metric-budget-total').innerText = `Budget Limit: ${data.total_budget_limit_formatted || formatINR(data.total_budget_limit)}`;

    // Populate Recent Transactions Table
    renderRecentTransactions(data.recent_transactions || []);

    // Render Charts
    renderTrendChart(data.trends);
    renderCategoryChart(data.category_spending);

  } catch (err) {
    console.error('Error loading dashboard data:', err);
    showToast('Failed to load dashboard data. Check network connection.', 'error');
  }
}

function renderRecentTransactions(transactions) {
  const tbody = document.getElementById('recent-transactions-tbody');
  if (!tbody) return;

  if (transactions.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="empty-state">
          No transactions recorded for ${AppState.currentMonth}.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = transactions.map(tx => {
    const isIncome = tx.type === 'income';
    const typeBadge = isIncome
      ? '<span class="badge badge-success">Income</span>'
      : '<span class="badge badge-neutral">Expense</span>';
    const amountClass = isIncome ? 'text-income' : 'text-expense';
    const prefix = isIncome ? '+' : '-';

    return `
      <tr>
        <td class="font-mono">${tx.date}</td>
        <td>${typeBadge}</td>
        <td><strong>${escapeHtml(tx.category || tx.title)}</strong></td>
        <td>${escapeHtml(tx.description || tx.title || '-')}</td>
        <td class="text-right font-mono ${amountClass}">
          <strong>${prefix}${formatINR(tx.amount)}</strong>
        </td>
      </tr>
    `;
  }).join('');
}

function renderTrendChart(trends) {
  const canvas = document.getElementById('trendChart');
  if (!canvas || !window.Chart) return;

  if (trendChartInstance) {
    trendChartInstance.destroy();
  }

  const ctx = canvas.getContext('2d');
  trendChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: trends ? trends.labels : [],
      datasets: [
        {
          label: 'Income (₹)',
          data: trends ? trends.incomes : [],
          backgroundColor: '#059669',
          borderRadius: 3,
          maxBarThickness: 32
        },
        {
          label: 'Expenses (₹)',
          data: trends ? trends.expenses : [],
          backgroundColor: '#dc2626',
          borderRadius: 3,
          maxBarThickness: 32
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            boxWidth: 12,
            font: { family: 'inherit', size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: ${formatINR(context.raw)}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false }
        },
        y: {
          ticks: {
            callback: function(value) {
              if (value >= 100000) return '₹' + (value / 100000).toFixed(1) + 'L';
              if (value >= 1000) return '₹' + (value / 1000).toFixed(0) + 'k';
              return '₹' + value;
            }
          },
          grid: { color: '#f1f5f9' }
        }
      }
    }
  });
}

function renderCategoryChart(categorySpending) {
  const canvas = document.getElementById('categoryChart');
  if (!canvas || !window.Chart) return;

  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  const categories = Object.keys(categorySpending || {});
  const amounts = Object.values(categorySpending || {});

  const ctx = canvas.getContext('2d');

  if (categories.length === 0) {
    categoryChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['No Expenses Recorded'],
        datasets: [{
          data: [1],
          backgroundColor: ['#e2e8f0']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } }
      }
    });
    return;
  }

  categoryChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: categories,
      datasets: [{
        data: amounts,
        backgroundColor: FINTECH_PALETTE.slice(0, categories.length),
        borderWidth: 1,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 10,
            font: { family: 'inherit', size: 11 }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.raw || 0;
              return ` ${label}: ${formatINR(value)}`;
            }
          }
        }
      },
      cutout: '68%'
    }
  });
}

function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
