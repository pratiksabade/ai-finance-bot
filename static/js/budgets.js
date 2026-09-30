/**
 * Budget Planner Controller
 * Manages category spending thresholds, variance analysis, and limit enforcement in INR.
 */

let allBudgetsCache = [];

async function loadBudgetsData() {
  const tbody = document.getElementById('budget-table-tbody');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Loading budget allocations...</td></tr>';

  try {
    const res = await fetch(`/api/budgets?month=${AppState.currentMonth}`);
    const data = await res.json();

    if (!res.ok || data.status !== 'success') {
      showToast(data.message || 'Error fetching budgets.', 'error');
      return;
    }

    allBudgetsCache = data.budgets || [];

    if (allBudgetsCache.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="empty-state">
            <h4>No Category Budgets Configured</h4>
            <p>Establish monthly spending caps for ${AppState.currentMonth} to monitor expense variance.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = allBudgetsCache.map(b => {
      let badgeHtml = '';
      let progressClass = 'progress-success';

      if (b.status === 'exceeded') {
        badgeHtml = '<span class="badge badge-danger">Exceeded</span>';
        progressClass = 'progress-danger';
      } else if (b.status === 'warning') {
        badgeHtml = '<span class="badge badge-warning">Approaching Limit</span>';
        progressClass = 'progress-warning';
      } else {
        badgeHtml = '<span class="badge badge-success">On Track</span>';
        progressClass = 'progress-success';
      }

      const cappedPct = Math.min(100, b.percentage);
      const remainingColor = b.remaining < 0 ? 'text-expense' : 'text-main';

      return `
        <tr>
          <td><strong>${escapeHtml(b.category)}</strong></td>
          <td class="text-right font-mono">${formatINR(b.limit)}</td>
          <td class="text-right font-mono">${formatINR(b.spent)}</td>
          <td class="text-right font-mono ${remainingColor}">
            <strong>${formatINR(b.remaining)}</strong>
          </td>
          <td>
            <div style="font-size: 11px; margin-bottom: 2px; display: flex; justify-content: space-between;">
              <span>${b.percentage.toFixed(1)}%</span>
              <span style="color: var(--text-subtle);">${formatINR(b.spent)} / ${formatINR(b.limit)}</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill ${progressClass}" style="width: ${cappedPct}%;"></div>
            </div>
          </td>
          <td>${badgeHtml}</td>
          <td class="text-right td-actions">
            <button class="btn btn-secondary btn-sm" onclick="editBudget(${b.id})">Edit</button>
            <button class="btn btn-danger btn-sm" onclick="deleteBudget(${b.id})">Delete</button>
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    console.error('Error fetching budgets:', err);
    tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Failed to load budgets.</td></tr>';
  }
}

function openAddBudgetModal() {
  document.getElementById('budget-form').reset();
  document.getElementById('budget-id-input').value = '';
  showModal('set-budget-modal');
}

function editBudget(id) {
  const b = allBudgetsCache.find(x => x.id === id);
  if (!b) return;

  document.getElementById('budget-id-input').value = b.id;
  document.getElementById('budget-category-input').value = b.category;
  document.getElementById('budget-limit-input').value = b.limit;
  showModal('set-budget-modal');
}

async function deleteBudget(id) {
  if (!confirm('Remove this category budget limit?')) return;

  try {
    const res = await fetch(`/api/budgets/${id}`, { method: 'DELETE' });
    const data = await res.json();

    if (res.ok && data.status === 'success') {
      showToast('Budget limit removed.', 'success');
      loadBudgetsData();
      loadDashboardData();
    } else {
      showToast(data.message || 'Failed to delete budget.', 'error');
    }
  } catch {
    showToast('Failed to reach server.', 'error');
  }
}

// Budget Form Submission
document.addEventListener('DOMContentLoaded', () => {
  const budgetForm = document.getElementById('budget-form');
  if (!budgetForm) return;

  budgetForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('budget-id-input').value;
    const category = document.getElementById('budget-category-input').value.trim();
    const limit = parseFloat(document.getElementById('budget-limit-input').value);
    const month = AppState.currentMonth;

    const payload = { category, limit, month };
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/budgets/${id}` : '/api/budgets';

    const saveBtn = document.getElementById('save-budget-btn');
    saveBtn.disabled = true;
    saveBtn.innerText = 'Saving...';

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (res.ok && data.status === 'success') {
        showToast(data.message || 'Budget saved.', 'success');
        closeModal('set-budget-modal');
        loadBudgetsData();
        loadDashboardData();
      } else {
        showToast(data.message || 'Operation failed.', 'error');
      }
    } catch {
      showToast('Network error while saving budget limit.', 'error');
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerText = 'Establish Limit';
    }
  });
});
