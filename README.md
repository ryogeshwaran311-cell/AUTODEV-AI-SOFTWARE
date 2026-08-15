# AutoDevAI ⚡
### Autonomous Multi-Agent Software Engineering System powered by Google Gemini

AutoDevAI is an end-to-end full-stack autonomous software engineering platform. It transforms natural-language project descriptions into complete, fully functional, production-ready applications with zero manual setup from the user.

---

## 🌟 Key Highlights

- 🤖 **8-Stage Multi-Agent Pipeline**: Requirement Agent → Planning Agent → Coding Agent → Database Agent → Testing Agent → Repair Agent → Documentation Agent → Final Validator.
- ⚡ **Zero Placeholder Code**: Synthesizes 100% complete, working source files without any `TODO`, `FIXME`, or coming soon placeholders.
- 🛠️ **Real Process Supervisor & Live Preview**: Automatically spawns isolated development servers with dynamic port allocation and displays the live app in an embedded responsive iframe.
- 🔄 **Autonomous Self-Repair**: Bounded 3-attempt healing loop automatically fixes syntax errors, missing dependencies, or schema bugs.
- 📦 **One-Click Distributable ZIP**: Exports clean source code bundles excluding `node_modules` and virtual environments.
- 🚀 **Cloud Deployment Generator**: Generates validated manifests for Vercel (Frontend SPA) and Render (Python Backend).
- 🎨 **Obsidian Glassmorphic DevTools UI**: High-impact developer dashboard with real-time log streaming, pipeline stepper, and code explorer.

---

## 🏗️ Architecture: Two Isolated Planes

1. **AutoDevAI Platform Plane** (Hosting & Orchestration):
   - **Frontend**: React 18 + Vite (`http://localhost:5173`)
   - **Backend**: Python 3.12+ Flask with CORS & SQLite (`http://localhost:5000`)
   - **AI Core**: Centralized Google Gemini Service (`gemini-2.5-flash` / `gemini-1.5-flash`) with exponential backoff and rate-limit protection.

2. **Generated Application Plane** (`generated_projects/<slug>/`):
   - Standalone, fully isolated full-stack applications.
   - Dynamic port assignment (e.g. Frontend: 5174+, Backend: 5001+).
   - Local SQLite database persistence (`db.create_all()`).

---

## 📁 Repository Structure

```
AutoDevAI/
├── backend/
│   ├── app.py                     # Flask server with REST API & CORS
│   ├── database.py                # AutoDevAI SQLite database (SQLAlchemy)
│   ├── models.py                  # Project, GenerationRun, AgentLog models
│   ├── requirements.txt           # Python backend dependencies
│   │
│   └── services/
│       ├── gemini_service.py      # Gemini API client with backoff & fallbacks
│       ├── requirement_agent.py   # Extracts user roles, entities & APIs
│       ├── planning_agent.py      # Designs DB schemas, routes & components
│       ├── coding_agent.py        # Generates complete full-stack source code
│       ├── project_generator.py   # Path traversal-safe workspace writer
│       ├── testing_agent.py       # AST syntax & dependency QA checks
│       ├── repair_agent.py        # Automated error remediation loop
│       ├── documentation_agent.py # Synthesizes project README.md
│       ├── validator.py           # 15-point checklist validator
│       ├── preview_service.py     # Process supervisor & port allocator
│       ├── deployment_service.py  # Vercel & Render deployment manager
│       └── zip_service.py         # Clean project ZIP archiver
│
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── main.jsx               # React entrypoint
│   │   ├── App.jsx                # Main platform dashboard
│   │   ├── index.css              # Obsidian glassmorphic design system
│   │   │
│   │   └── components/
│   │       ├── ProjectInput.jsx   # Prompt input with presets
│   │       ├── AgentPipeline.jsx  # Stepper & real-time log terminal
│   │       ├── ActionToolbar.jsx  # Live Preview, Deploy, Download ZIP
│   │       ├── PreviewPanel.jsx   # Embedded iframe with device toggle
│   │       ├── DeployModal.jsx    # Vercel & Render cloud deployer
│   │       ├── CodeExplorer.jsx   # Source file inspection tree
│   │       ├── ProjectHistory.jsx # Past generated projects drawer
│   │       └── ApiKeyModal.jsx    # Dynamic Gemini API configuration
│   │
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── generated_projects/            # Storage for isolated user projects
├── tests/                         # Automated unit & API tests
│   ├── test_agents.py
│   └── test_api.py
├── prompts/
│   └── system_prompts.md
├── docs/
│   └── architecture.md
├── .env
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12 or higher
- Node.js 18+ and npm
- Optional: Google Gemini API Key (get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey))

### 1. Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 3. Configure Environment Variables
Edit `.env` in the root folder:
```env
PORT=5000
HOST=0.0.0.0
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*(Note: You can also configure or change the API key directly via the dashboard UI settings).*

---

## 🏃 Running AutoDevAI

### Option A: Unified Mode (Recommended - Single Port 5000)
Runs both the compiled React frontend UI and the Flask REST API on port `5000`:
```bash
# 1. Build frontend static bundle
cd frontend && npm run build && cd ..

# 2. Start unified server
python backend/app.py
```
Open **`http://localhost:5000`** in your browser.

### Option B: Development Mode (Hot-Reloading)
Runs Flask backend on port `5000` and Vite dev server on port `5173` with instant HMR:
```bash
# Terminal 1: Backend
python backend/app.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

---

## 🧪 Running Automated Tests

Run the full end-to-end multi-agent test suite:
```bash
python -m unittest discover tests
```

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/projects/generate` | Initiates autonomous multi-agent pipeline |
| `GET` | `/api/projects` | Lists all generated projects in SQLite database |
| `GET` | `/api/projects/<id>` | Retrieves project details and workspace file tree |
| `GET` | `/api/projects/<id>/status` | Polls current agent stage, progress %, and live logs |
| `POST` | `/api/projects/<id>/preview/start` | Spawns isolated development servers for preview |
| `POST` | `/api/projects/<id>/preview/stop` | Terminates active preview background servers |
| `GET` | `/api/projects/<id>/preview/status` | Returns preview health, active ports, and live URL |
| `POST` | `/api/projects/<id>/deploy` | Triggers deployment configuration workflow |
| `GET` | `/api/projects/<id>/download` | Downloads clean source code ZIP archive |
| `GET` | `/api/projects/<id>/files/<path>` | Inspects file content in generated project |
| `GET` | `/api/health` | Platform health check |
| `GET` / `POST` | `/api/config` | Retrieves and dynamically updates Gemini settings |

---

## 🛡️ Security & Windows Safety

- **Path Traversal Protection**: All generated file writes and reads strictly check path boundaries against `generated_projects/<slug>/`.
- **Windows UTF-8 Logging**: Backend standard output wraps stdout buffers with UTF-8 to prevent emoji or Unicode console crashes.
- **Port Conflict Safeguards**: Dynamic port scanner assigns unoccupied ports for each generated project.

---

## 📄 License
MIT License. Built for the Google DeepMind Antigravity Software Challenge.
