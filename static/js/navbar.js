// Clean JS for navbar toggle (navbar.js)
document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');
    const navbarPanel = document.querySelector('.navbar-panel');

    if (!toggleButton || !navbarMenu) {
        return;
    }

    toggleButton.addEventListener('click', function() {
        navbarMenu.classList.toggle('active');
        toggleButton.classList.toggle('active');
        if (navbarPanel) {
            navbarPanel.classList.toggle('active');
        }
        toggleButton.setAttribute('aria-expanded', toggleButton.classList.contains('active') ? 'true' : 'false');
    });
});
