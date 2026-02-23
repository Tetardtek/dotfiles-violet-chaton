#!/usr/bin/env bash
# cava-read.sh — lit /tmp/waybar_cava → JSON waybar (interval: 1)
# Lance automatiquement le démon cava-waybar.sh si absent.

OUT="/tmp/waybar_cava"
PID="/tmp/waybar_cava.pid"
DAEMON="$HOME/.config/waybar/scripts/cava-waybar.sh"

# Démarrer le démon si pas actif
if [[ ! -f "$PID" ]] || ! kill -0 "$(cat "$PID" 2>/dev/null)" 2>/dev/null; then
    nohup bash "$DAEMON" >/dev/null 2>&1 &
fi

# Lire et retourner le JSON
if [[ -f "$OUT" ]]; then
    BAR=$(tail -1 "$OUT" 2>/dev/null)
    [[ -n "$BAR" ]] && printf '{"text":"%s","tooltip":"","class":""}\n' "$BAR" && exit 0
fi

printf '{"text":"▁▁▁▁▁▁▁▁","tooltip":"","class":"muted"}\n'
