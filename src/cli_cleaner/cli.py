
import typer

from cli_cleaner import commands

app = typer.Typer(help="A tool for quickly cleaning files in the project directory", add_completion=False, no_args_is_help=True)

app.add_typer(commands.clean.app)
app.add_typer(commands.presets.app)
