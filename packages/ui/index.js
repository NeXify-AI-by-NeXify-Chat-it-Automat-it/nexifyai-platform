/**
 * NeXifyAI Design System — Single Source of Truth
 * ================================================
 * Import this file to get ALL design tokens, components, and utilities.
 *
 * Usage:
 *   import { colors, spacing, typography, tokens } from '@nexifyai/design-system';
 *
 * OR in CSS:
 *   @import '@nexifyai/design-system/tokens.css';
 */

// ═══ Colors ═══
export const colors = {
  brand: {
    coral: '#FE9B7B',
    teal: '#14b8a6',
    navy: '#0f1923',
    slate: '#e2e8f0',
    glass: 'rgba(19, 26, 34, 0.85)',
  },
  semantic: {
    success: '#22C55E',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  },
  neutral: {
    50: '#f1f5f9', 100: '#e2e8f0', 200: '#c8d1dc',
    300: '#94a3b8', 400: '#64748b', 500: '#6b7b8d',
    600: '#475569', 700: '#334155', 800: '#1e293b',
    900: '#0f172a',
  },
};

// ═══ Spacing (4px Grid) ═══
export const spacing = {
  1: 4, 2: 8, 3: 12, 4: 16, 5: 20, 6: 24,
  7: 28, 8: 32, 10: 40, 12: 48, 16: 64, 24: 96, 32: 128,
};

// ═══ Typography ═══
export const typography = {
  fontFamily: {
    heading: "'Manrope', sans-serif",
    body: "'Inter', system-ui, -apple-system, sans-serif",
    mono: "'JetBrains Mono', monospace",
  },
  scale: {
    h1: { size: '2.5rem', weight: 800, lineHeight: 1.2 },
    h2: { size: '2rem', weight: 700, lineHeight: 1.25 },
    h3: { size: '1.5rem', weight: 600, lineHeight: 1.3 },
    h4: { size: '1.25rem', weight: 600, lineHeight: 1.35 },
    body: { size: '1rem', weight: 400, lineHeight: 1.6 },
    small: { size: '0.875rem', weight: 400, lineHeight: 1.5 },
    caption: { size: '0.75rem', weight: 400, lineHeight: 1.4 },
  },
};

// ═══ Component Tokens ═══
export const components = {
  navbar: {
    height: { desktop: '72px', mobile: '64px' },
    zIndex: 100,
  },
  sidebar: {
    width: { collapsed: '64px', expanded: '256px' },
    iconSize: '20px',
  },
  card: {
    padding: { desktop: '24px', mobile: '16px' },
    borderRadius: '16px',
    gap: '24px',
  },
  button: {
    primary: { height: '48px', minWidth: '160px', borderRadius: '6px' },
    secondary: { height: '44px', minWidth: '140px', borderRadius: '6px' },
    text: { height: '36px', borderRadius: '6px' },
  },
  input: {
    height: '48px',
    borderRadius: '6px',
  },
  badge: {
    borderRadius: '9999px',
    padding: '2px 10px',
    fontSize: '0.75rem',
  },
};

// ═══ All Tokens (for audit) ═══
export const tokens = {
  version: '2.0.0',
  colors,
  spacing,
  typography,
  components,
  rules: {
    ctaMaxPerViewport: 2,
    floatingElementMaxPerPage: 1,
    spacingUnit: 4,
    allowedSpacing: Object.values(spacing),
    mobileFirst: true,
  },
};

export default tokens;
