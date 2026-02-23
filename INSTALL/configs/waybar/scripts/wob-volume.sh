#!/usr/bin/env bash
# wob-volume.sh — scroll volume + feedback wob
# Usage: wob-volume.sh up|down|mute

STEP=5
FIFO="/tmp/wob.fifo"

get_vol() {
    wpctl get-volume @DEFAULT_AUDIO_SINK@ 2>/dev/null | \
        LC_ALL=C awk '{v=int($2*100); if(v>100)v=100; print v}'
}

case "$1" in
    up)
        wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ "${STEP}%+"
        ;;
    down)
        wpctl set-volume @DEFAULT_AUDIO_SINK@ "${STEP}%-"
        ;;
    mute)
        wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
        ;;
esac

# Feedback wob si le daemon tourne
if [[ -p "$FIFO" ]] && pgrep -x wob >/dev/null 2>&1; then
    echo "$(get_vol)" > "$FIFO"
fi
