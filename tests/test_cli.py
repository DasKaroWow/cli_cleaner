from pathlib import Path

from click.testing import Result
from typer import Typer
from typer.testing import CliRunner


def run_cli(app: Typer, *args: str) -> Result:
    return CliRunner().invoke(app, list(args))


def test_root_help(cli_app: Typer) -> None:
    result = run_cli(cli_app, "--help")

    assert result.exit_code == 0
    assert "clean" in result.stdout
    assert "presets" in result.stdout


def test_clean_help(cli_app: Typer) -> None:
    result = run_cli(cli_app, "clean", "--help")

    assert result.exit_code == 0
    assert "--dirs" in result.stdout
    assert "--files" in result.stdout
    assert "--globs" in result.stdout
    assert "--ignore-dirs" in result.stdout
    assert "--ignore-files" in result.stdout
    assert "--delete" in result.stdout


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

    assert result.exit_code != 0
    assert "Usage:" in result.output
    assert "Clean files" in result.output


def test_presets_list(cli_app: Typer) -> None:
    result = run_cli(cli_app, "presets", "list")

    assert result.exit_code == 0
    assert "Cleaner Presets" in result.output
    assert "python" in result.output


def test_presets_export_creates_file(cli_app: Typer, chdir_tmp: Path) -> None:
    result = run_cli(cli_app, "presets", "export", "python")

    exported = chdir_tmp / "python_exported.toml"

    assert result.exit_code == 0
    assert exported.exists()
    assert "[tool.cleaner.presets.python]" in exported.read_text(encoding="utf-8")


def test_presets_export_unknown_preset(cli_app: Typer) -> None:
    result = run_cli(cli_app, "presets", "export", "missing-preset")

    assert result.exit_code != 0
    assert "There is no preset with such name" in result.output
