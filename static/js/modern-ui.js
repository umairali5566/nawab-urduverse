/**
 * Modern Premium UI - Interactive Features
 * Optional smooth animations and user interactions
 * No dependencies - vanilla JavaScript
 */

// ============================================
// FADE-IN ANIMATIONS ON PAGE LOAD
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in to all cards on load
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animation = `fadeIn 0.5s ease-in forwards`;
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Add slide-in to navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.style.animation = 'slideIn 0.5s ease forwards';
    }

    // Add slide-in to sidebar
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.style.animation = 'slideUp 0.5s ease forwards';
        sidebar.style.animationDelay = '0.2s';
    }
});

// ============================================
// SMOOTH SCROLL TO ANCHOR LINKS
// ============================================

document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;

    const targetId = link.getAttribute('href').substring(1);
    if (!targetId) return;

    const targetElement = document.getElementById(targetId);
    if (!targetElement) return;

    e.preventDefault();

    targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
});

// ============================================
// ACTIVE NAVIGATION LINK HIGHLIGHTING
// ============================================

function highlightActiveNavLink() {
    const currentUrl = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-menu a');

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentUrl) {
            link.classList.add('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', highlightActiveNavLink);

// ============================================
// FORM VALIDATION & FEEDBACK
// ============================================

function setupFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'var(--danger, #ef4444)';
                    input.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
                } else {
                    input.style.borderColor = '';
                    input.style.boxShadow = '';
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'warning');
            }
        });

        // Clear error style on input
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.style.borderColor = '';
                this.style.boxShadow = '';
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', setupFormValidation);

// ============================================
// NOTIFICATION SYSTEM
// ============================================

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.maxWidth = '400px';
    notification.style.zIndex = '9999';
    notification.style.borderRadius = '10px';

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeIn 0.5s ease-out reverse';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

// ============================================
// BUTTON LOADING STATE
// ============================================

function setupButtonLoadingState() {
    document.addEventListener('submit', function(e) {
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"], .btn-submit');
        if (submitButton) {
            submitButton.textContent = 'Logging in...';
            submitButton.style.opacity = '0.7';
            // Don't disable the button to allow form submission
        }
    });
}

document.addEventListener('DOMContentLoaded', setupButtonLoadingState);

// ============================================
// TOGGLE SIDEBAR (Mobile Navigation)
// ============================================

function setupSidebarToggle() {
    // Create toggle button if not exists
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;

    // Check if we need a toggle button (mobile view)
    if (window.innerWidth < 768) {
        const toggleButton = document.createElement('button');
        toggleButton.className = 'sidebar-toggle';
        toggleButton.textContent = '☰ Menu';
        toggleButton.style.cssText = `
            display: block;
            margin-bottom: 15px;
            padding: 10px 15px;
            background: var(--accent, #2563eb);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
        `;

        sidebar.parentElement.insertBefore(toggleButton, sidebar);

        let isOpen = false;

        toggleButton.addEventListener('click', function() {
            isOpen = !isOpen;
            sidebar.style.display = isOpen ? 'block' : 'none';
            toggleButton.textContent = isOpen ? '✕ Close' : '☰ Menu';
        });

        // Hide by default on mobile
        sidebar.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', setupSidebarToggle);

// ============================================
// HOVER EFFECTS ENHANCEMENT
// ============================================

function setupHoverEffects() {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });
}

document.addEventListener('DOMContentLoaded', setupHoverEffects);

// ============================================
// TABLE SORTING (Optional)
// ============================================

function setupTableSorting() {
    const tables = document.querySelectorAll('table');

    tables.forEach(table => {
        const headers = table.querySelectorAll('th');

        headers.forEach((header, columnIndex) => {
            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';

            header.addEventListener('click', function() {
                const isAscending = this.dataset.ascending !== 'true';
                const rows = Array.from(table.querySelectorAll('tbody tr'));

                rows.sort((a, b) => {
                    const aValue = a.cells[columnIndex].textContent.trim();
                    const bValue = b.cells[columnIndex].textContent.trim();

                    // Try numeric sort
                    const aNum = parseFloat(aValue);
                    const bNum = parseFloat(bValue);

                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return isAscending ? aNum - bNum : bNum - aNum;
                    }

                    // String sort
                    return isAscending
                        ? aValue.localeCompare(bValue)
                        : bValue.localeCompare(aValue);
                });

                // Re-append rows in sorted order
                rows.forEach(row => table.querySelector('tbody').appendChild(row));

                // Update header state
                headers.forEach(h => delete h.dataset.ascending);
                this.dataset.ascending = isAscending;
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', setupTableSorting);

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K: Focus search (if exists)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"]');
            if (searchInput) searchInput.focus();
        }

        // Escape: Close any open modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.active');
            modals.forEach(modal => modal.classList.remove('active'));
        }
    });
}

document.addEventListener('DOMContentLoaded', setupKeyboardShortcuts);

// ============================================
// RESPONSIVE WINDOW RESIZE HANDLING
// ============================================

let resizeTimeout;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
        // Re-setup sidebar toggle on window resize
        setupSidebarToggle();
    }, 250);
});

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Add loading spinner to button
 * Usage: addLoadingSpinner(button)
 */
window.addLoadingSpinner = function(button) {
    const originalHTML = button.innerHTML;
    button.innerHTML = '<span class="spinner"></span> Loading...';
    button.disabled = true;

    return {
        stop: function() {
            button.innerHTML = originalHTML;
            button.disabled = false;
        }
    };
};

/**
 * Validate email
 * Usage: isValidEmail('user@example.com')
 */
window.isValidEmail = function(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

/**
 * Debounce function
 * Usage: const debouncedFunc = debounce(myFunc, 300);
 */
window.debounce = function(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
};

/**
 * Throttle function
 * Usage: const throttledFunc = throttle(myFunc, 1000);
 */
window.throttle = function(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// ============================================
// INITIALIZE ALL FEATURES
// ============================================

console.log('✨ Modern Premium UI Interactive Features Loaded');
