/**
 * Shared frontend interactions for Nawab UrduVerse.
 */

document.addEventListener("DOMContentLoaded", () => {
    initDarkMode();
    initReadingProgress();
    initScrollToTop();
    initGenericAuthRequiredTriggers();
    initBookmarkButtons();
    initLikeButtons();
    initShareButtons();
    initNewsletterForm();
    initCommentForms();
    initTooltips();
    initLazyLoading();
    initSidebarToggle();
    initReaderTools();
    initContentProtection();
    initReaderHistory();
    initPoetryTTS();
    initSearchSuggestions();
    initTiltCards();
    initFollowButtons();
    initNotificationActions();
    initPwaSupport();
});

function getCsrfToken() {
    const name = "csrftoken";
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let index = 0; index < cookies.length; index += 1) {
            const cookie = cookies[index].trim();
            if (cookie.startsWith(`${name}=`)) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function safeFetchJSON(url, options = {}) {
    const response = await fetch(url, options);
    let data = {};
    try {
        data = await response.json();
    } catch (error) {
        data = { success: false, message: "Unexpected server response." };
    }
    return { response, data };
}

function showToast(message, type = "success") {
    const existingToast = document.querySelector(".toast-notification");
    if (existingToast) existingToast.remove();

    const toast = document.createElement("div");
    toast.className = `toast-notification alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 280px;";
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);

    window.setTimeout(() => {
        toast.remove();
    }, 3200);
}

function isAuthenticatedUser() {
    return document.body?.dataset.authenticated === "true";
}

function getLoginUrl() {
    return document.body?.dataset.loginUrl || `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
}

function getRegisterUrl() {
    return document.body?.dataset.registerUrl || "/accounts/register/";
}

function getSiteName() {
    return document.body?.dataset.siteName || "Nawab UrduVerse";
}

function getCurrentUsername() {
    return document.body?.dataset.username || "";
}

function getAuthRequiredMessage(action = "interact") {
    const messages = {
        bookmark: "Log in to save this content to your bookmarks.",
        like: "Log in to like and build your personal reading profile.",
        share: "Log in to share content from the reading experience.",
        comment: "Log in to join the reader conversation.",
        copy: "Log in to copy text from the reading experience.",
        selection: "Log in to copy or select text from protected content.",
        screenshot: "This reading area is protected. Log in for a full interactive experience.",
        interact: "Create an account or sign in to bookmark, like, share, comment, or copy from the reading experience.",
    };
    return messages[action] || messages.interact;
}

function showAuthRequiredModal(action = "interact") {
    const modalElement = document.getElementById("authRequiredModal");
    const loginLink = document.getElementById("authRequiredLoginLink");
    const message = document.getElementById("authRequiredModalMessage");
    if (!modalElement || typeof bootstrap === "undefined") {
        showToast("Login required to interact with content.", "warning");
        return;
    }

    if (message) {
        message.textContent = getAuthRequiredMessage(action);
    }
    if (loginLink) {
        loginLink.href = getLoginUrl();
    }

    const instance = bootstrap.Modal.getOrCreateInstance(modalElement);
    instance.show();
}

function requireAuthOrPrompt(action = "interact") {
    if (isAuthenticatedUser()) return true;
    showAuthRequiredModal(action);
    return false;
}

function showContentProtectionOverlay() {
    const overlay = document.getElementById("contentProtectionOverlay");
    if (!overlay) return;

    overlay.classList.add("is-visible");
    window.clearTimeout(showContentProtectionOverlay.timeoutId);
    showContentProtectionOverlay.timeoutId = window.setTimeout(() => {
        overlay.classList.remove("is-visible");
    }, 1500);
}

function readStoredItems(key) {
    try {
        const value = window.localStorage.getItem(key);
        return value ? JSON.parse(value) : [];
    } catch (error) {
        return [];
    }
}

function writeStoredItems(key, items) {
    try {
        window.localStorage.setItem(key, JSON.stringify(items));
    } catch (error) {
        // Ignore storage errors.
    }
}

function upsertStoredItem(key, item, limit = 6) {
    const current = readStoredItems(key).filter((entry) => entry.id !== item.id);
    const next = [item, ...current].slice(0, limit);
    writeStoredItems(key, next);
    return next;
}

function escapeHTML(value = "") {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function initDarkMode() {
    const darkModeToggle = document.getElementById("darkModeToggle");
    const darkModeCSS = document.getElementById("dark-mode-css");
    if (!darkModeToggle) return;

    const isDarkMode = localStorage.getItem("darkMode") === "true";
    if (isDarkMode) {
        document.body.classList.add("dark-mode");
        darkModeCSS?.removeAttribute("disabled");
        darkModeToggle.innerHTML = '<i class="bi bi-sun"></i>';
    } else {
        darkModeToggle.innerHTML = '<i class="bi bi-moon"></i>';
    }

    darkModeToggle.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        const isDark = document.body.classList.contains("dark-mode");
        if (isDark) {
            darkModeCSS?.removeAttribute("disabled");
            darkModeToggle.innerHTML = '<i class="bi bi-sun"></i>';
        } else {
            darkModeCSS?.setAttribute("disabled", "true");
            darkModeToggle.innerHTML = '<i class="bi bi-moon"></i>';
        }
        localStorage.setItem("darkMode", String(isDark));
    });
}

