import os
import zipfile
import tempfile
import logging
from typing import Optional, Tuple

logger = logging.getLogger("AutoDevAI.ZipService")

class ZipService:
    """
    Packages the generated project into a clean, distributable ZIP archive
    excluding development runtime caches, virtual environments, and node_modules.
    """

    EXCLUDED_PATTERNS = [
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        ".pytest_cache",
        "dist",
        "build",
        ".DS_Store"
    ]

    def create_project_zip(self, project_path: str, project_slug: str) -> Tuple[str, str, int]:
        """
        Creates a zip archive of the given project directory.
        Returns: (zip_file_path, filename, file_size_bytes)
        """
        logger.info(f"Creating ZIP archive for project: {project_slug} from {project_path}")

        if not os.path.isdir(project_path):
            raise FileNotFoundError(f"Project directory not found: {project_path}")

        temp_dir = tempfile.gettempdir()
        zip_filename = f"{project_slug}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(project_path):
                # Filter out excluded directories in-place
                dirs[:] = [d for d in dirs if not any(ex in d for ex in self.EXCLUDED_PATTERNS)]

                for file in files:
                    if any(file.endswith(ex) for ex in [".pyc", ".pyo", ".pyd"]):
                        continue
                    if file in [".DS_Store", "Thumbs.db"]:
                        continue

                    full_file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_file_path, project_path)

                    # Place files under the project slug folder in the zip
                    arcname = os.path.join(project_slug, rel_path)
                    zf.write(full_file_path, arcname)

        size_bytes = os.path.getsize(zip_path)
        logger.info(f"Created ZIP archive {zip_filename} ({size_bytes} bytes)")
        return zip_path, zip_filename, size_bytes

zip_service = ZipService()
