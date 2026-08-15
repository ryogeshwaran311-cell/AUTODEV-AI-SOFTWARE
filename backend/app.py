import os
import io
import sys
import json
import logging
import threading
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Setup logging - use file handler to avoid Windows stderr issues in background threads
_log_file = os.path.join(os.path.dirname(__file__), "..", "autodevai.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AutoDevAI] %(message)s",
    handlers=[
        logging.FileHandler(os.path.abspath(_log_file), encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("AutoDevAI.Backend")

from backend.database import db
from backend.models import Project, GenerationRun, AgentLog, DeploymentRecord
from backend.services.gemini_service import gemini_service
from backend.services.requirement_agent import requirement_agent
from backend.services.planning_agent import planning_agent
from backend.services.coding_agent import coding_agent
from backend.services.project_generator import project_generator
from backend.services.testing_agent import testing_agent
from backend.services.repair_agent import repair_agent
from backend.services.documentation_agent import documentation_agent
from backend.services.validator import final_validator
from backend.services.preview_service import preview_service
from backend.services.deployment_service import deployment_service
from backend.services.zip_service import zip_service

def create_app():
    app = Flask(__name__)

    # Enable full CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # SQLite internal database
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, "autodevai.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('AUTODEVAI_DATABASE_URI', f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from sqlalchemy.pool import NullPool
    # Allow background threads to safely interact with SQLite on Windows
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"check_same_thread": False, "timeout": 30},
        "poolclass": NullPool,
    }

    db.init_app(app)

    with app.app_context():
        db.create_all()
        with db.engine.connect() as conn:
            conn.execute(db.text("PRAGMA journal_mode=DELETE"))
            conn.execute(db.text("PRAGMA busy_timeout=30000"))
            conn.commit()
        logger.info("AutoDevAI SQLite metadata database initialized.")

    # ------------------ HEALTH & CONFIG ENDPOINTS ------------------

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            "status": "healthy",
            "app": "AutoDevAI Platform",
            "gemini_configured": gemini_service.is_configured(),
            "active_model": gemini_service.model_name,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    @app.route('/api/config', methods=['GET', 'POST'])
    def handle_config():
        if request.method == 'POST':
            data = request.get_json() or {}
            new_key = data.get('gemini_api_key')
            new_model = data.get('gemini_model')
            if new_key:
                gemini_service.set_api_key(new_key)
            if new_model:
                gemini_service.model_name = new_model
            return jsonify({
                "success": True,
                "gemini_configured": gemini_service.is_configured(),
                "gemini_model": gemini_service.model_name
            }), 200

        return jsonify({
            "gemini_configured": gemini_service.is_configured(),
            "gemini_model": gemini_service.model_name,
            "fallback_models": gemini_service.fallback_models
        }), 200

    # ------------------ PROJECT GENERATION ENDPOINTS ------------------

    @app.route('/api/projects', methods=['GET'])
    def list_projects():
        projects = Project.query.order_by(Project.id.desc()).all()
        return jsonify({
            "success": True,
            "projects": [p.to_dict() for p in projects]
        }), 200

    @app.route('/api/projects/<int:project_id>', methods=['GET'])
    def get_project_details(project_id):
        project = Project.query.get_or_404(project_id)
        data = project.to_dict()
        
        # Add list of files if path exists
        file_tree = []
        if project.project_path and os.path.isdir(project.project_path):
            for root, _, files in os.walk(project.project_path):
                if any(ex in root for ex in ["node_modules", ".venv", "__pycache__", ".git"]):
                    continue
                for f in files:
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, project.project_path).replace("\\", "/")
                    file_tree.append(rel)
        data["files"] = sorted(file_tree)
        return jsonify({"success": True, "project": data}), 200

    @app.route('/api/projects/<int:project_id>/status', methods=['GET'])
    def get_project_status(project_id):
        project = Project.query.get_or_404(project_id)
        logs = AgentLog.query.filter_by(project_id=project_id).order_by(AgentLog.id.asc()).all()
        return jsonify({
            "success": True,
            "project_id": project.id,
            "status": project.status,
            "current_stage": project.current_stage,
            "progress_pct": project.progress_pct,
            "preview_url": project.preview_url,
            "logs": [l.to_dict() for l in logs]
        }), 200

    @app.route('/api/projects/generate', methods=['POST'])
    def generate_project():
        data = request.get_json() or {}
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return jsonify({"success": False, "error": "Software project prompt is required"}), 400

        # Create temporary project record in SQLite
        temp_name = "Generating Application..."
        temp_slug = f"project-{int(datetime.utcnow().timestamp())}"
        project = Project(
            name=temp_name,
            slug=temp_slug,
            prompt=prompt,
            status='RUNNING',
            current_stage='requirement',
            progress_pct=5
        )
        db.session.add(project)
        db.session.commit()

        # Log initial event
        init_log = AgentLog(
            project_id=project.id,
            stage='requirement',
            level='INFO',
            message=f"Received project idea: '{prompt[:70]}...'"
        )
        db.session.add(init_log)
        db.session.commit()

        # Launch pipeline in background thread
        thread = threading.Thread(
            target=_run_autonomous_pipeline,
            args=(app, project.id, prompt)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            "success": True,
            "project_id": project.id,
            "slug": project.slug,
            "status": "RUNNING",
            "message": "Autonomous multi-agent engineering pipeline initiated."
        }), 202

    # ------------------ PREVIEW & PROCESS MANAGEMENT ------------------

    @app.route('/api/projects/<int:project_id>/preview/start', methods=['POST'])
    def start_preview(project_id):
        project = Project.query.get_or_404(project_id)
        if not project.project_path or not os.path.isdir(project.project_path):
            return jsonify({"success": False, "error": "Project workspace path is invalid"}), 400

        result = preview_service.start_preview(project.id, project.project_path)
        if result.get("success"):
            project.preview_url = result.get("preview_url")
            project.frontend_port = result.get("frontend_port")
            project.backend_port = result.get("backend_port")
            db.session.commit()

        return jsonify(result), 200

    @app.route('/api/projects/<int:project_id>/preview/stop', methods=['POST'])
    def stop_preview(project_id):
        result = preview_service.stop_preview(project_id)
        return jsonify(result), 200

    @app.route('/api/projects/<int:project_id>/preview/status', methods=['GET'])
    def preview_status(project_id):
        status_info = preview_service.get_status(project_id)
        return jsonify({"success": True, "preview": status_info}), 200

    # ------------------ ZIP & DOWNLOAD ENDPOINTS ------------------

    @app.route('/api/projects/<int:project_id>/download', methods=['GET'])
    def download_project_zip(project_id):
        project = Project.query.get_or_404(project_id)
        if not project.project_path or not os.path.isdir(project.project_path):
            return jsonify({"success": False, "error": "Project workspace not available for download"}), 404

        try:
            zip_path, filename, size_bytes = zip_service.create_project_zip(project.project_path, project.slug)
            return send_file(
                zip_path,
                mimetype="application/zip",
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            logger.error(f"ZIP creation error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ------------------ DEPLOYMENT ENDPOINTS ------------------

    @app.route('/api/projects/<int:project_id>/deploy', methods=['POST'])
    def deploy_project(project_id):
        project = Project.query.get_or_404(project_id)
        data = request.get_json() or {}
        target = data.get("target", "vercel").lower()
        credentials = data.get("credentials", {})

        result = deployment_service.deploy(project.project_path, target=target, credentials=credentials)

        # Store deployment record
        dep_record = DeploymentRecord(
            project_id=project.id,
            target=target,
            status=result.get("status", "FAILED"),
            url=result.get("url"),
            logs=json.dumps(result)
        )
        db.session.add(dep_record)
        db.session.commit()

        return jsonify(result), 200

    # ------------------ CODE VIEWER ENDPOINT ------------------

    @app.route('/api/projects/<int:project_id>/files/<path:file_path>', methods=['GET'])
    def get_project_file_content(project_id, file_path):
        project = Project.query.get_or_404(project_id)
        if not project.project_path:
            return jsonify({"error": "Project workspace path not found"}), 404

        full_path = os.path.abspath(os.path.join(project.project_path, file_path))
        if not full_path.startswith(os.path.abspath(project.project_path)):
            return jsonify({"error": "Unauthorized file access"}), 403

        if not os.path.isfile(full_path):
            return jsonify({"error": "File not found"}), 404

        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return jsonify({"success": True, "file_path": file_path, "content": content}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ------------------ UNIFIED FRONTEND STATIC SERVING ------------------

    frontend_dist = os.path.abspath(os.path.join(PROJECT_ROOT, "frontend", "dist"))

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        # Never intercept API routes
        if path.startswith("api/") or path == "api":
            return jsonify({"error": "Endpoint not found"}), 404

        file_path = os.path.join(frontend_dist, path)
        if path and os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(frontend_dist, path)

        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(frontend_dist, "index.html")

        return jsonify({
            "status": "AutoDevAI Platform Backend Running",
            "message": "Frontend static build not found. Run 'npm run build' inside frontend directory."
        }), 200

    return app

_pipeline_db_lock = threading.Lock()

def _run_autonomous_pipeline(flask_app, project_id: int, prompt: str):
    """
    Executes the sequential 8-stage multi-agent pipeline in background thread.
    """
    debug_log_path = os.path.join(PROJECT_ROOT, "pipeline_error.log")

    def _write_debug(msg):
        try:
            with open(debug_log_path, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except Exception:
            pass

    try:
      with flask_app.app_context():
        try:
            project = db.session.get(Project, project_id)
        except Exception as e:
            _write_debug(f"[OUTER] failed to load project #{project_id}: {e}\n{traceback.format_exc()}")
            logger.error(f"Pipeline: failed to load project #{project_id}: {e}")
            return
        if not project:
            _write_debug(f"[OUTER] project #{project_id} not found")
            logger.error(f"Pipeline: project #{project_id} not found in database.")
            return

        def log_event(stage: str, level: str, message: str, details=None):
            try:
                logger.info(f"[{stage.upper()}] [{level}] {message}")
            except Exception:
                pass
            with _pipeline_db_lock:
                try:
                    entry = AgentLog(
                        project_id=project_id,
                        stage=stage,
                        level=level,
                        message=message,
                        details=details
                    )
                    db.session.add(entry)
                    db.session.commit()
                except Exception as log_err:
                    logger.warning(f"log_event db commit failed: {log_err}")
                    db.session.rollback()

        def save_project():
            """Thread-safe project save."""
            with _pipeline_db_lock:
                try:
                    db.session.commit()
                except Exception as save_err:
                    logger.warning(f"save_project db commit failed: {save_err}")
                    db.session.rollback()

        try:
            # Stage 1: Requirement Agent
            project.current_stage = "requirement"
            project.progress_pct = 12
            save_project()
            log_event("requirement", "INFO", "Requirement Agent extracting user roles, CRUD entities, and API specifications...")

            req_spec = requirement_agent.analyze(prompt)
            project.name = req_spec.get("project_name", "Application")
            base_slug = req_spec.get("project_slug", f"app-{project_id}")
            with _pipeline_db_lock:
                existing_slug = Project.query.filter(Project.slug == base_slug, Project.id != project_id).first()
            project.slug = f"{base_slug}-{project_id}" if existing_slug else base_slug
            project.description = req_spec.get("project_description", "")
            project.requirements_spec = req_spec
            save_project()
            log_event("requirement", "SUCCESS", f"Extracted specification for '{project.name}' with {len(req_spec.get('features', []))} features.", req_spec)

            # Stage 2: Planning Agent
            project.current_stage = "planning"
            project.progress_pct = 28
            save_project()
            log_event("planning", "INFO", "Planning Agent designing database schema, component layout, and REST API architecture...")

            plan_spec = planning_agent.plan(req_spec)
            project.plan_spec = plan_spec
            save_project()
            log_event("planning", "SUCCESS", f"Architected {len(plan_spec.get('database_models', []))} database models & {len(plan_spec.get('api_endpoints', []))} REST endpoints.", plan_spec)

            # Stage 3: Coding Agent
            project.current_stage = "coding"
            project.progress_pct = 45
            save_project()
            log_event("coding", "INFO", "Coding Agent synthesizing complete full-stack source code (Flask + SQLite + React + Vite)...")

            files_dict = coding_agent.generate_project_files(req_spec, plan_spec)
            log_event("coding", "SUCCESS", f"Generated {len(files_dict)} complete production-ready source files with zero placeholders.")

            # Stage 4: Database & Workspace Creation
            project.current_stage = "database"
            project.progress_pct = 60
            save_project()
            log_event("database", "INFO", "Creating isolated project workspace and initializing SQLite schema models...")

            ws_info = project_generator.create_project_workspace(
                project_slug=project.slug,
                files=files_dict,
                metadata={"name": project.name, "prompt": prompt}
            )
            project.project_path = ws_info["project_path"]
            save_project()
            log_event("database", "SUCCESS", f"Workspace established at {ws_info['project_path']} ({ws_info['files_written']} files).")

            # Stage 5: Testing Agent
            project.current_stage = "testing"
            project.progress_pct = 75
            save_project()
            log_event("testing", "INFO", "Testing Agent executing static QA, AST syntax verification, and dependency checks...")

            test_results = testing_agent.run_tests(project.project_path)

            # Stage 6: Repair Agent (if needed)
            if not test_results.get("passed", False):
                project.current_stage = "repair"
                save_project()
                log_event("repair", "WARNING", f"Test QA flagged {len(test_results.get('errors', []))} issues. Repair Agent triggering auto-remediation...", test_results)

                repair_res = repair_agent.repair(project.project_path, test_results)
                log_event("repair", "SUCCESS" if repair_res.get("repaired") else "WARNING", f"Repair completed in {repair_res.get('attempts')} attempts: {', '.join(repair_res.get('actions_taken', ['No changes']))}")
                test_results = repair_res.get("final_test_results", test_results)
            else:
                log_event("testing", "SUCCESS", f"Automated QA passed 100% ({test_results.get('checks_passed')}/{test_results.get('checks_run')} checks).")

            # Stage 7: Documentation Agent
            project.current_stage = "documentation"
            project.progress_pct = 88
            save_project()
            log_event("documentation", "INFO", "Documentation Agent generating comprehensive README.md...")

            readme_content = documentation_agent.generate_readme(project.project_path, req_spec, plan_spec)  # noqa: F841
            log_event("documentation", "SUCCESS", "Generated comprehensive README.md with setup, API docs, and deployment guides.")

            # Stage 8: Final Validation Checklist
            project.current_stage = "validation"
            project.progress_pct = 95
            save_project()
            log_event("validation", "INFO", "Final Validator executing 15-point deployment readiness checklist...")

            validation_res = final_validator.validate(project.project_path)
            project.validation_report = validation_res

            if validation_res.get("is_valid"):
                project.status = "READY"
                project.current_stage = "completed"
                project.progress_pct = 100
                save_project()
                log_event("validation", "SUCCESS", f"Final Validation Passed: {validation_res.get('passed_checks')}/{validation_res.get('total_checks')} checks verified. Status: READY.", validation_res)

                # Automatically spin up isolated live full-stack preview (bound to 0.0.0.0)
                try:
                    log_event("preview", "INFO", "Spinning up live full-stack preview environment (Host 0.0.0.0)...")
                    prev_res = preview_service.start_preview(project.id, project.project_path)
                    if prev_res.get("success"):
                        project.preview_url = prev_res.get("preview_url")
                        project.frontend_port = prev_res.get("frontend_port")
                        project.backend_port = prev_res.get("backend_port")
                        save_project()
                        log_event("preview", "SUCCESS", f"Live Preview active at {project.preview_url} (Backend Port: {project.backend_port}, Frontend Port: {project.frontend_port}).")
                    else:
                        log_event("preview", "WARNING", f"Preview startup notice: {prev_res.get('error')}")
                except Exception as p_err:
                    logger.warning(f"Preview auto-start note: {p_err}")
            else:
                project.status = "REPAIR_REQUIRED"
                project.current_stage = "validation_failed"
                save_project()
                log_event("validation", "ERROR", f"Final Validation failed with score {validation_res.get('score_pct')}%.", validation_res)

        except Exception as e:
            tb = traceback.format_exc()
            # Write full traceback to a debug file (visible even in background threads)
            try:
                import pathlib
                _dbg = pathlib.Path.home() / "autodevai_pipeline_error.log"
                with open(str(_dbg), "a", encoding="utf-8") as f:
                    f.write(f"\n=== Pipeline Error for project #{project_id} ===\n")
                    f.write(f"Stage: {project.current_stage}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"Traceback:\n{tb}\n")
            except Exception:
                pass
            logger.error(f"PIPELINE CRITICAL ERROR for project #{project_id}:\n{tb}")
            with _pipeline_db_lock:
                try:
                    db.session.rollback()
                    failed_proj = db.session.get(Project, project_id)
                    if failed_proj:
                        failed_proj.status = "FAILED"
                        failed_proj.current_stage = "failed"
                        db.session.commit()
                except Exception as cleanup_err:
                    logger.error(f"Pipeline cleanup error: {cleanup_err}")
                    db.session.rollback()
            log_event("pipeline", "ERROR", f"Pipeline failed at stage '{project.current_stage}': {str(e)[:300]}")

    except Exception as outer_e:
        _write_debug(f"\n=== OUTER UNCAUGHT EXCEPTION for project #{project_id} ===\n"
                     f"Error: {str(outer_e)}\nTraceback:\n{traceback.format_exc()}")

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    logger.info(f"AutoDevAI Platform Backend starting on http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)

