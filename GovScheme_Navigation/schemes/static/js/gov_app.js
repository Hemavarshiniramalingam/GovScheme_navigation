/**
 * GovScheme Navigator — Official Citizen Client Interactions (v2.0)
 * Handles Accessibility, Intake Wizard, Live Tracking, and Notifications
 */

document.addEventListener('DOMContentLoaded', () => {
  initAccessibility();
  initIntakeWizard();
  initNotifications();
  initQuickApplyModal();
  initStatusTrackerSimulator();
});

/* ==========================================================================
   1. Accessibility & High Contrast Controls (WCAG 2.1 AA)
   ========================================================================== */
function initAccessibility() {
  const contrastBtn = document.getElementById('toggleContrastBtn');
  const fontNormalBtn = document.getElementById('fontNormalBtn');
  const fontLargeBtn = document.getElementById('fontLargeBtn');
  const fontXLargeBtn = document.getElementById('fontXLargeBtn');

  // Load saved preferences
  if (localStorage.getItem('gov_contrast') === 'high') {
    document.body.classList.add('high-contrast');
    if (contrastBtn) contrastBtn.classList.add('active');
  }

  const savedFontSize = localStorage.getItem('gov_font_size');
  if (savedFontSize) {
    document.body.classList.add(savedFontSize);
    updateActiveFontBtn(savedFontSize);
  }

  if (contrastBtn) {
    contrastBtn.addEventListener('click', () => {
      document.body.classList.toggle('high-contrast');
      const isHigh = document.body.classList.contains('high-contrast');
      localStorage.setItem('gov_contrast', isHigh ? 'high' : 'normal');
      contrastBtn.classList.toggle('active', isHigh);
    });
  }

  function setFontSize(className) {
    document.body.classList.remove('font-small', 'font-large', 'font-xlarge');
    if (className) document.body.classList.add(className);
    localStorage.setItem('gov_font_size', className || '');
    updateActiveFontBtn(className);
  }

  function updateActiveFontBtn(className) {
    [fontNormalBtn, fontLargeBtn, fontXLargeBtn].forEach(b => b && b.classList.remove('active'));
    if (!className && fontNormalBtn) fontNormalBtn.classList.add('active');
    if (className === 'font-large' && fontLargeBtn) fontLargeBtn.classList.add('active');
    if (className === 'font-xlarge' && fontXLargeBtn) fontXLargeBtn.classList.add('active');
  }

  if (fontNormalBtn) fontNormalBtn.addEventListener('click', () => setFontSize(''));
  if (fontLargeBtn) fontLargeBtn.addEventListener('click', () => setFontSize('font-large'));
  if (fontXLargeBtn) fontXLargeBtn.addEventListener('click', () => setFontSize('font-xlarge'));
}

/* ==========================================================================
   2. Intake Form Step Wizard
   ========================================================================== */
function initIntakeWizard() {
  const intakeForm = document.getElementById('citizenIntakeForm');
  if (!intakeForm) return;

  const steps = document.querySelectorAll('.wizard-step-panel');
  const nodes = document.querySelectorAll('.step-node');
  let currentStep = 1;

  const nextBtn = document.getElementById('wizardNextBtn');
  const prevBtn = document.getElementById('wizardPrevBtn');
  const submitBtn = document.getElementById('wizardSubmitBtn');

  function showStep(stepNum) {
    steps.forEach((step, idx) => {
      step.style.display = (idx + 1 === stepNum) ? 'block' : 'none';
    });

    nodes.forEach((node, idx) => {
      const stepIndex = idx + 1;
      node.classList.remove('active', 'completed');
      if (stepIndex === stepNum) {
        node.classList.add('active');
      } else if (stepIndex < stepNum) {
        node.classList.add('completed');
      }
    });

    if (prevBtn) prevBtn.style.display = stepNum > 1 ? 'inline-flex' : 'none';
    if (nextBtn) nextBtn.style.display = stepNum < steps.length ? 'inline-flex' : 'none';
    if (submitBtn) submitBtn.style.display = stepNum === steps.length ? 'inline-flex' : 'none';
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (currentStep < steps.length) {
        currentStep++;
        showStep(currentStep);
      }
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
      }
    });
  }

  // Set initial state
  showStep(1);
}

/* ==========================================================================
   3. Notification Drawer & Real-time Alerts
   ========================================================================== */
