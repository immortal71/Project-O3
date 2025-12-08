# OncoPurpose - Design Style Guide

## Design Philosophy

### Visual Language
- **Professional Authority**: Clean, sophisticated design that instills confidence in pharmaceutical executives
- **Scientific Precision**: Every element serves a functional purpose, reflecting the rigorous nature of drug discovery
- **Innovative Edge**: Modern aesthetics that convey cutting-edge AI technology while maintaining enterprise credibility
- **Trust & Security**: Visual cues that reinforce data integrity and platform reliability

### Color Palette
**Accent Emerald**: #10B981 - Digital precision, clarity, focus
- **Background Dark**: #0F172A - Professional depth, focus, sophistication
- **Card Background**: #1E293B - Elevated surfaces, content hierarchy
- **Text Primary**: #F8FAFC - High contrast readability
- **Text Secondary**: #CBD5E1 - Supporting information, subtle emphasis

### Typography
- **Display Font**: "Inter" - Modern, geometric precision for headings
- **Body Font**: "Inter" - Excellent readability for data-heavy interfaces
- **Monospace**: "JetBrains Mono" - Code, data tables, technical specifications
- **Font Weights**: 300 (Light), 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)

## Visual Effects & Styling

### Glassmorphism Implementation
- **Card Surfaces**: `background: rgba(30, 41, 59, 0.8)` with `backdrop-filter: blur(12px)`
- **Modal Overlays**: `background: rgba(15, 23, 42, 0.7)` with `backdrop-filter: blur(8px)`
- **Floating Elements**: Subtle transparency with border highlights
- **Hover States**: Increased opacity and subtle glow effects

### Animation Library Usage
- **Anime.js**: Smooth property animations, staggered reveals, morphing transitions
- **ECharts.js**: Interactive data visualizations with consistent color theming
- **Splitting.js**: Text reveal animations for headings and key metrics
- **Typed.js**: Typewriter effects for hero taglines and dynamic content

### Interactive Elements
- **Button Hover**: Subtle scale (1.02x) with shadow expansion and color shift
- **Card Hover**: Lift effect with increased shadow and border glow
- **Loading States**: Skeleton screens with shimmer effects
- **Progress Indicators**: Smooth animated fills with percentage counters

### Background Effects
- **Primary Background**: Subtle gradient mesh using dark blues and teals
- **Particle System**: Floating molecular structures using p5.js (low opacity)
- **Grid Overlay**: Subtle dot grid pattern for technical aesthetic
- **Depth Layers**: Multiple z-index levels for visual hierarchy

## Component Styling

### Navigation Bar
- **Height**: 72px for premium feel and touch targets
- **Glass Effect**: Semi-transparent with backdrop blur
- **Active States**: Underline indicators with smooth transitions
- **Search Bar**: Prominent center placement with focus expansion

### Cards & Containers
- **Border Radius**: 12px for modern, friendly appearance
- **Shadows**: Multi-layer shadows for depth (`0 4px 6px -1px rgba(0, 0, 0, 0.1)`)
- **Borders**: 1px solid with subtle transparency
- **Padding**: Generous whitespace for premium feel

### Data Visualizations
- **Chart Colors**: Consistent with brand palette, maximum 3 colors per chart
- **Interaction States**: Hover highlights, click feedback, tooltip animations
- **Loading Animation**: Smooth data entry animations with staggered timing
- **Responsive Design**: Adaptive layouts for different screen sizes

### Form Elements
- **Input Fields**: Glassmorphism styling with focus states
- **Dropdowns**: Custom styling matching overall theme
- **Buttons**: Gradient backgrounds with hover animations
- **Validation**: Inline feedback with color-coded messaging

## Layout Principles

### Grid System
- **Container Max Width**: 1400px for optimal readability
- **Column Gaps**: 24px for generous spacing
- **Responsive Breakpoints**: 640px, 768px, 1024px, 1280px
- **Sidebar Width**: 280px for navigation panels

### Spacing Scale
- **Base Unit**: 8px for consistent rhythm
- **Component Spacing**: 16px, 24px, 32px, 48px
- **Section Spacing**: 64px, 96px for major breaks
- **Micro Spacing**: 4px for tight element relationships

### Content Hierarchy
- **Primary Actions**: Highest contrast and prominence
- **Secondary Actions**: Subtle styling with clear affordance
- **Supporting Content**: Reduced opacity and size
- **Navigation**: Consistent placement and styling

## Responsive Design

### Desktop First
- **Primary Target**: 1440px+ for professional workstations
- **Secondary**: 1024px+ for laptop compatibility
- **Mobile**: Simplified layouts with touch-optimized interactions

### Adaptive Components
- **Navigation**: Collapsible sidebar for smaller screens
- **Charts**: Responsive legends and simplified mobile views
- **Tables**: Horizontal scroll with sticky columns
- **Forms**: Single-column layouts on mobile

## Accessibility Standards

### Color Contrast
- **Text on Background**: Minimum 4.5:1 ratio
- **Interactive Elements**: Minimum 3:1 ratio for large text
- **Focus Indicators**: High contrast outlines
- **Error States**: Color plus icon/text indicators

### Motion & Animation
- **Reduced Motion**: Respect user preferences
- **Focus Management**: Clear focus indicators
- **Screen Readers**: Proper ARIA labels and descriptions
- **Keyboard Navigation**: Full keyboard accessibility

This design system ensures OncoPurpose maintains a consistent, professional appearance that builds trust with pharmaceutical industry users while providing an innovative, modern user experience.