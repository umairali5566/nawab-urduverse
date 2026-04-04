# Mobile App UI Design Guide
## Nawab Urdu Academy - Premium Urdu Literature Platform

---

## 📱 Design Philosophy

The mobile app follows the same premium design system as the web platform:
- **Apple-level premium UI** - Clean, sophisticated, minimalist
- **Medium-level readability** - Focus on content with generous whitespace
- **HamariWeb-level content** - Rich Urdu literature and poetry

### Core Principles

1. **Touch-Friendly** - All interactive elements minimum 44x44px
2. **Large Urdu Typography** - Optimized for reading Nastaliq script
3. **Smooth Interactions** - Native-feeling animations
4. **Dark Mode Default** - Easy on eyes, premium feel
5. **Offline Support** - Progressive Web App capabilities

---

## 🎨 Color Palette (Mobile)

```css
/* Primary Colors */
--bg-main: #0b1220;          /* Deep navy - main background */
--bg-secondary: #111827;      /* Slightly lighter navy */
--card-bg: rgba(255,255,255,0.05);  /* Subtle card backgrounds */
--glass: rgba(255,255,255,0.08);    /* Glassmorphism surfaces */

/* Accent Colors */
--gold: #d4af37;              /* Primary accent - gold */
--gold-light: #f5d67b;        /* Lighter gold for highlights */
--gold-dark: #b8942e;         /* Darker gold for pressed states */

/* Text Colors */
--text-primary: #ffffff;      /* Primary text - white */
--text-secondary: #9ca3af;      /* Secondary text - muted */
--text-muted: #6b7280;         /* Tertiary text */

/* Borders */
--border: rgba(255,255,255,0.1);    /* Subtle borders */
--border-gold: rgba(212,175,55,0.3); /* Gold accent borders */
```

---

## 🔤 Typography (Mobile)

### Font Stack
```css
--font-english: 'Inter', 'Poppins', sans-serif;
--font-urdu: 'Noto Nastaliq Urdu', 'Noto Naskh Arabic', serif;
```

### Font Sizes (Mobile Optimized)
```css
/* Base scale for mobile */
--text-hero: 28px;         /* Hero section titles */
--text-section: 22px;      /* Section headings */
--text-card-title: 17px;   /* Card titles */
--text-body: 15px;         /* Body text */
--text-small: 13px;        /* Small text */
--text-xs: 11px;           /* Extra small */

/* Urdu text - larger for readability */
--text-urdu-hero: 32px;
--text-urdu-body: 20px;    /* Minimum for Nastaliq */
--text-urdu-poetry: 24px;  /* Poetry display */
```

---

## 📐 Layout System

### Screen Structure
```
┌─────────────────────────────┐
│        Status Bar           │  44px
├─────────────────────────────┤
│                             │
│                             │
│       Content Area          │  Flexible
│                             │
│                             │
│                             │
├─────────────────────────────┤
│     Bottom Navigation       │  64px (Safe area + 64px)
└─────────────────────────────┘
```

### Safe Areas
```css
--safe-area-top: env(safe-area-inset-top);
--safe-area-bottom: env(safe-area-inset-bottom);
--navbar-height: 56px;        /* Compact mobile navbar */
--bottom-nav-height: 64px;     /* Bottom navigation */
```

---

## 🧭 Navigation Structure

### Bottom Navigation Bar
```
┌────────────────────────────────────┐
│   Home  │  Search │  Write │ Alerts │ Profile │
│    🏠   │    🔍   │   ✏️   │   🔔   │   👤   │
└────────────────────────────────────┘
```

### Navigation States
- **Default**: Icon + label, muted color
- **Active**: Gold highlight, bold text
- **Badge**: Red dot for notifications

### Mobile Drawer (Secondary Nav)
```
┌────────────────────────────┐
│  ≡  Nawab Urdu Academy    ✕  │
├────────────────────────────┤
│  🔍 Search                 │
├────────────────────────────┤
│  🏠 Home                   │
│  ✒️ Poetry                 │
│  📚 Novels                 │
│  📖 Stories                │
│  💬 Quotes                 │
│  📝 Blog                   │
│  🎬 Videos                 │
│  ✨ AI Studio              │
├────────────────────────────┤
│  👤 Profile    [Logout]    │
└────────────────────────────┘
```

---

## 📄 Screen Designs

### 1. Home Screen (Mobile)

```
┌─────────────────────────────┐
│  Nawab Urdu Academy      🔔   │  <- Header
├─────────────────────────────┤
│                             │
│  ┌───────────────────────┐  │
│  │   Featured Poetry     │  │  <- Hero Card
│  │   (Swipeable)         │  │
│  │   "Poetry text..."    │  │
│  │   - Author Name       │  │
│  └───────────────────────┘  │
│                             │
│  📂 Categories              │
│  ┌────┐┌────┐┌────┐┌────┐   │  <- Horizontal scroll
│  │ ✒️ ││ 📚 ││ 📖 ││ 💬 │   │
│  │Poetry│Novels│Stories│ │ │
│  └────┘└────┘└────┘└────┘   │
│                             │
│  🆕 Latest Poetry           │
│  ┌─────────────────────┐    │
│  │ Author • 2h ago      │    │
│  │ Urdu poetry text...  │    │  <- List items
│  │ ❤️ 123  💬 45  👁️ 1K │    │
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │ ...                 │    │
│  └─────────────────────┘    │
│                             │
├─────────────────────────────┤
│ 🏠  🔍  ✏️  🔔  👤         │  <- Bottom Nav
└─────────────────────────────┘
```

