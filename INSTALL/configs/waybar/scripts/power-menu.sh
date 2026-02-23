#!/usr/bin/env bash
# power-menu.sh — menu power dédié (wofi)

STYLE="$HOME/.config/wofi/power-style.css"

ENTRIES=(
    "󰌾  Verrouiller"
    "󰒲  Veille"
    "󰑓  Redémarrer"
    "󰐥  Éteindre"
)

CHOICE=$(printf '%s\n' "${ENTRIES[@]}" | \
    wofi --dmenu \
         --prompt "⏻  " \
         --style "$STYLE" \
         --width 210 \
         --height 160 \
         --y 70 \
         --location top_right)

case "$CHOICE" in
    "󰌾  Verrouiller")  loginctl lock-session ;;
    "󰒲  Veille")       systemctl suspend ;;
    "󰑓  Redémarrer")   systemctl reboot ;;
    "󰐥  Éteindre")     systemctl poweroff ;;
esac
