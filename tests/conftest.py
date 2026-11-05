import hashlib
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "routine"))
REAL_LOG = ROOT / "memory" / "x-post-log.md"
_REAL_HASH = hashlib.sha256(REAL_LOG.read_bytes()).hexdigest()


@pytest.fixture(autouse=True)
def temp_log(tmp_path, monkeypatch):
    """Every test reads and writes a temp copy of the log, never the real one."""
    p = tmp_path / "x-post-log.md"
    shutil.copy(REAL_LOG, p)
    monkeypatch.setenv("X_LOG_PATH", str(p))
    return p


def pytest_sessionfinish(session, exitstatus):
    now = hashlib.sha256(REAL_LOG.read_bytes()).hexdigest()
    assert now == _REAL_HASH, "a test changed memory/x-post-log.md"
