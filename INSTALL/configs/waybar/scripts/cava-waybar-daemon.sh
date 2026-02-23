#!/usr/bin/env bash
# cava-waybar-daemon.sh — lance CAVA en daemon → /tmp/waybar_cava
# Appeler au démarrage de la session

pkill -f "cava -p.*cava-waybar.cfg" 2>/dev/null
sleep 0.3

CFG="$HOME/.config/waybar/cava-waybar.cfg"
[[ ! -f "$CFG" ]] && { echo "Config manquante : $CFG"; exit 1; }

cava -p "$CFG" > /tmp/waybar_cava &
echo "CAVA daemon lancé (PID $!)"
