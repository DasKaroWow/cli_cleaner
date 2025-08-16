from pathlib import Path

from click.testing import Result
from typer import Typer
from typer.testing import CliRunner


def run_cli(app: Typer, *args: str) -> Result:
    return CliRunner().invoke(app, list(args))


def test_cli_help(cli_app: Typer) -> None:
    res = run_cli(cli_app, "--help")
    assert res.exit_code == 0
    assert "--dirs" in res.stdout or "-d" in res.stdout
    assert "--files" in res.stdout or "-f" in res.stdout
    assert "--globs" in res.stdout or "-g" in res.stdout
    assert "--ignore-dirs" in res.stdout or "-id" in res.stdout
    assert "--ignore-files" in res.stdout or "-if" in res.stdout


def test_dry_run_does_not_delete(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    res = run_cli(
        cli_app,
        "-d",
        "__pycache__",
        "-d",
        ".pytest_cache",
        "-g",
        "build/**",
        "-f",
        "notes.temp.txt",
    )
    assert res.exit_code == 0
    assert sample_tree["pycache_file"].exists()
    assert sample_tree["pytest_cache"].exists()
    assert sample_tree["build_artifact"].exists()
    assert sample_tree["temp_file"].exists()
    assert sample_tree["regular_file"].exists()


def test_delete_mode_removes_expected(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    res = run_cli(
        cli_app,
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
    assert res.exit_code == 0
    assert not sample_tree["pycache_file"].exists()
    assert not sample_tree["pytest_cache"].exists()
    assert not sample_tree["build_artifact"].exists()
    assert not sample_tree["temp_file"].exists()
    assert sample_tree["regular_file"].exists()


def test_ignored_dirs_and_files(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    res = run_cli(
        cli_app,
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
    assert res.exit_code == 0
    assert sample_tree["pycache_file"].exists()
    assert not sample_tree["pytest_cache"].exists()
    assert not sample_tree["build_artifact"].exists()
    assert not sample_tree["temp_file"].exists()


def test_never_touch_venv(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    res = run_cli(
        cli_app,
        "--dirs",
        "__pycache__",
        "--ignore-dirs",
        ".venv",
        "--delete",
    )
    assert res.exit_code == 0
    assert sample_tree["venv_pycache"].exists()


def test_globs_patterns(cli_app: Typer, sample_tree: dict[str, Path]) -> None:
    res = run_cli(
        cli_app,
        "-g",
        "build/**",
        "-g",
        "*.temp.*",
        "--delete",
    )
    assert res.exit_code == 0
    assert not sample_tree["build_artifact"].exists()
    assert not sample_tree["temp_file"].exists()
    assert sample_tree["regular_file"].exists()
