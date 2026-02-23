#!/usr/bin/env bash
# launcher.sh — boite à outils violet-chaton avec historique (wofi)

STYLE="$HOME/.config/wofi/style.css"
TERM="cosmic-term"
HIST_FILE="$HOME/.cache/waybar-launcher.hist"
MAX_HIST=5
HIST_ICON="󰄴  "

SEP="<span foreground='#3d2454'>────────────────────</span>"
HIST_HDR="<span foreground='#8be9fd' size='small'>  RÉCENTS</span>"

# ── Favoris (ordre fixe, toujours en haut) ───────────────────────────────────
FAVORITES=(
    "󰖟  Vivaldi"
    "󰆍  Terminal"
    "󰉋  Nemo"
    "󰨞  VSCode"
    "󰙯  Vesktop"
    "󱑤  btop"
    "󰊢  lazygit"
    "󰘳  pipes.sh"
    "󱒕  cbonsai"
)

# ── Historique (dernières applis lancées, dédoublonné) ───────────────────────
RECENT_ENTRIES=""
if [[ -f "$HIST_FILE" ]]; then
    RECENT_ENTRIES=$(awk '!seen[$0]++' "$HIST_FILE" | head -"$MAX_HIST" | \
        sed "s|^|${HIST_ICON}|")
fi

# ── Toutes les applis installées ─────────────────────────────────────────────
ALL_APPS=$(for f in \
        /usr/share/applications/*.desktop \
        ~/.local/share/applications/*.desktop \
        /var/lib/flatpak/exports/share/applications/*.desktop \
        ~/.local/share/flatpak/exports/share/applications/*.desktop; do
    [[ -f "$f" ]] || continue
    grep -q "^NoDisplay=true"    "$f" && continue
    grep -q "^Type=Application"  "$f" || continue
    grep -m1 "^Name=" "$f" | cut -d= -f2-
done | sort -u)

# ── Construction de la liste ─────────────────────────────────────────────────
FULL_LIST=$(
    printf '%s\n' "${FAVORITES[@]}"
    if [[ -n "$RECENT_ENTRIES" ]]; then
        echo "$SEP"
        echo "$HIST_HDR"
        echo "$RECENT_ENTRIES"
    fi
    echo "$SEP"
    echo "$ALL_APPS"
)

# ── Affichage wofi ───────────────────────────────────────────────────────────
CHOICE=$(echo "$FULL_LIST" | \
    wofi --dmenu \
         --prompt "  " \
         --style "$STYLE" \
         --width 300 \
         --height 500 \
         --x 16 \
         --y 70 \
         --location top_left)

[[ -z "$CHOICE" ]] && exit 0

# Enlever le préfixe historique si présent
CHOICE_CLEAN="${CHOICE#$HIST_ICON}"

# ── Mise à jour historique ────────────────────────────────────────────────────
save_history() {
    local app="$1"
    # Ignorer les favoris (déjà toujours visibles), séparateurs et power
    case "$app" in
        "󰖟  Vivaldi"|"󰆍  Terminal"|"󰉋  Nemo"|"󰨞  VSCode"|"󰙯  Vesktop") return ;;
        "󱑤  btop"|"󰊢  lazygit"|"󰘳  pipes.sh"|"󱒕  cbonsai") return ;;
        *"────"*|*"RÉCENTS"*|"") return ;;
    esac
    # Dépiler l'entrée existante et rajouter en tête
    local tmp
    tmp=$(grep -vxF "$app" "$HIST_FILE" 2>/dev/null)
    printf '%s\n%s\n' "$app" "$tmp" | head -20 > "$HIST_FILE"
}

# ── Actions ───────────────────────────────────────────────────────────────────
case "$CHOICE_CLEAN" in
    "󰖟  Vivaldi")       vivaldi-stable & ;;
    "󰆍  Terminal")      $TERM & ;;
    "󰉋  Nemo")          nemo & ;;
    "󰨞  VSCode")        code & ;;
    "󰙯  Vesktop")       flatpak run dev.vencord.Vesktop & ;;
    "󱑤  btop")          $TERM --command btop & ;;
    "󰊢  lazygit")       $TERM --command lazygit & ;;
    "󰘳  pipes.sh")      $TERM --command pipes.sh & ;;
    "󱒕  cbonsai")       $TERM --command bash -c "cbonsai -l; read" & ;;
    *"────"*|*"RÉCENTS"*) : ;;
    *)
        save_history "$CHOICE_CLEAN"
        DESKTOP=$(grep -rlm1 "^Name=$CHOICE_CLEAN$" \
            /usr/share/applications \
            ~/.local/share/applications \
            /var/lib/flatpak/exports/share/applications \
            ~/.local/share/flatpak/exports/share/applications \
            2>/dev/null | head -1)
        [[ -n "$DESKTOP" ]] && gtk-launch "$(basename "${DESKTOP%.desktop}")" &
        ;;
esac
