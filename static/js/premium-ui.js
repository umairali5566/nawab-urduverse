/**
 * Premium UI JavaScript for Nawab UrduVerse
 * Handles copy/share control, content protection, and interaction controls
 */

(function() {
    'use strict';

    // ============================================
    // COPY PROTECTION SYSTEM
    // ============================================

    class ContentProtection {
        constructor() {
            this.protectedElements = document.querySelectorAll('[data-protected-content]');
            this.isUserLoggedIn = document.body.dataset.userAuthenticated === 'true';
            this.init();
        }

        init() {
            this.protectedElements.forEach(element => {
                this.protectElement(element);
            });
        }

        protectElement(element) {
            if (this.isUserLoggedIn) return;

            // Disable text selection
            element.style.userSelect = 'none';
            element.style.webkitUserSelect = 'none';
            element.styleMozUserSelect = 'none';

            // Disable right-click context menu
            element.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.showLoginPrompt('Right-click disabled. Login to enable actions.');
            });

            // Disable copy shortcut (Ctrl+C)
            element.addEventListener('copy', (e) => {
                e.preventDefault();
                this.showLoginPrompt('Copy disabled. Login to copy poetry.');
            });

            // Disable cut shortcut (Ctrl+X)
            element.addEventListener('cut', (e) => {
                e.preventDefault();
                this.showLoginPrompt('Cut disabled. Login to copy poetry.');
            });

            // Disable drag
            element.addEventListener('dragstart', (e) => {
                e.preventDefault();
            });
        }

        showLoginPrompt(message) {
            // Use the new ContentAccessModal
            if (typeof contentAccessModal !== 'undefined') {
                contentAccessModal.show(message || 'Login required to copy or share content');
            }
        }
    }

    // ============================================
    // COPY BUTTON WITH LOGIN CHECK
    // ============================================

    class CopyButtonHandler {
        constructor() {
            this.copyButtons = document.querySelectorAll('[data-copy-target]');
            this.init();
        }

        init() {
            this.copyButtons.forEach(button => {
                button.addEventListener('click', (e) => this.handleCopy(e, button));
            });
        }

        async handleCopy(e, button) {
            e.preventDefault();
            
            if (!this.isLoggedIn()) {
                this.showLoginRequired();
                return;
            }

            const targetSelector = button.dataset.copyTarget;
            const targetElement = document.querySelector(targetSelector);
            
            if (!targetElement) {
                console.error('Copy target not found:', targetSelector);
                return;
            }

            try {
                const text = this.extractText(targetElement);
                await navigator.clipboard.writeText(text);
                this.showSuccess(button);
            } catch (err) {
                console.error('Copy failed:', err);
                this.showError(button);
            }
        }

        extractText(element) {
            // Extract plain text from the element
            const clone = element.cloneNode(true);
            
            // Remove any script/style elements
            clone.querySelectorAll('script, style').forEach(el => el.remove());
            
            // Get text content
            let text = clone.textContent || clone.innerText;
            
            // Clean up whitespace
            text = text.replace(/\s+/g, ' ').trim();
            
            return text;
        }

        isLoggedIn() {
            return document.body.dataset.userAuthenticated === 'true';
        }

        showLoginRequired() {
            // Use the new ContentAccessModal
            if (typeof contentAccessModal !== 'undefined') {
                contentAccessModal.show('Login required to copy or share content');
            }
        }

        showSuccess(button) {
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="bi bi-check"></i> Copied!';
            button.classList.add('copy-success');
            
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.classList.remove('copy-success');
            }, 2000);
        }

        showError(button) {
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="bi bi-x"></i> Failed';
            button.classList.add('copy-error');
            
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.classList.remove('copy-error');
            }, 2000);
        }
    }

    // ============================================
    // SHARE BUTTON WITH LOGIN CHECK
    // ============================================

    class ShareButtonHandler {
        constructor() {
            this.shareButtons = document.querySelectorAll('[data-reader-share]');
            this.init();
        }

        init() {
            this.shareButtons.forEach(button => {
                button.addEventListener('click', (e) => this.handleShare(e, button));
            });
        }

        async handleShare(e, button) {
            e.preventDefault();
            
            if (!this.isLoggedIn()) {
                this.showLoginRequired();
                return;
            }

            const shareData = {
                title: button.dataset.shareTitle || 'Nawab UrduVerse',
                url: button.dataset.shareUrl || window.location.href
            };

            // Track share on server
            const trackUrl = button.dataset.shareTrackUrl;
            if (trackUrl) {
                fetch(trackUrl, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        const countElement = document.getElementById('poetryShareCount');
                        if (countElement && data.shares_count) {
                            countElement.textContent = data.shares_count;
                        }
                    })
                    .catch(console.error);
            }

            // Try native share API first
            if (navigator.share) {
                try {
                    await navigator.share(shareData);
                    return;
                } catch (err) {
                    if (err.name !== 'AbortError') {
                        console.error('Share failed:', err);
                    }
                }
            }

            // Fallback to copy link
            this.copyShareLink(shareData.url);
        }

        isLoggedIn() {
            return document.body.dataset.userAuthenticated === 'true';
        }

        showLoginRequired() {
            // Use the new ContentAccessModal
            if (typeof contentAccessModal !== 'undefined') {
                contentAccessModal.show('Login required to copy or share content');
            }
        }

        async copyShareLink(url) {
            try {
                await navigator.clipboard.writeText(url);
                this.showCopied();
            } catch (err) {
                console.error('Failed to copy link:', err);
            }
        }

        showCopied() {
            const buttons = document.querySelectorAll('[data-reader-share]');
            buttons.forEach(button => {
                const originalHTML = button.innerHTML;
                button.innerHTML = '<i class="bi bi-check"></i> Link Copied!';
                button.classList.add('share-success');
                
                setTimeout(() => {
                    button.innerHTML = originalHTML;
                    button.classList.remove('share-success');
                }, 2000);
            });
        }
    }

    // ============================================
    // CONTENT ACCESS MODAL (Replaces full-screen overlay)
    // ============================================

    class ContentAccessModal {
        constructor() {
            this.modal = null;
            this.init();
        }

        init() {
            this.createModal();
            this.injectStyles();
        }

        createModal() {
            // Create a small centered modal for login prompts
            this.modal = document.createElement('div');
            this.modal.className = 'content-access-modal';
            this.modal.innerHTML = `
                <div class="content-access-modal__card">
                    <div class="content-access-modal__icon">
                        <i class="bi bi-lock"></i>
                    </div>
                    <div class="content-access-modal__content">
                        <strong>Login required to copy or share content</strong>
                    </div>
                    <div class="content-access-modal__actions">
                        <a href="/accounts/login/" class="btn btn-primary btn-sm">Login</a>
                        <a href="/accounts/register/" class="btn btn-outline-primary btn-sm">Join Free</a>
                    </div>
                    <button type="button" class="content-access-modal__close" aria-label="Close">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            `;
            document.body.appendChild(this.modal);

            // Close button handler
            this.modal.querySelector('.content-access-modal__close').addEventListener('click', () => {
                this.hide();
            });

            // Close on backdrop click
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.hide();
                }
            });
        }

        injectStyles() {
            const style = document.createElement('style');
            style.textContent = `
                .content-access-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    z-index: 9999;
                    display: none;
                    align-items: center;
                    justify-content: center;
                    pointer-events: none;
                    background: transparent;
                }
                .content-access-modal.active {
                    display: flex;
                    pointer-events: auto;
                }
                .content-access-modal__card {
                    position: relative;
                    background: var(--card-bg, #1a1f2e);
                    border: 1px solid rgba(212, 175, 55, 0.2);
                    border-radius: 16px;
                    padding: 24px;
                    max-width: 360px;
                    width: 90%;
                    text-align: center;
                    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
                    animation: modalSlideIn 0.3s ease;
                }
                @keyframes modalSlideIn {
                    from {
                        opacity: 0;
                        transform: translateY(-20px) scale(0.95);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }
                .content-access-modal__icon {
                    width: 48px;
                    height: 48px;
                    margin: 0 auto 16px;
                    border-radius: 50%;
                    background: rgba(212, 175, 55, 0.1);
                    border: 2px solid rgba(212, 175, 55, 0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    color: var(--premium-gold, #D4AF37);
                }
                .content-access-modal__content {
                    margin-bottom: 20px;
                    color: var(--text-primary, #F8FAFC);
                    font-size: 15px;
                    line-height: 1.5;
                }
                .content-access-modal__actions {
                    display: flex;
                    gap: 12px;
                    justify-content: center;
                }
                .content-access-modal__actions .btn {
                    flex: 1;
                }
                .content-access-modal__close {
                    position: absolute;
                    top: 12px;
                    right: 12px;
                    background: transparent;
                    border: none;
                    color: var(--text-muted, #94A3B8);
                    cursor: pointer;
                    padding: 4px;
                    font-size: 18px;
                    line-height: 1;
                    opacity: 0.6;
                    transition: opacity 0.2s;
                }
                .content-access-modal__close:hover {
                    opacity: 1;
                }
            `;
            document.head.appendChild(style);
        }

        show(message = 'Login required to copy or share content') {
            if (this.modal) {
                const content = this.modal.querySelector('.content-access-modal__content strong');
                if (content) {
                    content.textContent = message;
                }
                this.modal.classList.add('active');
                
                // Auto-hide after 4 seconds
                clearTimeout(this.autoHideTimer);
                this.autoHideTimer = setTimeout(() => {
                    this.hide();
                }, 4000);
            }
        }

        hide() {
            if (this.modal) {
                this.modal.classList.remove('active');
            }
        }
    }

    // Global instance
    const contentAccessModal = new ContentAccessModal();

    // ============================================
    // INTERACTIVE ELEMENTS
    // ============================================

    class InteractiveElements {
        constructor() {
            this.initLikeButtons();
            this.initBookmarkButtons();
            this.initHoverEffects();
        }

        initLikeButtons() {
            const likeButtons = document.querySelectorAll('.like-btn');
            
            likeButtons.forEach(button => {
                button.addEventListener('click', async (e) => {
                    e.preventDefault();
                    
                    if (!this.isLoggedIn()) {
                        this.showLoginRequired();
                        return;
                    }

                    const url = button.dataset.url;
                    if (!url) return;

                    try {
                        const response = await fetch(url, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': this.getCSRFToken(),
                            }
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            button.classList.toggle('active');
                            const countEl = button.querySelector('.like-count');
                            if (countEl && data.likes_count !== undefined) {
                                countEl.textContent = data.likes_count;
                            }
                            
                            // Toggle heart icon
                            const icon = button.querySelector('i');
                            if (icon) {
                                icon.classList.toggle('bi-heart');
                                icon.classList.toggle('bi-heart-fill');
                            }
                        }
                    } catch (err) {
                        console.error('Like failed:', err);
                    }
                });
            });
        }

        initBookmarkButtons() {
            const bookmarkButtons = document.querySelectorAll('[data-bookmark]');
            
            bookmarkButtons.forEach(button => {
                button.addEventListener('click', async (e) => {
                    e.preventDefault();
                    
                    if (!this.isLoggedIn()) {
                        this.showLoginRequired();
                        return;
                    }

                    const url = button.dataset.bookmark;
                    if (!url) return;

                    try {
                        const response = await fetch(url, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': this.getCSRFToken(),
                            }
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            button.classList.toggle('active');
                            
                            // Toggle bookmark icon
                            const icon = button.querySelector('i');
                            if (icon) {
                                icon.classList.toggle('bi-bookmark');
                                icon.classList.toggle('bi-bookmark-fill');
                            }
                        }
                    } catch (err) {
                        console.error('Bookmark failed:', err);
                    }
                });
            });
        }

        initHoverEffects() {
            // Add premium tilt effect to cards
            const tiltCards = document.querySelectorAll('[data-premium-tilt]');
            
            tiltCards.forEach(card => {
                card.addEventListener('mousemove', (e) => {
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    const centerX = rect.width / 2;
                    const centerY = rect.height / 2;
                    
                    const rotateX = (y - centerY) / 20;
                    const rotateY = (centerX - x) / 20;
                    
                    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
                });

                card.addEventListener('mouseleave', () => {
                    card.style.transform = '';
                });
            });
        }

        isLoggedIn() {
            return document.body.dataset.userAuthenticated === 'true';
        }

        showLoginRequired() {
            const overlay = document.querySelector('.content-protection-overlay');
            if (overlay) {
                overlay.classList.add('active');
                setTimeout(() => {
                    overlay.classList.remove('active');
                }, 3000);
            }
        }

        getCSRFToken() {
            const name = 'csrftoken';
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
    }

    // ============================================
    // SCROLL ANIMATIONS
    // ============================================

    class ScrollAnimations {
        constructor() {
            this.revealElements = document.querySelectorAll('.reveal-target');
            this.init();
        }

        init() {
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('is-visible');
                            observer.unobserve(entry.target);
                        }
                    });
                }, {
                    threshold: 0.1,
                    rootMargin: '0px 0px -50px 0px'
                });

                this.revealElements.forEach(el => observer.observe(el));
            } else {
                // Fallback for older browsers
                this.revealElements.forEach(el => el.classList.add('is-visible'));
            }
        }
    }

    // ============================================
    // INITIALIZE
    // ============================================

    document.addEventListener('DOMContentLoaded', () => {
        // Initialize all components
        // Note: ContentAccessModal is initialized at the top level as a global
        new ContentProtection();
        new CopyButtonHandler();
        new ShareButtonHandler();
        new InteractiveElements();
        new ScrollAnimations();

        // Add body class for user authentication state
        const userAuthenticated = document.body.dataset.userAuthenticated === 'true';
        
        // Animate page elements on load
        document.querySelectorAll('.site-main > *').forEach((el, index) => {
            el.style.animationDelay = `${index * 0.1}s`;
            el.classList.add('premium-animate-in');
        });
    });

    // Export for potential external use
    window.PremiumUI = {
        ContentProtection,
        CopyButtonHandler,
        ShareButtonHandler,
        ContentAccessModal,
        InteractiveElements,
        ScrollAnimations
    };

})();
