#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
#   violet-chaton — script d'installation automatique
#   Usage : bash install.sh
# ══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Initialiser le log avant de sourcer lib.sh pour que tous les sous-scripts
# partagent exactement le même fichier (INSTALL_LOG exporté = hérité par bash)
export INSTALL_LOG="$HOME/violet-chaton-install-$(date +%Y%m%d-%H%M%S).log"

source "$SCRIPT_DIR/scripts/lib.sh"

# ── Refus root ────────────────────────────────────────────────────────────────
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}${BOLD}  ERREUR : Ne pas lancer ce script en tant que root !${RESET}"
    echo -e "  Lance-le en tant qu'utilisateur normal : ${CYAN}bash install.sh${RESET}"
    echo -e "  ${MUTED}(sudo sera demandé automatiquement quand nécessaire)${RESET}"
    exit 1
fi

# ── Vérifications préalables ──────────────────────────────────────────────────
check_requirements() {
    local ok=true
    for cmd in curl git sudo unzip; do
        has_cmd "$cmd" || { warn "$cmd manquant — installer avec : sudo apt install $cmd"; ok=false; }
    done
    [ "$ok" = false ] && exit 1
}

# ── Menu principal ─────────────────────────────────────────────────────────────
show_menu() {
    echo -e "${PURPLE}  Que veux-tu faire ?${RESET}"
    echo ""
    echo -e "  ${CYAN}1)${RESET} Installation complète ${MUTED}(outils + configs + thèmes)${RESET}"
    echo -e "  ${CYAN}2)${RESET} Paquets apt seulement"
    echo -e "  ${CYAN}3)${RESET} Binaires manuels seulement ${MUTED}(lazygit, yazi, glow…)${RESET}"
    echo -e "  ${CYAN}4)${RESET} Déployer configs et thèmes seulement"
    echo -e "  ${RED}q)${RESET} Quitter"
    echo ""
    echo -ne "${PINK}  Choix : ${RESET}"
    read -r choice
}

run_step() {
    local script="$SCRIPT_DIR/scripts/$1"
    if [ -f "$script" ]; then
        bash "$script"
    else
        fail "Script introuvable : $1"
    fi
}

# ── Lancement ─────────────────────────────────────────────────────────────────
clear
banner
check_requirements
show_menu

case "$choice" in
    1)
        _log "Choix : Installation complète (1/2/3)"
        echo ""
        echo -e "${MUTED}  [1/3] Paquets apt${RESET}"
        run_step "01-packages-apt.sh"
        echo ""
        echo -e "${MUTED}  [2/3] Binaires manuels${RESET}"
        run_step "02-packages-manual.sh"
        echo ""
        echo -e "${MUTED}  [3/3] Configs et thèmes${RESET}"
        run_step "03-deploy-configs.sh"
        ;;
    2) _log "Choix : Paquets apt seulement" ; run_step "01-packages-apt.sh" ;;
    3) _log "Choix : Binaires manuels seulement" ; run_step "02-packages-manual.sh" ;;
    4) _log "Choix : Configs et thèmes seulement" ; run_step "03-deploy-configs.sh" ;;
    q|Q) echo -e "\n${MUTED}  Au revoir q:D${RESET}\n"; exit 0 ;;
    *) fail "Choix invalide"; exit 1 ;;
esac

banner_done
show_summary

echo -ne "${MUTED}  Appuie sur Entrée pour lancer zsh...${RESET}"
read -r _
echo ""

exec zsh
