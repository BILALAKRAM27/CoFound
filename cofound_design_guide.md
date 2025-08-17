# CoFound Design System Reference

## Overview
This design system provides a comprehensive guide for maintaining visual consistency across the CoFound collaborative platform. The design emphasizes modern aesthetics, accessibility, and responsive behavior.

## Color Palette

### CSS Custom Properties (Design Tokens)
```css
:root {
    --cf-primary: #1e3a8a;      /* Deep blue - primary brand color */
    --cf-secondary: #0ea5e9;    /* Sky blue - secondary actions */
    --cf-accent: #f59e0b;       /* Amber - highlights and badges */
    --cf-success: #10b981;      /* Emerald - success states */
    --cf-sidebar-bg: #f8fafc;   /* Slate gray - sidebar background */
    --cf-sidebar-border: #e2e8f0; /* Light gray - borders */
    --cf-text-primary: #1f2937; /* Dark gray - primary text */
    --cf-text-secondary: #6b7280; /* Medium gray - secondary text */
}
```

### Dark Mode Overrides
```css
[data-bs-theme="dark"] {
    --cf-sidebar-bg: #1e293b;
    --cf-sidebar-border: #334155;
    --cf-text-primary: #f1f5f9;
    --cf-text-secondary: #cbd5e1;
}
```

### Shadow Definitions
```css
--cf-card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--cf-card-shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
```

## Typography

### Font Stack
- **Primary Font Family**: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Font Weights Available**: 300, 400, 500, 600, 700
- **Base Line Height**: 1.6

### Typography Scale
- **Navbar Brand**: 1.5rem, font-weight: 700
- **Page Titles**: h3 class with `fw-bold`
- **Card Headers**: font-weight: 600
- **Navigation Links**: font-weight: 500
- **Body Text**: Default system sizing with Inter font

## Layout System

### Container Structure
- **Fixed Top Offset**: `padding-top: 76px` (body)
- **Sidebar Width**: 260px (fixed)
- **Main Content Margin**: `margin-left: 260px` (desktop)

### Responsive Breakpoints
- **Mobile**: `@media (max-width: 991.98px)`
  - Sidebar collapses to overlay
  - Main content full width
  - Reduced padding: 1rem
- **Small Mobile**: `@media (max-width: 576px)`
  - Further reduced padding: 0.5rem
  - Smaller navbar brand font

## Component Styles

### Navigation Bar
```css
.navbar {
    background: linear-gradient(135deg, var(--cf-primary) 0%, #2563eb 100%);
    box-shadow: var(--cf-card-shadow);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
```

#### Navbar Links
```css
.navbar-nav .nav-link {
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    margin: 0 2px;
    transition: all 0.3s ease;
}

.navbar-nav .nav-link:hover {
    color: white;
    background-color: rgba(255, 255, 255, 0.1);
    transform: translateY(-1px);
}

.navbar-nav .nav-link.active {
    background-color: rgba(255, 255, 255, 0.15);
}
```

### Sidebar Navigation
```css
.sidebar {
    background-color: var(--cf-sidebar-bg);
    border-right: 2px solid var(--cf-sidebar-border);
    width: 260px;
    box-shadow: 4px 0 6px -1px rgba(0, 0, 0, 0.1);
}
```

#### Sidebar Links
```css
.sidebar-nav .nav-link {
    color: var(--cf-text-secondary);
    padding: 0.875rem 1.5rem;
    font-weight: 500;
    border-radius: 0 25px 25px 0;
    margin-right: 1rem;
    transition: all 0.3s ease;
}

.sidebar-nav .nav-link:hover {
    color: var(--cf-primary);
    background-color: rgba(30, 58, 138, 0.1);
    transform: translateX(4px);
}

.sidebar-nav .nav-link.active {
    color: white;
    background: linear-gradient(135deg, var(--cf-primary) 0%, var(--cf-secondary) 100%);
    box-shadow: var(--cf-card-shadow);
}
```

