#!/bin/bash
# ── violet-chaton : fonctions partagées ───────────────────────────────────────

PINK='\033[38;2;255;121;198m'
PURPLE='\033[38;2;231;156;254m'
CYAN='\033[38;2;139;233;253m'
GREEN='\033[38;2;166;227;161m'
YELLOW='\033[38;2;249;226;175m'
RED='\033[38;2;243;139;168m'
MUTED='\033[38;2;108;112;134m'
TEXT='\033[38;2;248;248;242m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Log ────────────────────────────────────────────────────────────────────────
# INSTALL_LOG peut être pré-exporté par install.sh pour que tous les sous-scripts
# partagent le même fichier. Sinon, chaque script crée le sien.
: "${INSTALL_LOG:=$HOME/violet-chaton-install-$(date +%Y%m%d-%H%M%S).log}"
export INSTALL_LOG

_log() {
    printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$1" >> "$INSTALL_LOG"
}

# ── Bannières ─────────────────────────────────────────────────────────────────
banner() {
    echo ""
    echo -e "${PINK}${BOLD}  ╔══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${PINK}${BOLD}  ║                                                          ║${RESET}"
    echo -e "${PINK}${BOLD}  ║  ${PURPLE}░░  violet-chaton — setup automatique  ░░${PINK}   q:D        ║${RESET}"
    echo -e "${PINK}${BOLD}  ║                                                          ║${RESET}"
    echo -e "${PINK}${BOLD}  ╚══════════════════════════════════════════════════════════╝${RESET}"
    echo ""
    _log "════════════════════════════════════════"
    _log "  violet-chaton — installation démarrée"
    _log "════════════════════════════════════════"
}

banner_done() {
    _log ""
    _log "════════════════════════════════════════"
    _log "  Installation terminée"
    _log "════════════════════════════════════════"
    echo ""
    echo -e "${CYAN}${BOLD}  ╔══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${CYAN}${BOLD}  ║                                                          ║${RESET}"
    echo -e "${CYAN}${BOLD}  ║       ${GREEN}✓  Installation terminée avec succès !${CYAN}            ║${RESET}"
    echo -e "${CYAN}${BOLD}  ║   ${MUTED}Ouvre un nouveau terminal pour voir le résultat.${CYAN}      ║${RESET}"
    echo -e "${CYAN}${BOLD}  ║                                                          ║${RESET}"
    echo -e "${CYAN}${BOLD}  ╚══════════════════════════════════════════════════════════╝${RESET}"
    echo ""
    echo -e "  ${MUTED}Log complet :${RESET} ${TEXT}$INSTALL_LOG${RESET}"
    echo ""
}

# ── Fonctions de sortie (terminal + log) ───────────────────────────────────────
section() {
    echo ""
    echo -e "${PURPLE}${BOLD}  ┌─ $1 ${RESET}"
    _log ""
    _log "── $1"
}

step() {
    echo -e "${MUTED}  │  ${CYAN}→${RESET} $1"
    _log "   → $1"
}

ok() {
    echo -e "${MUTED}  │  ${GREEN}✓${RESET} $1"
    _log "   ✓ $1"
}

fail() {
    echo -e "${MUTED}  │  ${RED}✗${RESET} $1"
    _log "   ✗ ERREUR : $1"
}

warn() {
    echo -e "${MUTED}  │  ${YELLOW}!${RESET} $1"
    _log "   ! AVERT  : $1"
}

info() {
    echo -e "${MUTED}  │    ${MUTED}$1${RESET}"
    _log "     $1"
}

# ── Utilitaires ───────────────────────────────────────────────────────────────
has_cmd() {
    command -v "$1" &>/dev/null
}

ensure_dir() {
    mkdir -p "$1"
}

backup_dir() {
    local dir="$1"
    [ -d "$dir" ] || return 0
    # BACKUP_DIR est défini par 03-deploy-configs.sh
    [ -z "$BACKUP_DIR" ] && return 0
    local rel="${dir#"$HOME/"}"
    ensure_dir "$BACKUP_DIR/$rel"
    cp -r "$dir/." "$BACKUP_DIR/$rel/" 2>/dev/null
}

show_summary() {
    local log="$INSTALL_LOG"
    [ -f "$log" ] || return

    local successes errors warnings
    successes=$(grep -c "   ✓ " "$log" 2>/dev/null) || true; successes=${successes:-0}
    errors=$(grep -c " ✗ ERREUR" "$log" 2>/dev/null) || true; errors=${errors:-0}
    warnings=$(grep -c " ! AVERT" "$log" 2>/dev/null) || true; warnings=${warnings:-0}

    echo -e "${PURPLE}${BOLD}  ┌─ Résumé ────────────────────────────────────────────────────${RESET}"
    echo -e "  │  ${GREEN}✓ ${successes} réussis${RESET}   ${YELLOW}! ${warnings} avertissements${RESET}   ${RED}✗ ${errors} erreurs${RESET}"

    if [ "${errors:-0}" -gt 0 ] 2>/dev/null; then
        echo -e "  │"
        echo -e "  │  ${RED}Erreurs :${RESET}"
        grep " ✗ ERREUR" "$log" | sed 's/.*✗ ERREUR : //' | while IFS= read -r line; do
            echo -e "  │    ${RED}✗${RESET} $line"
        done
    fi

    if [ "${warnings:-0}" -gt 0 ] 2>/dev/null; then
        echo -e "  │"
        echo -e "  │  ${YELLOW}Avertissements :${RESET}"
        grep " ! AVERT" "$log" | sed 's/.*! AVERT  : //' | while IFS= read -r line; do
            echo -e "  │    ${YELLOW}!${RESET} $line"
        done
    fi
    echo ""
}
