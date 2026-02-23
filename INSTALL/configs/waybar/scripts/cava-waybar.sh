#!/usr/bin/env bash
# cava-waybar.sh — démon CAVA : écrit la visu dans /tmp/waybar_cava
# Lancé automatiquement par cava-read.sh, ne pas appeler directement.

BLOCKS=('▁' '▁' '▂' '▃' '▄' '▅' '▆' '▇' '█')
CFG="$HOME/.config/waybar/cava-waybar.cfg"
OUT="/tmp/waybar_cava"
PID="/tmp/waybar_cava.pid"

echo $$ > "$PID"

cleanup() { rm -f "$PID" "$OUT"; exit; }
trap cleanup EXIT INT TERM

cava -p "$CFG" | while IFS=';' read -ra VALUES; do
    BAR=""
    for v in "${VALUES[@]}"; do
        v="${v//[^0-9]/}"
        [[ -n "$v" ]] && BAR+="${BLOCKS[$v]:-▁}"
    done
    [[ -n "$BAR" ]] && printf '%s\n' "$BAR" > "$OUT"
done
