from pathlib import Path
import re

from click.testing import Result
from typer import Typer
from typer.testing import CliRunner


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def run_cli(app: Typer, *args: str) -> Result:
    return CliRunner().invoke(app, list(args))


def test_root_help(cli_app: Typer) -> None:
    result = run_cli(cli_app, "--help")
    output = strip_ansi(result.output)

    assert result.exit_code == 0
    assert "clean" in output
    assert "presets" in output


def test_clean_help(cli_app: Typer) -> None:
    result = run_cli(cli_app, "clean", "--help")
    output = strip_ansi(result.output)

    assert result.exit_code == 0
    assert "--dirs" in output
    assert "--files" in output
    assert "--globs" in output
    assert "--ignore-dirs" in output
    assert "--ignore-files" in output
    assert "--delete" in output


def test_dry_run_does_not_delete(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    result = run_cli(
        cli_app, "clean", "-d", "__pycache__", "-d", ".pytest_cache", "-g", "build/**", "-f", "notes.temp.txt"
    )

    assert result.exit_code == 0
    assert sample_tree["pycache_file"].exists()
    assert sample_tree["pytest_cache"].exists()
    assert sample_tree["build_artifact"].exists()
    assert sample_tree["temp_file"].exists()
    assert sample_tree["regular_file"].exists()


def test_delete_mode_removes_expected(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    result = run_cli(
        cli_app,
        "clean",
        "-d",
        "__pycache__",
        "-d",
        ".pytest_cache",
        "-g",
        "build/**",
        "-f",
        "notes.temp.txt",
        "--delete",
    )

    assert result.exit_code == 0
    assert not sample_tree["pycache_file"].exists()
    assert not sample_tree["pytest_cache"].exists()
    assert not sample_tree["build_artifact"].exists()
    assert not sample_tree["temp_file"].exists()
    assert sample_tree["regular_file"].exists()


def test_ignored_dirs_and_files(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    result = run_cli(
        cli_app,
        "clean",
        "-d",
        "__pycache__",
        "-d",
        ".pytest_cache",
        "-g",
        "build/**",
        "-f",
        "notes.temp.txt",
        "-f",
        "stray.log",
        "--ignore-dirs",
        "pkg",
        "--ignore-files",
        "stray.log",
        "--delete",
    )

    assert result.exit_code == 0
    assert sample_tree["pycache_file"].exists()
    assert not sample_tree["pytest_cache"].exists()
    assert not sample_tree["build_artifact"].exists()
    assert not sample_tree["temp_file"].exists()
    assert sample_tree["stray_log"].exists()


def test_never_touch_venv(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    result = run_cli(cli_app, "clean", "--dirs", "__pycache__", "--ignore-dirs", ".venv", "--delete")

    assert result.exit_code == 0
    assert sample_tree["venv_pycache"].exists()


def test_globs_patterns(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    result = run_cli(cli_app, "clean", "-g", "build/**", "-g", "*.temp.*", "--delete")

    assert result.exit_code == 0
    assert not sample_tree["build_artifact"].exists()
    assert not sample_tree["temp_file"].exists()
    assert sample_tree["regular_file"].exists()


def test_clean_without_args_shows_help(cli_app: Typer) -> None:
    result = run_cli(cli_app, "clean")
    output = strip_ansi(result.output)

    assert result.exit_code != 0
    assert "Usage:" in output
    assert "Clean files" in output


def test_presets_list(cli_app: Typer) -> None:
    result = run_cli(cli_app, "presets", "list")
    output = strip_ansi(result.output)

    assert result.exit_code == 0
    assert "Cleaner Presets" in output
    assert "python" in output


def test_presets_export_creates_file(cli_app: Typer, chdir_tmp: Path) -> None:
    result = run_cli(cli_app, "presets", "export", "python")

    exported = chdir_tmp / "python_exported.toml"

    assert result.exit_code == 0
    assert exported.exists()
    assert "[tool.cleaner.presets.python]" in exported.read_text(encoding="utf-8")


def test_presets_export_unknown_preset(cli_app: Typer) -> None:
    result = run_cli(cli_app, "presets", "export", "missing-preset")
    output = strip_ansi(result.output)

    assert result.exit_code != 0
    assert "There is no preset with such name" in output