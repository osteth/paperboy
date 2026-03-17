#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.local/share/paperboy"
BIN_DIR="$HOME/.local/bin"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "==> Paperboy installer"
echo ""

# Stop old print-daemon service if it exists
if systemctl --user is-active --quiet print-daemon 2>/dev/null; then
    echo "==> Stopping old print-daemon service..."
    systemctl --user stop print-daemon
    systemctl --user disable print-daemon
fi

# Dependencies
echo "==> Installing system dependencies..."
sudo apt install -y \
    python3-watchdog \
    python3-pypdf \
    ghostscript \
    libnotify-bin

# Directories
echo "==> Creating directories..."
mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$SYSTEMD_DIR"

# Copy files
echo "==> Installing Paperboy files..."
cp daemon.py    "$INSTALL_DIR/daemon.py"
cp configure.py "$INSTALL_DIR/configure.py"

# Launcher: paperboy-configure
cat > "$BIN_DIR/paperboy-configure" <<'EOF'
#!/usr/bin/env bash
python3 "$HOME/.local/share/paperboy/configure.py" "$@"
EOF
chmod +x "$BIN_DIR/paperboy-configure"

# Systemd user service
cp systemd/paperboy.service "$SYSTEMD_DIR/paperboy.service"
systemctl --user daemon-reload
systemctl --user enable paperboy

echo ""
echo "Paperboy installed successfully."
echo ""
echo "Next steps:"
echo "  1. Run 'paperboy-configure' to set up your printers and routing rules"
echo "  2. Run 'systemctl --user start paperboy' to start the daemon"
echo "  3. In Brave: print -> Save as PDF -> ~/Documents/PrintQueue"
echo ""
echo "Useful commands:"
echo "  paperboy-configure                      Open the configuration GUI"
echo "  systemctl --user start paperboy         Start daemon"
echo "  systemctl --user stop paperboy          Stop daemon"
echo "  journalctl --user -u paperboy -f        Watch live logs"
