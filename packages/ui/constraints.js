/**
 * NeXifyAI — Canonical Component Contracts (UI-E2)
 * 
 * Every UI component must conform to these constraints.
 * This is the UI equivalent of the Runtime Service Registry.
 * 
 * Principle: Canonical Design ≠ Rendered Design
 * These contracts define the CANONICAL truth.
 * The Design Audit (design-audit.js) detects violations.
 */

// ══════════════════════════════════════════════
// LOGO SYSTEM
// ══════════════════════════════════════════════

export const LogoContract = {
  desktop: {
    height: '36px',
    maxWidth: '200px',
    minWidth: '120px',
    gap: '10px',           // Icon ↔ Wordmark spacing
  },
  mobile: {
    height: '28px',
    maxWidth: '160px',
    minWidth: '100px',
    gap: '8px',
  },
  safeArea: '16px',        // Minimum clearance around logo
  alignment: 'flex-start', // Anchor in navbar
  forbidden: [
    'Never free-scale logo per page',
    'Never change logo height independently of navbar',
    'Never use logo without safe-area clearance',
  ],
};

// ══════════════════════════════════════════════
// NAVBAR / HEADER
// ══════════════════════════════════════════════

export const NavbarContract = {
  desktop: {
    height: '72px',
    paddingX: 'var(--space-6)',
  },
  mobile: {
    height: '64px',
    paddingX: 'var(--space-4)',
  },
  zIndex: 100,
  logoVerticalCenter: true,  // Logo must be vertically centered
  navLinkGap: 'var(--space-6)',
  forbidden: [
    'Never change navbar height per page',
    'Never use navbar taller than 80px',
    'Never place CTA inside navbar without vertical centering',
  ],
};

// ══════════════════════════════════════════════
// LAYOUT GRID
// ══════════════════════════════════════════════

export const LayoutContract = {
  container: {
    maxWidth: '1280px',
    narrow: '800px',
    wide: '1440px',
  },
  grid: {
    columns: 12,
    gap: 'var(--space-6)',
    gapMobile: 'var(--space-4)',
  },
  pagePadding: {
    desktop: 'var(--space-6)',
    mobile: 'var(--space-4)',
  },
  sectionGap: {
    desktop: '96px',
    mobile: '64px',
  },
  forbidden: [
    'Never use max-width > 1440px for content',
    'Never use asymmetric page padding',
    'Never change section-gap per page',
  ],
};

// ══════════════════════════════════════════════
// CTA SYSTEM (Max 3 Types)
// ══════════════════════════════════════════════

export const CTAContract = {
  types: ['primary', 'secondary', 'text'],
  primary: {
    height: '48px',
    minWidth: '160px',
    paddingX: 'var(--space-8)',
    fontWeight: 600,
    borderRadius: 'var(--radius-md)',
    backgroundColor: 'var(--color-accent)',
    textColor: 'var(--color-primary)',
  },
  secondary: {
    height: '44px',
    minWidth: '140px',
    paddingX: 'var(--space-6)',
    fontWeight: 600,
    borderRadius: 'var(--radius-md)',
    backgroundColor: 'transparent',
    borderColor: 'var(--color-accent)',
    textColor: 'var(--color-accent)',
  },
  text: {
    height: '36px',
    paddingX: 'var(--space-2)',
    fontWeight: 500,
    textColor: 'var(--color-accent)',
    textDecoration: 'underline',
  },
  gap: 'var(--space-4)',     // Spacing between adjacent CTAs
  maxPerViewport: 2,         // Never more than 2 CTAs in viewport
  hierarchy: {
    // Primary CTA is ALWAYS visually dominant
    weightRatio: '1.5 : 1 : 0.5',  // primary : secondary : text
  },
  forbidden: [
    'Never create a 4th CTA type',
    'Never make secondary CTA visually heavier than primary',
    'Never use more than 2 CTAs in hero section',
    'Never use different CTA heights on same page',
  ],
};

// ══════════════════════════════════════════════
// CARD / PANEL SYSTEM
// ══════════════════════════════════════════════

