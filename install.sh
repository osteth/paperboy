#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.local/share/paperboy"
BIN_DIR="$HOME/.local/bin"
SYSTEMD_DIR="$HOME/.config/systemd/user"
LITE=false

# --- Argument parsing -------------------------------------------------------

usage() {
    echo "Usage: ./install.sh [--lite | --full]"
    echo ""
    echo "  --lite   Daemon only — no GUI configurator or Tkinter dependency"
    echo "  --full   Full install including GUI configurator (default)"
    exit 0
}

for arg in "$@"; do
    case "$arg" in
        --lite) LITE=true ;;
        --full) LITE=false ;;
        --help|-h) usage ;;
        *) echo "Unknown option: $arg"; usage ;;
    esac
done

# --- Install ----------------------------------------------------------------

if $LITE; then
    echo "==> Paperboy installer (lite)"
else
    echo "==> Paperboy installer (full)"
fi
echo ""

# Base dependencies (daemon)
echo "==> Installing base dependencies..."
sudo apt install -y \
    python3-watchdog \
    python3-pypdf \
    ghostscript \
    libnotify-bin

# GUI dependencies (full only)
if ! $LITE; then
    echo "==> Installing GUI dependencies..."
    sudo apt install -y python3-tk
fi

# Directories
echo "==> Creating directories..."
mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$SYSTEMD_DIR"

# Core files
echo "==> Installing Paperboy files..."
cp daemon.py "$INSTALL_DIR/daemon.py"

# GUI files (full only)
if ! $LITE; then
    cp configure.py "$INSTALL_DIR/configure.py"

    cat > "$BIN_DIR/paperboy-configure" <<'EOF'
#!/usr/bin/env bash
python3 "$HOME/.local/share/paperboy/configure.py" "$@"
EOF
    chmod +x "$BIN_DIR/paperboy-configure"
fi

# Systemd user service
cp systemd/paperboy.service "$SYSTEMD_DIR/paperboy.service"
systemctl --user daemon-reload
systemctl --user enable paperboy

# --- Summary ----------------------------------------------------------------

echo ""
echo "Paperboy installed successfully."
echo ""
echo "Next steps:"
if $LITE; then
    echo "  1. Edit ~/.config/paperboy/config.json to set up your routing rules"
else
    echo "  1. Run 'paperboy-configure' to set up your printers and routing rules"
fi
echo "  2. Run 'systemctl --user start paperboy' to start the daemon"
echo "  3. In Brave: print -> Save as PDF -> ~/Documents/PrintQueue"
echo ""
echo "Useful commands:"
if ! $LITE; then
    echo "  paperboy-configure                      Open the configuration GUI"
fi
echo "  systemctl --user start paperboy         Start daemon"
echo "  systemctl --user stop paperboy          Stop daemon"
echo "  journalctl --user -u paperboy -f        Watch live logs"
