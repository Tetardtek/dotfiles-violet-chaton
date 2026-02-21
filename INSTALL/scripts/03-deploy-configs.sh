#!/bin/bash
# ── violet-chaton : déploiement des configs et thèmes ─────────────────────────
source "$(dirname "$0")/lib.sh"

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
THEMES="$SCRIPT_DIR/themes"
CONFIGS="$SCRIPT_DIR/configs"
BACKUP_DIR="$HOME/.config/violet-chaton-backups/$(date +%Y%m%d-%H%M%S)"

deploy_file() {
    local src="$1"
    local dst="$2"
    ensure_dir "$(dirname "$dst")"
    if [ -f "$dst" ]; then
        local rel="${dst#"$HOME/"}"
        ensure_dir "$BACKUP_DIR/$(dirname "$rel")"
        cp "$dst" "$BACKUP_DIR/$rel" 2>/dev/null
    fi
    if cp "$src" "$dst" 2>/dev/null; then
        ok "$(basename "$dst")"
    else
        fail "$(basename "$dst")"
    fi
}

# ── Configs shell ──────────────────────────────────────────────────────────────
section "Configs shell"
deploy_file "$CONFIGS/zshrc"    "$HOME/.zshrc"
deploy_file "$CONFIGS/bashrc"   "$HOME/.bashrc"

# Préserver user.name et user.email avant d'écraser le gitconfig
_GIT_NAME=$(git config --global user.name 2>/dev/null)
_GIT_EMAIL=$(git config --global user.email 2>/dev/null)
deploy_file "$CONFIGS/gitconfig" "$HOME/.gitconfig"
if [ -n "$_GIT_NAME" ]; then
    git config --global user.name "$_GIT_NAME"
    ok "user.name restauré : $_GIT_NAME"
fi
if [ -n "$_GIT_EMAIL" ]; then
    git config --global user.email "$_GIT_EMAIL"
    ok "user.email restauré : $_GIT_EMAIL"
fi

# ── Configs outils ─────────────────────────────────────────────────────────────
section "Configs outils"
deploy_file "$CONFIGS/starship.toml"    "$HOME/.config/starship.toml"
deploy_file "$CONFIGS/bat.conf"         "$HOME/.config/bat/config"
deploy_file "$CONFIGS/btop.conf"        "$HOME/.config/btop/btop.conf"
deploy_file "$CONFIGS/fastfetch.jsonc"  "$HOME/.config/fastfetch/config.jsonc"
deploy_file "$CONFIGS/atuin.toml"       "$HOME/.config/atuin/config.toml"
deploy_file "$CONFIGS/lazygit.yml"      "$HOME/.config/lazygit/config.yml"
deploy_file "$CONFIGS/yazi.toml"        "$HOME/.config/yazi/yazi.toml"
deploy_file "$CONFIGS/glow.yml"         "$HOME/.config/glow/glow.yml"

# ── Thèmes CLI ─────────────────────────────────────────────────────────────────
section "Thèmes violet-chaton (CLI)"
deploy_file "$THEMES/violet-chaton.theme.css" \
            "$HOME/.config/vesktop/themes/violet-chaton.theme.css"
# Flatpak — uniquement si Vesktop flatpak est déjà installé
if [ -d "$HOME/.var/app/dev.vencord.Vesktop" ]; then
    deploy_file "$THEMES/violet-chaton.theme.css" \
                "$HOME/.var/app/dev.vencord.Vesktop/config/vesktop/themes/violet-chaton.theme.css"
fi
deploy_file "$THEMES/violet-chaton-bat.tmTheme"   "$HOME/.config/bat/themes/violet-chaton.tmTheme"
deploy_file "$THEMES/violet-chaton-btop.theme"    "$HOME/.config/btop/themes/violet-chaton.theme"
deploy_file "$THEMES/violet-chaton-atuin.toml"    "$HOME/.config/atuin/themes/violet-chaton.toml"
deploy_file "$THEMES/violet-chaton-cava.conf"     "$HOME/.config/cava/config"
deploy_file "$THEMES/violet-chaton-yazi.toml"     "$HOME/.config/yazi/theme.toml"
deploy_file "$THEMES/violet-chaton-ls-colors.sh"  "$HOME/.local/share/violet-chaton/violet-chaton-ls-colors.sh"

