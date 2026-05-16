# NeXifyAI Website - Gerettet vom Emergent Preview Server

**Quelle:** `https://vscode-ba57f1c5-2c1c-49c6-a3fe-28cd8f27846c.preview.emergentagent.com/proxy/3000/`

## Inhalt
- **index.html** - Hauptseite (angepasst für lokales Serving)
- **bundle/** - Kompilierte Bundle-Dateien
  - bundle.js (9.3 MB) - Webpack Production-Bundle
  - bundle.js.map (8.2 MB) - Source Map
  - icon-mark.svg (252 B) - NeXifyAI Icon
- **source/src/** - 34 Source-Files extrahiert aus Source Map

## Technologie
- React 18 SPA (create-react-app / webpack)
- React Router v6
- react-three-fiber + drei (3D-Szenen)
- framer-motion (Animationen)
- i18n: Deutsch, Englisch, Niederländisch
- SEO: react-helmet-async
- DSGVO-konforme Impressum/Datenschutz-Seiten

## Starten
```bash
python3 serve.py [port]
# Default: http://localhost:8800
```
