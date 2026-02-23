#!/usr/bin/env bash
# disks.sh — liste les vrais systèmes de fichiers montés → JSON waybar
# Exclut tmpfs, devtmpfs, squashfs (snap), overlay, efi, etc.

TEXT=""
TOOLTIP="󰋊 Disques\n"

while IFS= read -r line; do
    fs=$(awk '{print $1}' <<< "$line")
    size=$(awk '{print $2}' <<< "$line")
    used=$(awk '{print $3}' <<< "$line")
    avail=$(awk '{print $4}' <<< "$line")
    pct=$(awk '{print $5}' <<< "$line")
    mnt=$(awk '{print $6}' <<< "$line")

    # Exclure mounts sans intérêt
    [[ "$mnt" == /snap/* ]]       && continue
    [[ "$mnt" == /boot/efi ]]     && continue
    [[ "$mnt" == /boot ]]         && continue
    [[ "$mnt" == /recovery ]]     && continue
    [[ "$mnt" == /run* ]]         && continue
    [[ "$mnt" == /sys* ]]         && continue
    [[ "$mnt" == /proc* ]]        && continue
    [[ "$mnt" == /dev* ]]         && continue

    # Icône selon le point de montage
    case "$mnt" in
        /)       icon="󰋊" ;;
        /home)   icon="󱂵" ;;
        /data*)  icon="󱦡" ;;
        /media*) icon="󰆼" ;;
        /mnt*)   icon="󱛟" ;;
        *)       icon="󰋊" ;;
    esac

    # Texte compact : icône + montage court + espace utilisé
    label=$(basename "$mnt")
    [[ "$mnt" == "/" ]] && label="/"
    [[ -n "$TEXT" ]] && TEXT+="  "
    TEXT+="${icon} ${label}: ${used}"

    TOOLTIP+="${icon} ${mnt}\n    Utilisé : ${used} / ${size} (${pct})\n    Libre   : ${avail}\n"

done < <(df -hP --exclude-type=tmpfs \
             --exclude-type=devtmpfs \
             --exclude-type=squashfs \
             --exclude-type=overlay \
             --exclude-type=fuse.portal \
             --exclude-type=efivarfs \
             2>/dev/null | tail -n +2 | sort -k6)

if [[ -z "$TEXT" ]]; then
    printf '{"text":"󰋊 N/A","tooltip":"Aucun disque détecté","class":"unavailable"}\n'
else
    # Échapper uniquement les guillemets pour JSON (\n reste tel quel = saut de ligne)
    TOOLTIP_JSON=$(printf '%s' "$TOOLTIP" | sed 's/"/\\"/g')
    printf '{"text":"%s","tooltip":"%s"}\n' "$TEXT" "$TOOLTIP_JSON"
fi
