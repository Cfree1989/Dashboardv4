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
| `.editorconfig` | Enforce whitespace/formatting standards for agents | INI |
| `.prettierrc` | Code formatting rules and style enforcement | JSON |
| `LICENSE` | Open source license text | Plain text |

## 2. `/docs` — Structured Textual References

| Sub-folder | Key Files to Generate | Why They Matter for AI |
|------------|----------------------|----------------------|
| `requirements/` | `user-stories.md`, `use-cases.md`, `acceptance-criteria.md` | Provides unambiguous "what & why" specifications that AI agents need |
| `context/` | `glossary.md`, `style-guide.md`, `decision-log.md` | Keeps tacit knowledge explicit → reduces hallucinations |
| `examples/` | `sample-components.md` | AI learns fastest from curated examples and patterns |

## 3. `/diagrams` — Visual, Machine-Readable Blueprints

| Sub-folder | Seed Files (Text-Based Diagrams) | Recommended Syntax |
|------------|----------------------------------|-------------------|
| `architecture/` | `system-c4.puml`, `infra.mmd` | PlantUML / Mermaid (C4 levels 1-4) |
| `uml/` | `domain-model.puml` (Class), `checkout-sequence.puml` (Sequence) | PlantUML |
| `flowcharts/` | `order-lifecycle.mmd`, `error-handling.mmd` | Mermaid flowcharts |
| `ui-mockups/` | `dashboard-desktop.png`, `dashboard.figma.json` | Images + design-to-code export |
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

**Test Structure:**
- `/tests/` – Testing framework and test files organized by project structure

**CI/CD:**
- `/ci/github-actions.yml` – Continuous integration and deployment automation

## 6. Optional Developer Experience Folders

Create these folders empty initially; the agent will populate them as needed:

- `/scripts/` – Build helpers and CLI tools for development workflow

## 7. Complete Project Repository Architecture

```
project-repository/
├── README.md
├── project-info.md
├── CLAUDE.md (or CURSOR.md)
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── .editorconfig
├── .prettierrc
├── LICENSE
│
├── docs/
│   ├── requirements/
│   │   ├── user-stories.md
│   │   ├── use-cases.md
│   │   └── acceptance-criteria.md
│   ├── context/
│   │   ├── glossary.md
│   │   ├── style-guide.md
│   │   └── decision-log.md
│   └── examples/
│       └── sample-components.md
│
├── diagrams/
│   ├── architecture/
│   │   ├── system-c4.puml
│   │   └── infra.mmd
│   │
│   ├── uml/
│   │   ├── domain-model.puml
│   │   └── checkout-sequence.puml
│   │
│   ├── flowcharts/
│   │   ├── order-lifecycle.mmd
│   │   └── error-handling.mmd
│   │
│   ├── ui-mockups/
│   │   ├── dashboard-desktop.png
│   │   └── dashboard.figma.json
│   │
│   └── data-models/
│       ├── er-diagram.puml
│       └── schema.prisma
│
├── semantic/
│   ├── fabrication-ontology.ttl
│   ├── kg.graphml
│   └── annotations.yml
│
├── tests/
│   └── (testing structure)
│
├── ci/
│   └── github-actions.yml
│
└── scripts/
    └── (build helpers)
```

### Architecture Notes:

1. **Root Level Files**: Essential configuration and documentation files that AI agents reference first
2. **docs/**: Structured documentation organized by purpose (requirements, API specs, context, examples)
3. **diagrams/**: Visual representations in text-based formats that can be version-controlled and AI-readable
4. **semantic/**: Knowledge layer components for domain understanding and semantic relationships
5. **tests/ & ci/**: Automation infrastructure for quality assurance and deployment
6. **Optional Folders**: Developer experience folders that start empty and grow organically

This architecture optimizes for AI coding agent effectiveness by providing:
- **Machine-readable formats** (YAML, JSON, PlantUML, Mermaid)
- **Clear separation of concerns** (documentation, diagrams, tests, etc.)
- **Semantic context** (ontologies, glossaries, decision logs)
- **Automation hooks** (CI/CD, testing frameworks)
- **Extensibility** (optional folders for future needs)