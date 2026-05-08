#!/usr/bin/env python3
"""
NeXifyAI — Temporal Design Graph (UI-E4)
Tracks design violations over time to detect:
1. Drift patterns (which files drift most, which tokens are ignored)
2. Violation lineage (copy-modify-diverge detection)
3. Recurrence (which violations keep coming back)
4. Confidence-based auto-fix suggestions

Usage:
    python violation_lineage.py                     # Full report
    python violation_lineage.py --entropy-map       # Top drift sources
    python violation_lineage.py --auto-fix-dry-run  # What would be auto-fixed
"""

import os
import re
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from enum import Enum

import os, sys, importlib.util
# Load design-audit.py (hyphenated filename, can't use regular import)
_audit_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'design-audit.py')
_spec = importlib.util.spec_from_file_location("design_audit", _audit_path)
_design_audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_design_audit)
scan_directory = _design_audit.scan_directory
TokenViolation = _design_audit.TokenViolation
ViolationSeverity = _design_audit.ViolationSeverity


# ══════════════════════════════════════════════
# ENTROPY MAPPING
# ══════════════════════════════════════════════

@dataclass
class EntropySource:
    """A file or component that generates disproportionate design drift."""
    file: str
    total_violations: int
    unique_colors: List[str]     # Non-standard colors used
    unique_spacings: List[int]    # Non-standard spacing values
    primary_drift_type: str       # "color", "spacing", "z-index", "typography"
    entropy_score: float          # 0.0-1.0, how "divergent" from canonical design
    is_forked_topology: bool      # True if this looks like a copy-pasted design


@dataclass
class ViolationLineage:
    """Traces where a violation pattern originated."""
    pattern: str                  # e.g., "color:#6b7b8d", "spacing:10px"
    origin_file: str              # File where this pattern first appeared
    propagated_files: List[str]   # Files that copied this pattern
    occurrence_count: int
    is_copy_paste: bool           # True if multiple files share identical values


@dataclass
class AutoFixSuggestion:
    """Confidence-scored auto-fix for a violation."""
    file: str
    line: int
    violation: str
    fix: str
    confidence: float             # 0.0-1.0
    risk: str                     # "safe", "review", "manual"


# ══════════════════════════════════════════════
# ENTROPY ANALYZER
# ══════════════════════════════════════════════

def entropy_map(scan_dir: str = None) -> List[EntropySource]:
    """Map design entropy sources across the codebase."""
    if scan_dir is None:
        scan_dir = '/opt/nexifyai-website-sicherheitskopie/frontend/src'
    
    violations = scan_directory(scan_dir)
    by_file = defaultdict(list)
    for v in violations:
        by_file[v.file].append(v)
    
    sources = []
    for filepath, file_violations in sorted(by_file.items(), key=lambda x: -len(x[1])):
        # Extract unique non-standard colors
        colors = []
        spacings = []
        z_indices = []
        
        for v in file_violations:
            if v.value.startswith('#'):
                colors.append(v.value)
            elif 'px' in v.value and ('padding' in v.value or 'margin' in v.value or 'gap' in v.value):
                try:
                    spacings.append(int(re.search(r'(\d+)px', v.value).group(1)))
                except:
                    pass
            elif 'z-index' in v.value:
                try:
                    z_indices.append(int(re.search(r'(-?\d+)', v.value).group(1)))
                except:
                    pass
        
        # Determine primary drift type
        type_counts = Counter(v.severity.value for v in file_violations)
        primary = type_counts.most_common(1)[0][0] if type_counts else "unknown"
        
        # Entropy score: ratio of unique colors to total violations × file weight
        total_weight = len(file_violations) / 100  # Normalize
        color_divergence = len(set(colors)) / max(1, len(colors)) if colors else 0
        entropy_score = min(1.0, total_weight * 0.6 + color_divergence * 0.4)
        
        # Forked topology detection: file has unique colors AND spacings not seen elsewhere
        is_forked = len(set(colors)) > 5 and len(set(spacings)) > 3
        
        sources.append(EntropySource(
            file=os.path.basename(filepath),
            total_violations=len(file_violations),
            unique_colors=list(set(colors))[:10],
            unique_spacings=list(set(spacings))[:10],
            primary_drift_type=primary,
            entropy_score=round(entropy_score, 2),
            is_forked_topology=is_forked,
        ))
    
    return sources


