/**
 * Expenses Management Controller
 * Handles CRUD operations, category filtering, and validation for expenses in INR.
 */

let allExpensesCache = [];

async function loadExpensesData() {
  const tbody = document.getElementById('expense-table-tbody');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Loading expenses ledger...</td></tr>';

  const filterEl = document.getElementById('expense-category-filter');
  const catFilter = filterEl ? filterEl.value : 'All';

  try {
    let url = `/api/expenses?month=${AppState.currentMonth}`;
    if (catFilter && catFilter !== 'All') {
      url += `&category=${encodeURIComponent(catFilter)}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok || data.status !== 'success') {
      showToast(data.message || 'Error fetching expense ledger.', 'error');
      return;
    }

    allExpensesCache = data.expenses || [];

    if (allExpensesCache.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <h4>No Expenses Recorded</h4>
            <p>No expenditures found for ${AppState.currentMonth}${catFilter !== 'All' ? ` under ${catFilter}` : ''}.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = allExpensesCache.map(exp => `
      <tr>
        <td class="font-mono">${exp.date}</td>
        <td>
          <span class="badge badge-neutral">
            ${escapeHtml(exp.category)}
          </span>
        </td>
        <td>${escapeHtml(exp.description || '-')}</td>
        <td class="text-right font-mono text-expense">
          <strong>-${formatINR(exp.amount)}</strong>
        </td>
        <td class="text-right td-actions">
          <button class="btn btn-secondary btn-sm" onclick="editExpense(${exp.id})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteExpense(${exp.id})">Delete</button>
        </td>
      </tr>
    `).join('');

  } catch (err) {
    console.error('Error fetching expenses:', err);
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Failed to load expenses.</td></tr>';
  }
}

function openAddExpenseModal() {
  document.getElementById('expense-form').reset();
  document.getElementById('expense-id-input').value = '';
  document.getElementById('expense-modal-title').innerText = 'Log Expense';
  document.getElementById('expense-date-input').value = new Date().toISOString().slice(0, 10);
  showModal('add-expense-modal');
}

function editExpense(id) {
  const exp = allExpensesCache.find(e => e.id === id);
  if (!exp) return;

  document.getElementById('expense-id-input').value = exp.id;
  document.getElementById('expense-category-input').value = exp.category;
  document.getElementById('expense-amount-input').value = exp.amount;
  document.getElementById('expense-date-input').value = exp.date;
  document.getElementById('expense-desc-input').value = exp.description || '';
  document.getElementById('expense-modal-title').innerText = 'Edit Expense Record';
  showModal('add-expense-modal');
}

async function deleteExpense(id) {
  if (!confirm('Are you sure you wish to delete this expense record?')) return;

  try {
    const res = await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
    const data = await res.json();

    if (res.ok && data.status === 'success') {
      showToast('Expense record deleted successfully.', 'success');
      loadExpensesData();
      loadDashboardData();
    } else {
      showToast(data.message || 'Failed to delete expense.', 'error');
    }
  } catch {
    showToast('Failed to reach server.', 'error');
  }
}

// Event Listeners for Expense UI
document.addEventListener('DOMContentLoaded', () => {
  const filterEl = document.getElementById('expense-category-filter');
  if (filterEl) {
    filterEl.addEventListener('change', () => loadExpensesData());
  }

  const expenseForm = document.getElementById('expense-form');
  if (!expenseForm) return;

  expenseForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('expense-id-input').value;
    const category = document.getElementById('expense-category-input').value.trim();
    const amount = parseFloat(document.getElementById('expense-amount-input').value);
    const date = document.getElementById('expense-date-input').value;
    const description = document.getElementById('expense-desc-input').value.trim();

    const payload = { category, amount, date, description };
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/expenses/${id}` : '/api/expenses';

    const saveBtn = document.getElementById('save-expense-btn');
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
        showToast(data.message || 'Expense recorded.', 'success');
        closeModal('add-expense-modal');
        loadExpensesData();
        loadDashboardData();
      } else {
        showToast(data.message || 'Operation failed.', 'error');
      }
    } catch {
      showToast('Network error while saving expense.', 'error');
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerText = 'Record Expense';
    }
  });
});
