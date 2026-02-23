#!/usr/bin/env bash
# wob-start.sh — lance le daemon wob via FIFO
# Appelé au démarrage de session (autostart)

FIFO="/tmp/wob.fifo"

pkill wob 2>/dev/null
rm -f "$FIFO"
mkfifo "$FIFO"

# Ouvrir le FIFO en lecture+écriture sur fd3 :
# - empêche wob de recevoir EOF entre deux écritures
# - wob hérite du fd et reste vivant même après la fin de ce script
exec 3<> "$FIFO"
wob --config "$HOME/.config/wob.ini" <&3 &
disown $!
