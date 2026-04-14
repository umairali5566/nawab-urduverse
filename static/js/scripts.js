/**
 * Shared UI cleanup script.
 * Mobile popup menu and search overlay triggers are intentionally disabled.
 */

document.addEventListener("DOMContentLoaded", () => {
    const hiddenSelectors = [
        ".mobile-menu",
        ".sidebar",
        ".sidebar-menu",
        ".search-modal",
        ".overlay",
        ".popup",
        ".drawer",
        ".mobile-drawer",
        ".mobile-overlay",
        ".mobile-nav",
        "#sideMenu",
        "#menuBackdrop",
        "#mobileDrawer",
        "#mobileOverlay",
    ];

    hiddenSelectors.forEach((selector) => {
        document.querySelectorAll(selector).forEach((element) => {
            element.style.display = "none";
            element.classList.remove("active", "open", "show", "is-open");
        });
    });
});