# ── COSMIC Desktop ─────────────────────────────────────────────────────────────
section "COSMIC — thème, terminal et toolkit"
COSMIC_SRC="$THEMES/cosmic"
COSMIC_DST="$HOME/.config/cosmic"

step "COSMIC Theme Dark..."
backup_dir "$COSMIC_DST/com.system76.CosmicTheme.Dark/v1"
ensure_dir "$COSMIC_DST/com.system76.CosmicTheme.Dark/v1"
if cp "$COSMIC_SRC/com.system76.CosmicTheme.Dark/v1/"* "$COSMIC_DST/com.system76.CosmicTheme.Dark/v1/" 2>/dev/null; then
    ok "CosmicTheme.Dark"
else
    fail "CosmicTheme.Dark"
fi

step "COSMIC Theme Mode (dark)..."
backup_dir "$COSMIC_DST/com.system76.CosmicTheme.Mode/v1"
ensure_dir "$COSMIC_DST/com.system76.CosmicTheme.Mode/v1"
if cp "$COSMIC_SRC/com.system76.CosmicTheme.Mode/v1/is_dark" "$COSMIC_DST/com.system76.CosmicTheme.Mode/v1/" 2>/dev/null; then
    ok "CosmicTheme.Mode"
else
    fail "CosmicTheme.Mode"
fi

step "COSMIC Terminal..."
backup_dir "$COSMIC_DST/com.system76.CosmicTerm/v1"
ensure_dir "$COSMIC_DST/com.system76.CosmicTerm/v1"
if cp "$COSMIC_SRC/com.system76.CosmicTerm/v1/"* "$COSMIC_DST/com.system76.CosmicTerm/v1/" 2>/dev/null; then
    ok "CosmicTerm"
else
    fail "CosmicTerm"
fi

# ── GTK3 — thème violet-chaton ─────────────────────────────────────────────
section "GTK3 — thème violet-chaton"
ensure_dir "$HOME/.config/gtk-3.0"
deploy_file "$THEMES/violet-chaton-gtk.css" "$HOME/.config/gtk-3.0/gtk.css"

# ── Nemo — gestionnaire de fichiers ────────────────────────────────────────
section "Nemo — configuration et thème"

step "Nemo comme gestionnaire de fichiers par défaut..."
if has_cmd xdg-mime; then
    xdg-mime default nemo.desktop inode/directory 2>/dev/null && \
    xdg-mime default nemo.desktop application/x-gnome-saved-search 2>/dev/null && \
    ok "Nemo défini par défaut" || warn "xdg-mime Nemo échoué"
else
    warn "xdg-mime non disponible — à faire manuellement"
fi

step "Préférences Nemo (gsettings)..."
if has_cmd gsettings; then
    gsettings set org.nemo.preferences default-folder-viewer 'icon-view' 2>/dev/null
    gsettings set org.nemo.preferences show-hidden-files false 2>/dev/null
    gsettings set org.nemo.preferences show-image-thumbnails 'always' 2>/dev/null
    gsettings set org.nemo.icon-view default-zoom-level 'standard' 2>/dev/null
    gsettings set org.nemo.list-view default-zoom-level 'small' 2>/dev/null
    ok "Préférences Nemo appliquées"
else
    warn "gsettings non disponible — préférences Nemo à configurer manuellement"
fi

step "Application du thème d'icônes candy-icons (GTK)..."
if has_cmd gsettings; then
    gsettings set org.gnome.desktop.interface icon-theme 'candy-icons-master' 2>/dev/null && \
        ok "icon-theme candy-icons-master (gsettings)" || warn "gsettings icon-theme échoué"
else
    warn "gsettings non disponible — thème d'icônes GTK à appliquer manuellement"
fi

step "COSMIC Toolkit (polices, icônes)..."
backup_dir "$COSMIC_DST/com.system76.CosmicTk/v1"
ensure_dir "$COSMIC_DST/com.system76.CosmicTk/v1"
if cp "$COSMIC_SRC/com.system76.CosmicTk/v1/"* "$COSMIC_DST/com.system76.CosmicTk/v1/" 2>/dev/null; then
    ok "CosmicTk"
else
    fail "CosmicTk"
fi

# ── Vivaldi ─────────────────────────────────────────────────────────────────────
section "Vivaldi — thème Rice Violet-Chaton"
VIVALDI_PREFS="$HOME/.config/vivaldi/Default/Preferences"

