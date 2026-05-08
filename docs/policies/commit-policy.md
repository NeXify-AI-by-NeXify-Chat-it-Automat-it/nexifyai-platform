# Commit Policy
# DOS v2.0 Chapter 13.1

## Conventional Commits (Pflicht)

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Typen

| Typ | Verwendung |
|---|---|
| `feat` | Neues Feature |
| `fix` | Bugfix |
| `docs` | Dokumentation |
| `style` | Formatierung (kein Code-Change) |
| `refactor` | Code-Refactoring |
| `perf` | Performance-Verbesserung |
| `test` | Tests |
| `chore` | Wartung (Deps, Config, Tooling) |
| `ci` | CI/CD-Änderungen |
| `security` | Security-Fix |

## Branch-Namen

| Branch | Verwendung |
|---|---|
| `main` | Production-ready. Kein Direct Push. |
| `develop` | Integration (optional) |
| `feat/*` | Feature-Entwicklung |
| `fix/*` | Bugfixes |
| `chore/*` | Dependency Updates |
| `release/*` | Release-Vorbereitung |

## Author-Identität

- **Name:** Pascal Courbois
- **Email:** u6288408171@gmail.com
- **GitHub:** nexifyai-dev
- Commits mit invalider Email (z.B. `nexifyai@nexifyai.de`) werden von Vercel blockiert.
