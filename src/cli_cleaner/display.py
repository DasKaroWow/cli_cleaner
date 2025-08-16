from pathlib import Path

from rich.console import Console
from rich.markup import escape
from rich.table import Table
from rich.theme import Theme

from cli_cleaner.config import DeletionParams


class CleanerConsole:
    def __init__(self, delete_mode: bool) -> None:
        theme = Theme(
            {
                "dry": "yellow",
                "delete": "bold red",
                "path": "dim",
                "ok": "green",
                "err": "bold red",
            }
        )
        self.console = Console(theme=theme)
        self.delete_mode = delete_mode

    def show_header(self, root: Path) -> None:
        icon = ":wastebasket:" if self.delete_mode else ":eyes:"
        text = "DELETING" if self.delete_mode else "DRY RUN"
        style = "delete" if self.delete_mode else "dry"
        self.console.rule(f"{icon} [{style}]{text} in [bold]{escape(root.as_posix())}[/bold][/]")

    def show_action(self, path: Path) -> None:
        icon = ":wastebasket:" if self.delete_mode else ":eyes:"
        verb = "Deleting" if self.delete_mode else "Would delete"
        self.console.print(
            f"{icon} [{'delete' if self.delete_mode else 'dry'}]{verb}[/]: [path]{escape(path.as_posix())}[/]"
        )

    def show_result(self, ok: bool) -> None:
        self.console.print(":white_check_mark: [ok]done[/]" if ok else ":x: [err]failed[/]")

    def show_footer(self, deleted: int, failed: int) -> None:
        icon = ":wastebasket:" if self.delete_mode else ":eyes:"
        text = (
            f"{deleted} items successfully deleted; {failed} could not be deleted"
            if self.delete_mode
            else f"{deleted} items will be deleted with --delete option"
        )
        style = "delete" if self.delete_mode else "dry"
        self.console.rule(f"{icon} [{style}]{text}[/]")

    def show_presets_table(self, presets: dict[str, DeletionParams]) -> None:
        table = Table(title="Cleaner Presets", show_lines=True)

        table.add_column("Preset", style="cyan", no_wrap=True)
        table.add_column("Dirs", style="magenta")
        table.add_column("Files", style="green")
        table.add_column("Globs", style="blue")
        table.add_column("Ignored Dirs", style="red")
        table.add_column("Ignored Files", style="red")

        for name, params in presets.items():
            table.add_row(
                name,
                ", ".join(params.dirs) if params.dirs else "-",
                ", ".join(params.files) if params.files else "-",
                ", ".join(params.globs) if params.globs else "-",
                ", ".join(params.ignored_dirs) if params.ignored_dirs else "-",
                ", ".join(params.ignored_files) if params.ignored_files else "-",
            )

        self.console.print(table)
