from pathlib import Path
from typing import Annotated

import typer

from cli_cleaner.core.config import load_presets
from cli_cleaner.display import CleanerConsole

app = typer.Typer(name="presets", help="List/show presets")


@app.callback()
def _group_options(  # pyright: ignore[reportUnusedFunction]
    context: typer.Context,
    config_path: Annotated[
        Path | None,
        typer.Option(
            "--config",
            help="Path to custom .toml file (applies to all 'presets' subcommands)",
        ),
    ] = None,
) -> None:
    context.obj = config_path.resolve() if config_path else None

@app.command("list", help="List of all presets")
def presets_list(
    context: typer.Context
) -> None:
    presets = load_presets(context.obj)
    console = CleanerConsole(False)
    console.show_presets_table(presets)

@app.command("export", help=r'Export preset to file named "{preset_name}_exported.toml"')
def presets_export(
    context: typer.Context,
    preset: Annotated[
        str,
        typer.Argument(..., help="Preset to export (e.g. python)")
    ]
) -> None:
    presets = load_presets(context.obj)
    chosen = presets.get(preset)
    if chosen is None:
        raise typer.BadParameter("There is no preset with such name")

    filepath = Path(f"{preset}_exported.toml")
    with filepath.open("w", encoding="utf-8") as file:
        file.write(f"[tool.cleaner.presets.{preset}]\n")
        file.write(f"dirs = {chosen.dirs}\n")
        file.write(f"files = {chosen.files}\n")
        file.write(f"globs = {chosen.globs}\n")
        file.write(f"ignored_dirs = {chosen.ignored_dirs}\n")
        file.write(f"ignored_files = {chosen.ignored_files}\n")

    console = CleanerConsole(False)
    console.show_message(f"Preset saved to {filepath.resolve()}", "success")
