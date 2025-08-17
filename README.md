# CLI Cleaner

[![Tests](https://github.com/DasKaroWow/cli_cleaner/actions/workflows/tests.yml/badge.svg)](https://github.com/DasKaroWow/cli_cleaner/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/cli-cleaner.svg)](https://pypi.org/project/cli_cleaner/)
[![Python versions](https://img.shields.io/pypi/pyversions/cli_cleaner.svg)](https://pypi.org/project/cli_cleaner/)
[![License](https://img.shields.io/github/license/DasKaroWow/cli_cleaner)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)


A command-line tool for safely cleaning files and directories in your project.
By default, it runs in **dry-run mode** (preview only, nothing deleted). Add `--delete` to actually remove files.

- Beautiful output powered by [rich](https://github.com/Textualize/rich)
- Options: `--dirs`, `--files`, `--globs`
- Built-in **presets** for popular stacks (Python, Node, Rust, Go, Java, …)
- **Custom presets** from `pyproject.toml` or `cleanerconfig.toml`
- Simple command `cleaner presets` to preview all available presets

---

## Installation

```bash
# Recommended (isolated CLI)
pipx install cli-cleaner

# Or via pip
pip install cli-cleaner
```

> Requires **Python ≥ 3.12**.

---

## Quick start

Dry run (no files deleted, only preview):

```bash
cleaner -d __pycache__ -d .pytest_cache -g "build/**" -f "notes.temp.txt"
```

Real deletion (⚠ irreversible):

```bash
cleaner -d __pycache__ -d .pytest_cache -g "build/**" -f "notes.temp.txt" --delete
```

Examples:

```bash
# delete *.pyc and __pycache__ directories (dry-run)
cleaner -g "**/*.pyc" -d __pycache__

# delete build artifacts in all subfolders
cleaner -g "build/**" -g "dist/**" --delete

# delete specific files but ignore some dirs/files
cleaner -f stray.log -f notes.temp.txt --ignore-dirs ".venv" --ignore-files stray.log --delete
```

---

## Presets

List all presets (built-in + from configs):

```bash
cleaner presets
```

Use a preset:

```bash
# built-in Python preset
cleaner --use python

# with real deletion
cleaner --use python --delete

# combine preset + extra options
cleaner --use node -g "*.log" --ignore-dirs ".vscode" --delete
```

### Built-in presets

Located in [`src/cli_cleaner/presets.toml`](src/cli_cleaner/presets.toml).
Available out of the box:

- `python` — `__pycache__`, `.pytest_cache`, `*.pyc`, `*.pyo`, `*$py.class`, `**/*.egg-info/**`, `htmlcov`, `build`, `dist`, etc.
  (*ignores*: `.git`, `.hg`, `.svn`, `.idea`, `.vscode`, `venv`, `.venv`)
- `node` — `node_modules`, `.next`, `.nuxt`, `.svelte-kit`, `.vite`, `dist`, `build`, logs, etc.
- `rust` — `target`, `coverage`
- `go` — `bin`, `build`, `dist`, `coverage`, `coverage.out`
- `java` — `target`, `build`, `out`, `.gradle`, compiled `.class/.jar/.war/.ear`
- `dotnet` — `bin`, `obj`, `.vs`, `TestResults`, `artifacts`, `coverage`
- `php` — `vendor`, `var/cache`, `var/log`, `bootstrap/cache`, `*.log`
- `ruby` — `vendor/bundle`, `.bundle`, `coverage`, `tmp`, `pkg`, `log/*.log`
- `swift` — `DerivedData`, `.build`, `.swiftpm`, `*.xcworkspace/xcuserdata/**`
- `android` — `build`, `.gradle`, `app/build`, `.cxx`, `captures`
- `latex` — all common intermediate files (`*.aux`, `*.log`, `*.toc`, …)
- `haskell` — `dist`, `dist-newstyle`, `.stack-work`, `coverage`
- `elixir` — `_build`, `deps`, `cover`
- `ansible` — `*.retry`
- `c_cpp` — `build`, `bin`, `obj`, `CMakeFiles`, `Debug`, `Release`, `.o/.so/.dll/.exe` artifacts
- `unity` — `Library`, `Temp`, `Build`, `Logs`, `Obj`
- `unreal` — `Binaries`, `DerivedDataCache`, `Intermediate`, `Saved/Logs`
- `os` — `.DS_Store`, `Thumbs.db`, `desktop.ini`

---

## Project configuration

CLI_Cleaner searches for configs upwards from the current directory in:

1. `pyproject.toml`
2. `cleanerconfig.toml`

Merge order (lowest → highest priority):

1. Built-in presets
2. `pyproject.toml`
3. `cleanerconfig.toml`
4. Custom file passed via `--config`

The last definition wins if names collide.

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
cleaner --use frontend --config "./ops/cleanerconfig.toml"
```

---

## Behavior

- Default = **dry-run** (safe).
  Use `--delete` to actually remove files.
- If no `--dirs`, `--files`, `--globs`, and no `--use` preset → error:
  ```
  You must provide at least one of --dirs, --files, or --globs
  ```
- Manual flags override preset values.
- Many presets include `ignored_dirs` (like `.git`, `.idea`, `.venv`) for safety.

---

## Typical scenarios

```bash
# Clean a Python project (dry-run)
cleaner --use python

# Clean a Python project (real deletion)
cleaner --use python --delete

# Node project + extra cleanup
cleaner --use node -g "*.log" --delete

# Custom: clean build artifacts but keep .venv
cleaner -g "build/**" -g "*.temp.*" --ignore-dirs ".venv" --delete

# Use custom preset from cleanerconfig.toml
cleaner --use frontend --delete
```
