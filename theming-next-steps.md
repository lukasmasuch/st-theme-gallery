# Streamlit Theming: Recommended Next Steps

Based on creating 40+ themes for Streamlit, here are recommendations for new theming options that would have the biggest impact on enabling better, more customizable themes.

---

## High Impact Additions

### 1. Dataframe Header Text Color ⭐

**Problem**: Currently there's no way to control the text color in dataframe/table headers independently. This causes contrast issues when using custom background colors.

```toml
dataframeHeaderTextColor = "#1a1a1a"
```

**Why it matters**: Dark sidebar themes with light main areas (or vice versa) often have unreadable dataframe headers because the text color is inherited unpredictably.

---

### 2. Button Styling

**Problem**: Button text color is auto-calculated from `primaryColor`, and there's no control over hover states.

```toml
buttonTextColor = "#ffffff"
buttonHoverBackgroundColor = "#0056b3"
buttonHoverTextColor = "#ffffff"
```

**Why it matters**: Many brand themes require specific button text colors (e.g., dark text on light buttons). Auto-calculation often produces incorrect results for pastel or mid-tone primary colors.

---

### 3. Letter Spacing & Line Height

**Problem**: No control over text spacing, which dramatically affects brand feel.

```toml
letterSpacing = "-0.01em"
lineHeight = 1.6
headingLetterSpacing = "-0.02em"
headingLineHeight = 1.2
```

**Why it matters**:
- Tight letter spacing = modern, tech-forward (Linear, Vercel)
- Loose letter spacing = elegant, luxury (Blackstone, fashion brands)
- Line height affects readability and density

---

### 4. Shadow/Elevation System

**Problem**: No way to add depth and visual hierarchy through shadows.

```toml
shadowColor = "rgba(0,0,0,0.1)"
cardShadow = "0 2px 8px"
# Or a simpler approach:
elevationLevel = "medium"  # none, low, medium, high
```

**Why it matters**: Shadows define visual hierarchy in modern design systems. Material UI, Apple, and many contemporary designs rely heavily on elevation to create depth and focus.

---

### 5. Semantic/Status Colors

**Problem**: Success, warning, error, and info states seem tied to the base color palette rather than being explicitly configurable.

```toml
successColor = "#10b981"
warningColor = "#f59e0b"
errorColor = "#ef4444"
infoColor = "#3b82f6"
```

**Why it matters**: Dashboard and data applications need consistent status indicators. Currently, these colors may clash with brand palettes or be difficult to distinguish.

---

### 6. Focus Ring Styling

**Problem**: Limited control over focus states for accessibility.

```toml
focusRingColor = "#0066cc"
focusRingWidth = "2px"
focusRingOffset = "2px"
focusRingStyle = "solid"  # solid, dashed, dotted
```

**Why it matters**: Critical for accessibility compliance (WCAG). Focus rings should match brand colors while remaining visible. Currently appears to use `primaryColor` which may not always provide sufficient contrast.

---

### 7. Input Field Styling

**Problem**: Form inputs share colors with other elements, limiting customization.

```toml
inputBackgroundColor = "#ffffff"
inputTextColor = "#1a1a1a"
inputPlaceholderColor = "#9ca3af"
inputBorderColor = "#d1d5db"
inputFocusBorderColor = "#0066cc"
```

**Why it matters**: Many designs call for inputs that are visually distinct from the background (e.g., white inputs on gray backgrounds, or bordered inputs in borderless themes).

---

### 8. Text Transform for Headings

**Problem**: No way to apply text transforms like uppercase without custom CSS.

```toml
headingTextTransform = "uppercase"  # uppercase, capitalize, lowercase, none
```

**Why it matters**: Many corporate brands (IBM, Blackstone, NTT) use uppercase headings as part of their identity. Currently requires injecting custom CSS.

---

## Medium Impact Additions

### Dataframe Enhancements
```toml
dataframeAlternateRowColor = "#f9fafb"  # Zebra striping
dataframeCellPadding = "8px 12px"
dataframeHeaderFontWeight = 600
```

### Tab Styling
```toml
tabActiveBackgroundColor = "#ffffff"
tabActiveTextColor = "#1a1a1a"
tabInactiveTextColor = "#6b7280"
tabIndicatorColor = "#0066cc"
tabIndicatorStyle = "underline"  # underline, background, pill
```

### Divider Styling
```toml
dividerColor = "#e5e7eb"
dividerThickness = "1px"
dividerStyle = "solid"
```

### Caption/Small Text
```toml
captionColor = "#6b7280"
captionFontSize = "0.875rem"
smallTextColor = "#9ca3af"
```

### Hover States
```toml
linkHoverColor = "#0056b3"
linkHoverUnderline = true
hoverBackgroundColor = "rgba(0,0,0,0.05)"
```

---

## Lower Priority (Nice to Have)

### Animation Controls
```toml
transitionDuration = "150ms"
transitionEasing = "ease-in-out"
enableAnimations = true
```

### Advanced Border Controls
```toml
borderWidth = "1px"
borderStyle = "solid"  # solid, dashed, dotted
```

### Scrollbar Styling
```toml
scrollbarTrackColor = "#f1f1f1"
scrollbarThumbColor = "#c1c1c1"
scrollbarThumbHoverColor = "#a1a1a1"
scrollbarWidth = "thin"  # thin, auto, none
```

---

## Summary: Top 3 Priorities

If only three additions could be made, these would unlock the most design possibilities:

| Priority | Feature | Impact |
|----------|---------|--------|
| 1 | `dataframeHeaderTextColor` | Solves immediate, common pain point |
| 2 | Button styling (`buttonTextColor`, hover states) | Essential for brand accuracy |
| 3 | Shadow/elevation system | Defines visual hierarchy, enables modern designs |

---

## Notes from Theme Development

### What Works Well
- Google Fonts integration via URL syntax is excellent
- Separate sidebar theming is powerful
- Color palette system (red, blue, green, etc.) is flexible
- Border radius controls are comprehensive

### Common Pain Points Encountered
1. Dataframe headers inheriting wrong text colors in mixed light/dark themes
2. Buttons with mid-tone primary colors having poor text contrast
3. No way to create "elevated" card designs without custom CSS
4. Uppercase headings require CSS injection
5. Focus states don't always match brand colors

### Themes Created for Reference
This analysis is based on creating themes for: Apple, Airbnb, Anthropic, AWS, Blackstone, Discord, Dracula, Dribbble, Figma, GitHub, Google, IBM, Linear, Microsoft, Netflix, Nord, Notion, NTT Data, NVIDIA, OpenAI, Shopify, Slack, Solarized (light/dark), Spotify, Stripe, Supabase, Tableau, Tailwind, Twitter, Vercel, Power BI, VS Code, One Dark Pro, Material UI, Snowflake, Hotdog, Modern Minimal, Hacker, Romantic, Dashboard Pro, Monochrome, Claude No. 1, and Futuristic.
