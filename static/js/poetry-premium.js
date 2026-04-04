/**
 * Premium Poetry Page JavaScript
 * Nawab UrduVerse - Interactions, Login Protection, and TTS
 */

(function() {
    'use strict';

    // ===================================
    // Configuration & State
    // ===================================
    const CONFIG = {
        animationDuration: 300,
        toastDuration: 3000,
        blurAmount: 8,
    };

    let state = {
        isAuthenticated: document.body.dataset.authenticated === 'true',
        loginUrl: document.body.dataset.loginUrl || '/accounts/login/',
        registerUrl: document.body.dataset.registerUrl || '/accounts/register/',
        username: document.body.dataset.username || '',
        siteName: document.body.dataset.siteName || 'Nawab UrduVerse',
        isProtected: false,
        ttsPlaying: false,
    };

    // ===================================
    // DOM Elements
    // ===================================
    const elements = {
        page: document.querySelector('.premium-poetry-page'),
        loginOverlay: document.getElementById('loginRequiredOverlay'),
        closeLoginBtn: document.getElementById('closeLoginOverlay'),
        poetryTextContainer: document.getElementById('poetryTextContainer'),
        contentBlurOverlay: document.getElementById('contentBlurOverlay'),
        actionBar: document.getElementById('actionBar'),
        ttsPlayer: document.getElementById('ttsPlayer'),
        ttsAudio: document.getElementById('ttsAudio'),
        ttsPlayBtn: document.getElementById('ttsPlayBtn'),
        ttsProgressBar: document.getElementById('ttsProgressBar'),
        ttsTime: document.getElementById('ttsTime'),
        ttsCloseBtn: document.getElementById('ttsCloseBtn'),
        screenshotProtection: document.getElementById('screenshotProtection'),
        likeCount: document.getElementById('likeCount'),
        shareCount: document.getElementById('shareCount'),
    };

    // ===================================
    // Initialization
    // ===================================
    function init() {
        if (!elements.page) return;

        initLoginProtection();
        initActionButtons();
        initTTS();
        initCopyProtection();
        initScreenshotProtection();
        initCommentForm();
        initScrollAnimations();
        initShareFunctionality();
        initBookmarkToggle();
        
        console.log('Premium Poetry Page initialized');
    }

    // ===================================
    // Login Protection System
    // ===================================
    function initLoginProtection() {
        // Check if content is protected
        if (elements.poetryTextContainer && elements.poetryTextContainer.dataset.protected === 'true') {
            state.isProtected = true;
            
            // Add event listeners to protected actions
            document.querySelectorAll('.copy-action, .action-btn[data-action="share"]').forEach(btn => {
                btn.addEventListener('click', showLoginOverlay);
            });
        }

        // Close login overlay handler
        if (elements.closeLoginBtn) {
            elements.closeLoginBtn.addEventListener('click', hideLoginOverlay);
        }

        // Close on backdrop click
        if (elements.loginOverlay) {
            elements.loginOverlay.addEventListener('click', (e) => {
                if (e.target === elements.loginOverlay) {
                    hideLoginOverlay();
                }
            });
        }

        // Keyboard escape to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && elements.loginOverlay && !elements.loginOverlay.classList.contains('hidden')) {
                hideLoginOverlay();
            }
        });
    }

    function showLoginOverlay() {
        if (elements.loginOverlay) {
            elements.loginOverlay.classList.remove('hidden');
            elements.loginOverlay.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    function hideLoginOverlay() {
        if (elements.loginOverlay) {
            elements.loginOverlay.classList.add('hidden');
            setTimeout(() => {
                elements.loginOverlay.style.display = 'none';
            }, CONFIG.animationDuration);
            document.body.style.overflow = '';
        }
    }

    // ===================================
    // Action Buttons
    // ===================================
    function initActionButtons() {
        // Like Button
        const likeBtn = document.querySelector('.like-action');
        if (likeBtn) {
            likeBtn.addEventListener('click', handleLike);
        }

        // Save/Bookmark Button
        const saveBtn = document.querySelector('.save-action');
        if (saveBtn) {
            saveBtn.addEventListener('click', handleSave);
        }

        // Copy Button
        const copyBtn = document.querySelector('.copy-action');
        if (copyBtn) {
            copyBtn.addEventListener('click', handleCopy);
        }

        // Share Button
        const shareBtn = document.querySelector('.share-action');
        if (shareBtn) {
            shareBtn.addEventListener('click', handleShare);
        }

        // Header actions
        const headerBookmarkBtn = document.querySelector('.bookmark-toggle');
        if (headerBookmarkBtn) {
            headerBookmarkBtn.addEventListener('click', handleHeaderBookmark);
        }

        const headerShareBtn = document.querySelector('.share-btn');
        if (headerShareBtn) {
            headerShareBtn.addEventListener('click', handleShare);
        }
    }

    async function handleLike(e) {
        const btn = e.currentTarget;
        const url = btn.dataset.url;

        if (!url) return;

        // Check authentication
        if (!state.isAuthenticated) {
            showLoginOverlay();
            return;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken(),
                },
            });

            const data = await response.json();

            if (data.success) {
                btn.classList.toggle('active');
                const icon = btn.querySelector('i');
                
                if (data.action === 'liked') {
                    icon.classList.remove('bi-heart');
                    icon.classList.add('bi-heart-fill');
                    btn.classList.add('active');
                } else {
                    icon.classList.remove('bi-heart-fill');
                    icon.classList.add('bi-heart');
                    btn.classList.remove('active');
                }

                // Update count
                if (elements.likeCount) {
                    elements.likeCount.textContent = data.likes_count || btn.querySelector('.action-btn__count').textContent;
                }

                showToast(data.message || (data.action === 'liked' ? 'Liked!' : 'Unliked'), 'success');
            }
        } catch (error) {
            console.error('Like error:', error);
            showToast('Something went wrong', 'error');
        }
    }

    async function handleSave(e) {
        const btn = e.currentTarget;
        
        if (!state.isAuthenticated) {
            showLoginOverlay();
            return;
        }

        // Toggle visual state immediately for better UX
        const icon = btn.querySelector('.action-btn__icon i');
        const headerIcon = document.querySelector('.bookmark-toggle i');
        
        const isCurrentlyActive = btn.classList.contains('active');
        
        // Optimistic update
        if (isCurrentlyActive) {
            btn.classList.remove('active');
            icon.classList.remove('bi-bookmark-fill');
            icon.classList.add('bi-bookmark');
            if (headerIcon) {
                headerIcon.classList.remove('bi-bookmark-fill');
                headerIcon.classList.add('bi-bookmark');
            }
            document.querySelector('.bookmark-toggle')?.classList.remove('active');
        } else {
            btn.classList.add('active');
            icon.classList.remove('bi-bookmark');
            icon.classList.add('bi-bookmark-fill');
            if (headerIcon) {
                headerIcon.classList.remove('bi-bookmark');
                headerIcon.classList.add('bi-bookmark-fill');
            }
            document.querySelector('.bookmark-toggle')?.classList.add('active');
        }

        // Get URL from data attribute
        const url = document.querySelector('.bookmark-toggle')?.dataset.url;
        if (!url) return;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken(),
                },
            });

            const data = await response.json();
            
            if (!data.success) {
                // Revert on error
                if (isCurrentlyActive) {
                    btn.classList.add('active');
                    icon.classList.add('bi-bookmark-fill');
                    icon.classList.remove('bi-bookmark');
                } else {
                    btn.classList.remove('active');
                    icon.classList.add('bi-bookmark');
                    icon.classList.remove('bi-bookmark-fill');
                }
                showToast(data.message || 'Something went wrong', 'error');
            } else {
                showToast(data.message || (data.action === 'saved' ? 'Saved to bookmarks!' : 'Removed from bookmarks'), 'success');
            }
        } catch (error) {
            console.error('Save error:', error);
            showToast('Something went wrong', 'error');
        }
    }

    async function handleHeaderBookmark(e) {
        const btn = e.currentTarget;
        const url = btn.dataset.url;

        if (!state.isAuthenticated) {
            showLoginOverlay();
            return;
        }

        if (!url) return;

        const icon = btn.querySelector('i');
        const isCurrentlyActive = btn.classList.contains('active');

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken(),
                },
            });

            const data = await response.json();

            if (data.success) {
                btn.classList.toggle('active');
                
                if (data.action === 'saved') {
                    icon.classList.remove('bi-bookmark');
                    icon.classList.add('bi-bookmark-fill');
                    btn.classList.add('active');
                    // Update action bar button too
                    const actionSaveBtn = document.querySelector('.save-action');
                    if (actionSaveBtn) {
                        actionSaveBtn.classList.add('active');
                        const actionIcon = actionSaveBtn.querySelector('.action-btn__icon i');
                        if (actionIcon) {
                            actionIcon.classList.remove('bi-bookmark');
                            actionIcon.classList.add('bi-bookmark-fill');
                        }
                    }
                } else {
                    icon.classList.remove('bi-bookmark-fill');
                    icon.classList.add('bi-bookmark');
                    btn.classList.remove('active');
                    // Update action bar button too
                    const actionSaveBtn = document.querySelector('.save-action');
                    if (actionSaveBtn) {
                        actionSaveBtn.classList.remove('active');
                        const actionIcon = actionSaveBtn.querySelector('.action-btn__icon i');
                        if (actionIcon) {
                            actionIcon.classList.add('bi-bookmark');
                            actionIcon.classList.remove('bi-bookmark-fill');
                        }
                    }
                }

                showToast(data.message || (data.action === 'saved' ? 'Saved!' : 'Removed'), 'success');
            }
        } catch (error) {
            console.error('Bookmark error:', error);
            showToast('Something went wrong', 'error');
        }
    }

    async function handleCopy(e) {
        const btn = e.currentTarget;
        const copyText = btn.dataset.copyText;

        if (!state.isAuthenticated) {
            showLoginOverlay();
            return;
        }

        if (!copyText) {
            // Try to get text from poetry container
            const poetryText = document.querySelector('#poetryText');
            if (poetryText) {
                copyText = poetryText.innerText;
            }
        }

        try {
            await navigator.clipboard.writeText(copyText);
            
            // Visual feedback
            btn.classList.add('copied');
            const icon = btn.querySelector('i');
            icon.classList.remove('bi-clipboard');
            icon.classList.add('bi-check');
            
            showToast('Copied to clipboard!', 'success');

            setTimeout(() => {
                btn.classList.remove('copied');
                icon.classList.remove('bi-check');
                icon.classList.add('bi-clipboard');
            }, 2000);
        } catch (error) {
            console.error('Copy error:', error);
            showToast('Failed to copy', 'error');
        }
    }

    function handleShare(e) {
        const btn = e.currentTarget;
        const shareTitle = btn.dataset.shareTitle || state.siteName;
        const shareText = btn.dataset.shareText || '';
        const shareUrl = btn.dataset.shareUrl || window.location.href;

        if (navigator.share) {
            navigator.share({
                title: shareTitle,
                text: shareText,
                url: shareUrl,
            }).then(() => {
                // Track share
                trackShare(shareUrl);
            }).catch(console.error);
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(`${shareTitle}\n\n${shareUrl}`).then(() => {
                showToast('Link copied! Share it with friends', 'success');
                trackShare(shareUrl);
            });
        }
    }

    async function trackShare(url) {
        const shareTrackBtn = document.querySelector('[data-share-track-url]');
        if (shareTrackBtn) {
            const trackUrl = shareTrackBtn.dataset.shareTrackUrl;
            try {
                const response = await fetch(trackUrl, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCSRFToken(),
                    },
                });
                const data = await response.json();
                if (elements.shareCount && data.shares_count) {
                    elements.shareCount.textContent = data.shares_count;
                }
            } catch (error) {
                console.error('Share tracking error:', error);
            }
        }
    }

    // ===================================
    // TTS (Text-to-Speech)
    // ===================================
    function initTTS() {
        const ttsBtn = document.querySelector('.tts-action');
        
        if (!ttsBtn || !elements.ttsAudio) return;

        const ttsUrl = ttsBtn.dataset.ttsUrl;

        ttsBtn.addEventListener('click', async () => {
            if (state.ttsPlaying) {
                toggleTTS('pause');
                return;
            }

            // Show player
            if (elements.ttsPlayer) {
                elements.ttsPlayer.style.display = 'block';
            }

            // If no audio loaded, fetch it
            if (!elements.ttsAudio.src || elements.ttsAudio.src === window.location.href) {
                await loadTTS(ttsUrl);
            }

            toggleTTS('play');
        });

        // Play/Pause button
        if (elements.ttsPlayBtn) {
            elements.ttsPlayBtn.addEventListener('click', () => {
                toggleTTS(elements.ttsAudio.paused ? 'play' : 'pause');
            });
        }

        // Close button
        if (elements.ttsCloseBtn) {
            elements.ttsCloseBtn.addEventListener('click', () => {
                toggleTTS('stop');
                if (elements.ttsPlayer) {
                    elements.ttsPlayer.style.display = 'none';
                }
            });
        }

        // Audio events
        elements.ttsAudio.addEventListener('timeupdate', updateTTSProgress);
        elements.ttsAudio.addEventListener('ended', () => {
            state.ttsPlaying = false;
            updateTTSPlayButton();
        });

        // Progress bar click
        const ttsProgress = document.querySelector('.tts-progress');
        if (ttsProgress) {
            ttsProgress.addEventListener('click', (e) => {
                const rect = ttsProgress.getBoundingClientRect();
                const percent = (e.clientX - rect.left) / rect.width;
                elements.ttsAudio.currentTime = percent * elements.ttsAudio.duration;
            });
        }
    }

    async function loadTTS(url) {
        try {
            const response = await fetch(url);
            const data = await response.json();

            if (data.success && data.audio_url) {
                elements.ttsAudio.src = data.audio_url;
            } else {
                showToast(data.message || 'TTS unavailable', 'error');
                if (elements.ttsPlayer) {
                    elements.ttsPlayer.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('TTS load error:', error);
            showToast('Failed to load audio', 'error');
            if (elements.ttsPlayer) {
                elements.ttsPlayer.style.display = 'none';
            }
        }
    }

    function toggleTTS(action) {
        if (!elements.ttsAudio.src) return;

        switch (action) {
            case 'play':
                elements.ttsAudio.play();
                state.ttsPlaying = true;
                break;
            case 'pause':
                elements.ttsAudio.pause();
                state.ttsPlaying = false;
                break;
            case 'stop':
                elements.ttsAudio.pause();
                elements.ttsAudio.currentTime = 0;
                state.ttsPlaying = false;
                if (elements.ttsProgressBar) {
                    elements.ttsProgressBar.style.width = '0%';
                }
                break;
        }

        updateTTSPlayButton();
    }

    function updateTTSPlayButton() {
        if (!elements.ttsPlayBtn) return;
        
        const icon = elements.ttsPlayBtn.querySelector('i');
        if (state.ttsPlaying) {
            icon.classList.remove('bi-play-fill');
            icon.classList.add('bi-pause-fill');
        } else {
            icon.classList.remove('bi-pause-fill');
            icon.classList.add('bi-play-fill');
        }
    }

    function updateTTSProgress() {
        if (!elements.ttsAudio.duration) return;

        const percent = (elements.ttsAudio.currentTime / elements.ttsAudio.duration) * 100;
        
        if (elements.ttsProgressBar) {
            elements.ttsProgressBar.style.width = `${percent}%`;
        }

        if (elements.ttsTime) {
            const current = formatTime(elements.ttsAudio.currentTime);
            const total = formatTime(elements.ttsAudio.duration);
            elements.ttsTime.textContent = `${current} / ${total}`;
        }
    }

    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    // ===================================
    // Copy Protection
    // ===================================
    function initCopyProtection() {
        if (!state.isAuthenticated) {
            // Disable text selection
            document.body.style.userSelect = 'none';
            document.body.style.webkitUserSelect = 'none';

            // Disable right-click
            document.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                showToast('Sign in to interact with content', 'error');
            });

            // Disable copy/paste shortcuts
            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'a')) {
                    e.preventDefault();
                    showToast('Sign in to copy content', 'error');
                }
            });

            // Disable drag
            document.addEventListener('dragstart', (e) => {
                e.preventDefault();
            });
        }
    }

    // ===================================
    // Screenshot Protection
    // ===================================
    function initScreenshotProtection() {
        if (!state.isAuthenticated && elements.screenshotProtection) {
            // Add watermark with username
            const watermark = elements.screenshotProtection.querySelector('.watermark-overlay');
            if (watermark && state.username) {
                watermark.setAttribute('data-watermark', state.username);
            }

            // Show/hide based on login state
            // Note: CSS-level screenshot protection is limited
        }
    }

    // ===================================
    // Comment Form
    // ===================================
    function initCommentForm() {
        const commentForm = document.querySelector('[data-comment-form]');
        
        if (!commentForm) return;

        commentForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!state.isAuthenticated) {
                showLoginOverlay();
                return;
            }

            const textarea = commentForm.querySelector('textarea');
            const text = textarea.value.trim();

            if (!text) {
                showToast('Please write a comment', 'error');
                return;
            }

            const formData = new FormData(commentForm);
            const actionUrl = commentForm.action;

            try {
                const response = await fetch(actionUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCSRFToken(),
                    },
                });

                const data = await response.json();

                if (data.success) {
                    textarea.value = '';
                    showToast('Comment posted!', 'success');
                    // Optionally reload comments or append new one
                    location.reload();
                } else {
                    showToast(data.message || 'Failed to post comment', 'error');
                }
            } catch (error) {
                console.error('Comment error:', error);
                showToast('Something went wrong', 'error');
            }
        });

        // Reply buttons
        document.querySelectorAll('.reply-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!state.isAuthenticated) {
                    showLoginOverlay();
                    return;
                }
                // Scroll to comment form
                const commentForm = document.querySelector('[data-comment-form]');
                if (commentForm) {
                    commentForm.scrollIntoView({ behavior: 'smooth' });
                    commentForm.querySelector('textarea').focus();
                }
            });
        });

        // Show/hide replies
        document.querySelectorAll('.show-replies-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const commentId = btn.dataset.commentId;
                const repliesContainer = document.getElementById(`replies-${commentId}`);
                if (repliesContainer) {
                    repliesContainer.classList.toggle('visible');
                    const isVisible = repliesContainer.classList.contains('visible');
                    btn.innerHTML = `<i class="bi bi-chat-left"></i> ${isVisible ? 'Hide' : 'Show'} Replies`;
                }
            });
        });
    }

    // ===================================
    // Share Functionality
    // ===================================
    function initShareFunctionality() {
        // Already handled in action buttons
    }

    // ===================================
    // Bookmark Toggle (Header)
    // ===================================
    function initBookmarkToggle() {
        // Already handled in action buttons
    }

    // ===================================
    // Scroll Animations
    // ===================================
    function initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px',
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe related cards
        document.querySelectorAll('.related-card').forEach(card => {
            observer.observe(card);
        });

        // Observe comments
        document.querySelectorAll('.comment-item').forEach(comment => {
            observer.observe(comment);
        });
    }

    // ===================================
    // Toast Notifications
    // ===================================
    function showToast(message, type = 'success') {
        // Remove existing toast
        const existingToast = document.querySelector('.premium-toast');
        if (existingToast) {
            existingToast.remove();
        }

        // Create toast
        const toast = document.createElement('div');
        toast.className = `premium-toast ${type}`;
        toast.innerHTML = `
            <i class="bi ${type === 'success' ? 'bi-check-circle' : 'bi-exclamation-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('visible');
        });

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('visible');
            setTimeout(() => toast.remove(), CONFIG.animationDuration);
        }, CONFIG.toastDuration);
    }

    // ===================================
    // Utility Functions
    // ===================================
    function getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        // Fallback: get from cookie
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

    // ===================================
    // Initialize on DOM Ready
    // ===================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
