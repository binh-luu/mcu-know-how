# Style Rules Reference

This document lists every CSS class and design token in the `html-report-style` report template. Colors, spacing, and typography are defined via CSS variables in `:root`.

## Color Tokens (CSS Variables)

```css
:root {
  --sidebar-w: 260px;       /* sidebar width */
  --accent: #1a6fd4;         /* primary blue */
  --accent-light: #e8f0fb;   /* light accent bg */
  --red: #d93025;
  --orange: #ea8600;
  --yellow: #f9ab00;
  --green: #1e8e3e;
  --bg: #f8f9fa;             /* page bg */
  --surface: #ffffff;        /* cards, sidebar footer */
  --border: #dadce0;
  --text: #202124;
  --text-muted: #5f6368;
  --code-bg: #1e1e2e;
  --code-text: #cdd6f4;
  --tag-red: #fce8e6;
  --tag-orange: #fef3e2;
  --tag-green: #e6f4ea;
  --tag-yellow: #fef9e0;
}
```

All semantic colors derive from these tokens. Do not hardcode other colors unless extending.

## Semantic Badges & Chips

| Class | Purpose | Recommended Use |
|-------|---------|-----------------|
| `.badge-red` | Red badge | Errors, blockers |
| `.badge-orange` | Orange badge | Warnings, required |
| `.badge-yellow` | Yellow badge | Advisory, caution |
| `.badge-blue` | Blue badge | Information, optional |
| `.badge-green` | Green badge | Success, passed |
| `.conf-high` | High confidence | Verified claims |
| `.conf-medium` | Medium confidence | Needs review |
| `.conf-low` | Low confidence | Uncertain |
| `.conf-advisory` | Advisory only | Suggestions |

## Component Classes

| Class | Element | Description |
|-------|---------|-------------|
| `.section` | any | Hidden by default (`.active` shows) |
| `.section.active` | any | Visible section |
| `.section-title` | heading | Large section heading |
| `.section-subtitle` | text | Subtle description under title |
| `.alert` | container | Alert box wrapper |
| `.alert-icon` | span | Leading emoji/icon |
| `.alert-body` | div | Alert text container |
| `.alert-title` | div | Alert heading |
| `.alert-desc` | div | Alert body text |
| `.card` | div | White panel with border |
| `.card-title` | div | Card heading |
| `.code-block` | pre | Code panel styling |
| `.code-block .file-label` | span | Filename badge in code block |
| `.chip` | span | Small tag/badge |
| `.metric-box` | div | Big number + label box |
| `.progress-bar` | div | Thin bar container |
| `.progress-fill` | div | Colored fill (set width inline) |
| `.timeline` | div | Vertical timeline container |
| `.tl-item` | div | Single timeline entry |
| `.tl-dot` | div | Circle marker on timeline |
| `.tl-dot-[red|orange|yellow|green|blue]` | div | Colored marker |
| `.compare` | div | Before/after comparison |
| `.compare-bad` / `.compare-good` | div | Comparison sides |
| `.flow` | div | Horizontal step pipeline |
| `.flow-box` | div | Single step box |
| `.flow-arrow` | div | Arrow between steps |

## Flow Diagram Classes (Colored Blocks)

Six colored block classes for step flows (example: `b0` through `b6`):

```css
.b0 { background:linear-gradient(135deg,#1a6fd4,#155bb0) } /* Step 1 */
.b1 { background:linear-gradient(135deg,#0e9488,#0b7a70) } /* Step 2 */
.b2 { background:linear-gradient(135deg,#5b4bd4,#4636b8) } /* Step 3 */
/* ... etc */
```

## Typography

| Class | Font | Size | Weight |
|-------|------|------|--------|
| body | Segoe UI | 14px | normal |
| `.section-title` | Segoe UI | 22px | 700 |
| `.section-subtitle` | Segoe UI | 13px | muted |
| `.card-title` | Segoe UI | 15px | 700 |
| `.alert-title` | Segoe UI | 13px | 700 |
| `.alert-desc` | Segoe UI | 13px | normal |

Code uses Cascadia Code, Fira Code, Consolas fallback, size 12.5px, line-height 1.7.

## Spacing

- Section padding: `32px 36px 60px`
- Card padding: `20px 24px`
- Grid gaps: `16px`
- Flow gaps: `6px`
- Border radius: `8-12px` depending on component

## Responsive Breakpoints

```css
@media (max-width:820px) {
  .blk-flow { grid-template-columns: repeat(2, 1fr) }
  .precond  { grid-template-columns: repeat(2, 1fr) }
  .loop-grid{ grid-template-columns: 1fr }
}
```

## Animations

| Class | Animation | Use |
|-------|-----------|-----|
| `.swe-hl` | Glow pulse | Highlight important element |
| `.animated-dash` | Dash move | SVG paths |
| `.section.active .card, .section.active .alert, .section.active .svg-wrap` | Float in | Section entrance |

## Extending the Stylesheet

To add custom colors, extend `:root` at the bottom of `reference-style.css`:

```css
:root {
  --myproject-accent: #008080;
  --myproject-warn: #ff6600;
}
```

Then reference in your HTML:
```html
<style>
.my-badge { background: var(--myproject-accent); color: white; }
</style>
```