export const CardContract = {
  padding: {
    desktop: 'var(--space-6)',
    mobile: 'var(--space-4)',
  },
  gap: 'var(--space-6)',
  borderRadius: 'var(--radius-lg)',
  shadow: 'var(--shadow-default)',
  maxWidth: '400px',  // Cards should not dominate layout
  forbidden: [
    'Never use card padding < 16px',
    'Never use card as full-width page section',
    'Never mix different card padding on same page',
  ],
};

// ══════════════════════════════════════════════
// INPUT FIELD SYSTEM
// ══════════════════════════════════════════════

export const InputContract = {
  height: '48px',
  paddingX: 'var(--space-4)',
  borderRadius: 'var(--radius-md)',
  borderColor: 'var(--color-neutral-300)',
  focusBorderColor: 'var(--color-accent)',
  labelGap: 'var(--space-2)',
  forbidden: [
    'Never use input height < 44px (accessibility)',
    'Never use different input heights on same form',
    'Never use inputs without visible focus state',
  ],
};

// ══════════════════════════════════════════════
// FLOATING ELEMENTS
// ══════════════════════════════════════════════

export const FloatingElementContract = {
  maxCountPerPage: 1,        // Never more than 1 floating element
  position: 'bottom-right',  // Only allowed position
  offset: 'var(--space-6)',
  zIndex: 300,               // Must use z-modal
  minTriggerDistance: '600px', // Only show after scrolling
  forbidden: [
    'Never use > 1 floating element per page',
    'Never use floating CTA that competes with main CTA',
    'Never use floating element without scroll-distance trigger',
  ],
};

// ══════════════════════════════════════════════
// TYPOGRAPHY HIERARCHY (Enforced)
// ══════════════════════════════════════════════

export const TypographyContract = {
  scale: {
    h1: { size: '2.5rem', weight: 800, lineHeight: 1.2, maxWidth: '800px' },
    h2: { size: '2rem', weight: 700, lineHeight: 1.25, maxWidth: '700px' },
    h3: { size: '1.5rem', weight: 600, lineHeight: 1.3, maxWidth: '600px' },
    h4: { size: '1.25rem', weight: 600, lineHeight: 1.35 },
    body: { size: '1rem', weight: 400, lineHeight: 1.6, maxWidth: '650px' },
    small: { size: '0.875rem', weight: 400, lineHeight: 1.5 },
    caption: { size: '0.75rem', weight: 400, lineHeight: 1.4 },
  },
  fontFamily: {
    heading: "'Manrope', sans-serif",
    body: "'Inter', system-ui, -apple-system, sans-serif",
    mono: "'JetBrains Mono', monospace",
  },
  forbidden: [
    'Never use heading font for body text',
    'Never use body font size for headings',
    'Never use > 800px line-width for readability',
  ],
};

// ══════════════════════════════════════════════
// SPACING SCALE (Strict — no free values)
// ══════════════════════════════════════════════

export const SpacingScale = {
  unit: 4,  // Base unit in px
  allowed: [4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 96, 128],
  forbidden: [
    'Never use spacing not divisible by 4',
    'Never use padding: 13px, margin-top: 19px, etc.',
    'Always use var(--space-N) tokens',
  ],
};

// ══════════════════════════════════════════════
// RESPONSIVE BREAKPOINTS
// ══════════════════════════════════════════════

export const ResponsiveContract = {
  breakpoints: {
    sm: 375,
    md: 768,
    lg: 1024,
    xl: 1280,
    xxl: 1440,
  },
  mobileFirst: true,  // Always design mobile-first
  forbidden: [
    'Never use custom breakpoints outside this scale',
    'Never design desktop-first',
  ],
};

// ══════════════════════════════════════════════
// ALL CONTRACTS (for audit traversal)
// ══════════════════════════════════════════════

export const ALL_CONTRACTS = {
  logo: LogoContract,
  navbar: NavbarContract,
  layout: LayoutContract,
  cta: CTAContract,
  card: CardContract,
  input: InputContract,
  floating: FloatingElementContract,
  typography: TypographyContract,
  spacing: SpacingScale,
  responsive: ResponsiveContract,
};

export const CONTRACT_VERSION = '1.0.0';
