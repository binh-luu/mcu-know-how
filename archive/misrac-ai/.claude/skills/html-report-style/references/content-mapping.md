# Content Mapping & Customization

This guide explains how to customize the `html-report-style` template for different project types.

## Placeholder Token Convention

The template uses `<<TOKEN>>` placeholders. Replace them with real values:

| Token | Description | Example Values |
|-------|-------------|----------------|
| `<<REPORT TITLE>>` | Main report header | "Deployment Report Q3", "MISRA Compliance Audit" |
| `<<PROJECT / REPORT CATEGORY>>` | Short uppercase label | "MISRA-C:2012 FIXING ASSISTANT", "SOFTWARE RELEASE" |
| `<<CONTEXT META>>` | Version, date, or stack | "v1.2 · Linux · Python 3.10" |
| `<<ALERT TITLE>>` | Alert heading | "Critical Update", "Key Finding" |
| `<<ALERT BODY>>` | Alert paragraph | "Lorem ipsum...", "Key points..." |
| `<<CARD N TITLE>>` | Card heading | "Duration", "Impact", "Timeline" |
| `<<CARD N BODY>>` | Card paragraph | "Describes a metric or insight" |

## Deployment Report Template Mapping

For a software deployment report, customize these sections:

| Section | What to Include |
|---------|-----------------|
| **Overview** | Release notes, version numbers, deployment date, key objectives |
| **Deployment** | Pre-requisites checklist, deployment steps, rollback plan, verification commands |
| **Architecture** | System diagram, component breakdown, data flow, dependencies |
| **Results** | Deployment metrics, test coverage, performance deltas, success indicators |
| **Appendix** | Full changelog, links to related docs, environment details |

### Deployment-Specific Placeholders

```
<<DEPLOYMENT SUBTITLE>>   → "Step-by-step deployment procedure"
<<SETUP STEPS TITLE>>     → "Environment Setup", "Configuration"
<<PIPELINE TITLE>>        → "Deployment Pipeline"
<<Step 1/2/3>>          → "Build", "Test", "Deploy", "Verify"
<<PROGRES TITLE>>         → "Deployment Progress"
<<Metric A/B/C>>          → "Build", "Tests", "Coverage"
```

## Technical Documentation Template Mapping

For technical docs, restructure:

| Section | What to Include |
|---------|-----------------|
| **Overview** | Problem statement, scope, document purpose |
| **System** | Architecture diagrams, APIs, data models |
| **Implementation** | Code snippets, examples, gotchas |
| **Validation** | Test results, metrics, verification logs |
| **Appendix** | Full API docs, external links, version history |

## Proposal Template Mapping

For project proposals, use this structure:

| Section | What to Include |
|---------|-----------------|
| **Problem** | Issue / opportunity |
| **Solution** | Proposed approach, benefits |
| **Timeline** | Delivery phases, milestones |
| **Resources** | Budget, staffing, tools |
| **Appendix** | Supporting data, references |

## Sidebar Customization

To add/remove sections, edit two places together:

```html
<!-- In sidebar -->
<div class="nav-item" onclick="show('new-section')">
  <span class="icon">✨</span> N · New Section
</div>

<!-- In main -->
<div id="section-new-section" class="section">
  <div class="section-title">✨ N · New Section</div>
  ...
</div>
```

## Injecting Dynamic Content

### Method 1: Command-line placeholder replacement

```bash
# Install skill scripts if needed
pip install -r requirements.txt

# Replace placeholders
python scripts/replace_placeholders.py \
  --input assets/reference-report.html \
  --output report.html \
  --vars '{"REPORT TITLE":"My Deployment Report","CONTEXT META":"v2.1"}'
```

### Method 2: Manual editing

Open `reference-report.html` in an editor and replace:

| Before | After |
|--------|-------|
| `<<REPORT TITLE>>` | `Q3 Deployment Report` |
| `<<PROJECT / REPORT CATEGORY>>` | `SOFTWARE DEPLOYMENT` |
| `<<CONTEXT META>>` | `Python 3.10 · Linux · July 2026` |

## Branding Customization

To match your brand colors, update `:root` in the `<style>` block:

```css
:root {
  --accent: #your-primary;        /* sidebar highlight, links */
  --accent-light: #your-light;      /* alert blue bg */
  --red: #your-danger;
  --green: #your-success;
  /* ...etc */
}
```

Then regenerate or update `reference-style.css`.