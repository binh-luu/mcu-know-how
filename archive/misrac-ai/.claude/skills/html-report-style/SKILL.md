---
name: html-report-style
description: Generate HTML reports with identical styling to MISRA_C_AI_Assistant.html for software deployment reports, technical documentation, and proposals.
---

# Skill: html-report-style

Generate standalone HTML reports with the exact structure and styling of `MISRA_C_AI_Assistant.html` for software deployment reports, technical documentation, and project proposals.

## What this skill does

Creates reports that match the visual design, component patterns, and coding practices used in `MISRA_C_AI_Assistant.html`. All reports are fully self-contained and optimized for distribution:

- **Identical appearance** to existing documentation
- **Consistent visual language** across all project reports
- **Zero external dependencies** when opened directly in browsers
- **Standardized layout patterns** for maintainability
- **Cross-container suitable** (browser, email, print)

## When to use this skill

Use this skill when you need to generate:

- Software deployment reports with architecture diagrams and status overviews
- Technical documentation with code examples and validation results
- Project proposals with timeline graphics and resource summaries
- Any standalone report that should match the visual design of existing documentation

Many users standardize on this visual template for consistency across multiple deliverables.

## Getting Started

Copy the reference report template and customize it with your content:

```
## Commands

# Generate a new report with defaults
/path/to/skill/commands report

# Show usage help
/path/to/skill commands report --help
```

### 1. Quick Report Generation

Generate a new report using predefined templates:

```bash
# Create a software deployment report
/path/to/skill commands report deployment --title "Q3 Deployment" --subtitle "Q3 release procedures" --output deployment-report.html

# Create a technical documentation report
/path/to/skill commands report techdoc --title "Architecture Overview" --subtitle "System design and components" --output techdoc.html

# Create a project proposal
/path/to/skill commands report proposal --title "MISRA Modernization" --subtitle "Proposal for MISRA-C:2012 automation" --output proposal.html
```

### 2. Template Customization

The skill includes reference documentation for:

- **`references/report-structure.md`** – HTML layout patterns and navigation
- **`references/content-mapping.md`** – placeholder tokens and customization
- **`references/style-rules.md`** – CSS classes and design tokens

## Template Files

### Assets

| File | Purpose |
|------|---------|
| `assets/reference-report.html` | Self-contained HTML template with embedded CSS |
| `assets/reference-style.css` | CSS extracted from original MISRA report |

### Scripts

| File | Purpose |
|------|---------|
| `scripts/extract_report_style.py` | Extract CSS from HTML files |

### References

| File | Purpose |
|------|---------|
| `references/report-structure.md` | HTML layout patterns |
| `references/content-mapping.md` | Placeholder tokens and customization |
| `references/style-rules.md` | CSS classes and design tokens |

## Report Templates

The skill provides three project-specific report templates:

### 1. Deployment Reports

Structure optimized for:

- **Overview section** – Summary, metrics, key insights
- **Deployment section** – Pipeline steps, prerequisites, verification commands
- **Architecture section** – System diagrams, component structure
- **Results section** – Deployment metrics, validation status
- **Appendix section** – Changelog, links, environment details

**Placeholder tokens for deployment:**

| Token | Example content |
|-------|-----------------|
| `<<DEPLOYMENT SUBTITLE>>` | "Step-by-step deployment procedure" |
| `<<PIPELINE TITLE>>` | "Deployment Pipeline" |
| `<<SETUP STEPS TITLE>>` | "Environment Setup" |
| `<<Step 1>>` | "Build", "Test", "Deploy", "Verify" |

### 2. Technical Documentation

Structure optimized for:

- **Overview** – Problem statement, scope, objectives
- **System** – Architecture diagrams, API definitions, data models
- **Implementation** – Code examples, configuration, gotchas
- **Validation** – Test results, performance metrics, verification logs
- **Appendix** – API docs, external references, version history

### 3. Proposal Reports

Structure optimized for:

- **Problem** – Issue statement, opportunity identification
- **Solution** – Proposed approach, benefits, distinguishing features
- **Timeline** – Delivery phases, milestones, completion dates
- **Resources** – Budget, staffing, tool requirements
- **Appendix** – Supporting data, reference materials, contacts

## Customization Methods

### Method 1: Static HTML Generation

Generate complete HTML reports with existing content:

```bash
python scripts/generate_static_report.py \
  --template deployment \
  --title "Q3 Deployment Report" \
  --output q3-deployment.html \
  --vars "{\"VERSION\": \"2.1.0\", \"DEPLOYMENT_DATE\": \"2026-07-15\"}"
```