function initReadingProgress() {
    const progressBar = document.querySelector(".reading-progress-bar");
    if (!progressBar) return;

    window.addEventListener("scroll", () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
        progressBar.style.width = `${progress}%`;
    });
}

function initScrollToTop() {
    let scrollBtn = document.querySelector(".scroll-to-top");
    if (!scrollBtn) {
        scrollBtn = document.createElement("div");
        scrollBtn.className = "scroll-to-top";
        scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        document.body.appendChild(scrollBtn);
    }

    window.addEventListener("scroll", () => {
        scrollBtn.classList.toggle("visible", window.pageYOffset > 300);
    });

    scrollBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

function initGenericAuthRequiredTriggers() {
    document.querySelectorAll("[data-auth-required]").forEach((element) => {
        if (element.dataset.bound === "1") return;
        element.dataset.bound = "1";

        element.addEventListener("click", (event) => {
            event.preventDefault();
            requireAuthOrPrompt(element.dataset.authAction || "interact");
        });
    });
}

function initBookmarkButtons() {
    document.querySelectorAll(".bookmark-toggle").forEach((btn) => {
        if (btn.dataset.bound === "1") return;
        btn.dataset.bound = "1";

        btn.addEventListener("click", async (event) => {
            event.preventDefault();
            if (!requireAuthOrPrompt(btn.dataset.authAction || "bookmark")) return;

            const contentType = btn.dataset.contentType;
            const objectId = btn.dataset.objectId;
            if (!contentType || !objectId) return;

            const { response, data } = await safeFetchJSON(`/bookmark/${contentType}/${objectId}/`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCsrfToken(),
                },
            });

            if (response.status === 403) {
                showAuthRequiredModal("bookmark");
                return;
            }

            if (!data.success) {
                showToast(data.message || "Unable to update bookmark.", "danger");
                return;
            }

            const bookmarked = Boolean(data.bookmarked);
            btn.classList.toggle("active", bookmarked);
            btn.setAttribute("aria-pressed", String(bookmarked));

            const icon = btn.querySelector("i");
            const label = btn.querySelector(".bookmark-label");
            if (icon) {
                icon.classList.toggle("bi-bookmark-fill", bookmarked);
                icon.classList.toggle("bi-bookmark", !bookmarked);
            }
            if (label) {
                label.textContent = bookmarked ? "محفوظ" : "محفوظ کریں";
            }

            showToast(data.message || (bookmarked ? "Saved to bookmarks." : "Removed from bookmarks."));
        });
    });
}