# ══════════════════════════════════════════════
# VIOLATION LINEAGE (Copy-Modify-Diverge Detection)
# ══════════════════════════════════════════════

def violation_lineage(scan_dir: str = None) -> List[ViolationLineage]:
    """Detect violation patterns that appear across multiple files (copy-paste drift)."""
    if scan_dir is None:
        scan_dir = '/opt/nexifyai-website-sicherheitskopie/frontend/src'
    
    violations = scan_directory(scan_dir)
    
    # Group violations by value pattern
    by_value = defaultdict(list)
    for v in violations:
        # Normalize the value for comparison
        key = f"{v.value.strip()}"
        by_value[key].append(v)
    
    lineages = []
    for pattern, vlist in by_value.items():
        if len(vlist) < 2:
            continue  # Only care about patterns that appear multiple times
        
        files = list(set(v.file for v in vlist))
        if len(files) < 2:
            continue  # Same file, different lines — not lineage
        
        # Sort by line number to find origin (lowest line = likely origin)
        sorted_v = sorted(vlist, key=lambda v: v.line)
        origin = sorted_v[0]
        
        lineages.append(ViolationLineage(
            pattern=pattern[:80],
            origin_file=os.path.basename(origin.file),
            propagated_files=[os.path.basename(f) for f in files if f != origin.file],
            occurrence_count=len(vlist),
            is_copy_paste=len(files) >= 3,  # 3+ files with same value = likely copy-paste
        ))
    
    # Sort by most propagated
    return sorted(lineages, key=lambda l: -l.occurrence_count)


# ══════════════════════════════════════════════
# AUTO-FIX SUGGESTIONS (Confidence-based)
# ══════════════════════════════════════════════

SPACING_MAP = {4: '--space-1', 8: '--space-2', 12: '--space-3', 16: '--space-4',
               20: '--space-5', 24: '--space-6', 28: '--space-7', 32: '--space-8',
               40: '--space-10', 48: '--space-12', 64: '--space-16', 96: '--space-24', 128: '--space-32'}

ALLOWED_SPACING = {4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 96, 128}

Z_SCALE = {0: '--z-base', 50: '--z-dropdown', 100: '--z-sticky', 200: '--z-overlay',
           300: '--z-modal', 400: '--z-toast', 500: '--z-tooltip'}

ALLOWED_Z = {0, 50, 100, 200, 300, 400, 500}


def auto_fix_suggestions(scan_dir: str = None) -> List[AutoFixSuggestion]:
    """Generate confidence-scored auto-fix suggestions."""
    if scan_dir is None:
        scan_dir = '/opt/nexifyai-website-sicherheitskopie/frontend/src'
    
    violations = scan_directory(scan_dir)
    suggestions = []
    
    for v in violations:
        fix = None
        confidence = 0.0
        risk = "manual"
        
        # Spacing auto-fix
        if 'px' in v.value and ('padding' in v.value or 'margin' in v.value or 'gap' in v.value):
            match = re.search(r'(\d+)px', v.value)
            if match:
                px = int(match.group(1))
                if px <= 2:
                    continue  # 1-2px borders are fine
                nearest = min(ALLOWED_SPACING, key=lambda x: abs(x - px))
                diff = abs(px - nearest)
                
                if diff == 0:
                    fix = f"var({SPACING_MAP[nearest]})"
                    confidence = 1.0
                    risk = "safe"
                elif diff <= 2:
                    fix = f"var({SPACING_MAP[nearest]})  /* was {px}px, nearest token: {nearest}px */"
                    confidence = 0.9 - (diff * 0.1)
                    risk = "safe" if diff <= 1 else "review"
                elif diff <= 6:
                    fix = f"var({SPACING_MAP[nearest]})  /* ⚠️ was {px}px, verify visual match */"
                    confidence = 0.7
                    risk = "review"
                else:
                    fix = f"/* MANUAL: {px}px → nearest token {nearest}px (big gap) */"
                    confidence = 0.4
                    risk = "manual"
        
        # Z-index auto-fix
        elif 'z-index' in v.value:
            match = re.search(r'(-?\d+)', v.value)
            if match:
                z = int(match.group(1))
                nearest = min(ALLOWED_Z, key=lambda x: abs(x - z))
                diff = abs(z - nearest)
                
                if diff <= 10:
                    fix = f"var({Z_SCALE[nearest]})"
                    confidence = 0.95
                    risk = "safe"
                elif diff <= 50:
                    fix = f"var({Z_SCALE[nearest]})  /* was z-index:{z} */"
                    confidence = 0.7
                    risk = "review"
                else:
                    fix = f"/* MANUAL: z-index:{z} → var({Z_SCALE[nearest]}) */"
                    confidence = 0.4
                    risk = "manual"
        
        # Height auto-fix (input fields)
        elif 'height' in v.value and 'px' in v.value:
            match = re.search(r'(\d+)px', v.value)
            if match:
                h = int(match.group(1))
                if 44 <= h <= 50:
                    fix = "var(--input-height)"
                    confidence = 0.9
                    risk = "safe"
                elif 70 <= h <= 80:
                    fix = "var(--navbar-height)"
                    confidence = 0.85
                    risk = "safe"
        
        if fix:
            suggestions.append(AutoFixSuggestion(
                file=os.path.basename(v.file),
                line=v.line,
                violation=v.value[:60],
                fix=fix,
                confidence=round(confidence, 2),
                risk=risk,
            ))
    
    return suggestions


