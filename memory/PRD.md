# NeXifyAI Landing Page — Product Requirements Document

## Original Problem Statement
Premium DACH B2B landing page for "NeXifyAI by NeXify" — enterprise AI automation. Core claim: "Chat it. Automate it." Primary goal: generate qualified B2B strategy calls. Target: DACH + NL + Global. Real 3D animated web experience with full multilingual support.

## Brand & Legal
- **Name**: NeXifyAI by NeXify | **Entity**: NeXify Automate (NL, KvK: 90483944)
- **CEO**: Pascal Courbois | **USt-ID**: NL865786276B01

## Architecture
- Frontend: React 18, @react-three/fiber v8, react-markdown, remark-gfm
- Backend: FastAPI, MongoDB (motor), JWT+Argon2 auth
- LLM: GPT-4o-mini via Emergent LLM Key
- Email: Resend API
- i18n: Custom React Context (DE/NL/EN)

## Implemented Features (All Verified)

### UI Polish Pass — Iteration 11 (April 2026)
- All CI-colored buttons: rounded corners (6-8px)
- All modals: border-radius 12px (booking, chat)
- Chat trigger: pill-shaped (50px radius)
- Language switcher: premium pill design with active glow
- Form fields: flush alignment (2-column grid for name pairs and phone/company)
- Cards, badges, FAQ items, pricing cards: consistent rounded corners
- Typography: JetBrains Mono for code, improved font weights
- Enhanced 3D effects: 120 hero nodes, 500 data streams, 90 globe nodes, 30 arcs

### Chat Icon Fix + LLM Quality — Iteration 10
- SVG arrows replacing Material Symbols chat_bubble (font-independent)
- System prompt: GESPRÄCHSSTIL UND TONALITÄT section (conversational, not template-like)
- Welcome messages: proactive in all 3 languages

### Form Labels + i18n — Iteration 9
- Fixed duplicate Name labels → Vorname/Nachname (DE), First Name/Last Name (EN), Voornaam/Achternaam (NL)
- Fixed hardcoded Telefon → translated phone labels
- Separate validation messages per field

### Chat Markdown + 3D Graphics — Iteration 8
- ReactMarkdown + remark-gfm rendering
- Process Pipeline v2, Orchestration Hub-Spoke, Enhanced Globe

### Admin CRM + Calendar — Iteration 7
- Monthly calendar, slot blocking, customer management

### Earlier Iterations (5-6)
- Multilingual (DE/NL/EN), SEO, 400+ Integrations messaging, Legal pages

## Testing History
- Iteration 7: 28/28 | 8: 40/40 | 9: 40/40 | 10: 40/40 | 11: 100% (all features)

## Upcoming Tasks
- P1: Automated email sequences (booking confirmation, 24h reminder, 48h follow-up)
- P1: Lighthouse Performance Optimization (3D lazy-loading, font preloading)
- P2: Analytics Dashboard in Admin area
- P2: App.js Refactoring (>740 lines)

## Backlog
- Cookie settings granular page, Admin CSV export, MFA, A/B testing

---
*Last updated: 02.04.2026 — Comprehensive UI polish, rounded corners, enhanced 3D, typography upgrade. Iteration 11: ALL tests PASSED.*
