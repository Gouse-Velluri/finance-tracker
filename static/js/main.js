/**
 * FinanceTracker - Main JavaScript
 * Features: AJAX delete, dark mode toggle, toast handling
 */

document.addEventListener('DOMContentLoaded', function () {

  // ─── AJAX Delete ──────────────────────────────────────────────────────────
  document.querySelectorAll('.ajax-delete').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const url = this.dataset.url;
      const rowId = this.dataset.row;
      const name = this.dataset.name || 'this item';

      if (!confirm(`Delete "${name}"? This cannot be undone.`)) return;

      const row = document.getElementById(rowId);
      if (row) row.classList.add('deleting');

      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                        getCookie('csrftoken');

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json',
        },
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (data.success) {
            if (row) {
              row.style.transition = 'opacity 0.3s, max-height 0.3s';
              row.style.opacity = '0';
              row.style.maxHeight = '0';
              row.style.overflow = 'hidden';
              setTimeout(() => row.remove(), 300);
            }
            showToast(data.message || 'Deleted successfully!', 'success');
          } else {
            if (row) row.classList.remove('deleting');
            showToast('Delete failed. Please try again.', 'danger');
          }
        })
        .catch(function () {
          if (row) row.classList.remove('deleting');
          showToast('Network error. Please try again.', 'danger');
        });
    });
  });


  // ─── Dark Mode Toggle ────────────────────────────────────────────────────
  const darkBtn = document.getElementById('darkModeToggle');
  if (darkBtn) {
    darkBtn.addEventListener('click', function () {
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                        getCookie('csrftoken');

      fetch('/toggle-dark-mode/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
      })
        .then(res => res.json())
        .then(data => {
          // Toggle theme immediately without reload
          const html = document.documentElement;
          if (data.dark_mode) {
            html.setAttribute('data-bs-theme', 'dark');
            document.body.classList.add('dark-mode');
            darkBtn.querySelector('i').className = 'bi bi-sun';
          } else {
            html.setAttribute('data-bs-theme', 'light');
            document.body.classList.remove('dark-mode');
            darkBtn.querySelector('i').className = 'bi bi-moon';
          }
        })
        .catch(() => {
          // Fallback: just toggle UI
          const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
          document.documentElement.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
        });
    });
  }


  // ─── Auto-dismiss Toasts ────────────────────────────────────────────────
  document.querySelectorAll('.toast').forEach(el => {
    const toast = bootstrap.Toast.getOrCreateInstance(el, { delay: 4000 });
    toast.show();
    setTimeout(() => toast.hide(), 4000);
  });


  // ─── Helper: show dynamic toast ──────────────────────────────────────────
  function showToast(message, type = 'success') {
    const container = document.querySelector('.toast-container');
    if (!container) return;

    const icons = {
      success: 'bi-check-circle',
      danger: 'bi-exclamation-circle',
      warning: 'bi-exclamation-triangle',
      info: 'bi-info-circle',
    };

    const el = document.createElement('div');
    el.className = `toast align-items-center text-bg-${type} border-0 mb-2`;
    el.setAttribute('role', 'alert');
    el.innerHTML = `
      <div class="d-flex">
        <div class="toast-body fw-semibold">
          <i class="bi ${icons[type] || 'bi-info-circle'} me-2"></i>${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    container.appendChild(el);
    const toast = bootstrap.Toast.getOrCreateInstance(el, { delay: 3500 });
    toast.show();
    setTimeout(() => el.remove(), 4000);
  }


  // ─── Helper: get cookie by name ──────────────────────────────────────────
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // ─── Highlight active nav ────────────────────────────────────────────────
  // Already handled by template conditional classes, but ensure proper page
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.href && link.href !== window.location.origin + '/' &&
        path.startsWith(new URL(link.href).pathname) &&
        new URL(link.href).pathname !== '/') {
      link.classList.add('active');
    }
  });

});