function initLikeButtons() {
    document.querySelectorAll(".like-btn").forEach((btn) => {
        if (btn.dataset.bound === "1") return;
        btn.dataset.bound = "1";

        btn.addEventListener("click", async (event) => {
            event.preventDefault();
            if (!requireAuthOrPrompt("like")) return;
            const url = btn.dataset.url;
            if (!url) return;

            const { response, data } = await safeFetchJSON(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (response.status === 403) {
                showAuthRequiredModal("like");
                return;
            }

            if (!data.success) {
                showToast(data.message || "Unable to update like.", "danger");
                return;
            }

            btn.classList.toggle("active", Boolean(data.liked));
            const countEl = btn.querySelector(".like-count");
            if (countEl && typeof data.likes_count !== "undefined") {
                countEl.textContent = data.likes_count;
            }
            showToast(data.message || "Updated.");
        });
    });
}

function initShareButtons() {
    document.querySelectorAll("[data-reader-share], .share-btn").forEach((btn) => {
        if (btn.dataset.bound === "1") return;
        btn.dataset.bound = "1";

        btn.addEventListener("click", async (event) => {
            event.preventDefault();
            if (!requireAuthOrPrompt("share")) return;

            const shareUrl = btn.dataset.shareUrl || window.location.href;
            const shareTitle = btn.dataset.shareTitle || document.title;
            const shareTrackUrl = btn.dataset.shareTrackUrl || "";
            const payload = { title: shareTitle, text: shareTitle, url: shareUrl };

            const updateShareCount = (sharesCount) => {
                const explicitTarget = btn.dataset.shareCountTarget
                    ? document.querySelector(btn.dataset.shareCountTarget)
                    : null;
                const inlineTarget = btn.querySelector(".share-count");
                const fallbackTarget = document.getElementById("poetryShareCount");
                const target = explicitTarget || inlineTarget || fallbackTarget;
                if (target && typeof sharesCount !== "undefined") {
                    target.textContent = sharesCount;
                }
            };

            const trackShare = async () => {
                if (!shareTrackUrl) return;
                const { data } = await safeFetchJSON(shareTrackUrl, {
                    method: "GET",
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                });
                if (data.success) updateShareCount(data.shares_count);
            };

            if (navigator.share) {
                try {
                    await navigator.share(payload);
                    await trackShare();
                    return;
                } catch (error) {
                    // Fall back to clipboard below.
                }
            }

            try {
                await navigator.clipboard.writeText(shareUrl);
                showToast("Link copied to clipboard.");
                await trackShare();
            } catch (error) {
                showToast("Unable to share this content right now.", "danger");
            }
        });
    });
}

function initNewsletterForm() {
    const form = document.getElementById("newsletterForm");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const { data } = await safeFetchJSON(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: { "X-CSRFToken": getCsrfToken() },
        });
        showToast(data.message || "Unable to subscribe.", data.success ? "success" : "danger");
        if (data.success) form.reset();
    });
}

function initCommentForms() {
    document.querySelectorAll("[data-comment-form]").forEach((form) => {
        if (form.dataset.bound === "1") return;
        form.dataset.bound = "1";

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const { response, data } = await safeFetchJSON(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: { "X-CSRFToken": getCsrfToken() },
            });

            if (response.status === 403) {
                showAuthRequiredModal("comment");
                return;
            }

            if (!data.success) {
                showToast(data.message || "Unable to post comment.", "danger");
                return;
            }

            showToast(data.message || "Comment posted.");
            window.location.reload();
        });
    });
}

function initTooltips() {
    if (typeof bootstrap === "undefined") return;
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((element) => {
        new bootstrap.Tooltip(element);
    });
}

function initLazyLoading() {
    if (!("IntersectionObserver" in window)) return;
    const lazyImages = document.querySelectorAll("img[data-src]");
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute("data-src");
            observer.unobserve(img);
        });
    });
    lazyImages.forEach((img) => imageObserver.observe(img));
}

function initSidebarToggle() {
    const sidebar = document.getElementById("sideMenu") || document.querySelector(".sidebar");
    const toggleBtn = document.getElementById("sidebarToggle");
    const backdrop = document.getElementById("menuBackdrop");
    const closeBtn = document.getElementById("drawerClose");
    if (!sidebar || !toggleBtn) return;

    const closeMenu = () => {
        sidebar.classList.remove("open", "is-open");
        toggleBtn.setAttribute("aria-expanded", "false");
        backdrop?.classList.remove("show");
    };

    const openMenu = () => {
        sidebar.classList.add("open", "is-open");
        toggleBtn.setAttribute("aria-expanded", "true");
        backdrop?.classList.add("show");
    };

    toggleBtn.addEventListener("click", (event) => {
        event.preventDefault();
        if (sidebar.classList.contains("open") || sidebar.classList.contains("is-open")) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    backdrop?.addEventListener("click", closeMenu);
    closeBtn?.addEventListener("click", closeMenu);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closeMenu();
    });
    window.addEventListener("resize", () => {
        if (window.innerWidth >= 992) closeMenu();
    });
}

