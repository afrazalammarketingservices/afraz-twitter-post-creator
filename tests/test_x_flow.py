import json
import subprocess
import sys
from pathlib import Path

import pytest

from samples import get

FLOW = Path(__file__).resolve().parents[1] / "automation" / "routine" / "x_flow.py"


@pytest.mark.parametrize("name", ["mon", "fri"])
def test_dry_run_stops_before_publish(name, tmp_path, temp_log):
    folder = tmp_path / f"2026-11-09_{name}-sample"
    folder.mkdir()
    (folder / "draft.json").write_text(json.dumps(get(name)), encoding="utf-8")
    p = subprocess.run([sys.executable, str(FLOW), str(folder / "draft.json"), "--dry-run"],
                       capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stdout + p.stderr
    out = json.loads(p.stdout)
    assert out["dry_run"] is True and out["published"] is False
    assert out["reply_text"] and out["parts"] == get(name)["parts"]
    assert not (folder / "publish_result.json").exists()
    if name == "fri":
        assert Path(out["image"]).exists()
        assert json.loads((folder / "thread.json").read_text(encoding="utf-8")) == out["parts"]
