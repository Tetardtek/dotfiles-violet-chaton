#!/usr/bin/env bash
# wob-brightness.sh — scroll luminosité + feedback wob
# Usage: wob-brightness.sh up|down

STEP=5
FIFO="/tmp/wob.fifo"

case "$1" in
    up)   brightnessctl set "${STEP}%+" -q ;;
    down) brightnessctl set "${STEP}%-" -q ;;
esac

# Feedback overlay
if [[ -p "$FIFO" ]]; then
    BRIGHT=$(brightnessctl -m 2>/dev/null | awk -F, '{gsub(/%/,"",$4); print int($4)}')
    echo "b:${BRIGHT}" > "$FIFO"
fi
