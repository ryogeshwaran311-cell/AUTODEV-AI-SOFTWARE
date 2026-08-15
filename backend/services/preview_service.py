import os
import sys
import time
import socket
import logging
import subprocess
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger("AutoDevAI.PreviewService")

class PreviewService:
    """
    Manages dynamic port allocation, isolated background process execution,
    and HTTP health check probing for generated projects.
    """

    def __init__(self):
        # In-memory process registry: {project_id: {"backend_proc": ..., "frontend_proc": ..., "backend_port": ..., "frontend_port": ..., "status": ...}}
        self.active_processes: Dict[int, Dict[str, Any]] = {}

    def find_free_port(self, starting_from: int = 5001, max_search: int = 100) -> int:
        """Finds an available TCP port starting from a specified number."""
        for port in range(starting_from, starting_from + max_search):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                res = s.connect_ex(('127.0.0.1', port))
                if res != 0:
                    # Port is free
                    return port
        raise RuntimeError(f"No free TCP ports available in range {starting_from}-{starting_from+max_search}")

    def is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0

    def start_preview(self, project_id: int, project_path: str) -> Dict[str, Any]:
        """
        Spawns backend & frontend processes for the project and monitors health.
        """
        logger.info(f"Initiating preview server for project #{project_id} at {project_path}")

        # If already running, return current status
        if project_id in self.active_processes:
            curr = self.active_processes[project_id]
            if curr.get("status") == "RUNNING":
                return {
                    "success": True,
                    "status": "RUNNING",
                    "preview_url": curr.get("preview_url"),
                    "frontend_port": curr.get("frontend_port"),
                    "backend_port": curr.get("backend_port"),
                    "message": "Preview server is already active."
                }
            else:
                self.stop_preview(project_id)

        # 1. Allocate dedicated ports
        backend_port = self.find_free_port(starting_from=5010)
        frontend_port = self.find_free_port(starting_from=max(5200, backend_port + 1))

        backend_dir = os.path.join(project_path, "backend")
        frontend_dir = os.path.join(project_path, "frontend")

        backend_env = os.environ.copy()
        backend_env["PORT"] = str(backend_port)
        backend_env["HOST"] = "0.0.0.0"

        # 2. Start Backend Subprocess (binds to 0.0.0.0 and port)
        backend_cmd = [sys.executable, "app.py"]
        logger.info(f"Starting backend on port {backend_port} with cmd: {' '.join(backend_cmd)}")
        
        try:
            backend_proc = subprocess.Popen(
                backend_cmd,
                cwd=backend_dir,
                env=backend_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
        except Exception as e:
            logger.error(f"Failed to start generated backend process: {e}")
            return {"success": False, "error": f"Failed to start backend: {e}"}

        # 3. Ensure Frontend node_modules is linked
        platform_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        platform_node_modules = os.path.join(platform_root, "frontend", "node_modules")
        fe_node_modules = os.path.join(frontend_dir, "node_modules")

        if os.path.isdir(platform_node_modules) and not os.path.exists(fe_node_modules):
            try:
                if sys.platform == "win32":
                    subprocess.run(f'cmd /c mklink /J "{fe_node_modules}" "{platform_node_modules}"', shell=True, capture_output=True)
                else:
                    os.symlink(platform_node_modules, fe_node_modules, target_is_directory=True)
                logger.info(f"Linked node_modules into {fe_node_modules}")
            except Exception as link_err:
                logger.warning(f"Could not link node_modules to {fe_node_modules}: {link_err}")

        # 4. Start Frontend Dev Server (bound to 0.0.0.0)
        local_vite_bin = os.path.join(platform_node_modules, "vite", "bin", "vite.js")

        frontend_env = os.environ.copy()
        frontend_env["NODE_PATH"] = platform_node_modules
        frontend_env["BACKEND_PORT"] = str(backend_port)
        frontend_env["PORT"] = str(frontend_port)
        frontend_env["HOST"] = "0.0.0.0"

        if os.path.isfile(local_vite_bin):
            vite_cmd = ["node", local_vite_bin, "--port", str(frontend_port), "--host", "0.0.0.0"]
        else:
            npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"
            vite_cmd = [npx_cmd, "--yes", "vite", "--port", str(frontend_port), "--host", "0.0.0.0"]

        logger.info(f"Starting frontend on port {frontend_port} with cmd: {' '.join(vite_cmd)}")

        try:
            frontend_proc = subprocess.Popen(
                vite_cmd,
                cwd=frontend_dir,
                env=frontend_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
        except Exception as e:
            logger.error(f"Failed to start generated frontend process: {e}")
            try:
                backend_proc.kill()
            except Exception:
                pass
            return {"success": False, "error": f"Failed to start frontend: {e}"}

        preview_url = f"http://127.0.0.1:{frontend_port}"

        # 5. Record process in registry
        proc_info = {
            "project_id": project_id,
            "project_path": project_path,
            "backend_proc": backend_proc,
            "frontend_proc": frontend_proc,
            "backend_port": backend_port,
            "frontend_port": frontend_port,
            "preview_url": preview_url,
            "status": "RUNNING",
            "started_at": time.time()
        }
        self.active_processes[project_id] = proc_info

        # 6. Brief health check poll (wait up to 5s for ports to bind)
        for _ in range(10):
            time.sleep(0.5)
            if self.is_port_in_use(frontend_port) and self.is_port_in_use(backend_port):
                break

        return {
            "success": True,
            "status": "RUNNING",
            "preview_url": preview_url,
            "frontend_port": frontend_port,
            "backend_port": backend_port,
            "backend_pid": backend_proc.pid,
            "frontend_pid": frontend_proc.pid,
            "message": f"Preview live at {preview_url}"
        }

    def stop_preview(self, project_id: int) -> Dict[str, Any]:
        """Terminates preview processes for a given project."""
        if project_id not in self.active_processes:
            return {"success": True, "message": "No active preview process found for this project."}

        proc_info = self.active_processes.pop(project_id)
        be_proc = proc_info.get("backend_proc")
        fe_proc = proc_info.get("frontend_proc")

        if be_proc:
            try:
                be_proc.terminate()
                be_proc.wait(timeout=1)
            except Exception:
                try: be_proc.kill()
                except Exception: pass

        if fe_proc:
            try:
                fe_proc.terminate()
                fe_proc.wait(timeout=1)
            except Exception:
                try: fe_proc.kill()
                except Exception: pass

        logger.info(f"Stopped preview processes for project #{project_id}")
        return {"success": True, "message": "Preview server stopped successfully."}

    def get_status(self, project_id: int) -> Dict[str, Any]:
        """Returns the current preview state and health for a project."""
        if project_id not in self.active_processes:
            return {
                "active": False,
                "status": "STOPPED",
                "preview_url": None
            }

        info = self.active_processes[project_id]
        fe_port = info.get("frontend_port")
        be_port = info.get("backend_port")

        fe_alive = self.is_port_in_use(fe_port)
        be_alive = self.is_port_in_use(be_port)

        return {
            "active": True,
            "status": "RUNNING" if fe_alive else "STARTING",
            "preview_url": info.get("preview_url"),
            "frontend_port": fe_port,
            "backend_port": be_port,
            "frontend_alive": fe_alive,
            "backend_alive": be_alive
        }

preview_service = PreviewService()
