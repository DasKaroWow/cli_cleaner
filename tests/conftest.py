from pathlib import Path

import pytest
from typer import Typer


@pytest.fixture()
def chdir_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """cd в пустую временную директорию проекта."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _touch(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("x", encoding="utf-8")
    return p


@pytest.fixture()
def sample_tree(chdir_tmp: Path) -> dict[str, Path]:
    """
    ├─ pkg/__pycache__/a.pyc
    ├─ pkg/module.py
    ├─ build/artifact.bin
    ├─ .pytest_cache/...
    ├─ notes.temp.txt
    ├─ keep/.venv/__pycache__/ignored.pyc
    └─ stray.log
    """
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
        "venv_pycache": root / "keep" / ".venv" / "__pycache__" / "ignored.pyc",
    }


@pytest.fixture()
def cli_app() -> Typer:
    try:
        from cli_cleaner.__main__ import app  # type: ignore

        return app
    except Exception as error:
        pytest.skip(f"Unable to import Typer app: {error}")
