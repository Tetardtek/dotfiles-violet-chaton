#!/usr/bin/env bash
# cpu-temp.sh — température CPU auto-détection → JSON waybar
# Priorité 1 : thermal zone x86_pkg_temp (Intel) ou k10temp (AMD)
# Priorité 2 : hwmon coretemp / k10temp / zenpower
# Retourne vide si aucune source trouvée

emit() {
    local temp=$1
    local cls="normal"
    (( temp >= 80 )) && cls="critical"
    (( temp >= 65 && temp < 80 )) && cls="warning"
    printf '{"text":" %d°","tooltip":"CPU %d°C","class":"%s","percentage":%d}\n' \
        "$temp" "$temp" "$cls" "$temp"
    exit 0
}

# Priorité 1 — thermal_zone x86_pkg_temp (Intel) / TCPU / k10temp (AMD)
for zone in /sys/class/thermal/thermal_zone*/; do
    zone_type=$(cat "${zone}type" 2>/dev/null) || continue
    case "$zone_type" in
        x86_pkg_temp|k10temp|TCPU|cpu_thermal)
            temp_raw=$(cat "${zone}temp" 2>/dev/null) || continue
            emit $(( temp_raw / 1000 ))
            ;;
    esac
done

# Priorité 2 — hwmon coretemp (Intel desktop) ou k10temp (AMD)
for hw in /sys/class/hwmon/hwmon*/; do
    hw_name=$(cat "${hw}name" 2>/dev/null) || continue
    case "$hw_name" in
        coretemp|k10temp|zenpower|amd_energy)
            for f in "${hw}temp1_input" "${hw}temp2_input"; do
                [[ -r "$f" ]] || continue
                temp_raw=$(cat "$f" 2>/dev/null) || continue
                emit $(( temp_raw / 1000 ))
            done
            ;;
    esac
done

# Aucune source — module masqué
printf '{"text":"","class":"unavailable"}\n'
