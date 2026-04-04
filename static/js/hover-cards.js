/**
 * Dynamic Hover Cards JavaScript
 * Enables interactive hover effects for cards with content reveal
 */

(function() {
    'use strict';

    /**
     * Initialize 3D Tilt Effect for cards
     * Creates a perspective tilt effect based on mouse position
     */
    function initTiltCards() {
        const tiltCards = document.querySelectorAll('[data-tilt], .hover-tilt-card');
        
        if (!tiltCards.length) return;

        tiltCards.forEach(card => {
            // Store the original transition
            const originalTransition = getComputedStyle(card).transition;
            
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = ((y - centerY) / centerY) * -10;
                const rotateY = ((x - centerX) / centerX) * 10;
                
                card.style.setProperty('--rotate-x', `${rotateX}deg`);
                card.style.setProperty('--rotate-y', `${rotateY}deg`);
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.setProperty('--rotate-x', '0deg');
                card.style.setProperty('--rotate-y', '0deg');
            });
        });
    }

    /**
     * Initialize Parallax Effect for cards
     * Adds subtle parallax movement on mouse position
     */
    function initParallaxCards() {
        const parallaxCards = document.querySelectorAll('.hover-parallax-card');
        
        if (!parallaxCards.length) return;

        parallaxCards.forEach(card => {
            const bg = card.querySelector('.parallax-bg');
            if (!bg) return;

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left - rect.width / 2) / rect.width;
                const y = (e.clientY - rect.top - rect.height / 2) / rect.height;
                
                const moveX = x * 20;
                const moveY = y * 20;
                
                bg.style.transform = `translate(${moveX}px, ${moveY}px) scale(1.15)`;
            });
            
            card.addEventListener('mouseleave', () => {
                bg.style.transform = 'scale(1)';
            });
        });
    }

    /**
     * Initialize Stagger Reveal Cards
     * Handles the staggered animation for list items
     */
    function initStaggerReveal() {
        const staggerCards = document.querySelectorAll('.hover-stagger-reveal');
        
        if (!staggerCards.length) return;

        staggerCards.forEach(card => {
            const items = card.querySelectorAll('.stagger-item');
            
            // Set initial state
            items.forEach((item, index) => {
                item.style.transitionDelay = `${index * 0.05}s`;
            });
        });
    }

    /**
     * Initialize Card Image Lazy Loading
     * Adds smooth reveal for images inside hover cards
     */
    function initCardImageReveal() {
        const cardImages = document.querySelectorAll('.hover-reveal-card img, .hover-zoom-container img');
        
        if (!cardImages.length) return;

        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('image-loaded');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px 0px'
        });

        cardImages.forEach(img => {
            img.addEventListener('load', () => {
                img.classList.add('image-loaded');
            });
            
            if (img.complete) {
                img.classList.add('image-loaded');
            } else {
                imageObserver.observe(img);
            }
        });
    }

    /**
     * Initialize Ripple Effect for Card Buttons
     * Adds material design style ripple effect
     */
    function initCardRipple() {
        const cardButtons = document.querySelectorAll('.hover-reveal-card .btn, .hover-overlay-card .btn');
        
        cardButtons.forEach(button => {
            button.classList.add('ripple-effect');
        });
    }

    /**
     * Initialize Magnetic Effect for Card Links
     * Subtle magnetic pull towards cursor
     */
    function initMagneticEffect() {
        const magneticElements = document.querySelectorAll('[data-magnetic]');
        
        if (!magneticElements.length) return;

        magneticElements.forEach(element => {
            const strength = parseFloat(element.dataset.magnetic) || 0.3;
            
            element.addEventListener('mousemove', (e) => {
                const rect = element.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                
                const deltaX = (e.clientX - centerX) * strength;
                const deltaY = (e.clientY - centerY) * strength;
                
                element.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
            });
            
            element.addEventListener('mouseleave', () => {
                element.style.transform = 'translate(0, 0)';
            });
        });
    }

    /**
     * Initialize Cursor Follower for Special Cards
     * Adds a custom cursor follower for certain cards
     */
    function initCursorFollower() {
        const followerCards = document.querySelectorAll('[data-cursor-follower]');
        
        if (!followerCards.length) return;

        const follower = document.createElement('div');
        follower.className = 'cursor-follower';
        follower.style.cssText = `
            position: fixed;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(108, 74, 182, 0.3) 0%, transparent 70%);
            pointer-events: none;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s ease;
            mix-blend-mode: multiply;
        `;
        document.body.appendChild(follower);

        followerCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                follower.style.opacity = '1';
            });
            
            card.addEventListener('mouseleave', () => {
                follower.style.opacity = '0';
            });
            
            card.addEventListener('mousemove', (e) => {
                follower.style.left = `${e.clientX - 15}px`;
                follower.style.top = `${e.clientY - 15}px`;
            });
        });
    }

    /**
     * Smooth scroll anchor handling for card links
     */
    function initSmoothScroll() {
        document.querySelectorAll('.hover-reveal-card a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Keyboard accessibility for flip cards
     */
    function initFlipCardAccessibility() {
        const flipCards = document.querySelectorAll('.hover-flip-card');
        
        flipCards.forEach(card => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.setAttribute('aria-label', 'Click to flip card');
            
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const inner = card.querySelector('.card-inner');
                    if (inner) {
                        const isFlipped = inner.style.transform === 'rotateY(180deg)';
                        inner.style.transform = isFlipped ? 'rotateY(0)' : 'rotateY(180deg)';
                    }
                }
            });
        });
    }

    /**
     * Reduced motion detection and handling
     */
    function handleReducedMotion() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        
        function applyMotionPreference() {
            if (prefersReducedMotion.matches) {
                document.body.classList.add('reduced-motion');
            } else {
                document.body.classList.remove('reduced-motion');
            }
        }
        
        prefersReducedMotion.addEventListener('change', applyMotionPreference);
        applyMotionPreference();
    }

    /**
     * Initialize all hover card functionality
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                initTiltCards();
                initParallaxCards();
                initStaggerReveal();
                initCardImageReveal();
                initCardRipple();
                initMagneticEffect();
                initCursorFollower();
                initSmoothScroll();
                initFlipCardAccessibility();
                handleReducedMotion();
            });
        } else {
            initTiltCards();
            initParallaxCards();
            initStaggerReveal();
            initCardImageReveal();
            initCardRipple();
            initMagneticEffect();
            initCursorFollower();
            initSmoothScroll();
            initFlipCardAccessibility();
            handleReducedMotion();
        }
    }

    // Auto-initialize
    init();

    // Expose to global scope for manual initialization
    window.HoverCards = {
        initTiltCards,
        initParallaxCards,
        initStaggerReveal,
        initCardImageReveal,
        initMagneticEffect
    };
})();