function initNotifications() {
  const notifBtn = document.getElementById('openNotifDrawerBtn');
  const closeBtn = document.getElementById('closeNotifDrawerBtn');
  const drawer = document.getElementById('notifDrawer');
  const overlay = document.getElementById('notifOverlay');
  const notifList = document.getElementById('notifList');
  const notifBadge = document.getElementById('notifCountBadge');

  if (!notifBtn || !drawer) return;

  function toggleDrawer(open) {
    drawer.classList.toggle('open', open);
    if (overlay) overlay.classList.toggle('open', open);
    if (open) fetchNotifications();
  }

  notifBtn.addEventListener('click', (e) => {
    e.preventDefault();
    toggleDrawer(true);
  });

  if (closeBtn) closeBtn.addEventListener('click', () => toggleDrawer(false));
  if (overlay) overlay.addEventListener('click', () => toggleDrawer(false));

  function fetchNotifications() {
    fetch('/api/notifications/')
      .then(res => res.json())
      .then(data => {
        if (!data.success || !notifList) return;
        
        if (notifBadge) {
          notifBadge.textContent = data.unread_count > 0 ? data.unread_count : data.count;
          notifBadge.style.display = data.count > 0 ? 'inline-block' : 'none';
        }

        if (data.notifications.length === 0) {
          notifList.innerHTML = '<p style="color:var(--text-muted); font-size:0.875rem; text-align:center; padding:30px 0;">No active alerts at this moment.</p>';
          return;
        }

        notifList.innerHTML = data.notifications.map(n => `
          <div class="notif-item ${n.is_read ? '' : 'unread'}" data-id="${n.id}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <span class="notif-title">${escapeHtml(n.title)}</span>
              <span class="notif-time">${escapeHtml(n.time_ago)}</span>
            </div>
            <p class="notif-msg">${escapeHtml(n.message)}</p>
            ${n.action_url && n.action_url !== '#' ? `<a href="${n.action_url}" style="font-size:0.75rem; font-weight:700; color:var(--gov-blue-primary); margin-top:4px; text-decoration:none;">View Application Status &rarr;</a>` : ''}
          </div>
        `).join('');
      })
      .catch(err => console.error('Error fetching notifications:', err));
  }

  // Initial fetch for badge count
  fetchNotifications();
}

/* ==========================================================================
   4. One-Click Assisted Quick Apply Modal
   ========================================================================== */
function initQuickApplyModal() {
  window.openQuickApplyModal = function(schemeCode, schemeName) {
    const modal = document.getElementById('quickApplyModal');
    if (!modal) return;
    
    document.getElementById('modalSchemeName').textContent = schemeName;
    document.getElementById('modalSchemeCode').value = schemeCode;
    modal.style.display = 'flex';
  };

  window.closeQuickApplyModal = function() {
    const modal = document.getElementById('quickApplyModal');
    if (modal) modal.style.display = 'none';
  };

  const submitBtn = document.getElementById('confirmQuickApplyBtn');
  if (submitBtn) {
    submitBtn.addEventListener('click', () => {
      const schemeCode = document.getElementById('modalSchemeCode').value;
      const applicantName = document.getElementById('modalApplicantName').value.trim() || 'Citizen Applicant';
      const applicantPhone = document.getElementById('modalApplicantPhone').value.trim() || '+91 98765 00000';
      const applicantEmail = document.getElementById('modalApplicantEmail').value.trim() || 'citizen@example.gov.in';

      submitBtn.disabled = true;
      submitBtn.textContent = 'Generating Application ID...';

      fetch('/api/quick-apply/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scheme_code: schemeCode,
          applicant_name: applicantName,
          applicant_phone: applicantPhone,
          applicant_email: applicantEmail,
        })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          window.location.href = data.redirect_url;
        } else {
          alert('Error: ' + data.error);
          submitBtn.disabled = false;
          submitBtn.textContent = 'Submit Official Application';
        }
      })
      .catch(err => {
        console.error(err);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Official Application';
      });
    });
  }
}

/* ==========================================================================
   5. Interactive Status Tracker & Stage Simulator
   ========================================================================== */
function initStatusTrackerSimulator() {
  window.simulateStatusChange = function(appNum, targetStatus, remarks, actionNote) {
    const btn = event ? event.currentTarget : null;
    if (btn) btn.disabled = true;

    fetch('/api/simulate-transition/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_num: appNum,
        target_status: targetStatus,
        remarks: remarks || `Simulated transition to ${targetStatus}`,
        officer: 'Nodal Verification Authority',
        action_note: actionNote || ''
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // Reload page to reflect live timeline and notification trigger
        window.location.reload();
      } else {
        alert('Simulation error: ' + data.error);
        if (btn) btn.disabled = false;
      }
    })
    .catch(err => {
      console.error(err);
      if (btn) btn.disabled = false;
    });
  };
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
}
