# Contributing to Paperboy

Thanks for your interest in contributing! Here's everything you need to get started.

## Reporting Bugs

Open an issue at [github.com/osteth/paperboy/issues](https://github.com/osteth/paperboy/issues) and include:

- Your Linux distro and version
- Python version (`python3 --version`)
- Steps to reproduce the problem
- The relevant section of `~/.local/share/paperboy/paperboy.log`

## Suggesting Features

Open an issue with the **enhancement** label. Describe the use case — what problem does it solve and how would it work?

## Development Setup

```bash
git clone https://github.com/osteth/paperboy.git
cd paperboy

# Install dependencies
sudo apt install -y python3-watchdog python3-pypdf python3-tk ghostscript libnotify-bin

# Run the GUI directly
python3 configure.py

# Run the daemon directly (Ctrl+C to stop)
python3 daemon.py
```

Config is read from `~/.config/paperboy/config.json`. The daemon watches whatever `watch_dir` is set to in that file.

## Project Structure

```
paperboy/
├── daemon.py         # Watchdog-based daemon — watches directory, routes PDFs
├── configure.py      # Tkinter GUI configurator
├── install.sh        # Installer (--lite / --full)
├── uninstall.sh      # Uninstaller
├── paperboy.desktop  # Desktop entry for system app registration
├── systemd/
│   └── paperboy.service  # systemd user service unit
├── AppIcon.png       # App icon (500x500)
└── AppIcon.xcf       # GIMP source file for icon
```

## Submitting a Pull Request

1. Fork the repo and create a branch from `master`
2. Make your changes
3. Test manually — run the daemon and drop a PDF into the watch directory, open the GUI and verify your changes work
4. Open a pull request with a clear description of what changed and why

## Code Style

- Python: follow PEP 8, 4-space indentation
- Keep functions focused — the daemon and GUI are intentionally separate concerns
- If adding a new routing criterion, update both `daemon.py` (matching logic) and `configure.py` (GUI field + treeview column)
- Shell scripts: `set -euo pipefail`, double-quote variables

## Adding Paper Sizes

Paper sizes are defined in the `PAPER_SIZES` dict in `configure.py`. Dimensions are in PDF points (1 point = 1/72 inch). To add a new size:

```python
"My Size (WxH)": (width_inches * 72, height_inches * 72),
```

The daemon uses a tolerance of ±20 points (~0.28") when matching, so exact precision isn't required.
