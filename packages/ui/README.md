# NeXifyAI Design System v2.0

Single Source of Truth for all NeXifyAI projects.

## Architecture

```
packages/ui/
├── tokens.css        → CSS Custom Properties (runtime)
├── constraints.js    → Canonical Component Contracts (design-time)
├── index.js          → Unified JS entry point
├── design-audit.py   → Violation Scanner (CI tool)
├── violation_lineage.py → Temporal Design Graph (drift tracking)
└── README.md         → This file
```

## Brand Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--color-accent` | `#FE9B7B` (Coral) | Primary CTA, Links, Highlights |
| `--color-accent-2` | `#14b8a6` (Teal) | Secondary highlights, Success |
| `--color-primary` | `#0f1923` (Deep Navy) | Backgrounds, Dark Theme |
| `--color-success` | `#22C55E` | Success states |
| `--color-warning` | `#F59E0B` | Warning states |
| `--color-danger` | `#EF4444` | Error states |

**Important:** The only brand accent is `#FE9B7B` (Coral). No Indigo (`#6366F1`) or Violet (`#8B5CF6`).

## Spacing (4px Grid)

Allowed values: 4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 96, 128

CSS tokens: `var(--space-1)` through `var(--space-32)`

## Typography

| Level | Size | Weight | Font |
|-------|------|--------|------|
| h1 | 2.5rem | 800 | Manrope |
| h2 | 2rem | 700 | Manrope |
| h3 | 1.5rem | 600 | Manrope |
| body | 1rem | 400 | Inter |
| small | 0.875rem | 400 | Inter |

## Icons

- Library: @phosphor-icons/react (weight: regular)
- Sizes: sidebar=20px, button=16px, table=18px, hero=24px

## CI Enforcement

```bash
# Run design audit (token violation scan)
python3 packages/ui/design-audit.py

# Check drift budget
python3 packages/ui/design-audit.py --fail-on high --drift-budget 5

# View violation lineage (copy-paste detection)
python3 packages/ui/violation_lineage.py --lineage

# Auto-fix safe violations (dry run)
python3 packages/ui/violation_lineage.py --auto-fix-dry-run
```