# ══════════════════════════════════════════════
# REPORTING
# ══════════════════════════════════════════════

def full_report(scan_dir: str = None) -> str:
    """Complete temporal design graph report."""
    lines = [
        "═══ TEMPORAL DESIGN GRAPH ═══",
        "",
        "═══ ENTROPY SOURCES ═══",
    ]
    
    sources = entropy_map(scan_dir)
    for s in sources[:6]:
        fork = " ⚠️ FORKED TOPOLOGY" if s.is_forked_topology else ""
        lines.append(f"  {s.file}: {s.total_violations} violations, entropy={s.entropy_score}, drift={s.primary_drift_type}{fork}")
    
    lines.append("")
    lines.append("═══ VIOLATION LINEAGE (Copy-Modify-Diverge) ═══")
    
    lineages = violation_lineage(scan_dir)
    for l in lineages[:10]:
        if l.is_copy_paste:
            files = ', '.join(l.propagated_files[:3])
            if len(l.propagated_files) > 3:
                files += f" +{len(l.propagated_files)-3} more"
            lines.append(f"  📋 '{l.pattern}' → origin:{l.origin_file} → propagated to {len(l.propagated_files)} files: {files} [{l.occurrence_count}×]")
    
    lines.append("")
    lines.append("═══ AUTO-FIX SUGGESTIONS ═══")
    
    fixes = auto_fix_suggestions(scan_dir)
    safe = [f for f in fixes if f.risk == 'safe']
    review = [f for f in fixes if f.risk == 'review']
    manual = [f for f in fixes if f.risk == 'manual']
    
    lines.append(f"  Safe (auto-applicable): {len(safe)}")
    lines.append(f"  Review (visual check needed): {len(review)}")
    lines.append(f"  Manual (requires designer): {len(manual)}")
    
    for f in safe[:5]:
        lines.append(f"    ✅ {f.file}:{f.line} '{f.violation}' → {f.fix} [{f.confidence}]")
    
    for f in review[:3]:
        lines.append(f"    🔍 {f.file}:{f.line} '{f.violation}' → {f.fix} [{f.confidence}]")
    
    return "\n".join(lines)


if __name__ == '__main__':
    import sys
    
    if '--entropy-map' in sys.argv:
        for s in entropy_map():
            print(f"{s.entropy_score:.2f} {s.file}: {s.total_violations} violations ({s.primary_drift_type})")
    elif '--lineage' in sys.argv:
        for l in violation_lineage()[:15]:
            if l.is_copy_paste:
                print(f"COPY-PASTE: '{l.pattern}' → {l.origin_file} → {len(l.propagated_files)} files ({l.occurrence_count}×)")
    elif '--auto-fix-dry-run' in sys.argv:
        for f in auto_fix_suggestions():
            if f.risk == 'safe':
                print(f"SAFE {f.confidence:.2f} {f.file}:{f.line}: {f.violation} → {f.fix}")
    else:
        print(full_report())
