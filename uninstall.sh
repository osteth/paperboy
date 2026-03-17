#!/usr/bin/env bash
set -euo pipefail

echo "==> Uninstalling Paperboy..."

systemctl --user stop    paperboy 2>/dev/null || true
systemctl --user disable paperboy 2>/dev/null || true

rm -f  "$HOME/.local/bin/paperboy-configure"
rm -rf "$HOME/.local/share/paperboy"
rm -f  "$HOME/.config/systemd/user/paperboy.service"

systemctl --user daemon-reload

echo ""
echo "Paperboy uninstalled."
echo "Your config at ~/.config/paperboy/ has been preserved."
echo "To also remove config: rm -rf ~/.config/paperboy"
