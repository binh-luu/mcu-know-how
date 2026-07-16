from __future__ import annotations

from pathlib import Path


def discover_source_files(src_dir: Path | str) -> list[str]:
    """Return a sorted list of source-like files under the source directory."""
    root = Path(src_dir)
    if not root.exists():
        return []

    files = [
        path.name
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in {".c", ".h", ".cpp", ".hpp"}
    ]
    return sorted(files)
