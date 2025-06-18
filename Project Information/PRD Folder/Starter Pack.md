# Project Repository Documentation Structure

This document outlines the recommended structure and organization for project documentation to optimize AI coding agent effectiveness.

## 1. Repository Root Files

| File | Purpose | Format |
|------|---------|--------|
| `README.md` | Human-first quick-start guide, links to every documentation section | Markdown |
| `project-info.md` | "Minimal brain" – goals, domain glossary, coding conventions, repository etiquette | Markdown |
| `CLAUDE.md` (or `CURSOR.md`) | Cursor-specific tips, bash aliases, red-flag patterns, troubleshooting recipes | Markdown |
| `CONTRIBUTING.md` | PR rules, branch naming, commit style guidelines | Markdown |
| `CODE_OF_CONDUCT.md` | Behavior rules for collaborators | Markdown |
| `.editorconfig` & `.prettier*` | Enforce whitespace/formatting standards for agents | INI / JSON |
| `LICENSE` | Open source license text | Plain text |

## 2. `/docs` — Structured Textual References

| Sub-folder | Key Files to Generate | Why They Matter for AI |
|------------|----------------------|----------------------|
| `requirements/` | `user-stories.md`, `use-cases.md`, `acceptance-criteria.md` | Provides unambiguous "what & why" specifications that AI agents need |
| `api-specs/` | `openapi.yaml` (REST), `tools.mcp.json` (Model Context Protocol) | Exposes every external "tool" call in machine-readable format |
| `context/` | `glossary.md`, `style-guide.md`, `decision-log.md` | Keeps tacit knowledge explicit → reduces hallucinations |
| `examples/` | `sample-test.py`, `sample-service.py` | AI learns fastest from curated examples |

## 3. `/diagrams` — Visual, Machine-Readable Blueprints

| Sub-folder | Seed Files (Text-Based Diagrams) | Recommended Syntax |
|------------|----------------------------------|-------------------|
| `architecture/` | `system-c4.puml`, `infra.mmd` | PlantUML / Mermaid (C4 levels 1-4) |
| `uml/` | `domain-model.puml` (Class), `checkout-sequence.puml` (Sequence) | PlantUML |
| `flowcharts/` | `order-lifecycle.mmd`, `error-handling.mmd` | Mermaid flowcharts |
| `ui-mockups/` | `dashboard-mobile.png`, `dashboard-desktop.png`, `dashboard.figma.json` | Images + design-to-code export |
| `data-models/` | `er-diagram.puml`, `schema.prisma` (or SQL) | PlantUML ER |

> **Tip:** Commit the `.puml`/`.mmd` source files—Cursor can render PNGs later.

## 4. `/semantic` — Knowledge Layer

| Asset | File Name | Format |
|-------|-----------|--------|
| Domain ontology | `fabrication-ontology.ttl` | RDF / Turtle |
| Project knowledge graph snapshot | `kg.graphml` | GraphML / JSON-LD |
| Semantic annotations map | `annotations.yml` | YAML linking requirements ↔ UML ↔ tests |

These components deliver the "shared vocabulary" and rich context through ontologies, knowledge graphs, and semantic metadata.

## 5. `/tests` & `/ci` — Automation Hooks

Generate minimal templates to enable Cursor to wire tests and pipelines from day one:

**Test Files:**
- `/tests/__init__.py`
- `/tests/test_placeholder.py`

**CI/CD:**
- `/ci/github-actions.yml` (or `azure-pipelines.yml`)

## 6. Optional Developer Experience Folders

Create these folders empty initially; the agent will populate them as needed:

- `/scripts/` – Helper CLI tools
- `/migrations/` – Database schema evolution
- `/datasets/` – Sample CSV/JSON for fixtures  
- `/notebooks/` – Exploratory Jupyter work