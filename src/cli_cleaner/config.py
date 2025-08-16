import importlib.resources as resources
import tomllib
import unicodedata as ud
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeletionParams(BaseSettings):
    dirs: list[str] = []
    files: list[str] = []
    globs: list[str] = []
    ignored_dirs: list[str] = []
    ignored_files: list[str] = []
    root: Path = Field(default_factory=Path.cwd)
    delete_mode: bool = False

    model_config = SettingsConfigDict(extra="forbid")

    @field_validator("dirs", "files", "globs", "ignored_dirs", "ignored_files", mode="before")
    @classmethod
    def normalize(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [ud.normalize("NFC", value)]
        return [ud.normalize("NFC", v) for v in value]


def find_configs(start: Path | None = None) -> tuple[Path | None, Path | None]:
    if start is None:
        start = Path.cwd()
    pyproject = None
    cleanerconfig = None

    for path in [start, *start.parents]:
        if (filepath := (path / "pyproject.toml")).exists():
            pyproject = pyproject or filepath.resolve()
        if (filepath := (path / "cleanerconfig.toml")).exists():
            cleanerconfig = cleanerconfig or filepath.resolve()

    return pyproject, cleanerconfig


def load_presets(customconfig_path: Path | None = None) -> dict[str, DeletionParams]:
    pyproject_path, cleanerconfig_path = find_configs()

    presets = {}
    with resources.files("cli_cleaner").joinpath("presets.toml").open("rb") as file:
        builtin_dict = tomllib.load(file)
        presets |= builtin_dict.get("tool", {}).get("cleaner", {}).get("presets", {})

    if pyproject_path:
        with pyproject_path.open("rb") as file:
            pyproject_dict = tomllib.load(file)
            presets |= pyproject_dict.get("tool", {}).get("cleaner", {}).get("presets", {})

    if cleanerconfig_path:
        with cleanerconfig_path.open("rb") as file:
            cleanerconfig_dict = tomllib.load(file)
            presets |= cleanerconfig_dict.get("tool", {}).get("cleaner", {}).get("presets", {})

    if customconfig_path:
        with customconfig_path.open("rb") as file:
            customconfig_dict = tomllib.load(file)
            presets |= customconfig_dict.get("tool", {}).get("cleaner", {}).get("presets", {})

    return {preset_name: DeletionParams(**settings) for preset_name, settings in presets.items()}