### 2. Search Screen

```
┌─────────────────────────────┐
│  ←  Search           ✕      │
├─────────────────────────────┤
│  ┌─────────────────────┐    │
│  │  🔍 Search poetry... │    │  <- Search bar
│  └─────────────────────┘    │
│                             │
│  🔍 Recent Searches         │
│  • Mirza Ghalib             │
│  • Romantic poetry          │
│                             │
│  🏷️ Popular Tags            │
│  [Ghazal] [Love] [Nature]   │
│  [Sad] [Philosophy] [Life]  │
│                             │
│  📋 Filter                  │
│  ┌────┐┌────┐┌────┐┌────┐   │
│  │ ✒️ ││ 📝 ││ 👤 ││ 🎬 │   │
│  │Poetry││Blog││Author││Video│   │
│  └────┘└────┘└────┘└────┘   │
│                             │
│  📜 Results (156)           │
│  ...                        │
│                             │
├─────────────────────────────┤
│ 🏠  🔍  ✏️  🔔  👤         │
└─────────────────────────────┘
```

### 3. Poetry View Screen

```
┌─────────────────────────────┐
│  ←        ⋮ Share           │  <- Header with actions
├─────────────────────────────┤
│                             │
│  ┌─────────────────────┐    │
│  │                     │    │
│  │   Urdu Poetry       │    │  <- Large centered text
│  │   Text Here...      │    │     Dark background
│  │                     │    │
│  │   With proper       │    │
│  │   Nastaliq font     │    │
│  │                     │    │
│  └─────────────────────┘    │
│                             │
│  Author Name                │
│  @username • Category       │
│                             │
│  ┌──────┐┌──────┐┌──────┐   │  <- Action buttons
│  │ ❤️   ││ 📚   ││ 📤   │   │
│  │ 123  ││ Save ││Share │   │
│  └──────┘└──────┘└──────┘   │
│                             │
│  ─────────────────────────  │
│  Related Poetry             │
│  ...                        │
│                             │
├─────────────────────────────┤
│ 🏠  🔍  ✏️  🔔  👤         │
└─────────────────────────────┘
```

### 4. Author Profile Screen

```
┌─────────────────────────────┐
│  ←  ... (More options)       │
├─────────────────────────────┤
│         ┌──────┐             │
│         │      │             │
│         │ 📷   │             │  <- Profile image
│         │      │             │
│         └──────┘             │
│       Author Name            │
│       @username              │
│       ✓ Verified             │
│                             │
│  Bio text here describing    │
│  the author's work and       │
│  achievements...             │
│                             │
│  ┌────────┐┌────────┐       │
│  │Follower││Following│       │
│  │  12.5K ││   150  │       │
│  └────────┘└────────┘       │
│                             │
│  [ + Follow ]               │  <- Primary CTA
│                             │
│  ─────────────────────────  │
│  📜 Poetry (45)              │
│  ┌────┐┌────┐┌────┐┌────┐   │  <- Content tabs
│  │ 📚 ││ 💬 ││ 🎬 ││ 📝 │   │
│  │Poetry││Quotes││Videos││Blog│   │
│  └────┘└────┘└────┘└────┘   │
│                             │
│  [Grid of content items]     │
│                             │
├─────────────────────────────┤
│ 🏠  🔍  ✏️  🔔  👤         │
└─────────────────────────────┘
```

### 5. Write/Compose Screen

```
┌─────────────────────────────┐
│  ✕  New Poetry      [Save]  │
├─────────────────────────────┤
│                             │
│  Title                      │
│  ┌─────────────────────┐    │
│  │ Enter title...      │    │
│  └─────────────────────┘    │
│                             │
│  Category                   │
│  [Select ▼]                 │
│                             │
│  ┌─────────────────────┐    │
│  │                     │    │
│  │  Urdu poetry text  │    │  <- Main text area
│  │  starts here...    │    │     with Urdu keyboard
│  │                     │    │
│  │                     │    │
│  │                     │    │
│  │                     │    │
│  └─────────────────────┘    │
│                             │
│  Tags                       │
│  [+] Add tags               │
│  #love #romantic #poetry    │
│                             │
│  Cover Image                │
│  [📷 Add Image]             │
│                             │
│  ┌─────────────────────┐    │
│  │ ✨ AI Suggestions   │    │  <- AI features
│  │ Get AI help...      │    │
│  └─────────────────────┘    │
│                             │
├─────────────────────────────┤
│ 🏠  🔍  ✏️  🔔  👤         │
└─────────────────────────────┘
```

