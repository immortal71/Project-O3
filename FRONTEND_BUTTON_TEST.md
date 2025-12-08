# Frontend Button & Interaction Test Checklist

## Test Date: December 1, 2025

---

## 1. **index (1).html** - Landing Page

### Navigation
- [ ] "Request Demo" button (nav) - Opens demo modal
- [ ] All nav links work (Home, Features, Pricing, etc.)

### Hero Section
- [ ] "Get Started Free" button - Opens demo modal
- [ ] "Watch Demo" button - Currently shows alert, needs implementation

### Recent Discoveries Cards
- [ ] "View" buttons on discovery cards (4 total) - No current action
- [ ] "Explore" buttons on pipeline cards (4 total) - No current action

### Pricing Section  
- [ ] "Start Free Trial" button (Starter plan) - No action
- [ ] "Get Started" button (Professional plan - Popular) - No action
- [ ] "Contact Sales" button (Enterprise plan) - No action

### Demo Modal
- [ ] Modal open/close functionality - ✓ Working
- [ ] Form submit button - Shows success alert
- [ ] Close button (X) - ✓ Working
- [ ] Click outside modal to close - ✓ Working

**Backend Needs:**
- Connect demo form to email service or CRM
- Implement "Watch Demo" video player
- Link discovery/pipeline cards to actual data

---

## 2. **dashboard (1).html** - Main Dashboard

### Navigation
- [ ] Theme toggle (🌙/☀️) - ✓ Working with localStorage
- [ ] Color scheme selector (🎨) - ✓ Working (4 schemes)
- [ ] All nav links (Home, Dashboard, Discovery, Research, Analytics)
- [ ] User profile dropdown/menu - Not implemented

### Overview Section
- [ ] "Apply Filters" button - No action defined
- [ ] "Export Report" button - No action defined
- [ ] KPI cards interactive? - Display only

### Tables
- [ ] "View Details" buttons in tables - No navigation
- [ ] Sort functionality on table headers - Not implemented
- [ ] Pagination controls - Not visible/implemented

**Backend Needs:**
- Connect "Apply Filters" to filter API
- Implement "Export Report" (PDF/CSV generation)
- Connect "View Details" to details page with drug ID
- Implement table sorting and pagination

---

## 3. **discovery.html** - Drug Discovery

### Navigation
- [ ] Theme toggle (🌙/☀️) - ✓ Working
- [ ] Color scheme selector (🎨) - ✓ Working
- [ ] Search bar functionality - Not connected
- [ ] Nav links work - ✓ Links present

### Search Panel (Sidebar)
- [ ] Analysis Mode toggle (Fast/Deep) - UI works, no backend
- [ ] Cancer Type dropdown - Display only
- [ ] Drug Name input - Display only
- [ ] Molecular Target input - Display only
- [ ] Current Indication input - Display only
- [ ] "+ Advanced Filters" toggle - ✓ Shows/hides filters
- [ ] Confidence threshold slider - ✓ UI works
- [ ] Patent status checkboxes - Display only
- [ ] Clinical trial phase dropdown - Display only
- [ ] Market size dropdown - Display only
- [ ] "🔬 Analyze Opportunities" button - **No action defined**

### Quick Filters
- [ ] Filter tag buttons (4 total) - ✓ Opacity toggle works

### Results Section
- [ ] Sort dropdown - Display only
- [ ] Grid/List view toggles - No action
- [ ] "Load More Results" button - No action

**Backend Needs:**
- Connect analyze button to `/api/discovery/analyze` endpoint
- Implement search/filter logic
- Generate results grid dynamically
- Implement view mode switching
- Pagination for results

---

## 4. **library.html** - Research Library

### Navigation
- [ ] Search bar - Has event listener, no backend
- [ ] Nav links - ✓ Present

### Filters
- [ ] Category checkboxes - ✓ Event listeners attached
- [ ] "View Full Paper" buttons - Has click handlers, no navigation

**Backend Needs:**
- Connect search to paper database
- Implement category filtering
- Link to actual paper PDFs or details page

---

## 5. **analytics (1).html** - Analytics Dashboard

### Charts
- [ ] Charts render - ✓ Using ECharts
- [ ] Charts resize on window resize - ✓ Event listener present
- [ ] Interactive tooltips - ✓ Built into ECharts

### Filters/Controls
- [ ] Date range selector - Not visible in code
- [ ] Export options - Not visible

**Backend Needs:**
- Connect charts to live data API
- Implement data refresh mechanism
- Add export functionality

---

## 6. **settings (1).html** - Settings Page

### Settings Categories
- [ ] Tab navigation - ✓ Event listeners present
- [ ] "Save Changes" buttons (4 sections) - Shows alert, no backend
- [ ] "Generate New Key" button - Shows alert, no backend
- [ ] "View Activity" button - Shows alert, no backend

**Backend Needs:**
- Implement settings save to database
- API key generation and management
- Activity log retrieval

---

## 7. **details.html** - Drug Details

### Tab Navigation
- [ ] Tab switching - ✓ Event listeners present
- [ ] Content display - ✓ Working

### Interactions
- [ ] No buttons requiring backend found
- [ ] Display-only page

---

## PRIORITY BACKEND ENDPOINTS NEEDED

### High Priority
1. **POST /api/discovery/analyze** - Main discovery analysis
   - Input: Cancer type, drug name, filters, analysis mode
   - Output: List of repurposing opportunities with confidence scores

2. **GET /api/drugs/{id}/details** - Drug detail information
   - Output: Full drug profile for details page

3. **POST /api/demo/request** - Demo request form
   - Input: Name, email, organization, message
   - Output: Success confirmation, send email

4. **GET /api/dashboard/overview** - Dashboard KPI data
   - Output: Active analyses, drugs screened, success rate, etc.

5. **POST /api/reports/export** - Export dashboard report
   - Input: Filters, date range
   - Output: PDF or CSV file

### Medium Priority
6. **GET /api/library/papers** - Research papers
   - Input: Search query, category filters
   - Output: List of papers with metadata

7. **GET /api/analytics/charts** - Chart data
   - Input: Date range, metric type
   - Output: Time series data for charts

8. **POST /api/settings/save** - Save user settings
   - Input: Settings object by category
   - Output: Success confirmation

9. **POST /api/settings/api-key** - Generate API key
   - Output: New API key

### Low Priority
10. **GET /api/discovery/results/{id}** - Cached analysis results
11. **POST /api/filters/save** - Save filter presets
12. **GET /api/activity/log** - User activity log

---

## NEXT STEPS

1. ✅ **Test all UI interactions** (buttons, toggles, forms)
2. ⏳ **Document missing backend connections**
3. **Start implementing backend endpoints** ← WE ARE HERE
4. **Connect frontend buttons to backend APIs**
5. **Add loading states and error handling**
6. **Implement data validation**

---

## NOTES
- Theme switching works across all pages ✓
- Color schemes persist in localStorage ✓
- Most forms are visual only - no POST handlers
- No loading spinners or error messages implemented
- No authentication/authorization system visible
