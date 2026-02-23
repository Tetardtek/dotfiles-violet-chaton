#!/usr/bin/env bash
# network.sh — bande passante réseau → JSON waybar

STATE_FILE="/tmp/waybar_net_state"

# Détecter l'interface active
IFACE=""
for candidate in enp7s0 enp6s0 eth0; do
    if [[ -d "/sys/class/net/$candidate" && "$(cat /sys/class/net/$candidate/operstate 2>/dev/null)" == "up" ]]; then
        IFACE="$candidate"; TYPE="eth"; break
    fi
done
if [[ -z "$IFACE" ]]; then
    for candidate in wlp8s0 wlp0s20f3 wlan0; do
        if [[ -d "/sys/class/net/$candidate" && "$(cat /sys/class/net/$candidate/operstate 2>/dev/null)" == "up" ]]; then
            IFACE="$candidate"; TYPE="wifi"; break
        fi
    done
fi

if [[ -z "$IFACE" ]]; then
    echo '{"text":"󰤭 déco","tooltip":"Déconnecté","class":"disconnected"}'
    exit 0
fi

RX_NOW=$(cat "/sys/class/net/$IFACE/statistics/rx_bytes" 2>/dev/null || echo 0)
TX_NOW=$(cat "/sys/class/net/$IFACE/statistics/tx_bytes" 2>/dev/null || echo 0)
NOW=$(date +%s%N)

if [[ -f "$STATE_FILE" ]]; then
    read -r RX_PREV TX_PREV TIME_PREV < "$STATE_FILE"
    ELAPSED=$(( (NOW - TIME_PREV) / 1000000 ))   # ms
    if (( ELAPSED > 0 )); then
        DOWN_BPS=$(( (RX_NOW - RX_PREV) * 1000 / ELAPSED ))
        UP_BPS=$(( (TX_NOW - TX_PREV) * 1000 / ELAPSED ))
    else
        DOWN_BPS=0; UP_BPS=0
    fi
else
    DOWN_BPS=0; UP_BPS=0
fi

echo "$RX_NOW $TX_NOW $NOW" > "$STATE_FILE"

# Formatage humain
human() {
    local B=$1
    if   (( B >= 1073741824 )); then LC_ALL=C awk "BEGIN{printf \"%.1fG\", $B/1073741824}"
    elif (( B >=    1048576 )); then LC_ALL=C awk "BEGIN{printf \"%.1fM\", $B/1048576}"
    elif (( B >=       1024 )); then LC_ALL=C awk "BEGIN{printf \"%.0fK\", $B/1024}"
    else echo "${B}B"
    fi
}

DOWN_H=$(human $DOWN_BPS)
UP_H=$(human $UP_BPS)
RX_TOTAL=$(human $RX_NOW)
TX_TOTAL=$(human $TX_NOW)

ICON_DOWN="󰇚"; ICON_UP="󰕒"
[[ "$TYPE" == "wifi" ]] && ICON_NET="󰤨" || ICON_NET="󰈀"

TEXT="${ICON_DOWN} ${DOWN_H}/s  ${ICON_UP} ${UP_H}/s"
TOOLTIP="${ICON_NET} ${IFACE}\n${ICON_DOWN} ${DOWN_H}/s  ${ICON_UP} ${UP_H}/s\n\n󰇚 Total reçu   : ${RX_TOTAL}\n󰕒 Total envoyé : ${TX_TOTAL}"

printf '{"text":"%s","tooltip":"%s","class":"%s"}\n' "$TEXT" "$TOOLTIP" "$TYPE"
