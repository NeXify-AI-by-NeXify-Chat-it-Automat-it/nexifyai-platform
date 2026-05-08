# NeXifyAI Design System

**Package:** `/packages/ui`  
**Version:** 1.0.0  
**DOS-Referenz:** Kapitel 9

## Struktur

```
packages/ui/
├── index.js          # Package-Index, CTA-Typen, Breakpoints, Accessibility
├── tokens.css        # Design Tokens (CSS Custom Properties)
├── README.md         # Diese Datei
└── components/       # Wiederverwendbare UI-Komponenten (folgt)
```

## Verwendung

```js
import { CTA_TYPES, BREAKPOINTS } from '@nexifyai/ui';
import '@nexifyai/ui/tokens.css';
```

## Regeln (DOS v2.0 9.2)

1. **Nur Komponenten aus diesem Package** — keine One-Off-UI
2. **Maximal 3 CTA-Typen:** Primary, Secondary, Text
3. **WCAG 2.1 AA** Mindeststandard
4. **Mobile-First:** Breakpoints 375 / 768 / 1024 / 1280 / 1440
5. **Dark-Mode-kompatibel:** Alle Tokens müssen theme-fähig sein

## Änderungen

Nur via PR mit Design-Review. Token-Änderungen sind BREAKING (MAJOR-Version).