### Cards
```css
.card {
    border: none;
    border-radius: 16px;
    box-shadow: var(--cf-card-shadow);
    transition: all 0.3s ease;
    background-color: var(--bs-body-bg);
}

.card:hover {
    box-shadow: var(--cf-card-shadow-hover);
    transform: translateY(-2px);
}

.card-header {
    background: linear-gradient(135deg, var(--cf-primary) 0%, var(--cf-secondary) 100%);
    color: white;
    border-radius: 16px 16px 0 0;
    padding: 1.25rem 1.5rem;
    font-weight: 600;
}
```

### Buttons

#### Base Button Styles
```css
.btn {
    font-weight: 500;
    border-radius: 10px;
    padding: 0.625rem 1.25rem;
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
```

#### Button Variants
```css
.btn-primary {
    background: linear-gradient(135deg, var(--cf-primary) 0%, var(--cf-secondary) 100%);
}

.btn-accent {
    background: linear-gradient(135deg, var(--cf-accent) 0%, #f97316 100%);
    color: white;
}

.theme-toggle {
    background: none;
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    border-radius: 50px;
    padding: 0.5rem 0.75rem;
    transition: all 0.3s ease;
}
```

### Dropdown Menus
```css
.dropdown-menu {
    border: none;
    box-shadow: var(--cf-card-shadow-hover);
    border-radius: 12px;
    padding: 0.5rem 0;
    margin-top: 0.5rem;
}

.dropdown-item {
    padding: 0.75rem 1.25rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.dropdown-item:hover {
    background-color: var(--cf-primary);
    color: white;
    transform: translateX(4px);
}
```

## Interactive Elements

### Badges
- **Accent Badge**: `bg-accent rounded-pill`
- **Success Badge**: `bg-success rounded-pill`
- **Status Badges**: Various Bootstrap color variants

### Icons
- **Icon Library**: Bootstrap Icons
- **Icon Spacing**: `me-1` or `me-2` for inline icons
- **Sidebar Icons**: `margin-right: 0.75rem`, `font-size: 1.1rem`

## Animation & Transitions

### Standard Transitions
```css
transition: all 0.3s ease;  /* Most interactive elements */
transition: all 0.2s ease;  /* Fast interactions (dropdown items) */
```

### Hover Transforms
- **Cards**: `translateY(-2px)`
- **Buttons**: `translateY(-2px)`
- **Navbar Links**: `translateY(-1px)`
- **Sidebar Links**: `translateX(4px)`
- **Dropdown Items**: `translateX(4px)`

### Loading Animation
```css
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
```

## Scrollbar Styling
```css
.sidebar::-webkit-scrollbar {
    width: 6px;
}

.sidebar::-webkit-scrollbar-track {
    background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
    background-color: var(--cf-sidebar-border);
    border-radius: 3px;
}
```

## Footer
```css
.footer {
    background-color: var(--cf-sidebar-bg);
    border-top: 2px solid var(--cf-sidebar-border);
    padding: 2rem 0;
    margin-top: 3rem;
}
```

## Utility Classes

### Spacing
- **Page Content**: `padding: 2rem` (desktop), `padding: 1rem` (tablet), `padding: 0.5rem` (mobile)
- **Card Body**: `padding: 1.25rem 1.5rem` (headers)

### State Management Classes
- **Collapsed Sidebar**: `.sidebar.collapsed { margin-left: -260px; }`
- **Expanded Content**: `.main-content.expanded { margin-left: 0; }`
- **Mobile Sidebar Show**: `.sidebar.show { margin-left: 0; }`

## JavaScript Integration

### Theme Toggle
- Uses `data-bs-theme` attribute on `<html>`
- Stores preference in `localStorage`
- Toggles between 'light' and 'dark' values

### Sidebar Behavior
- Desktop: Toggle collapse/expand
- Mobile: Overlay show/hide
- Auto-hide on outside click (mobile only)

## Best Practices

1. **Consistent Spacing**: Use Bootstrap spacing utilities (mb-3, me-2, etc.)
2. **Color Usage**: Always use CSS custom properties for brand colors
3. **Transitions**: Apply standard 0.3s ease transitions to interactive elements
4. **Shadows**: Use defined shadow variables for consistency
5. **Border Radius**: Cards use 16px, buttons use 10px, badges use pill class
6. **Typography**: Maintain font-weight hierarchy (300-700 range)
7. **Icons**: Always include appropriate margin classes for spacing