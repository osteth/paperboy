#!/usr/bin/env bash
set -euo pipefail

echo "==> Uninstalling Paperboy..."

systemctl --user stop    paperboy 2>/dev/null || true
systemctl --user disable paperboy 2>/dev/null || true

rm -f  "$HOME/.local/bin/paperboy-configure"
rm -rf "$HOME/.local/share/paperboy"
rm -f  "$HOME/.config/systemd/user/paperboy.service"
rm -f  "$HOME/.local/share/icons/hicolor/512x512/apps/paperboy.png"
rm -f  "$HOME/.local/share/applications/paperboy.desktop"

systemctl --user daemon-reload
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo ""
echo "Paperboy uninstalled."
echo "Your config at ~/.config/paperboy/ has been preserved."
echo "To also remove config: rm -rf ~/.config/paperboy"
