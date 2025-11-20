from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXECUTABLE = REPO_ROOT / "assets" / "quakelive" / "quakelive_steam.exe"
DEFAULT_CFG = REPO_ROOT / "assets" / "quakelive" / "baseq3" / "default.cfg"

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="Default.cfg bootstrap validation requires Windows executables"
)


@pytest.fixture(name="isolated_filesystem")
def fixture_isolated_filesystem(tmp_path: Path) -> tuple[Path, Path]:
    basepath = tmp_path / "basepath"
    homepath = tmp_path / "homepath"

    base_baseq3 = basepath / "baseq3"
    home_baseq3 = homepath / "baseq3"
    base_baseq3.mkdir(parents=True, exist_ok=True)
    home_baseq3.mkdir(parents=True, exist_ok=True)

    shutil.copy(DEFAULT_CFG, base_baseq3 / "default.cfg")

    return basepath, homepath


def test_default_cfg_bootstrap_avoids_fatal(isolated_filesystem: tuple[Path, Path]) -> None:
    basepath, homepath = isolated_filesystem

    if not EXECUTABLE.exists():
        pytest.skip(f"Quake Live executable missing: {EXECUTABLE}")

    command = [
        str(EXECUTABLE),
        "+set",
        "fs_basepath",
        str(basepath),
        "+set",
        "fs_homepath",
        str(homepath),
        "+set",
        "fs_game",
        "",
        "+set",
        "fs_cdpath",
        "",
        "+set",
        "fs_copyfiles",
        "0",
        "+set",
        "logFile",
        "2",
        "+set",
        "com_dedicated",
        "1",
        "+set",
        "s_initsound",
        "0",
        "+set",
        "com_skipRenderer",
        "1",
        "+quit",
    ]

    result = subprocess.run(
        command,
        cwd=EXECUTABLE.parent,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=os.environ.copy(),
    )

    log_path = homepath / "baseq3" / "qconsole.log"
    log_text = log_path.read_text(encoding="utf-8", errors="ignore") if log_path.exists() else ""
    combined_output = "\n".join(part for part in (result.stdout, result.stderr, log_text) if part)

    assert "Couldn't load default.cfg" not in combined_output
    assert result.returncode == 0, combined_output or "process returned non-zero exit status"
    assert combined_output, "No console output captured from filesystem bootstrap"
    assert "FS_Startup" in combined_output or "FS_InitFilesystem" in combined_output
