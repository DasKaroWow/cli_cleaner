# CLI Cleaner

[![Tests](https://github.com/DasKaroWow/cli_cleaner/actions/workflows/tests.yml/badge.svg)](https://github.com/DasKaroWow/cli_cleaner/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/cli-cleaner.svg)](https://pypi.org/project/cli_cleaner/)
[![Python versions](https://img.shields.io/pypi/pyversions/cli_cleaner.svg)](https://pypi.org/project/cli_cleaner/)
[![License](https://img.shields.io/github/license/DasKaroWow/cli_cleaner)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A command-line tool for safely cleaning files and directories in your project.

By default, it runs in **dry-run mode**: it only shows what would be deleted. Add `--delete` to actually remove files.

- Beautiful output powered by [rich](https://github.com/Textualize/rich)
- Flexible cleanup rules with `--dirs`, `--files`, `--globs`
- Built-in **presets** for popular stacks: Python, Node, Rust, Go, Java, and more
- **Custom presets** from `pyproject.toml` or `cleanerconfig.toml`
- Dedicated subcommands for cleanup and preset management

Commands:

    cleaner clean ...
    cleaner presets list
    cleaner presets export <name>

> Requires **Python ≥ 3.12**.

---

## Installation

```bash
pipx install cli-cleaner
```

Or:

```bash
pip install cli-cleaner
```

---

## Quick start

Dry run:

```bash
cleaner clean -d __pycache__ -d .pytest_cache -g "build/**" -f "notes.temp.txt"
```

Real deletion:

```bash
cleaner clean -d __pycache__ -d .pytest_cache -g "build/**" -f "notes.temp.txt" --delete
```

Examples:

```bash
cleaner clean -g "**/*.pyc" -d __pycache__
cleaner clean -g "build/**" -g "dist/**" --delete
cleaner clean -f stray.log -f notes.temp.txt --ignore-dirs ".venv" --ignore-files stray.log --delete
```

---

## Commands

### `cleaner clean`

Main cleanup command.

```bash
cleaner clean [OPTIONS]
```

Supported options:

- `--dirs`, `-d` — directory names to delete
- `--files`, `-f` — file names to delete
- `--globs`, `-g` — glob patterns to delete
- `--ignore-dirs`, `-id` — directories to ignore
- `--ignore-files`, `-if` — files to ignore
- `--root`, `-r` — root directory for cleanup
- `--use`, `-u` — preset name
- `--config` — explicit path to a TOML config file with presets
- `--delete` — actually delete files instead of dry-run

Examples:

```bash
cleaner clean --use python
cleaner clean --use python --delete
cleaner clean -g "*.log" -d build --delete
```

### `cleaner presets list`

Show all available presets, including built-in ones and presets loaded from config files.

```bash
cleaner presets list
```

With custom config:

```bash
cleaner presets list --config "./ops/cleanerconfig.toml"
```

### `cleaner presets export`

Export a preset into a separate TOML file named `{preset_name}_exported.toml`.

```bash
cleaner presets export python
```

With custom config:

```bash
cleaner presets export frontend --config "./ops/cleanerconfig.toml"
```

---

## Presets

List all presets:

```bash
cleaner presets list
```

Export a preset:

```bash
cleaner presets export python
```

Use a preset:

```bash
cleaner clean --use python
cleaner clean --use python --delete
cleaner clean --use node -g "*.log" --ignore-dirs ".vscode" --delete
```

### Built-in presets

Built-in presets are stored in [`src/cli_cleaner/presets.toml`](src/cli_cleaner/presets.toml).

Available out of the box:

- `python` — `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.tox`, `.nox`, `.hypothesis`, `htmlcov`, `build`, `dist`, `.pytype`, `.pyre`, `*.pyc`, `*.pyo`, `*$py.class`, `**/*.egg-info/**`, `.coverage.*`, `pytest-*.xml`, `pytest-*.log`
- `node` — `node_modules`, `.parcel-cache`, `.next`, `.nuxt`, `.svelte-kit`, `.vite`, `.turbo`, `.cache`, `coverage`, `dist`, `build`, `out`, `*.log`, `*.tsbuildinfo`
- `rust` — `target`, `coverage`
- `go` — `bin`, `build`, `dist`, `coverage`, `coverage.out`
- `java` — `target`, `build`, `out`, `.gradle`, `.idea/modules`, compiled `.class`, `.jar`, `.war`, `.ear` artifacts
- `dotnet` — `bin`, `obj`, `.vs`, `TestResults`, `artifacts`, `coverage`
- `php` — `vendor`, `var/cache`, `var/log`, `storage/framework/cache`, `bootstrap/cache`, `coverage`, `build`, `dist`, `*.log`
- `ruby` — `vendor/bundle`, `.bundle`, `coverage`, `tmp`, `pkg`, `log/*.log`
- `swift` — `DerivedData`, `.build`, `.swiftpm`, `build`, Xcode user data
- `android` — `build`, `.gradle`, `app/build`, `.cxx`, `captures`, `coverage`
- `latex` — common intermediate files like `*.aux`, `*.bbl`, `*.log`, `*.toc`, `*.out`, `*.synctex.gz`
- `haskell` — `dist`, `dist-newstyle`, `.stack-work`, `coverage`
- `elixir` — `_build`, `deps`, `cover`
- `ansible` — `*.retry`
- `c_cpp` — `build`, `bin`, `obj`, `.cache`, `CMakeFiles`, `Debug`, `Release`, `x64`, `x86`, common binary/object artifacts
- `unity` — `Library`, `Temp`, `Build`, `Logs`, `Obj`
- `unreal` — `Binaries`, `DerivedDataCache`, `Intermediate`, `Saved/Logs`
- `os` — `.DS_Store`, `Thumbs.db`, `desktop.ini`

Many presets also include default ignored directories such as `.git`, `.hg`, `.svn`, `.idea`, `.vscode`, `venv`, and `.venv`.

---

## Project configuration

CLI Cleaner searches upward from the current working directory for:

1. `pyproject.toml`
2. `cleanerconfig.toml`

Preset merge order from lowest to highest priority:

1. Built-in presets
2. `pyproject.toml`
3. `cleanerconfig.toml`
4. File passed explicitly via `--config`

If the same preset name appears multiple times, the last source wins.

### Example: `pyproject.toml`

```toml
[tool.cleaner.presets.my_python]
dirs = ["__pycache__", ".pytest_cache", "build", "dist"]
files = [".coverage", "coverage.xml"]
globs = ["**/*.pyc", "**/*.pyo", "**/*.egg-info/**"]
ignored_dirs = [".git", ".idea", ".vscode", ".venv"]
ignored_files = []
```

### Example: `cleanerconfig.toml`

```toml
[tool.cleaner.presets.frontend]
dirs = ["node_modules", ".next", ".turbo", "dist", "build"]
files = [".eslintcache"]
globs = ["*.log", "*.tsbuildinfo"]
ignored_dirs = [".git", ".idea", ".vscode"]
ignored_files = []
```

### Explicit config path

```bash
cleaner clean --use frontend --config "./ops/cleanerconfig.toml"
```

You can also use the same config file for preset inspection and export:

```bash
cleaner presets list --config "./ops/cleanerconfig.toml"
cleaner presets export frontend --config "./ops/cleanerconfig.toml"
```

---

## Behavior

- Default mode is **dry-run**
- Add `--delete` to actually remove files
- `cleaner clean` without arguments shows command help
- To run cleanup, provide at least one selector:
  - `--dirs`
  - `--files`
  - `--globs`
  - or use a preset with `--use`
- Manual CLI flags override preset values
- Many presets include ignored directories for safety, such as `.git`, `.idea`, `.vscode`, `venv`, `.venv`

---

## Typical scenarios

```bash
cleaner clean --use python
cleaner clean --use python --delete
cleaner clean --use node -g "*.log" --delete
cleaner clean -g "build/**" -g "*.temp.*" --ignore-dirs ".venv" --delete
cleaner clean --use frontend --delete
cleaner presets list --config "./ops/cleanerconfig.toml"
cleaner presets export python
```
