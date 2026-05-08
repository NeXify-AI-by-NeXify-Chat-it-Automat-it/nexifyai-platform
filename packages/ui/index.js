/**
 * NeXifyAI Design System — Package Index
 * DOS v2.0 Chapter 9: Design-System
 * Version: 1.0.0 | Stand: 2026-05-08
 *
 * Das zentrale UI-System für alle NeXifyAI-Projekte.
 * Keine One-Off UI — alle Komponenten entstehen über dieses Package.
 */

// Design Tokens (als CSS Custom Properties)
export { default as tokens } from './tokens.css';

// CTA-Typen (maximal 3 erlaubt: Primary / Secondary / Text)
export const CTA_TYPES = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  TEXT: 'text',
};

// WCAG 2.1 AA Mindeststandard
export const ACCESSIBILITY = {
  MIN_COLOR_CONTRAST: 4.5,  // AA für normalen Text
  MIN_FOCUS_OUTLINE: '2px solid var(--color-accent)',
  MIN_TARGET_SIZE: '44px',   // Touch-Target
};

// Breakpoints (Mobile-First)
export const BREAKPOINTS = {
  sm: 375,
  md: 768,
  lg: 1024,
  xl: 1280,
  xxl: 1440,
};

// Version
export const DESIGN_SYSTEM_VERSION = '1.0.0';
