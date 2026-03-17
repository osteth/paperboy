# Paperboy

**Automatic PDF Print Router for Linux**

Paperboy watches a directory for incoming PDFs and automatically routes them to the correct printer based on filename, page size, and color content — no manual printer selection needed.

## Use Case

Perfect for e-commerce workflows (Shopify, Etsy, eBay, etc.) where you need:

- **Shipping labels** (4×6") → thermal label printer (Rollo, Dymo, Zebra, etc.)
- **Packing slips / documents** → laser or inkjet printer (Brother, HP, etc.)

Instead of manually selecting a printer each time, "print to PDF" into the watch folder and Paperboy handles the rest.

## Features

- Watches a directory for new PDFs
- Routes by **filename pattern** (glob), **page size**, and **color content**
- Detects color vs. black & white content via ghostscript
- Rules evaluated top-to-bottom — first match wins
- Configurable post-print action: **delete** or **archive** to a chosen directory
- Modern dark-themed GUI configurator — no config file editing needed
- Registered as a system application (searchable in app launcher)
- Runs as a systemd user service (auto-starts on login)
- Desktop notifications on print or error
- Logs to `~/.local/share/paperboy/paperboy.log`

## Requirements

- Ubuntu 20.04+ or any systemd-based Linux distro
- Python 3.10+
- `python3-watchdog`
- `python3-pypdf`
- `python3-tk` (full install only — GUI configurator)
- `ghostscript` (color detection — optional but recommended)
- `libnotify-bin` (desktop notifications)

All dependencies are installed automatically by `install.sh`.

## Installation

```bash
git clone <repo-url> paperboy
cd paperboy
chmod +x install.sh
./install.sh
```

### Install options

```bash
./install.sh          # Full install — daemon + GUI configurator (default)
./install.sh --full   # Same as above, explicit
./install.sh --lite   # Daemon only — no GUI, no Tkinter dependency
```

Then open the configurator to set up your rules:

```bash
paperboy-configure
```

## Usage

### Workflow

1. In your browser (Brave, Chrome, Firefox), open the print dialog
2. Set destination to **Save as PDF**
3. Save to your watch directory (default: `~/Documents/PrintQueue`)
4. Paperboy detects the file, checks its filename, size, and color, routes to the correct printer, then deletes or archives it

### Configurator

Run `paperboy-configure` to open the GUI. It can also be found by searching "Paperboy" in your system app launcher.

**Settings:**
- Set the watch directory
- Choose what happens after a successful print: **Delete** the PDF or **Archive** it to a chosen directory

**Routing Rules:**
- Add rules that map combinations of filename pattern, paper size, and color to a printer
- Reorder rules with Move Up / Move Down — first match wins
- Double-click a rule to edit it

**Daemon Controls:**
- Start, stop, or restart the daemon directly from the GUI
- View live logs in a terminal window

### Routing Rules

Each rule can match on any combination of:

| Field            | Description                                              |
|------------------|----------------------------------------------------------|
| Filename Pattern | Glob pattern matched against the PDF filename, e.g. `*shipping*`, `invoice_*.pdf`. Leave blank to match any filename. |
| Paper Size       | Match by page dimensions (see table below)               |
| Color            | Any, Color only, or Black & White only                   |

Rules are matched **top-to-bottom** — the first rule where all fields match wins. Put specific rules above general defaults.

### CLI

```bash
# Start / stop / restart
systemctl --user start   paperboy
systemctl --user stop    paperboy
systemctl --user restart paperboy

# Check status
systemctl --user status paperboy

# Watch live logs
journalctl --user -u paperboy -f

# Open configurator
paperboy-configure
```

## Supported Paper Sizes

| Name           | Dimensions       |
|----------------|------------------|
| 4×6 Label      | 4" × 6"          |
| 4×4 Label      | 4" × 4"          |
| 3×3 Label      | 3" × 3"          |
| 2×7 Label      | 2" × 7"          |
| 5×7            | 5" × 7"          |
| Letter         | 8.5" × 11"       |
| A4             | 210mm × 297mm    |
| Legal          | 8.5" × 14"       |
| Any (default)  | Matches anything |

## Color Routing

Requires `ghostscript`. Paperboy reads the CMYK ink coverage of each page:

- **Any** — route regardless of color content
- **Color only** — route only if the PDF contains color ink
- **Black & White only** — route only if all content is monochrome

If ghostscript is not installed, all color rules fall back to matching as "Any".

## After Print

| Option  | Behaviour                                                      |
|---------|----------------------------------------------------------------|
| Delete  | PDF is removed after a successful print                        |
| Archive | PDF is moved to the configured archive directory. If a file with the same name already exists, a numeric suffix is added (e.g. `file_1.pdf`) |

## Config File

The configuration is stored at `~/.config/paperboy/config.json` and is managed by the GUI. Manual editing is supported — restart the daemon after any changes.

```json
{
  "watch_dir": "~/Documents/PrintQueue",
  "after_print": "delete",
  "archive_dir": "~/Documents/PrintArchive",
  "rules": [
    {
      "name": "Shipping Labels",
      "filename_pattern": "*shipping*",
      "width_pt": 288,
      "height_pt": 432,
      "color": "any",
      "printer": "Rollo_X1040"
    },
    {
      "name": "Default",
      "filename_pattern": null,
      "width_pt": null,
      "height_pt": null,
      "color": "any",
      "printer": "Brother_DCP_L2550DW_series"
    }
  ]
}
```

## Uninstall

```bash
./uninstall.sh
```

Your config at `~/.config/paperboy/` is preserved. To also remove it:

```bash
rm -rf ~/.config/paperboy
```

## License

MIT
