import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("AutoDevAI.ProjectGenerator")

class ProjectGenerator:
    """
    Manages safe creation of isolated project workspaces under generated_projects/.
    Enforces path traversal safety and metadata tracking.
    """

    def __init__(self, base_dir: str = "generated_projects"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def sanitize_slug(self, name: str) -> str:
        """Sanitizes project name to safe alphanumeric slug."""
        clean = re.sub(r'[^a-zA-Z0-9_-]', '-', name.strip().lower())
        clean = re.sub(r'-+', '-', clean).strip('-')
        return clean or "generated-app"

    def create_project_workspace(
        self,
        project_slug: str,
        files: Dict[str, str],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates directory structure and writes all source files.
        Guarantees path traversal prevention.
        """
        safe_slug = self.sanitize_slug(project_slug)
        project_path = os.path.abspath(os.path.join(self.base_dir, safe_slug))

        # Security check: project_path must strictly reside within self.base_dir
        if not project_path.startswith(self.base_dir):
            raise ValueError(f"Security Alert: Path traversal attempt detected: {project_path}")

        os.makedirs(project_path, exist_ok=True)
        logger.info(f"Writing project workspace at: {project_path}")

        written_files: List[str] = []

        for rel_path, content in files.items():
            # Clean rel_path
            clean_rel = os.path.normpath(rel_path).lstrip(os.path.sep).lstrip("/").lstrip("\\")
            full_file_path = os.path.abspath(os.path.join(project_path, clean_rel))

            # Security verification
            if not full_file_path.startswith(project_path):
                logger.warning(f"Skipping potentially unsafe relative file path: {rel_path}")
                continue

            # Ensure parent directory exists
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

            # Write file with UTF-8 encoding
            with open(full_file_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(content)

            written_files.append(clean_rel)

        # Auto-link node_modules into project frontend
        frontend_dir = os.path.join(project_path, "frontend")
        if os.path.isdir(frontend_dir):
            platform_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            platform_node_modules = os.path.join(platform_root, "frontend", "node_modules")
            fe_node_modules = os.path.join(frontend_dir, "node_modules")
            if os.path.isdir(platform_node_modules) and not os.path.exists(fe_node_modules):
                try:
                    import sys, subprocess
                    if sys.platform == "win32":
                        subprocess.run(f'cmd /c mklink /J "{fe_node_modules}" "{platform_node_modules}"', shell=True, capture_output=True)
                    else:
                        os.symlink(platform_node_modules, fe_node_modules, target_is_directory=True)
                except Exception as link_err:
                    logger.warning(f"Could not link node_modules: {link_err}")

        # Write metadata.json
        meta_payload = {
            "slug": safe_slug,
            "project_name": metadata.get("name", safe_slug),
            "created_at": datetime.utcnow().isoformat(),
            "file_count": len(written_files),
            "files": written_files,
            "metadata": metadata
        }
        with open(os.path.join(project_path, "metadata.json"), "w", encoding="utf-8") as mf:
            json.dump(meta_payload, mf, indent=2)

        return {
            "project_path": project_path,
            "slug": safe_slug,
            "files_written": len(written_files),
            "files_list": written_files
        }

project_generator = ProjectGenerator()
