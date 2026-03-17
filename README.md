# Paperboy

**Automatic PDF Print Router for Linux**

Paperboy watches a directory for incoming PDFs and automatically routes them to the correct printer based on page size and color content — no manual printer selection needed.

## Use Case

Perfect for e-commerce workflows (Shopify, Etsy, eBay, etc.) where you need:

- **Shipping labels** (4×6") → thermal label printer (Rollo, Dymo, Zebra, etc.)
- **Packing slips / documents** → laser or inkjet printer (Brother, HP, etc.)

Instead of manually selecting a printer each time, "print to PDF" into the watch folder and Paperboy handles the rest.

## Features

- Watches a directory for new PDFs
- Detects page size and routes to the matching printer
- Detects color vs. black & white content (via ghostscript) for fine-grained routing
- GUI configurator — no config file editing needed
- Runs as a systemd user service (auto-starts on login)
- Desktop notifications on print or error
- Logs to `~/.local/share/paperboy/paperboy.log`

## Requirements

- Ubuntu 20.04+ or any systemd-based Linux distro
- Python 3.10+
- `python3-watchdog`
- `python3-pypdf`
- `ghostscript` (for color detection — optional but recommended)
- `libnotify-bin` (for desktop notifications)

## Installation

```bash
git clone <repo-url> paperboy
cd paperboy
chmod +x install.sh
./install.sh
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
4. Paperboy detects the file, checks its size and color, routes to the correct printer, and deletes the PDF

### Configurator

Run `paperboy-configure` to open the GUI:

- Set your watch directory
- Add routing rules: map paper sizes and color types to printers
- Start, stop, or restart the daemon
- View live logs

Rules are evaluated **top-to-bottom** — first match wins. Put specific rules (e.g. 4×6 label) above general defaults.

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

If ghostscript is not installed, all "Color" and "B&W" rules fall back to matching as "Any".

## Uninstall

```bash
./uninstall.sh
```

Your config at `~/.config/paperboy/` is preserved. Remove it manually if desired.

## License

MIT