function initReaderTools() {
    const bindOnce = (element, key = "bound") => {
        if (!element || element.dataset[key] === "1") return false;
        element.dataset[key] = "1";
        return true;
    };

    const resolveTarget = (selector, fallbackEl) => {
        if (selector) {
            const found = document.querySelector(selector);
            if (found) return found;
        }
        return fallbackEl?.closest(".reader-shell")?.querySelector(".reader-content") || null;
    };

    document.querySelectorAll("[data-font-action]").forEach((btn) => {
        if (!bindOnce(btn)) return;
        btn.addEventListener("click", () => {
            const action = btn.dataset.fontAction;
            const target = resolveTarget(btn.dataset.readerTarget, btn);
            if (!target) return;

            const computed = parseFloat(window.getComputedStyle(target).fontSize) || 20;
            const step = parseFloat(btn.dataset.fontStep || 1);
            const min = parseFloat(btn.dataset.fontMin || 15);
            const max = parseFloat(btn.dataset.fontMax || 40);
            let next = computed;

            if (action === "increase") next = Math.min(max, computed + step);
            if (action === "decrease") next = Math.max(min, computed - step);
            target.style.fontSize = `${next}px`;
        });
    });

    document.querySelectorAll("[data-copy-target]").forEach((btn) => {
        if (!bindOnce(btn)) return;
        btn.addEventListener("click", async () => {
            if (!requireAuthOrPrompt("copy")) return;
            const target = document.querySelector(btn.dataset.copyTarget || "");
            const content = target?.innerText?.trim();
            if (!content) return;
            try {
                await navigator.clipboard.writeText(content);
                showToast("Copied to clipboard.");
            } catch (error) {
                showToast("Unable to copy text.", "danger");
            }
        });
    });

    document.querySelectorAll("[data-reader-dark-target]").forEach((btn) => {
        if (!bindOnce(btn)) return;
        const syncLabel = (active) => {
            const icon = btn.querySelector("i");
            if (icon) {
                icon.className = active ? "bi bi-sun" : "bi bi-moon-stars";
            }
            const textNode = Array.from(btn.childNodes).find((node) => node.nodeType === Node.TEXT_NODE);
            if (textNode) {
                textNode.textContent = active ? " Day Mode" : " Reading Mode";
            } else if (!btn.dataset.readerModeLabelBound) {
                btn.insertAdjacentText("beforeend", active ? " Day Mode" : " Reading Mode");
            }
            btn.dataset.readerModeLabelBound = "1";
        };

        syncLabel(false);
        btn.addEventListener("click", () => {
            const target = document.querySelector(btn.dataset.readerDarkTarget || "");
            if (!target) return;
            target.classList.toggle("reader-dark");
            const active = target.classList.contains("reader-dark");
            btn.setAttribute("aria-pressed", String(active));
            syncLabel(active);
        });
    });
}