---

## 🎯 Interaction Design

### Touch Targets
```css
/* Minimum touch target size */
--touch-target-min: 44px;

/* Spacing between touch targets */
--touch-gap: 8px;
```

### Gestures
| Gesture | Action | Context |
|---------|--------|---------|
| Tap | Select/Action | Buttons, items |
| Long Press | Context menu | Poetry, authors |
| Swipe Left | Quick actions | Delete, share |
| Swipe Right | Navigate back | All screens |
| Pull Down | Refresh | Lists |
| Pull Up | Load more | Lists |

### Animations
```css
/* Timing functions */
--transition-fast: 150ms ease;
--transition-base: 250ms ease;
--transition-slow: 400ms ease;

/* Common animations */
--animate-fade-in: fadeIn 0.3s ease;
--animate-slide-up: slideUp 0.3s ease;
--animate-scale: scale 0.2s ease;
```

### Haptic Feedback
- Light: Selection changes
- Medium: Button press
- Heavy: Successful action (save, publish)

---

## 📐 Component Guidelines

### Cards
```css
.card {
    background: var(--card-bg);
    border-radius: 16px;      /* 20px → 16px for mobile */
    padding: 16px;
    border: 1px solid var(--border);
    margin-bottom: 12px;
}
```

### Buttons
```css
.btn {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 24px;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
}

.btn-primary {
    background: var(--gold);
    color: var(--bg-main);
}

.btn-secondary {
    background: var(--glass);
    border: 1px solid var(--border);
}
```

### Input Fields
```css
.input {
    min-height: 48px;
    padding: 14px 16px;
    font-size: 16px;        /* Prevents iOS zoom */
    border-radius: 12px;
}
```

### Lists
```css
.list-item {
    min-height: 64px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
}
```

### Bottom Sheets
```css
.bottom-sheet {
    border-radius: 20px 20px 0 0;
    max-height: 90vh;
}
```

---

## 🌙 Dark Mode (Default)

Dark mode is the default for the mobile app:

```css
@media (prefers-color-scheme: dark) {
    :root {
        --bg-main: #0b1220;
        --bg-secondary: #111827;
        --text-primary: #ffffff;
        --text-secondary: #9ca3af;
    }
}
```

### Light Mode (Optional toggle)
```css
@media (prefers-color-scheme: light) {
    :root {
        --bg-main: #f8fafc;
        --bg-secondary: #ffffff;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
    }
}
```

---

## ⚡ Performance Optimizations

### Lazy Loading
```javascript
// Images
<img loading="lazy" src="..." />

// Components
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));
```

### Virtual Scrolling
For long lists (>50 items):
```javascript
// Use react-window or similar
<VirtualList
    height={window.innerHeight - 200}
    rowCount={items.length}
    rowHeight={80}
    rowRenderer={RowRenderer}
/>
```

### Image Optimization
```javascript
// Next/Image or similar
<Image
    src={src}
    width={400}
    height={300}
    placeholder="blur"
    loading="lazy"
/>
```

---

## ♿ Accessibility

### Requirements
- Minimum contrast ratio: 4.5:1
- Focus indicators on all interactive elements
- Screen reader support with proper ARIA labels
- Dynamic type support

### Implementation
```html
<!-- Touch target with label -->
<button aria-label="Like this poetry" class="btn btn-icon">
    <i class="bi bi-heart"></i>
</button>

<!-- Semantic structure -->
<article role="article" aria-labelledby="poetry-title">
    <h2 id="poetry-title">Poetry Title</h2>
</article>
```

---

## 📲 PWA Configuration

### Manifest
```json
{
    "name": "Nawab Urdu Academy",
    "short_name": "Urdu Academy",
    "theme_color": "#0b1220",
    "background_color": "#0b1220",
    "display": "standalone",
    "orientation": "portrait",
    "start_url": "/",
    "icons": [
        {
            "src": "/static/images/icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/static/images/icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}
```

### Offline Support
- Cache static assets
- Store user preferences locally
- Queue actions when offline
- Sync when back online

---

## 📋 Mobile Design Checklist

- [ ] Bottom navigation with 5 items
- [ ] Safe area padding applied
- [ ] Touch targets ≥ 44px
- [ ] Urdu text readable (≥ 20px)
- [ ] Swipe gestures work
- [ ] Pull to refresh functional
- [ ] Infinite scroll for lists
- [ ] Dark mode default
- [ ] Haptic feedback on actions
- [ ] PWA installable
- [ ] Offline functionality
- [ ] Performance: < 3s load time
- [ ] Accessibility: VoiceOver/TalkBack support

---

## 🔗 Resources

- [Material Design Guidelines](https://material.io/design)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Web.dev Mobile Best Practices](https://web.dev/responsive-content-in-css/)
- [Noto Nastaliq Urdu Font](https://fonts.google.com/specimen/Noto+Nastaliq+Urdu)

---

*This document is part of the Nawab Urdu Academy design system.*
*Last updated: March 2026*
