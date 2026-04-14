document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("homePoetrySearchInput");
    const resetButton = document.getElementById("homeSearchReset");
    const resultsSection = document.getElementById("homeSearchResultsSection");
    const resultsContainer = document.getElementById("homeSearchResults");
    const summary = document.getElementById("homeSearchSummary");
    const searchForm = document.getElementById("homeSearchForm");

    if (!searchInput || !resultsSection || !resultsContainer || !summary) return;

    let timeoutId = null;

    const escapeHTML = (value = "") =>
        String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");

    const setResetVisibility = () => {
        if (!resetButton) return;
        resetButton.hidden = searchInput.value.trim().length === 0;
    };

    const hideResults = () => {
        resultsSection.hidden = true;
        resultsContainer.innerHTML = "";
        summary.textContent = "Search across the latest published poems.";
    };

    const renderEmpty = (query) => {
        resultsSection.hidden = false;
        summary.textContent = `No instant poetry matches for "${query}". Press Enter for a full site search.`;
        resultsContainer.innerHTML = '<div class="home-search-empty">Try a broader keyword, a poet name, or continue to the full search page.</div>';
    };

    const renderResults = (results, query) => {
        resultsSection.hidden = false;
        summary.textContent = `${results.length} quick poetry result${results.length === 1 ? "" : "s"} for "${query}".`;
        resultsContainer.innerHTML = results
            .map(
                (item) => `
                    <article class="home-search-result">
                        <h3><a href="${escapeHTML(item.url)}">${escapeHTML(item.title)}</a></h3>
                        <p class="urdu-text">${escapeHTML(item.content_preview)}</p>
                        <div class="home-search-result-meta">
                            <span><i class="bi bi-person"></i> ${escapeHTML(item.author)}</span>
                            <span><i class="bi bi-eye"></i> ${escapeHTML(item.views)}</span>
                        </div>
                    </article>
                `
            )
            .join("");
    };

    const performSearch = async (query) => {
        if (query.length < 2) {
            hideResults();
            return;
        }

        try {
            const response = await fetch(`/search/poetry/?q=${encodeURIComponent(query)}`, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });
            const data = await response.json();
            const results = data.results || [];

            if (!data.success || results.length === 0) {
                renderEmpty(query);
                return;
            }

            renderResults(results, query);
        } catch (error) {
            renderEmpty(query);
        }
    };

    searchInput.addEventListener("input", () => {
        window.clearTimeout(timeoutId);
        setResetVisibility();
        const query = searchInput.value.trim();
        timeoutId = window.setTimeout(() => performSearch(query), 220);
    });

    searchInput.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            searchInput.value = "";
            setResetVisibility();
            hideResults();
            searchInput.blur();
        }
    });

    resetButton?.addEventListener("click", () => {
        searchInput.value = "";
        setResetVisibility();
        hideResults();
        searchInput.focus();
    });

    searchForm?.addEventListener("submit", (event) => {
        if (!searchInput.value.trim()) {
            event.preventDefault();
        }
    });
});
