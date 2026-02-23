#!/usr/bin/env bash
# gpu.sh — NVIDIA GPU stats → JSON waybar

DATA=$(nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total \
    --format=csv,noheader,nounits 2>/dev/null)

if [[ -z "$DATA" ]]; then
    echo '{"text":"","tooltip":"GPU non disponible","class":"","percentage":0}'
    exit 0
fi

LOAD=$(echo "$DATA" | awk -F', ' '{print $1}')
TEMP=$(echo "$DATA" | awk -F', ' '{print $2}')
MEM_USED=$(echo "$DATA" | awk -F', ' '{print $3}')
MEM_TOTAL=$(echo "$DATA" | awk -F', ' '{print $4}')

if   (( LOAD > 90 )); then CLASS="critical"
elif (( LOAD > 70 )); then CLASS="warning"
else                       CLASS="normal"
fi

TEXT="󰢮 ${LOAD}%  ${TEMP}°"
TOOLTIP="󰢮 GPU\nCharge : ${LOAD}%\nTempérature : ${TEMP}°C\nVRAM : ${MEM_USED} / ${MEM_TOTAL} MiB"

printf '{"text":"%s","tooltip":"%s","class":"%s","percentage":%s}\n' \
    "$TEXT" "$TOOLTIP" "$CLASS" "$LOAD"
