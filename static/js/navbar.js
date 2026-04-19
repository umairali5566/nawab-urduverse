// Enhanced navbar toggle with mobile overlay
document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.querySelector('.navbar-toggle');
    const mobileOverlay = document.querySelector('.navbar-mobile-overlay');
    const mobileClose = document.querySelector('.navbar-mobile-close');
    const body = document.body;

    if (!toggleButton || !mobileOverlay) {
        return;
    }

    // Toggle mobile menu
    function toggleMobileMenu() {
        const isActive = mobileOverlay.classList.contains('active');
        mobileOverlay.classList.toggle('active');
        toggleButton.classList.toggle('active');
        body.classList.toggle('mobile-menu-open');

        // Update ARIA attributes
        toggleButton.setAttribute('aria-expanded', !isActive ? 'true' : 'false');

        // Prevent body scroll when menu is open
        if (!isActive) {
            body.style.overflow = 'hidden';
        } else {
            body.style.overflow = '';
        }
    }

    // Event listeners
    toggleButton.addEventListener('click', toggleMobileMenu);

    if (mobileClose) {
        mobileClose.addEventListener('click', toggleMobileMenu);
    }

    // Close menu when clicking overlay
    mobileOverlay.addEventListener('click', function(e) {
        if (e.target === mobileOverlay) {
            toggleMobileMenu();
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileOverlay.classList.contains('active')) {
            toggleMobileMenu();
        }
    });

    // Close menu on window resize (if desktop breakpoint reached)
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && mobileOverlay.classList.contains('active')) {
            toggleMobileMenu();
        }
    });
});
