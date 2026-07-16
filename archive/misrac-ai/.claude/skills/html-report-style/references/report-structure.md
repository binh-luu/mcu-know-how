# Report Structure Reference

This document describes the HTML structure used by `html-report-style` reports. All generated reports follow this layout pattern.

## Overall Document Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Report Title</title>
  <style>/* CSS */</style>
</head>
<body>
  <!-- Sidebar -->
  <nav id="sidebar">...</nav>
  <!-- Main Content -->
  <main id="main">
    <!-- Section blocks -->
    <div id="section-<key>" class="section [active]">...</div>
  </main>
  <script>function show(id) {...}</script>
</body>
</html>
```

## Sidebar Anatomy

| Element | Class/ID | Purpose | Customizable |
|---------|----------|---------|--------------|
| Header container | `#sidebar-header` | Project title block | Content only |
| Project name | `.project` | Short uppercase prefix | Yes |
| Report title | `.title` | Main heading | Yes |
| Meta info | `.meta` | Date, version, tech stack | Yes |
| Nav sections | `.nav-section` | Section headers | Add/remove |
| Nav items | `.nav-item` | Clickable navigation | Add/remove |
| Footer | `#sidebar-footer` | Authors, contacts | Yes |

### Sidebar Navigation Convention

Each nav item must link to a section:

```html
<div class="nav-item" onclick="show('deployment')">
  <span class="icon">🚀</span> 2 · Deployment
</div>
```

The `onclick` value (`deployment`) must match the section ID suffix:

```html
<div id="section-deployment" class="section">...</div>
```

## Main Content Sections

### Section Block

```html
<div id="section-<key>" class="section [active]">
  <div class="section-title">🎯 Title</div>
  <div class="section-subtitle">Subtitle</div>
  <!-- content -->
</div>
```

- **First section** should have `class="section active"` to render by default
- Use emojis in titles for visual scanning

## Content Components

### Alert Boxes

| Class | Color | Use Case |
|-------|-------|----------|
| `alert-blue` | Light blue | Informational |
| `alert-green` | Light green | Success / positive |
| `alert-orange` | Light orange | Warning / caution |
| `alert-yellow` | Light yellow | Attention |
| `alert-red` | Light red | Critical / error |

```html
<div class="alert alert-blue">
  <div class="alert-icon">ℹ️</div>
  <div class="alert-body">
    <div class="alert-title">Title</div>
    <div class="alert-desc">Description text.</div>
  </div>
</div>
```

### Cards

```html
<div class="card">
  <div class="card-title">Title</div>
  <p>Body text.</p>
</div>
```

Use in grids:
- `.grid-2` — two equal columns
- `.grid-3` — three equal columns

### Metric Boxes

```html
<div class="metric-box">
  <div class="value">42</div>
  <div class="label">Metric Name</div>
  <div class="sub">Sub-label</div>
</div>
```

### Code Blocks

```html
<div class="code-block"><pre><span class="file-label">file.c</span>
<span class="ln">1</span><span class="comment">// comment</span>
<span class="ln">2</span><span class="keyword">int</span> <span class="fn">main</span>() {
<span class="ln">3</span>    <span class="number">42</span>;</pre></div>
```

Syntax classes: `keyword`, `string`, `number`, `fn`, `type`, `comment`, `ln` (line numbers).

### Tables

```html
<table>
  <tr><th>Header A</th><th>Header B</th></tr>
  <tr><td>Cell A</td><td>Cell B</td></tr>
</table>
```

### Flow Diagrams

Horizontal pipeline of boxes:

```html
<div class="flow">
  <div class="flow-box" style="border-color:var(--accent)">
    <div class="fb-t">Step title</div>
    <div class="fb-s">detail</div>
  </div>
  <div class="flow-arrow">→</div>
  <!-- repeat boxes -->
</div>
```

### Progress Bars

```html
<div class="progress-row">
  <div class="progress-label"><span>Metric</span><span>87%</span></div>
  <div class="progress-bar">
    <div class="progress-fill" style="width:87%;background:var(--green)"></div>
  </div>
</div>
```

### Compare Boxes

```html
<div class="compare">
  <div class="compare-box compare-bad">
    <div class="compare-label">Before</div>
    <p>Old state.</p>
  </div>
  <div class="compare-box compare-good">
    <div class="compare-label">After</div>
    <p>New state.</p>
  </div>
</div>
```

## JavaScript Navigation

The `show(id)` function toggles section visibility:

```javascript
function show(id) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const el = document.getElementById('section-' + id);
  if (el) el.classList.add('active');
  const nav = document.querySelector(`[onclick="show('${id}')"]`);
  if (nav) nav.classList.add('active');
  window.scrollTo(0, 0);
}
```

Do not modify unless you understand the section ↔ nav pairing.