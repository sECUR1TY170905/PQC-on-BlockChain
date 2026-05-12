"""Shim that exposes shared helpers to the Kyber scripts."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))

# Trỏ ngược ra 3 cấp thư mục để về gốc project, rồi trỏ tới file shared chung
SHARED_COMMON = os.path.abspath(os.path.join(current_dir, "../../../shared/python/common.py"))
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
# Look for 'shared' folder to find SUITE_ROOT
_current = PROJECT_ROOT
SUITE_ROOT = PROJECT_ROOT # Default fallback
for _ in range(5):
    if (_current / "shared").exists():
        SUITE_ROOT = _current
        break
    _current = _current.parent

os.environ.setdefault("PQC_PROJECT_ROOT", str(PROJECT_ROOT))
os.environ.setdefault("PQC_SUITE_ROOT", str(SUITE_ROOT))

spec = importlib.util.spec_from_file_location("_suite_shared_common", SHARED_COMMON)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

for name in dir(module):
    if not name.startswith("_"):
        globals()[name] = getattr(module, name)
