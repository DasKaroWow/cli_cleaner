from pathlib import Path

import pytest
from typer import Typer

from cli_cleaner.cli import app


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    return path


@pytest.fixture
def cli_app() -> Typer:
    return app


@pytest.fixture
def chdir_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def sample_tree(chdir_tmp: Path) -> dict[str, Path]:
    root = chdir_tmp
    _touch(root / "pkg" / "__pycache__" / "a.pyc")
    _touch(root / ".pytest_cache" / "state.json")
    _touch(root / "build" / "artifact.bin")
    _touch(root / "notes.temp.txt")
    _touch(root / "pkg" / "module.py")
    _touch(root / "stray.log")
    _touch(root / "keep" / ".venv" / "__pycache__" / "ignored.pyc")

    return {
        "pycache_file": root / "pkg" / "__pycache__" / "a.pyc",
        "pytest_cache": root / ".pytest_cache",
        "build_artifact": root / "build" / "artifact.bin",
        "temp_file": root / "notes.temp.txt",
        "regular_file": root / "pkg" / "module.py",
        "stray_log": root / "stray.log",
        "venv_pycache": root / "keep" / ".venv" / "__pycache__" / "ignored.pyc",
    }
