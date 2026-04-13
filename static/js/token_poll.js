/* ============================================================
   ClinicFlow — AJAX Token Polling
   Polls /tokens/api/status/<doctor_id>/ every 5 seconds
   and updates the live token display elements on the page.
   ============================================================ */

(function () {
  'use strict';

  const POLL_INTERVAL = 5000; // ms

  function updateTokenDisplay(data) {
    // Current token
    const curEl = document.getElementById('live-current-token');
    if (curEl) {
      curEl.textContent = data.current_token !== null ? '#' + data.current_token : '—';
    }

    // Current patient name
    const curNameEl = document.getElementById('live-current-patient');
    if (curNameEl) {
      curNameEl.textContent = data.current_patient || 'No active patient';
    }

    // Next token
    const nextEl = document.getElementById('live-next-token');
    if (nextEl) {
      nextEl.textContent = data.next_token !== null ? '#' + data.next_token : '—';
    }

    // Waiting count
    const waitEl = document.getElementById('live-waiting-count');
    if (waitEl) {
      waitEl.textContent = data.waiting_count;
    }

    // Patient's own token position highlight
    const myTokenEl = document.getElementById('live-my-token');
    if (myTokenEl && data.my_token !== null) {
      myTokenEl.textContent = '#' + data.my_token;
      const isCurrent = data.current_token === data.my_token;
      myTokenEl.classList.toggle('token-called', isCurrent);
      myTokenEl.classList.toggle('token-waiting', !isCurrent);

      const statusMsg = document.getElementById('live-my-status');
      if (statusMsg) {
        if (isCurrent) {
          statusMsg.textContent = '🟢 Your turn! Please proceed to the doctor\'s room.';
          statusMsg.className = 'mt-2 text-success fw-semibold';
        } else {
          const ahead = data.current_token !== null
            ? Math.max(0, data.my_token - data.current_token - 1)
            : data.my_token - 1;
          statusMsg.textContent = `⏳ ${ahead} patient(s) ahead of you.`;
          statusMsg.className = 'mt-2 text-warning';
        }
      }
    }

    // Last updated timestamp
    const tsEl = document.getElementById('live-timestamp');
    if (tsEl) {
      const now = new Date();
      tsEl.textContent = 'Updated ' + now.toLocaleTimeString('en-IN');
    }
  }

  function startPolling(doctorId) {
    const apiUrl = '/tokens/api/status/' + doctorId + '/';

    function poll() {
      fetch(apiUrl, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(r => r.json())
        .then(data => updateTokenDisplay(data))
        .catch(() => { /* silent fail on network error */ });
    }

    poll(); // immediate first call
    setInterval(poll, POLL_INTERVAL);
  }

  // Auto-start if a data-doctor-id attribute is found on the page
  document.addEventListener('DOMContentLoaded', function () {
    const widget = document.getElementById('token-poll-widget');
    if (widget) {
      const doctorId = widget.dataset.doctorId;
      if (doctorId) startPolling(doctorId);
    }
  });

  // Also expose globally so templates can start manually
  window.ClinicTokenPoll = { startPolling };
})();