function initContentProtection() {
    const protectedRoots = Array.from(document.querySelectorAll("[data-protected-content]"));
    if (!protectedRoots.length) return;

    protectedRoots.forEach((root) => {
        if (!root.querySelector(".content-watermark")) {
            const watermark = document.createElement("div");
            const label = document.createElement("span");
            watermark.className = "content-watermark";
            watermark.setAttribute("aria-hidden", "true");
            label.textContent = getCurrentUsername() || getSiteName();
            watermark.appendChild(label);
            root.appendChild(watermark);
        }
    });

    if (isAuthenticatedUser()) return;

    document.body.classList.add("is-anonymous-user");

    const protectedSelector = [
        ".reader-content",
        ".quote-reader-text",
        "#videoDescription",
        ".video-media-card .card-body",
    ].join(",");

    protectedRoots.forEach((root) => {
        root.addEventListener("contextmenu", (event) => {
            if (!event.target.closest(protectedSelector)) return;
            event.preventDefault();
            showAuthRequiredModal("interact");
        });

        root.addEventListener("copy", (event) => {
            if (!event.target.closest(protectedSelector)) return;
            event.preventDefault();
            showAuthRequiredModal("copy");
        });

        root.addEventListener("cut", (event) => {
            if (!event.target.closest(protectedSelector)) return;
            event.preventDefault();
            showAuthRequiredModal("copy");
        });

        root.addEventListener("selectstart", (event) => {
            if (!event.target.closest(protectedSelector)) return;
            event.preventDefault();
            showAuthRequiredModal("selection");
        });

        root.addEventListener("dragstart", (event) => {
            if (!event.target.closest(protectedSelector)) return;
            event.preventDefault();
        });
    });

    document.addEventListener("keydown", (event) => {
        const isCopyShortcut = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "c";
        const isPrintScreen = event.key === "PrintScreen";
        const activeElement = document.activeElement;
        const isTypingContext = activeElement
            && (activeElement.tagName === "INPUT"
                || activeElement.tagName === "TEXTAREA"
                || activeElement.isContentEditable);
        const selection = window.getSelection ? window.getSelection() : null;
        const hasProtectedSelection = selection && protectedRoots.some((root) => root.contains(selection.anchorNode));
        if (isCopyShortcut) {
            if (isTypingContext && !hasProtectedSelection) return;
            event.preventDefault();
            showAuthRequiredModal("copy");
        }
        if (isPrintScreen) {
            showContentProtectionOverlay();
        }
    });

    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
            showContentProtectionOverlay();
        }
    });

    window.addEventListener("blur", () => {
        showContentProtectionOverlay();
    });
}

function initReaderHistory() {
    const trackedRoot = document.querySelector("[data-protected-content]");
    const homeHistorySection = document.getElementById("homeHistorySection");
    const recentKey = "nawabRecentlyViewed";
    const continueKey = "nawabContinueReading";

    const renderHistoryItem = (item, type) => {
        const progressMarkup = type === "continue" && typeof item.progress === "number"
            ? `<div class="home-history-progress"><span style="width:${Math.max(6, Math.min(100, item.progress))}%"></span></div>`
            : "";
        const meta = escapeHTML(item.meta || item.type || "Reading");
        const title = escapeHTML(item.title || "Reading");
        const url = escapeHTML(item.url || "#");
        return `
            <a href="${url}" class="home-history-card">
                <div class="home-history-card__meta">${meta}</div>
                <h3>${title}</h3>
                ${progressMarkup}
                <span class="home-history-card__action">${type === "continue" ? "Continue reading" : "Open again"}</span>
            </a>
        `;
    };

    const renderHomeHistory = () => {
        if (!homeHistorySection) return;
        const recentList = document.getElementById("recentlyViewedList");
        const continueList = document.getElementById("continueReadingList");
        if (!recentList || !continueList) return;

        const recentItems = readStoredItems(recentKey).slice(0, 4);
        const continueItems = readStoredItems(continueKey).slice(0, 4);

        recentList.innerHTML = recentItems.length
            ? recentItems.map((item) => renderHistoryItem(item, "recent")).join("")
            : '<div class="home-history-empty">Your recently viewed pages will appear here.</div>';

        continueList.innerHTML = continueItems.length
            ? continueItems.map((item) => renderHistoryItem(item, "continue")).join("")
            : '<div class="home-history-empty">Start reading a chapter to build your continue-reading list.</div>';

        homeHistorySection.hidden = !recentItems.length && !continueItems.length;
    };

    renderHomeHistory();
    if (!trackedRoot) return;

    const title = trackedRoot.dataset.contentTitle || document.title;
    const url = trackedRoot.dataset.contentUrl || window.location.href;
    const id = trackedRoot.dataset.contentId || url;
    const type = trackedRoot.dataset.contentType || "reading";

    upsertStoredItem(recentKey, {
        id,
        title,
        url,
        type,
        meta: type.charAt(0).toUpperCase() + type.slice(1),
        savedAt: Date.now(),
    });

    const continueUrl = trackedRoot.dataset.continueUrl || "";
    if (!continueUrl) return;

    const saveContinueState = () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const progress = scrollHeight > 0 ? Math.round((scrollTop / scrollHeight) * 100) : 0;

        upsertStoredItem(continueKey, {
            id,
            title,
            url: continueUrl,
            type,
            meta: "Continue reading",
            progress,
            savedAt: Date.now(),
        });
    };

    let saveTimer = null;
    const queueSaveContinueState = () => {
        window.clearTimeout(saveTimer);
        saveTimer = window.setTimeout(saveContinueState, 180);
    };

    saveContinueState();
    window.addEventListener("scroll", queueSaveContinueState, { passive: true });
    window.addEventListener("beforeunload", saveContinueState);
}

