# AutoDevAI System Architecture

## Overview
AutoDevAI operates two isolated architectural planes:
1. **AutoDevAI Platform Plane**: The hosting platform managing agent coordination, SQLite metadata storage, dynamic process supervision, and dashboard UI.
2. **Generated Application Plane**: Completely isolated, standalone full-stack applications residing inside `generated_projects/<slug>/`.

```
┌─────────────────────────────────────────────────────────────┐
│                      AutoDevAI Dashboard                    │
│                (React 18 + Vite - Port 5173)                │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼──────────────────────────────┐
│                    AutoDevAI Backend Core                   │
│                 (Flask + SQLite - Port 5000)                │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
┌──────▼────────┐       ┌──────▼────────┐       ┌──────▼────────┐
│  Multi-Agent  │       │    Process    │       │    Cloud      │
│   Pipeline    │       │  Supervisor   │       │  Deployer &   │
│ (8-Stages)    │       │  & Previewer  │       │  ZIP Exporter │
└──────┬────────┘       └──────┬────────┘       └──────┬────────┘
       │                       │                       │
┌──────▼───────────────────────▼───────────────────────▼──────┐
│                     generated_projects/                     │
│  ├── student-management-system/ (Backend: 5001 / Frontend: 5174)│
│  ├── ecommerce-micro-store/     (Backend: 5002 / Frontend: 5175)│
│  └── task-kanban-board/         (Backend: 5003 / Frontend: 5176)│
└─────────────────────────────────────────────────────────────┘
```

## Agent Pipeline Flow
1. **Requirement Agent**: Deconstructs user intent into structured JSON.
2. **Planning Agent**: Designs schema, models, REST API specifications, and component hierarchy.
3. **Coding Agent**: Generates complete source files without placeholders.
4. **Database & Generator**: Creates directory workspace and initializes SQLite schema.
5. **Testing Agent**: Runs AST syntax, dependency validation, and quality checks.
6. **Repair Agent**: Performs self-healing remediation (max 3 cycles).
7. **Documentation Agent**: Generates complete project `README.md`.
8. **Final Validator**: 15-point checklist certification to mark `READY`.
