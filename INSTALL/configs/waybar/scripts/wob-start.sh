#!/usr/bin/env bash
# wob-start.sh — lance l'overlay violet-chaton via FIFO
# Appelé au démarrage de session (autostart)

FIFO="/tmp/wob.fifo"

pkill -f wob-overlay.py 2>/dev/null
rm -f "$FIFO"
mkfifo "$FIFO"

# Ouvrir le FIFO en lecture+écriture sur fd3 :
# empêche l'overlay de recevoir EOF entre deux écritures
exec 3<> "$FIFO"
python3 "$HOME/.config/waybar/scripts/wob-overlay.py" &
disown $!