function initPoetryTTS() {
    const playBtn = document.getElementById("poetryTtsPlay");
    const pauseBtn = document.getElementById("poetryTtsPause");
    const stopBtn = document.getElementById("poetryTtsStop");
    const statusEl = document.getElementById("poetryTtsStatus");
    const audioEl = document.getElementById("poetryTtsAudio");
    if (!playBtn || !pauseBtn || !stopBtn || !audioEl) return;

    const setStatus = (message) => {
        if (statusEl) statusEl.textContent = message;
    };

    const enableControls = (enabled) => {
        pauseBtn.disabled = !enabled;
        stopBtn.disabled = !enabled;
    };

    let isLoading = false;
    let speechMode = false;
    let utterance = null;

    const stopSpeech = () => {
        if ("speechSynthesis" in window) window.speechSynthesis.cancel();
        speechMode = false;
        utterance = null;
    };

    const startBrowserSpeech = () => {
        if (!("speechSynthesis" in window)) {
            setStatus("No TTS engine is available in this browser.");
            return false;
        }
        const text = document.getElementById("poetryReaderContent")?.innerText?.trim();
        if (!text) {
            setStatus("No poetry text found for playback.");
            return false;
        }

        stopSpeech();
        speechMode = true;
        utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "ur-PK";
        utterance.rate = 0.9;
        utterance.onend = () => {
            enableControls(false);
            setStatus("Playback finished.");
            speechMode = false;
            utterance = null;
        };

        window.speechSynthesis.speak(utterance);
        enableControls(true);
        setStatus("Playing browser Urdu voice...");
        return true;
    };

    playBtn.addEventListener("click", async () => {
        if (isLoading) return;
        const ttsUrl = playBtn.dataset.ttsUrl;
        if (!ttsUrl) return;

        if (speechMode && "speechSynthesis" in window && window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
            setStatus("Resumed browser voice.");
            return;
        }

        if (audioEl.src) {
            try {
                await audioEl.play();
                enableControls(true);
                setStatus("Playing Urdu voice...");
                return;
            } catch (error) {
                // Continue to server generation.
            }
        }

        isLoading = true;
        playBtn.disabled = true;
        setStatus("Generating Urdu AI voice...");

        try {
            const { data } = await safeFetchJSON(ttsUrl, {
                method: "GET",
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });

            if (!data.success || !data.audio_url) {
                startBrowserSpeech();
                return;
            }

            stopSpeech();
            speechMode = false;
            audioEl.src = data.audio_url;
            await audioEl.play();
            enableControls(true);
            setStatus(`Playing Urdu voice (${data.engine || "TTS"})`);
        } catch (error) {
            startBrowserSpeech();
        } finally {
            playBtn.disabled = false;
            isLoading = false;
        }
    });

    pauseBtn.addEventListener("click", () => {
        if (speechMode && "speechSynthesis" in window) {
            if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
                window.speechSynthesis.pause();
                setStatus("Browser voice paused.");
            }
            return;
        }

        if (!audioEl.paused) {
            audioEl.pause();
            setStatus("Audio paused.");
        }
    });

    stopBtn.addEventListener("click", () => {
        if (speechMode) stopSpeech();
        audioEl.pause();
        audioEl.currentTime = 0;
        enableControls(false);
        setStatus("Audio stopped.");
    });

    audioEl.addEventListener("ended", () => {
        enableControls(false);
        setStatus("Playback finished.");
    });
}

