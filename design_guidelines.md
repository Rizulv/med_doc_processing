# Design Guidelines: Medical Doc AI

## Design Approach

**Selected Approach:** Design System - Material Design 3  
**Justification:** Medical document processing requires clarity, efficiency, and trust. Material Design provides the structured foundation needed for information-dense healthcare applications while maintaining professional aesthetics.

**Reference Inspiration:** Linear (for clean data presentation) + Healthcare SaaS dashboards (for clinical credibility)

**Core Principles:**
1. **Clinical Clarity** - Medical data must be immediately scannable
2. **Evidence-Based Design** - Every visual element supports decision-making
3. **Confidence Through Structure** - Consistent patterns build professional trust
4. **Efficiency First** - Minimize clicks, maximize information density

---

## Typography System

### Font Families
- **Primary (UI/Body):** Inter or Roboto - 400, 500, 600 weights
- **Data/Code Display:** JetBrains Mono - 400, 500 weights for ICD-10 codes, confidence scores

### Hierarchy
- **Page Titles:** 32px/2rem, weight 600, tight letter-spacing
- **Section Headers:** 24px/1.5rem, weight 600
- **Card Titles:** 18px/1.125rem, weight 500
- **Body Text:** 16px/1rem, weight 400
- **Labels/Metadata:** 14px/0.875rem, weight 500
- **Code/Data Values:** 14px/0.875rem, monospace, weight 500
- **Micro-labels:** 12px/0.75rem, weight 400, uppercase with letter-spacing

---

## Layout System

### Spacing Scale (Tailwind)
**Primary Units:** 2, 4, 6, 8, 12, 16, 24  
Use consistently across margins, padding, and gaps.

### Grid Structure
- **Container:** max-w-7xl (1280px) for main content
- **Narrow Content:** max-w-4xl for document text display
- **Card Grids:** grid-cols-1 md:grid-cols-2 lg:grid-cols-3

### Page Layouts

**Upload Page:**
- Centered single-column layout (max-w-2xl)
- Large dropzone with clear visual feedback
- Results panel full-width below upload (max-w-4xl)

**Documents List:**
- Full-width table or card grid
- Left sidebar for filters (future: date range, document type)
- Sticky header with search and upload button

**Document Detail:**
- Two-column split on desktop (lg:grid-cols-3)
  - Main column (col-span-2): Full document text in readable container
  - Sidebar (col-span-1): Sticky classification results, codes, metadata
- Single column stack on mobile

---

## Component Library

### Upload Interface

**Dropzone Card:**
- Elevated card (shadow-lg) with dashed border (border-2 border-dashed)
- Height: min-h-[320px] for generous drop target
- Center-aligned icon (document icon, 64px) and text
- Hover state: subtle scale transform and border emphasis
- Active drag state: distinct visual treatment

**File Preview:**
- Compact file info card: filename, size, type icon
- Clear remove/replace action

**Upload Button:**
- Large contained button (px-8 py-3)
- Loading spinner replaces text during processing
- Disabled state during upload

### Results Display

**Classification Panel:**
- Prominent card with document type badge
- Confidence meter: horizontal progress bar with percentage label
- Rationale text with subtle background differentiation
- Evidence quotes in italic with quotation marks

**ICD-10 Codes Section:**
- Each code as a distinct card or list item
- Code displayed in monospace (bold, larger)
- Description as primary text
- Confidence score with visual indicator (chip or mini-progress)
- Evidence expandable/collapsible

**Summary Card:**
- Clinical summary in readable paragraph format (max-w-prose)
- Evidence citations as footnotes or inline highlights
- Provider context indicator

### Data Tables

**Documents List:**
- Dense table with alternating row backgrounds
- Columns: Filename, Type, Upload Date, Status, Actions
- Sortable headers
- Row hover state for interactivity
- Quick action icons (view, download) aligned right

### Navigation

**App Bar:**
- Fixed top position with subtle elevation
- Logo/app name left-aligned
- Primary actions right-aligned (Upload Document button)
- Minimal height (64px) to maximize content space

**Breadcrumbs:**
- Show on detail pages: Documents > [Filename]
- Small, subtle, positioned below app bar

### Status Indicators

**Confidence Badges:**
- High (≥0.8): Distinct treatment
- Medium (0.5-0.79): Warning state treatment  
- Low (<0.5): Alert state treatment
- Displayed as chips or mini-progress bars

**Document Type Tags:**
- Pill-shaped badges for the 5 types
- Each type has consistent visual treatment
- Used in lists and detail headers

### Interactive Elements

**Buttons:**
- Primary: Contained style for main actions (Upload, Run Pipeline)
- Secondary: Outlined style for alternative actions
- Text: For tertiary actions (Cancel, Clear)
- Size: Medium (px-6 py-2.5) for most, Large for primary CTAs

**Links:**
- Document names as primary clickable elements
- Underline on hover for clarity
- Visited state differentiation

### Cards & Containers

**Standard Card:**
- Rounded corners (rounded-lg)
- Subtle shadow (shadow-md)
- Padding: p-6
- Hover elevation increase for clickable cards

**Data Cards (for codes, results):**
- Compact padding (p-4)
- Clear header/body separation with borders or background
- Grouped in grids with gap-4

### Loading States

**Skeleton Screens:**
- Use for initial page loads
- Match final content structure
- Subtle pulse animation

**Inline Spinners:**
- For button actions
- Size matches button text height

---

## Medical-Specific Patterns

### Evidence Display
- Quoted text in italic with subtle left border
- Source line references if available
- Expandable for long quotes

### Confidence Visualization
- Always pair numerical score with visual indicator
- Use consistent scale across all features (0.0-1.0)
- Label clearly: "Confidence: 0.85"

### Clinical Data Hierarchy
- Critical findings elevated visually
- ICD-10 codes given prominence with monospace treatment
- Summary presented as the "what this means" conclusion

### Error & Edge Cases
- Empty states with clear next actions ("Upload your first document")
- Low-confidence warnings displayed prominently
- Error messages in clinical language (not technical jargon)

---

## Responsive Behavior

**Breakpoints:**
- Mobile: < 768px (single column, stacked)
- Tablet: 768px-1024px (2-column where appropriate)
- Desktop: ≥1024px (full multi-column layouts)

**Mobile Priorities:**
- Upload interface remains prominent and easy to use
- Results stack vertically with summary first
- Tables convert to cards on mobile
- Sticky headers for context retention

---

## Animations

**Use Sparingly:**
- Card hover elevations (subtle)
- Button state transitions
- Dropzone drag feedback
- Loading spinners only

**Avoid:**
- Page transitions
- Decorative animations
- Auto-scrolling or attention-grabbing effects

---

## Accessibility

- Maintain 4.5:1 contrast ratios for all text
- Focus indicators on all interactive elements
- Keyboard navigation for complete workflows
- ARIA labels for medical terminology
- Screen reader announcements for confidence scores and classifications