document.addEventListener("DOMContentLoaded", () => {
    const helpers = window.NawabUrduAcademy || {};
    const showToast = helpers.showToast || ((message) => window.alert(message));

    const searchBtn = document.getElementById("searchBtn");
    const rekhtaQuery = document.getElementById("rekhtaQuery");
    const rekhtaFrame = document.getElementById("rekhtaFrame");
    const loadingSpinner = document.getElementById("loadingSpinner");
    const blockedMessage = document.getElementById("blockedMessage");
    const openRekhtaBtn = document.getElementById("openRekhtaBtn");

    let currentQuery = "";
    let iframeLoaded = false;

    const showLoading = () => {
        loadingSpinner.classList.remove("d-none");
        rekhtaFrame.style.display = "none";
        blockedMessage.classList.add("d-none");
    };

    const hideLoading = () => {
        loadingSpinner.classList.add("d-none");
    };

    const showIframe = () => {
        rekhtaFrame.style.display = "block";
        blockedMessage.classList.add("d-none");
    };

    const showFallback = () => {
        rekhtaFrame.style.display = "none";
        blockedMessage.classList.remove("d-none");
        openRekhtaBtn.href = `https://www.rekhta.org/search?q=${encodeURIComponent(currentQuery)}`;
    };

    const performSearch = (query) => {
        if (!query.trim()) {
            showToast("Please enter a search query.", "warning");
            return;
        }

        currentQuery = query.trim();
        iframeLoaded = false;

        showLoading();

        const url = `https://www.rekhta.org/search?q=${encodeURIComponent(currentQuery)}`;
        rekhtaFrame.src = url;

        // Set a timeout to check if iframe loaded
        setTimeout(() => {
            if (!iframeLoaded) {
                showFallback();
                hideLoading();
            }
        }, 5000); // 5 seconds timeout
    };

    rekhtaFrame.addEventListener("load", () => {
        iframeLoaded = true;
        hideLoading();
        showIframe();
    });

    rekhtaFrame.addEventListener("error", () => {
        showFallback();
        hideLoading();
    });

    searchBtn?.addEventListener("click", () => {
        const query = rekhtaQuery.value;
        performSearch(query);
    });

    rekhtaQuery?.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            const query = rekhtaQuery.value;
            performSearch(query);
        }
    });
});
