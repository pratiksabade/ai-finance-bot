/**
 * Savings Goals Controller
 * Manages capital accumulation targets, progress tracking, and deposits in INR.
 */

let allGoalsCache = [];

async function loadGoalsData() {
  const container = document.getElementById('goals-grid');
  if (!container) return;

  container.innerHTML = '<div class="empty-state" style="grid-column: 1 / -1;">Loading savings goals...</div>';

  try {
    const res = await fetch('/api/goals');
    const data = await res.json();

    if (!res.ok || data.status !== 'success') {
      showToast(data.message || 'Error fetching goals.', 'error');
      return;
    }

    allGoalsCache = data.goals || [];

    if (allGoalsCache.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <h4>No Savings Goals Established</h4>
          <p>Create a capital goal such as an Emergency Fund (6 months expenses), Laptop Upgrade, or Education reserve.</p>
          <button class="btn btn-primary btn-sm" onclick="openAddGoalModal()">+ Create First Goal</button>
        </div>
      `;
      return;
    }

    container.innerHTML = allGoalsCache.map(g => {
      const isCompleted = g.is_completed;
      const progressClass = isCompleted ? 'progress-success' : 'progress-blue';

      return `
        <div class="metric-card" style="display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
              <h4 style="font-size: 15px;">${escapeHtml(g.name)}</h4>
              ${isCompleted
                ? '<span class="badge badge-success">Completed</span>'
                : `<span class="badge badge-neutral font-mono">${g.progress_percentage}%</span>`}
            </div>

            <div style="margin: 12px 0;">
              <div style="font-size: 20px; font-weight: 700;" class="font-mono">
                ${formatINR(g.current_amount)}
                <span style="font-size: 13px; font-weight: 400; color: var(--text-subtle);">
                  / ${formatINR(g.target_amount)}
                </span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill ${progressClass}" style="width: ${g.progress_percentage}%;"></div>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                <span>Remaining: <strong class="font-mono">${formatINR(g.remaining_amount)}</strong></span>
                <span>Target: <strong class="font-mono">${g.target_date}</strong></span>
              </div>
            </div>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 12px; margin-top: 12px;">
            <button class="btn btn-secondary btn-sm" onclick="openDepositModal(${g.id}, '${escapeHtml(g.name)}')">
              + Allocate Funds
            </button>
            <div style="display: flex; gap: 6px;">
              <button class="btn btn-secondary btn-sm" onclick="editGoal(${g.id})">Edit</button>
              <button class="btn btn-danger btn-sm" onclick="deleteGoal(${g.id})">Delete</button>
            </div>
          </div>
        </div>
      `;
    }).join('');

  } catch (err) {
    console.error('Error fetching goals:', err);
    container.innerHTML = '<div class="empty-state" style="grid-column: 1 / -1;">Failed to load goals.</div>';
  }
}

function openAddGoalModal() {
  document.getElementById('goal-form').reset();
  document.getElementById('goal-id-input').value = '';
  document.getElementById('goal-modal-title').innerText = 'Create Savings Goal';
  document.getElementById('goal-date-input').value = new Date(Date.now() + 90 * 86400000).toISOString().slice(0, 10);
  showModal('add-goal-modal');
}

function editGoal(id) {
  const g = allGoalsCache.find(x => x.id === id);
  if (!g) return;

  document.getElementById('goal-id-input').value = g.id;
  document.getElementById('goal-name-input').value = g.name;
  document.getElementById('goal-target-input').value = g.target_amount;
  document.getElementById('goal-current-input').value = g.current_amount;
  document.getElementById('goal-date-input').value = g.target_date;
  document.getElementById('goal-modal-title').innerText = 'Edit Savings Goal';
  showModal('add-goal-modal');
}

function openDepositModal(id, name) {
  document.getElementById('deposit-form').reset();
  document.getElementById('deposit-goal-id').value = id;
  document.getElementById('deposit-goal-name').innerText = `Adding funds to target: "${name}"`;
  showModal('deposit-goal-modal');
}

async function deleteGoal(id) {
  if (!confirm('Are you sure you wish to delete this savings goal?')) return;

  try {
    const res = await fetch(`/api/goals/${id}`, { method: 'DELETE' });
    const data = await res.json();

    if (res.ok && data.status === 'success') {
      showToast('Savings goal deleted.', 'success');
      loadGoalsData();
      loadDashboardData();
    } else {
      showToast(data.message || 'Failed to delete goal.', 'error');
    }
  } catch {
    showToast('Failed to reach server.', 'error');
  }
}

// Goals Form & Deposit Submissions
document.addEventListener('DOMContentLoaded', () => {
  const goalForm = document.getElementById('goal-form');
  if (goalForm) {
    goalForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('goal-id-input').value;
      const name = document.getElementById('goal-name-input').value.trim();
      const target_amount = parseFloat(document.getElementById('goal-target-input').value);
      const current_amount = parseFloat(document.getElementById('goal-current-input').value || 0);
      const target_date = document.getElementById('goal-date-input').value;

      const payload = { name, target_amount, current_amount, target_date };
      const method = id ? 'PUT' : 'POST';
      const url = id ? `/api/goals/${id}` : '/api/goals';

      const saveBtn = document.getElementById('save-goal-btn');
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
          showToast(data.message || 'Goal saved.', 'success');
          closeModal('add-goal-modal');
          loadGoalsData();
          loadDashboardData();
        } else {
          showToast(data.message || 'Operation failed.', 'error');
        }
      } catch {
        showToast('Network error while saving goal.', 'error');
      } finally {
        saveBtn.disabled = false;
        saveBtn.innerText = 'Save Goal';
      }
    });
  }

  const depositForm = document.getElementById('deposit-form');
  if (depositForm) {
    depositForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('deposit-goal-id').value;
      const amount = parseFloat(document.getElementById('deposit-amount-input').value);

      try {
        const res = await fetch(`/api/goals/${id}/deposit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount })
        });
        const data = await res.json();

        if (res.ok && data.status === 'success') {
          showToast(data.message || 'Funds allocated.', 'success');
          closeModal('deposit-goal-modal');
          loadGoalsData();
          loadDashboardData();
        } else {
          showToast(data.message || 'Deposit failed.', 'error');
        }
      } catch {
        showToast('Network error while recording deposit.', 'error');
      }
    });
  }
});
