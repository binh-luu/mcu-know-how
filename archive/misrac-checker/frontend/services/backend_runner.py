from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path
from typing import Any


class BackendRunner:
    """Small wrapper around backend CLI commands for the Streamlit UI."""

    def __init__(self, project_root: Path | str) -> None:
        self.project_root = Path(project_root).resolve()

    def run_scan(self, source_file: str, timeout: int = 600) -> dict[str, Any]:
        source_path = f"src/{source_file}"
        command = [sys.executable, "main.py", source_path]
        return self._run_command(command, timeout=timeout)

    def start_analysis(
        self,
        logs: list[str],
        result_holder: dict[str, Any],
        done_flag: list[bool],
        patch_dir: str,
        output_path: str = "results.json",
    ) -> None:
        """Start the analysis workflow in a background thread, appending to logs list."""
        command = [
            sys.executable,
            "-m",
            "backend.cli",
            "analyze",
            "--output",
            output_path,
            "--patch-dir",
            patch_dir,
        ]

        def _run():
            process = subprocess.Popen(
                command,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            all_output: list[str] = []
            try:
                for line in process.stdout:
                    all_output.append(line)
                    logs.append(line)
            except Exception:
                pass
            finally:
                process.wait()

            returncode = process.returncode
            full_text = "".join(all_output)
            result_holder.update(
                {
                    "command": " ".join(command),
                    "returncode": returncode,
                    "stdout": full_text,
                    "stderr": "",
                }
            )
            done_flag[0] = True

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def run_analysis(self, patch_dir: str, output_path: str = "results.json", timeout: int = 1800) -> dict[str, Any]:
        command = [
            sys.executable,
            "-m",
            "backend.cli",
            "analyze",
            "--output",
            output_path,
            "--patch-dir",
            patch_dir,
        ]
        result = self._run_command(command, timeout=timeout)
        result["patch_files"] = self.list_patch_files(Path(patch_dir))
        return result

    def list_patch_files(self, patch_dir: Path | str) -> list[Path]:
        patch_path = Path(patch_dir)
        if not patch_path.exists():
            return []
        return sorted([item for item in patch_path.glob("*.patch") if item.is_file()])

    def run_init(self, timeout: int = 300) -> dict[str, Any]:
        """Initialize vector store with Example Suite data."""
        command = [
            sys.executable,
            "-m",
            "backend.cli",
            "init",
        ]
        return self._run_command(command, timeout=timeout)

    def _run_command(self, command: list[str], timeout: int) -> dict[str, Any]:
        completed = subprocess.run(
            command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
