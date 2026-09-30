/**
 * Income Management Controller
 * Handles CRUD operations for income streams in INR.
 */

let allIncomesCache = [];

async function loadIncomeData() {
  const tbody = document.getElementById('income-table-tbody');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Loading income streams...</td></tr>';

  try {
    const res = await fetch(`/api/income?month=${AppState.currentMonth}`);
    const data = await res.json();

    if (!res.ok || data.status !== 'success') {
      showToast(data.message || 'Error fetching income records.', 'error');
      return;
    }

    allIncomesCache = data.incomes || [];

    if (allIncomesCache.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <h4>No Income Records</h4>
            <p>No income logged for ${AppState.currentMonth}. Record your salary or other inflows.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = allIncomesCache.map(inc => `
      <tr>
        <td class="font-mono">${inc.date}</td>
        <td><strong>${escapeHtml(inc.source)}</strong></td>
        <td>${escapeHtml(inc.description || '-')}</td>
        <td class="text-right font-mono text-income">
          <strong>+${formatINR(inc.amount)}</strong>
        </td>
        <td class="text-right td-actions">
          <button class="btn btn-secondary btn-sm" onclick="editIncome(${inc.id})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteIncome(${inc.id})">Delete</button>
        </td>
      </tr>
    `).join('');

  } catch (err) {
    console.error('Error fetching incomes:', err);
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Failed to load data.</td></tr>';
  }
}

function openAddIncomeModal() {
  document.getElementById('income-form').reset();
  document.getElementById('income-id-input').value = '';
  document.getElementById('income-modal-title').innerText = 'Record Income';
  document.getElementById('income-date-input').value = new Date().toISOString().slice(0, 10);
  showModal('add-income-modal');
}

function editIncome(id) {
  const inc = allIncomesCache.find(i => i.id === id);
  if (!inc) return;

  document.getElementById('income-id-input').value = inc.id;
  document.getElementById('income-source-input').value = inc.source;
  document.getElementById('income-amount-input').value = inc.amount;
  document.getElementById('income-date-input').value = inc.date;
  document.getElementById('income-desc-input').value = inc.description || '';
  document.getElementById('income-modal-title').innerText = 'Edit Income Record';
  showModal('add-income-modal');
}

async function deleteIncome(id) {
  if (!confirm('Are you sure you wish to delete this income entry?')) return;

  try {
    const res = await fetch(`/api/income/${id}`, { method: 'DELETE' });
    const data = await res.json();

    if (res.ok && data.status === 'success') {
      showToast('Income entry removed successfully.', 'success');
      loadIncomeData();
      loadDashboardData();
    } else {
      showToast(data.message || 'Failed to delete income.', 'error');
    }
  } catch {
    showToast('Failed to reach server.', 'error');
  }
}

// Income Form Submit Event
document.addEventListener('DOMContentLoaded', () => {
  const incomeForm = document.getElementById('income-form');
  if (!incomeForm) return;

  incomeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('income-id-input').value;
    const source = document.getElementById('income-source-input').value.trim();
    const amount = parseFloat(document.getElementById('income-amount-input').value);
    const date = document.getElementById('income-date-input').value;
    const description = document.getElementById('income-desc-input').value.trim();

    const payload = { source, amount, date, description };
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/income/${id}` : '/api/income';

    const saveBtn = document.getElementById('save-income-btn');
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
        showToast(data.message || 'Income saved.', 'success');
        closeModal('add-income-modal');
        loadIncomeData();
        loadDashboardData();
      } else {
        showToast(data.message || 'Operation failed.', 'error');
      }
    } catch {
      showToast('Network error while saving income.', 'error');
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerText = 'Save Income';
    }
  });
});
