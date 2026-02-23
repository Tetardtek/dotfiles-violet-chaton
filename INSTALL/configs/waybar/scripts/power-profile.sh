#!/usr/bin/env bash
# power-profile.sh — profil énergie ACPI → JSON waybar
#   Sans argument : affiche le profil courant en JSON
#   --toggle      : cycle vers le profil suivant + applique la luminosité

# Luminosité par profil (%)
BRIGHT_performance=80
BRIGHT_balanced=60
BRIGHT_low_power=30   # low-power → clé sans tiret

_bright_for() {
    local key="${1//-/_}"
    local var="BRIGHT_${key}"
    echo "${!var:-60}"
}

if [[ "$1" == "--toggle" ]]; then
    CURRENT=$(cat /sys/firmware/acpi/platform_profile 2>/dev/null || echo "balanced")
    case "$CURRENT" in
        performance) NEXT="balanced"     ;;
        balanced)    NEXT="low-power"    ;;
        *)           NEXT="performance"  ;;
    esac

    echo "$NEXT" > /sys/firmware/acpi/platform_profile

    # Appliquer la luminosité du nouveau profil
    BRIGHT=$(_bright_for "$NEXT")
    brightnessctl set "${BRIGHT}%" -q

    # Feedback overlay
    if [[ -p /tmp/wob.fifo ]]; then
        echo "b:${BRIGHT}" > /tmp/wob.fifo 2>/dev/null || true
    fi

    # Rafraîchir le module waybar
    pkill -RTMIN+8 waybar
    exit 0
fi

# ── Affichage JSON ────────────────────────────────────────────────────────────

PROFILE=$(cat /sys/firmware/acpi/platform_profile 2>/dev/null || echo "unknown")

case "$PROFILE" in
    performance) ICON="󱐋"; CLASS="performance" ;;
    balanced)    ICON="󰾅"; CLASS="balanced"    ;;
    low-power)   ICON="󰌪"; CLASS="low-power"   ;;
    *)           ICON="󰒓"; CLASS="unknown"     ;;
esac

printf '{"text":"%s","tooltip":"Profil énergie : %s","class":"%s"}\n' \
    "$ICON" "$PROFILE" "$CLASS"
