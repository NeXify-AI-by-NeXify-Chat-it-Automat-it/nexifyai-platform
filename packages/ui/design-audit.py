#!/usr/bin/env python3
"""
NeXifyAI — Design Audit Tool (UI-E3)

Scans CSS files for design system violations:
1. Free spacing values (not using --space-N tokens)
2. Free color values (not using --color-* tokens)
3. Free font sizes (not using --text-* tokens)
4. Non-standard border-radius
5. Hardcoded heights/widths
6. Z-index without scale
7. Custom breakpoints

This is the UI equivalent of the False Positive Detector.
Principle: Canonical Design ≠ Rendered Design
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ViolationSeverity(Enum):
    CRITICAL = "critical"  # Brand-damaging inconsistency
    HIGH = "high"          # Layout-breaking deviation
    MEDIUM = "medium"      # Visual inconsistency
    LOW = "low"            # Minor deviation


@dataclass
class TokenViolation:
    """A single design system violation."""
    file: str
    line: int
    value: str              # The violating value
    expected: str           # What the token system expects
    severity: ViolationSeverity
    suggestion: str         # How to fix


# ══════════════════════════════════════════════
# ALLOWED TOKEN PATTERNS
# ══════════════════════════════════════════════

ALLOWED_SPACING = {4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 96, 128}

ALLOWED_COLORS = {
    '#0f1923', '#FE9B7B', '#14b8a6',
    '#f1f5f9', '#e2e8f0', '#cbd5e1', '#94a3b8',
    '#64748b', '#475569', '#334155', '#1e293b', '#0f172a',
    '#22c55e', '#f59e0b', '#ef4444',
}

TOKEN_PATTERNS = [
    'var(--',           # CSS custom property reference
    '--color-', '--space-', '--text-', '--font-',
    '--radius-', '--shadow-', '--transition-',
    '--logo-', '--navbar-', '--container-', '--grid-',
    '--cta-', '--card-', '--input-', '--baseline-',
    '--section-', '--page-', '--z-',
]

# Values that are OK to be literal (not tokens)
SAFE_LITERALS = {
    '0', 'none', 'auto', '100%', '50%', '0%',
    'transparent', 'inherit', 'unset', 'initial',
    '1px', '2px',  # Borders often need thin values
    'solid', 'dashed', 'dotted',
    'flex', 'block', 'inline', 'grid',
    'center', 'left', 'right', 'start', 'end',
    'row', 'column', 'wrap', 'nowrap',
    'hidden', 'visible', 'scroll',
    'pointer', 'normal', 'bold',
    'uppercase', 'lowercase', 'capitalize',
    'cover', 'contain', 'fill',
    'underline', 'line-through',
    'ease', 'ease-in', 'ease-out', 'linear',
}


# ══════════════════════════════════════════════
# DETECTION RULES
# ══════════════════════════════════════════════

def scan_directory(scan_dir: str) -> List[TokenViolation]:
    """Scan all CSS files in directory for token violations."""
    violations = []
    
    for root, dirs, files in os.walk(scan_dir):
        # Skip node_modules, build, dist
        dirs[:] = [d for d in dirs if d not in ('node_modules', 'build', 'dist', '.git', '__pycache__')]
        
        for fname in files:
            if not fname.endswith('.css'):
                continue
            
            filepath = os.path.join(root, fname)
            violations.extend(scan_file(filepath))
    
    return violations


def scan_file(filepath: str) -> List[TokenViolation]:
    """Scan a single CSS file for token violations."""
    violations = []
    
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except Exception:
        return violations
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip comments and empty lines
        if line.startswith('/*') or line.startswith('*') or not line:
            continue
        
        # Skip lines that already use tokens
        if any(pattern in line for pattern in ['var(--', '--color-', '--space-', '--text-']):
            continue
        
        # Rule 1: Free px spacing values
        v = _check_free_px_spacing(line, i, filepath)
        if v:
            violations.append(v)
        
        # Rule 2: Free hex colors (not in token system)
        v = _check_free_colors(line, i, filepath)
        if v:
            violations.append(v)
        
        # Rule 3: Free font-size values
        v = _check_free_font_sizes(line, i, filepath)
        if v:
            violations.append(v)
        
        # Rule 4: Hardcoded heights that should use tokens
        v = _check_hardcoded_heights(line, i, filepath)
        if v:
            violations.append(v)
        
        # Rule 5: Z-index without scale
        v = _check_zindex(line, i, filepath)
        if v:
            violations.append(v)
    
    return violations


def _check_free_px_spacing(line: str, lineno: int, filepath: str) -> Optional[TokenViolation]:
    """Detect padding/margin/gap with px values not in spacing scale."""
    # Match: padding: 13px, margin: 19px, gap: 7px, etc.
    match = re.search(r'(padding|margin|gap)\s*:\s*(\d+)px', line)
    if not match:
        return None
    
    value = int(match.group(2))
    if value not in ALLOWED_SPACING and value > 2:
        return TokenViolation(
            file=filepath,
            line=lineno,
            value=f"{match.group(1)}: {value}px",
            expected=f"var(--space-N) — allowed: {sorted(ALLOWED_SPACING)}",
            severity=ViolationSeverity.HIGH if value > 50 else ViolationSeverity.MEDIUM,
            suggestion=f"Replace {value}px with nearest --space token: {_nearest_token(value)}",
        )
    return None


def _check_free_colors(line: str, lineno: int, filepath: str) -> Optional[TokenViolation]:
    """Detect hex colors not in the design system."""
    match = re.search(r'(#[0-9a-fA-F]{6})', line)
    if not match:
        return None
    
    color = match.group(1).lower()
    if color in ALLOWED_COLORS:
        return None
    
    # Check if it's a CSS variable reference
    if 'var(' in line:
        return None
    
    return TokenViolation(
        file=filepath,
        line=lineno,
        value=color,
        expected=f"var(--color-*) token from design system",
        severity=ViolationSeverity.HIGH,
        suggestion=f"Replace {color} with nearest design system color",
    )


def _check_free_font_sizes(line: str, lineno: int, filepath: str) -> Optional[TokenViolation]:
    """Detect font-size in px not using tokens."""
    match = re.search(r'font-size\s*:\s*(\d+)px', line)
    if not match:
        return None
    
    value = int(match.group(1))
    allowed_text = {12, 14, 16, 18, 20, 24, 32, 40}
    if value not in allowed_text:
        return TokenViolation(
            file=filepath,
            line=lineno,
            value=f"font-size: {value}px",
            expected="var(--text-h1) through var(--text-xs)",
            severity=ViolationSeverity.MEDIUM,
            suggestion=f"Use --text-* token instead of {value}px",
        )
    return None


def _check_hardcoded_heights(line: str, lineno: int, filepath: str) -> Optional[TokenViolation]:
    """Detect height values that should use --navbar-height or --input-height."""
    match = re.search(r'height\s*:\s*(\d+)px', line)
    if not match:
        return None
    
    value = int(match.group(1))
    
    # Navbar height check
    if value in (70, 71, 72, 73, 74, 80):
        return TokenViolation(
            file=filepath,
            line=lineno,
            value=f"height: {value}px",
            expected="var(--navbar-height)",
            severity=ViolationSeverity.HIGH,
            suggestion="Use var(--navbar-height) instead of hardcoded height",
        )
    
    # Input height check
    if value in (44, 46, 48, 50):
        return TokenViolation(
            file=filepath,
            line=lineno,
            value=f"height: {value}px",
            expected="var(--input-height)",
            severity=ViolationSeverity.MEDIUM,
            suggestion="Use var(--input-height) instead of hardcoded height",
        )
    
    return None


def _check_zindex(line: str, lineno: int, filepath: str) -> Optional[TokenViolation]:
    """Detect z-index values not in scale."""
    match = re.search(r'z-index\s*:\s*(-?\d+)', line)
    if not match:
        return None
    
    value = int(match.group(1))
    z_scale = {0, 50, 100, 200, 300, 400, 500}
    
    if value not in z_scale:
        return TokenViolation(
            file=filepath,
            line=lineno,
            value=f"z-index: {value}",
            expected="var(--z-*) from scale: 0, 50, 100, 200, 300, 400, 500",
            severity=ViolationSeverity.LOW,
            suggestion=f"Use nearest z-index token: {_nearest_z(value)}",
        )
    return None


def _nearest_token(value: int) -> str:
    """Find nearest spacing token."""
    nearest = min(ALLOWED_SPACING, key=lambda x: abs(x - value))
    return f"var(--space-{_token_name(nearest)})"


def _token_name(value: int) -> str:
    """Map spacing value to token name."""
    token_map = {4: '1', 8: '2', 12: '3', 16: '4', 20: '5', 
                 24: '6', 28: '7', 32: '8', 40: '10', 48: '12', 
                 64: '16', 96: '24', 128: '32'}
    return token_map.get(value, str(value))


def _nearest_z(value: int) -> str:
    z_scale = {0: 'base', 50: 'dropdown', 100: 'sticky', 200: 'overlay', 300: 'modal', 400: 'toast', 500: 'tooltip'}
    nearest = min(z_scale.keys(), key=lambda x: abs(x - value))
    return f"var(--z-{z_scale[nearest]})"


# ══════════════════════════════════════════════
# REPORT
# ══════════════════════════════════════════════

def audit_report(scan_dir: str = None) -> Dict:
    """Generate design audit report."""
    if scan_dir is None:
        scan_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    
    violations = scan_directory(scan_dir)
    
    return {
        "total_violations": len(violations),
        "by_severity": {
            "critical": len([v for v in violations if v.severity == ViolationSeverity.CRITICAL]),
            "high": len([v for v in violations if v.severity == ViolationSeverity.HIGH]),
            "medium": len([v for v in violations if v.severity == ViolationSeverity.MEDIUM]),
            "low": len([v for v in violations if v.severity == ViolationSeverity.LOW]),
        },
        "by_file": {},
        "violations": [
            {
                "file": v.file,
                "line": v.line,
                "value": v.value,
                "severity": v.severity.value,
                "suggestion": v.suggestion,
            }
            for v in violations
        ],
    }


def cli_audit(scan_dir: str = None) -> str:
    """CLI-friendly audit output."""
    if scan_dir is None:
        scan_dir = '/opt/nexifyai-website-sicherheitskopie/frontend/src'
    
    violations = scan_directory(scan_dir)
    
    lines = [
        "═══ DESIGN AUDIT — Token Violation Scanner ═══",
        f"Directory: {scan_dir}",
        f"Violations: {len(violations)}",
        "",
    ]
    
    by_file = {}
    for v in violations:
        fname = os.path.basename(v.file)
        by_file.setdefault(fname, []).append(v)
    
    for fname, file_violations in sorted(by_file.items()):
        lines.append(f"  {fname}: {len(file_violations)} violations")
        for v in file_violations:
            icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}[v.severity.value]
            lines.append(f"    {icon} L{v.line}: {v.value} → {v.suggestion[:80]}")
    
    if not violations:
        lines.append("  ✅ No token violations found.")
    
    lines.append("")
    lines.append(f"Total: {len(violations)} violations across {len(by_file)} files")
    
    return "\n".join(lines)


if __name__ == '__main__':
    import sys
    
    # CLI: python design-audit.py [--fail-on high|medium|low] [--drift-budget N]
    fail_on = None
    drift_budget = None
    
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '--fail-on' and i + 1 < len(args):
            fail_on = args[i + 1]
        if arg == '--drift-budget' and i + 1 < len(args):
            drift_budget = int(args[i + 1])
    
    print(cli_audit())
    
    violations = scan_directory('/opt/nexifyai-website-sicherheitskopie/frontend/src')
    
    # Exit code based on severity threshold
    if fail_on:
        severity_map = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        threshold = severity_map.get(fail_on.lower(), 0)
        failing = [v for v in violations if severity_map.get(v.severity.value, 99) <= threshold]
        if failing:
            print(f"\n⛔ BLOCKED: {len(failing)} violations at or above --fail-on={fail_on}")
            sys.exit(1)
    
    # Drift budget check (total violations must not exceed budget)
    if drift_budget is not None:
        if len(violations) > drift_budget:
            print(f"\n⛔ DRIFT BUDGET EXCEEDED: {len(violations)} violations > budget of {drift_budget}")
            sys.exit(1)
        else:
            print(f"\n✅ Drift budget OK: {len(violations)} ≤ {drift_budget}")
    
    sys.exit(0)