### Method 2: Template Modification

Edit the generated HTML files and:

1. Replace all `<<PLACEHOLDER>>` tokens with real content
2. Add/remove `.section` blocks in both the main content and sidebar navigation
3. Update sidebar `.nav-item` elements to match new sections
4. Maintain the `onclick="show('...')"` convention for all sections

**Navigation consistency:** Every `.nav-item` must have a matching `.section` with the same suffix:

```html
<!-- Sidebar -->
<div class="nav-item" onclick="show('new-section')">
  <span class="icon">✨</span> 1 · New Section
</div>

<!-- Main content -->
<div id="section-new-section" class="section">...</div>
```

### Method 3: Dynamic Content Injection

Run the replacement scripts to populate placeholder tokens:

```bash
#!/bin/bash
# replace_placeholders.sh
input="assets/reference-report.html"
output="custom-report.html"

# Replace deployment-specific placeholders
export REPORT_TITLE="Q3 2026 Deployment"
export PROJECT_CATEGORY="SOFTWARE"
export CONTEXT_META="v2.1 · Linux · Python 3.10"
sed -e "s|<<REPORT TITLE>>|$REPORT_TITLE|g" \
    -e "s|<<PROJECT / REPORT CATEGORY>>|$PROJECT_CATEGORY|g" \
    -e "s|<<CONTEXT META>>|$CONTEXT_META|g" \
    "$input" > "$output"
```

## Visual Customization

### Color Customization

Extend the color system by modifying CSS variables in the `<style>` block:

```css
<style>
:root {
  --accent: #your-primary-color;       /* primary brand color */
  --accent-light: #your-light-color;   /* light variant */
  --red: #your-danger-color;
  --green: #your-success-color;
  --orange: #your-warning-color;
  --yellow: #your-attention-color;
  /* ... keep other tokens for consistency */
}
</style>
```

### Component Extensions

Add custom layout elements by:

1. Creating new sections with unique keys (e.g., `new-section`)
2. Adding corresponding navigation items in the sidebar
3. Maintaining the `.section` and `.nav-item` pairing
4. Applying appropriate style classes from `style-rules.md`

## File Structure Overview

```
html-report-style/
├── SKILL.md                    # Instructions for using the skill
├── assets/                     # Report templates and styles
│   ├── reference-report.html   # Complete HTML template
│   ├── reference-style.css     # CSS extracted from original report
│   └── reference-screenshot.png # Optional visual example
├── references/                 # Documentation for customization
│   ├── report-structure.md     # Layout patterns
│   ├── content-mapping.md     # Placeholder tokens
│   └── style-rules.md         # CSS classes and design tokens
└── scripts/                    # Utility scripts
    └── extract_report_style.py # Extract CSS from HTML files
```

## Best Practices

### Maintain Consistency

- Reuse component snippets throughout your reports
- Follow the `<<PLACEHOLDER>>` pattern for dynamic content
- Maintain the one-to-one mapping between sidebar navigation and content sections

### Optimize for Distribution

- All reports are standalone with embedded styles
- Compatible with browsers, email clients, and print
- No external resource dependencies

### Keep Documentation Updated

- Reference the latest version of style documentation
- Update examples when components change
- Maintain component patterns for maintainability

## Troubleshooting

### Issues

**Issue:** Placeholder tokens not replaced
**Solution:** Use the replacement scripts or sed/awk commands to replace `<<PLACEHOLDER>>` tokens

**Issue:** Sidebar navigation doesn't match sections
**Solution:** Ensure every `onclick="show('...')"` has a matching `id="section-..."`

**Issue:** Colors don't match brand guidelines
**Solution:** Update CSS variables (`--accent`, `--red`, etc.) to brand colors

**Issue:** Reports don't render in email clients
**Solution:** Use inline styles and the built-in CSS module for maximum compatibility

## Extending the Skill

### Add New Templates

Add new template types by:

1. Creating a new entry in the skill instructions
2. Adding corresponding placeholder tokens
3. Testing the new structure with the reference report

### Contribution

This skill is designed to be extensible:

- Add new report templates or component examples
- Update style documentation with new patterns
- Improve scripts for better placeholder replacement
- Share customizations for common report types

## Related Skills

- `github-issue-analyzer` – Generate reports from GitHub issues
- `deployment-workflow` – Create deployment pipeline documentation
- `architecture-diagrams` – Add system architecture visualizations
- `code-quality-reporter` – Generate code quality assessment reports

## Credits

Based on the visual design and component patterns from `MISRA_C_AI_Assistant.html`.

The template is designed to match that report's structure while being adaptable to various project report types.