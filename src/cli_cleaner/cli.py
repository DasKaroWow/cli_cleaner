from pathlib import Path
from typing import Annotated

import typer

from cli_cleaner import core
from cli_cleaner.config import DeletionParams, load_presets
from cli_cleaner.display import CleanerConsole

app = typer.Typer(help="A tool for quickly cleaning files in the project directory", add_completion=False)


@app.command("presets")
def list_presets(
    config_path: Annotated[
        Path | None,
        typer.Option(
            "--config", help="Path to config file", show_default="path to cleanerconfig.toml in root of your project"
        ),
    ] = None,
) -> None:
    presets = load_presets(config_path)
    console = CleanerConsole(False)
    console.show_presets_table(presets)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    dirs: Annotated[
        list[str] | None, typer.Option("--dirs", "-d", help="Folder names to delete", show_default="[]")
    ] = None,
    files: Annotated[
        list[str] | None, typer.Option("--files", "-f", help="File names to delete", show_default="[]")
    ] = None,
    globs: Annotated[
        list[str] | None, typer.Option("--globs", "-g", help="Patterns to delete", show_default="[]")
    ] = None,
    ignored_dirs: Annotated[
        list[str] | None, typer.Option("--ignore-dirs", "-id", help="Folders to ignore", show_default="[]")
    ] = None,
    ignored_files: Annotated[
        list[str] | None, typer.Option("--ignore-files", "-if", help="Files to ignore", show_default="[]")
    ] = None,
    root: Annotated[
        Path | None,
        typer.Option("--root", "-r", help="Root dir where will be deletion", show_default="current working directory"),
    ] = None,
    preset_name: Annotated[str | None, typer.Option("--use", "-u", help="Preset to use")] = None,
    config_path: Annotated[
        Path | None,
        typer.Option(
            "--config",
            help="Path to config file where presets are",
            show_default="path to cleanerconfig.toml in root of your project",
        ),
    ] = None,
    delete_mode: Annotated[bool, typer.Option("--delete", help="Actually delete files instead of dry run")] = False,
) -> None:
    if ctx.invoked_subcommand is not None:
        return

    presets = load_presets(config_path)
    deletion_params = presets.get(preset_name) if preset_name else DeletionParams()
    if deletion_params is None:
        raise typer.BadParameter("There is no preset with such name")
    deletion_params = deletion_params.model_copy(
        update={
            "dirs": dirs or deletion_params.dirs,
            "files": files or deletion_params.files,
            "globs": globs or deletion_params.globs,
            "ignored_dirs": ignored_dirs or deletion_params.ignored_dirs,
            "ignored_files": ignored_files or deletion_params.ignored_files,
            "root": root or deletion_params.root,
            "delete_mode": delete_mode,
        }
    )

    if not (deletion_params.dirs or deletion_params.files or deletion_params.globs):
        raise typer.BadParameter("You must provide at least one of --dirs, --files, or --globs")

    console = CleanerConsole(deletion_params.delete_mode)

    console.show_header(deletion_params.root)

    filepaths = core.find_targets(
        deletion_params.root,
        deletion_params.dirs,
        deletion_params.files,
        deletion_params.globs,
        deletion_params.ignored_dirs,
        deletion_params.ignored_files,
    )
    deleted, failed = core.process_targets(console, filepaths, deletion_params.delete_mode)

    console.show_footer(deleted, failed)
