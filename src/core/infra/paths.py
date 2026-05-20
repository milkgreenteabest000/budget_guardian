"""Repo 根目錄與 data/（layout：repo_root/src/core/infra/paths.py）。"""

from pathlib import Path

# .../src/core/infra → parent×3 = repo root
_INFRA_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _INFRA_DIR.parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