function initSearchSuggestions() {
    document.querySelectorAll("[data-search-autocomplete]").forEach((wrapper) => {
        if (wrapper.dataset.bound === "1") return;
        wrapper.dataset.bound = "1";

        const searchInput = wrapper.querySelector("[data-search-input]") || wrapper.querySelector('input[name="q"]');
        const suggestionsBox = wrapper.querySelector("[data-search-suggestions]") || wrapper.querySelector(".search-suggestions");
        if (!searchInput || !suggestionsBox) return;

        let timeout = null;

        const closeSuggestions = () => {
            suggestionsBox.innerHTML = "";
            suggestionsBox.classList.remove("show");
        };

        searchInput.addEventListener("input", () => {
            clearTimeout(timeout);
            const query = searchInput.value.trim();
            if (query.length < 2) {
                closeSuggestions();
                return;
            }

            timeout = window.setTimeout(async () => {
                const { data } = await safeFetchJSON(`/search/suggestions/?q=${encodeURIComponent(query)}`);
                const suggestions = data.suggestions || [];
                if (!suggestions.length) {
                    closeSuggestions();
                    return;
                }

                suggestionsBox.innerHTML = suggestions
                    .map(
                        (item) => `
                        <a href="${item.url}" class="search-suggestion-item">
                            <strong>${item.label}</strong>
                            <span>${item.type} - ${item.subtitle}</span>
                        </a>`
                    )
                    .join("");
                suggestionsBox.classList.add("show");
            }, 200);
        });

        document.addEventListener("click", (event) => {
            if (!wrapper.contains(event.target)) closeSuggestions();
        });
    });
}

function initTiltCards() {
    if (window.innerWidth < 992) return;
    const cards = document.querySelectorAll(".content-card, .glass-card, .premium-plan-card, .video-media-card");
    cards.forEach((card) => {
        if (card.dataset.tiltBound === "1") return;
        card.dataset.tiltBound = "1";

        card.addEventListener("mousemove", (event) => {
            const rect = card.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            const rotateY = ((x / rect.width) - 0.5) * 6;
            const rotateX = ((y / rect.height) - 0.5) * -6;
            card.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });
    });
}

function initFollowButtons() {
    document.querySelectorAll(".follow-toggle-btn").forEach((btn) => {
        if (btn.dataset.bound === "1") return;
        btn.dataset.bound = "1";

        btn.addEventListener("click", async () => {
            const url = btn.dataset.followUrl;
            if (!url) return;

            const { response, data } = await safeFetchJSON(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (response.status === 403) {
                window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
                return;
            }

            if (!data.success) {
                showToast(data.message || "Unable to update follow state.", "danger");
                return;
            }

            btn.classList.toggle("btn-primary", Boolean(data.following));
            btn.classList.toggle("btn-outline-primary", !data.following);
            const label = btn.querySelector(".follow-label");
            if (label) {
                label.textContent = data.following ? "Following" : (btn.dataset.followLabelDefault || "Follow");
            }
            showToast(data.following ? "Follow updated." : "Follow removed.");
            window.location.reload();
        });
    });
}

function initNotificationActions() {
    const button = document.querySelector("[data-mark-notifications-read]");
    if (!button) return;

    button.addEventListener("click", async () => {
        const { data } = await safeFetchJSON("/notifications/mark-read/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCsrfToken(),
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        if (!data.success) {
            showToast("Unable to mark notifications as read.", "danger");
            return;
        }

        showToast("Notifications marked as read.");
        window.location.reload();
    });
}

function initPwaSupport() {
    if (!("serviceWorker" in navigator)) return;

    window.addEventListener("load", () => {
        navigator.serviceWorker
            .register("/static/sw.js", { scope: "/" })
            .catch((error) => {
                console.error("Service worker registration failed:", error);
            });
    });
}

window.NawabUrduVerse = {
    showToast,
    getCsrfToken,
};
