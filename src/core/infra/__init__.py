"""底層設施：路徑、JSON、SQLite、通知占位（集中在同一資料夾，減少 core 根目錄檔案數）。"""

from . import notifications
from .data_loader import load_user, load_vendor
from .db import (
    DB_PATH_STR,
    create_approval,
    get_connection_path,
    save_decision,
    save_transaction,
)
from .paths import DATA_DIR, PROJECT_ROOT

__all__ = [
    "DATA_DIR",
    "DB_PATH_STR",
    "PROJECT_ROOT",
    "create_approval",
    "get_connection_path",
    "load_user",
    "load_vendor",
    "notifications",
    "save_decision",
    "save_transaction",
]