if [ ! -f "$VIVALDI_PREFS" ]; then
    echo ""
    echo -e "${PINK}${BOLD}  ┌──────────────────────────────────────────────────────────┐${RESET}"
    echo -e "${PINK}${BOLD}  │  Vivaldi n'a pas encore été lancé.                       │${RESET}"
    echo -e "${PINK}  │  ${TEXT}Lance Vivaldi maintenant, attends qu'il démarre,${PINK}         │${RESET}"
    echo -e "${PINK}  │  ${TEXT}puis ferme-le et appuie sur Entrée pour continuer.${PINK}       │${RESET}"
    echo -e "${PINK}${BOLD}  └──────────────────────────────────────────────────────────┘${RESET}"
    echo ""
    read -rp "  → Appuie sur Entrée une fois Vivaldi fermé..." _
    echo ""
fi

if [ ! -f "$VIVALDI_PREFS" ]; then
    warn "Preferences Vivaldi toujours introuvable — thème non injecté"
else
    step "Injection du thème Rice Violet-Chaton..."
    python3 - "$VIVALDI_PREFS" "$THEMES/violet-chaton-vivaldi.json" <<'PYEOF'
import json, sys

prefs_path = sys.argv[1]
theme_path = sys.argv[2]

with open(prefs_path, 'r') as f:
    prefs = json.load(f)

with open(theme_path, 'r') as f:
    new_themes = json.load(f)

theme = new_themes[0]
theme_id = theme['id']

# Injecter dans vivaldi.themes.user (dédoublonner par id)
user_themes = prefs.setdefault('vivaldi', {}).setdefault('themes', {}).setdefault('user', [])
user_themes = [t for t in user_themes if t.get('id') != theme_id]
user_themes.append(theme)
prefs['vivaldi']['themes']['user'] = user_themes

# Activer le thème (dark et light schedule)
prefs.setdefault('vivaldi', {}).setdefault('theme', {}).setdefault('schedule', {}).setdefault('o_s', {})
prefs['vivaldi']['theme']['schedule']['o_s']['light'] = theme_id
prefs['vivaldi']['theme']['schedule']['o_s']['dark'] = theme_id

with open(prefs_path, 'w') as f:
    json.dump(prefs, f, separators=(',', ':'))

print("ok")
PYEOF
    if [ $? -eq 0 ]; then
        ok "Vivaldi thème injecté"
        info "→ Redémarre Vivaldi pour appliquer le thème"
    else
        fail "Vivaldi injection échouée"
    fi
fi

# ── Logo fastfetch ─────────────────────────────────────────────────────────────
section "Logo fastfetch"
if [ -f "$SCRIPT_DIR/assets/violet-chaton-logo.png" ]; then
    deploy_file "$SCRIPT_DIR/assets/violet-chaton-logo.png" "$HOME/.config/fastfetch/violet-chaton-logo.png"
else
    warn "Logo non trouvé dans assets/ — fastfetch démarrera sans logo"
fi

# ── Rebuild caches ─────────────────────────────────────────────────────────────
section "Rebuild des caches"

step "Cache bat (thème violet-chaton)..."
if has_cmd batcat; then
    batcat cache --build &>/dev/null && ok "bat cache" || fail "bat cache"
fi

step "PATH ~/.local/bin..."
export PATH="$HOME/.local/bin:$PATH"

# ── Étapes manuelles ───────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}${BOLD}  ╔══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${YELLOW}${BOLD}  ║        Étapes manuelles requises après install           ║${RESET}"
echo -e "${YELLOW}${BOLD}  ╠══════════════════════════════════════════════════════════╣${RESET}"
echo -e "${YELLOW}  ║  ${TEXT}1. Vivaldi : lance le navigateur une fois avant install${YELLOW}  ║${RESET}"
echo -e "${YELLOW}  ║  ${MUTED}   puis relance ce script si le thème n'est pas injecté${YELLOW} ║${RESET}"
echo -e "${YELLOW}${BOLD}  ╚══════════════════════════════════════════════════════════╝${RESET}"
echo ""

if [ -d "$BACKUP_DIR" ]; then
    echo -e "  ${MUTED}Configs précédentes sauvegardées dans :${RESET}"
    echo -e "  ${TEXT}$BACKUP_DIR${RESET}"
    echo ""
fi
