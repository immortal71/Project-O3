# OncoPurpose - Project Outline

## File Structure
```
/mnt/okcomputer/output/
├── index.html              # Landing page
├── dashboard.html          # Main dashboard
├── discovery.html          # Drug discovery interface
├── details.html           # Drug detail page
├── library.html           # Research library
├── analytics.html         # Analytics dashboard
├── settings.html          # Account settings
├── main.js               # Core JavaScript functionality
├── resources/            # Assets directory
│   ├── hero-bg.jpg       # Hero background image
│   ├── drug-structures/  # Drug structure images
│   ├── company-logos/    # Pharma company logos
│   └── user-avatars/     # User profile images
├── interaction.md        # Interaction design document
├── design.md            # Design style guide
└── outline.md           # This project outline
```

## Page Breakdown

### 1. index.html - Landing Page
**Purpose**: Professional landing page for enterprise pharma companies
**Key Sections**:
- Navigation bar with logo and demo request
- Hero section with AI-powered messaging
- Value propositions with animated counters
- Feature highlights with interactive icons
- Pricing tiers with hover effects
- Trust signals and company logos
- Footer with contact information

**Interactive Elements**:
- Animated hero text with Typed.js
- Hover effects on feature cards
- Pricing tier expansion on click
- Demo request modal form
- Smooth scroll animations

### 2. dashboard.html - Main Dashboard
**Purpose**: Central hub for drug repurposing insights
**Key Sections**:
- Top navigation with search and user profile
- Left sidebar with quick actions
- KPI cards row (4 metrics)
- Interactive chart: "Top Cancer Types by Opportunity"
- Data table: "Recent High-Confidence Matches"
- Action buttons for each table row

**Interactive Elements**:
- Real-time search with autocomplete
- Animated KPI counters
- Interactive ECharts visualization
- Sortable/filterable data table
- Save/export functionality

### 3. discovery.html - Drug Discovery Interface
**Purpose**: Main search and discovery tool
**Key Sections**:
- Two-panel layout
- Left panel: Search interface with filters
- Right panel: Results grid with drug cards
- Advanced filters (collapsible)
- Model selector toggle (Fast/Deep analysis)

**Interactive Elements**:
- Dynamic search with real-time results
- Filter combinations with URL state
- Card hover effects with action reveals
- Confidence score animations
- Pagination with smooth transitions

### 4. details.html - Drug Detail Page
**Purpose**: Comprehensive drug analysis and insights
**Key Sections**:
- Hero section with drug info and confidence score
- Tabbed content (Evidence/Business/Clinical/Regulatory)
- Interactive charts and visualizations
- Evidence summary with research papers
- Business intelligence with ROI calculator
- Clinical insights and recommendations

**Interactive Elements**:
- Tab switching with content animation
- Interactive mechanism diagrams
- Expandable evidence sections
- ROI calculator with real-time updates
- Download/export report functionality

### 5. library.html - Research Library
**Purpose**: Scientific literature and research database
**Key Sections**:
- Filter sidebar with multiple categories
- Results grid with paper previews
- Search functionality with highlighting
- Sort and filter controls
- Quick actions for each paper

**Interactive Elements**:
- Multi-filter combination logic
- Search result highlighting
- Paper preview modal
- Citation generator
- Save to project functionality

### 6. analytics.html - Analytics Dashboard
**Purpose**: Portfolio analytics and business intelligence
**Key Sections**:
- Portfolio overview metrics
- Success probability distribution chart
- Market opportunity matrix scatter plot
- Timeline projections Gantt chart
- Export and reporting tools

**Interactive Elements**:
- Interactive chart filtering
- Drill-down capabilities
- Date range selection
- Export functionality
- Real-time data updates

### 7. settings.html - Account Settings
**Purpose**: User and team management
**Key Sections**:
- Account information form
- Team management interface
- API access configuration
- Notification preferences
- Billing and subscription details

**Interactive Elements**:
- Form validation with real-time feedback
- Team member invitation system
- API key generation/management
- Notification toggle switches
- Subscription plan comparison

## Core JavaScript Functionality (main.js)

### Animation Systems
- Page load animations with staggered reveals
- Smooth transitions between sections
- Loading states with skeleton screens
- Success/error notification toasts

### Data Management
- Mock data generation for realistic content
- Search and filtering logic
- Sorting algorithms for tables
- Local storage for user preferences

### Interactive Components
- Modal system for forms and details
- Chart initialization and configuration
- Form validation and submission
- Real-time search functionality

### Navigation System
- Smooth page transitions
- Active state management
- Breadcrumb generation
- URL state synchronization

## Visual Assets Required

### Hero and Background Images
- Professional pharma/lab environment hero image
- Abstract molecular/AI visualization backgrounds
- Subtle texture overlays for depth

### Drug Structure Images
- 20+ common drug molecular structures
- Consistent styling and format
- High resolution for detail views

### Company Logos
- Pharmaceutical company logos for trust signals
- Consistent sizing and treatment
- SVG format for scalability

### User Interface Icons
- Custom icon set for platform features
- Consistent style and weight
- Multiple sizes for different contexts

## Technical Implementation

### Libraries Integration
- **Anime.js**: Page transitions and micro-interactions
- **ECharts.js**: All data visualizations and charts
- **Splitting.js**: Text animation effects
- **Typed.js**: Hero section typewriter effects
- **p5.js**: Background particle systems

### Responsive Design
- Desktop-first approach (1440px+)
- Tablet optimization (768px-1024px)
- Mobile adaptations (320px-768px)
- Touch-friendly interactions

### Performance Optimization
- Lazy loading for images and charts
- Debounced search inputs
- Efficient DOM manipulation
- Minimal external dependencies

This comprehensive outline ensures OncoPurpose delivers a professional, feature-rich platform that meets enterprise pharmaceutical industry standards while providing an innovative, user-friendly experience.