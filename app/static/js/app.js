/**
 * AI Powered LMS — Core JavaScript
 * Handles theme toggle, global search, CSRF tokens, dynamic forms, notifications.
 */

// ── CSRF Token for AJAX ──
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

function ajaxHeaders() {
    return {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
    };
}

// ── Theme Toggle ──
(function initTheme() {
    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
})();

document.getElementById('themeToggle')?.addEventListener('click', function () {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next);
});

function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle i');
    if (icon) {
        icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
    }
}

// ── Global Search ──
const searchInput = document.getElementById('globalSearch');
const searchResults = document.getElementById('searchResults');
let searchTimeout;

if (searchInput) {
    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        searchTimeout = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`, {
                headers: ajaxHeaders(),
            })
                .then(r => r.json())
                .then(data => renderSearchResults(data))
                .catch(() => {
                    searchResults.style.display = 'none';
                });
        }, 300);
    });

    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
}

function renderSearchResults(data) {
    if (!searchResults) return;
    let html = '';
    const categories = {
        students: { icon: 'bi-person', label: 'Students', urlBase: '/admin/students/' },
        departments: { icon: 'bi-diagram-3', label: 'Departments', urlBase: '/admin/departments/' },
        subjects: { icon: 'bi-book', label: 'Subjects', urlBase: '/admin/subjects/' },
        knowledge: { icon: 'bi-database', label: 'Knowledge Base', urlBase: '/admin/knowledge-base/' },
        chats: { icon: 'bi-chat', label: 'Chats', urlBase: '/admin/chat-logs/' },
        downloads: { icon: 'bi-download', label: 'Downloads', urlBase: '/admin/downloads/' },
    };

    for (const [key, config] of Object.entries(categories)) {
        if (data[key] && data[key].length > 0) {
            html += `<h6 class="dropdown-header"><i class="bi ${config.icon} me-1"></i>${config.label}</h6>`;
            data[key].forEach(item => {
                const name = item.name || item.title || item.question || item.email || '';
                const link = `${config.urlBase}${item.id || ''}`;
                html += `<a class="dropdown-item small" href="${link}">${name}</a>`;
            });
        }
    }

    if (!html) {
        html = '<span class="dropdown-item-text text-muted small">No results found</span>';
    }

    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
}

// ── Dynamic Dependent Dropdowns (Department → Program → Class) ──
function loadPrograms(departmentId, targetSelect, callback) {
    if (!departmentId) {
        targetSelect.innerHTML = '<option value="">-- Select Program --</option>';
        if (callback) callback();
        return;
    }
    fetch(`/api/programs?department_id=${departmentId}`)
        .then(r => r.json())
        .then(data => {
            let html = '<option value="">-- Select Program --</option>';
            data.forEach(p => {
                html += `<option value="${p.id}">${p.name}</option>`;
            });
            targetSelect.innerHTML = html;
            if (callback) callback();
        });
}

function loadClasses(programId, targetSelect, callback) {
    if (!programId) {
        targetSelect.innerHTML = '<option value="">-- Select Class --</option>';
        if (callback) callback();
        return;
    }
    fetch(`/api/classes?program_id=${programId}`)
        .then(r => r.json())
        .then(data => {
            let html = '<option value="">-- Select Class --</option>';
            data.forEach(c => {
                html += `<option value="${c.id}">${c.name}</option>`;
            });
            targetSelect.innerHTML = html;
            if (callback) callback();
        });
}

function loadSubjects(departmentId, targetSelect) {
    if (!departmentId) {
        targetSelect.innerHTML = '<option value="">-- Select Subject --</option>';
        return;
    }
    fetch(`/api/subjects?department_id=${departmentId}`)
        .then(r => r.json())
        .then(data => {
            let html = '<option value="">-- Select Subject --</option>';
            data.forEach(s => {
                html += `<option value="${s.id}">${s.name}</option>`;
            });
            targetSelect.innerHTML = html;
        });
}

// ── Confirm Delete ──
document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
        if (!confirm(this.dataset.confirm || 'Are you sure?')) {
            e.preventDefault();
        }
    });
});

// ── Toast Notification ──
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function createToastContainer() {
    const c = document.createElement('div');
    c.id = 'toastContainer';
    c.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    c.style.zIndex = '9999';
    document.body.appendChild(c);
    return c;
}

// ── Auto-hide alerts after 5 seconds ──
document.querySelectorAll('.alert-dismissible').forEach(alert => {
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert?.close();
    }, 5000);
});
