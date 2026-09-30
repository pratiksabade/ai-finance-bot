/**
 * AI Financial Advisor Controller
 * Communicates with the backend Gemini advisory endpoint and renders diagnostic reports.
 * Adheres strictly to: Non-vibe UI, no purple gradients, crisp rectangular cards,
 * no em dashes, no emoji icons, and Indian Rupee standard.
 */

async function checkAIStatus() {
  const indicator = document.getElementById('ai-status-indicator');
  if (!indicator) return;

  try {
    const res = await fetch('/api/ai/status');
    const data = await res.json();

    if (data.is_configured) {
      indicator.innerHTML = `
        <div class="badge badge-success" style="padding: 6px 10px;">
          <svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          Google Gemini Integration: Active & Operational
        </div>
      `;
    } else {
      indicator.innerHTML = `
        <div class="badge badge-warning" style="padding: 6px 10px;">
          <svg class="icon icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          Google Gemini API Key Missing in .env (Educational advisory mode)
        </div>
      `;
    }
  } catch (err) {
    indicator.innerHTML = `
      <div class="badge badge-neutral" style="padding: 6px 10px;">
        AI Status Check: Offline
      </div>
    `;
  }
}

async function triggerAIDiagnostic() {
  const btn = document.getElementById('run-ai-analysis-btn');
  const resultsContainer = document.getElementById('ai-results-content');
  if (!btn || !resultsContainer) return;

  btn.disabled = true;
  btn.innerHTML = `
    <svg class="icon icon-sm" viewBox="0 0 24 24"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
    Analyzing Cash Flow Data...
  `;

  resultsContainer.innerHTML = `
    <div style="padding: 32px; text-align: center; color: var(--text-muted);">
      <p style="font-size: 14px; margin-bottom: 8px;">Compiling cash flow ledger for ${AppState.currentMonth} and querying Google Gemini...</p>
      <div style="font-size: 12px; color: var(--text-subtle);">Evaluating category expenditures, savings percentage, and budget variance in INR.</div>
    </div>
  `;

  try {
    const res = await fetch('/api/ai/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ month: AppState.currentMonth })
    });
    const data = await res.json();

    if (data.status === 'success') {
      renderAIAnalysisResults(data);
      showToast('AI financial diagnostic generated.', 'success');
    } else if (data.status === 'unconfigured') {
      resultsContainer.innerHTML = `
        <div class="empty-state" style="border: 1px solid var(--border-color); border-radius: 4px; padding: 24px; background: #fff;">
          <h4 style="color: var(--warning); margin-bottom: 8px;">Gemini API Key Required</h4>
          <p style="margin-bottom: 12px;">${escapeHtml(data.message)}</p>
          <div style="background: var(--bg-subtle); padding: 12px; border-radius: 4px; text-align: left; max-width: 480px; margin: 0 auto; font-size: 12px;">
            1. Open <code>.env</code> in your root folder.<br>
            2. Add: <code>GEMINI_API_KEY=your_key_here</code><br>
            3. Restart the Flask application and re-run diagnostic.
          </div>
        </div>
      `;
    } else {
      resultsContainer.innerHTML = `
        <div class="empty-state" style="border: 1px solid var(--danger-border); border-radius: 4px; padding: 24px; background: var(--danger-bg);">
          <h4 style="color: var(--danger-text); margin-bottom: 6px;">Advisory Diagnostic Service Notice</h4>
          <p style="color: var(--danger-text); font-size: 13px;">${escapeHtml(data.message || 'The AI service could not complete the analysis.')}</p>
        </div>
      `;
    }
  } catch (err) {
    console.error('Error during AI diagnostic:', err);
    resultsContainer.innerHTML = `
      <div class="empty-state">
        <h4 style="color: var(--danger);">Network Connection Failed</h4>
        <p>Could not connect to the backend AI service. Verify your server is running.</p>
      </div>
    `;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg class="icon icon-sm" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
      Run AI Diagnostic
    `;
  }
}

function renderAIAnalysisResults(data) {
  const container = document.getElementById('ai-results-content');
  if (!container) return;

  const insights = data.insights || {};
  const sections = Object.entries(insights);

  if (sections.length === 0 && data.raw_markdown) {
    // If raw markdown without sections
    container.innerHTML = `<div style="white-space: pre-wrap; font-size: 14px; line-height: 1.6;">${escapeHtml(data.raw_markdown)}</div>`;
    return;
  }

  let html = `<div style="display: flex; flex-direction: column; gap: 16px;">`;

  for (const [title, content] of sections) {
    html += `
      <div class="table-card" style="margin-bottom: 0; padding: 18px 20px;">
        <h3 style="font-size: 15px; margin-bottom: 10px; color: var(--primary); display: flex; align-items: center; gap: 8px;">
          <svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          ${escapeHtml(title)}
        </h3>
        <div style="font-size: 13px; line-height: 1.6; color: var(--text-muted); white-space: pre-line;">
          ${escapeHtml(content)}
        </div>
      </div>
    `;
  }

  html += `</div>`;
  container.innerHTML = html;
}

// Event Bindings
document.addEventListener('DOMContentLoaded', () => {
  const runBtn = document.getElementById('run-ai-analysis-btn');
  if (runBtn) {
    runBtn.addEventListener('click', triggerAIDiagnostic);
  }
});
