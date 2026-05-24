# NeXifyAI Design System — CI Niederländisch Orange/Weiß

## CI-Farben (Verbindlich)

### Primärfarben
| Token | Hex | Verwendung |
|-------|-----|------------|
| `--nx-accent` | `#FF6B00` | CI-Oranje — Buttons, CTAs, Highlights, KPIs, Akzente |
| `--nx-accent-h` | `#FF8533` | Hover-State Orange |
| White | `#FFFFFF` | Texte auf Orange-Hintergrund, Icons, primärer Textkontrast |

### Hintergrund
| Token | Hex | Verwendung |
|-------|-----|------------|
| `--nx-dark` | `#0c1117` | Page Background |
| `--nx-surface` | `#131a22` | Cards, Panels |
| `--nx-glass` | `rgba(19,26,34,0.6)` | Glass-Morphism Surfaces |

### Semantische Farben (Ausnahmen CI-Regel)
| Farbe | Hex | NUR für |
|-------|-----|---------|
| Grün | `#10b981` | Bestätigungen, Erfolg |
| Rot | `#ef4444` | Warnmeldungen, Fehler |
| Blau | `#2563EB` | Informationen, Links (sekundär) |

### Typografie
- Font: DM Sans (Google Fonts)
- H1: 2.5rem–3.5rem, 800 weight
- Body: 0.8125rem–0.875rem, 400 weight
- Buttons: 0.8125rem, 700 weight, Weiß auf Orange

### Buttons
- Primär: `background: #FF6B00; color: #fff` (Orange + Weiß)
- Sekundär: `border: 1px solid rgba(255,107,0,0.2); color: #FF6B00`
- Border-Radius: 8px (--r-sm)
- Hover: translateY(-1px) + hellerer Orangeton

### Regeln
1. Kein Dollar-Zeichen ($) — nur EUR (€)
2. Keine billigen SVG-Icons — Material Symbols (Google) oder Lucide React
3. D/A/CH-Lokalisierung (MwSt 21% wg. NL-Firmensitz)
4. Orange/Weiß in ALLEN UI-Elementen, KPIs, Visuals
5. Ausnahmen NUR für Warnmeldungen (Rot) und Bestätigungen (Grün)
