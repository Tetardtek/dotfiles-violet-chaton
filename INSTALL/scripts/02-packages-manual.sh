#!/bin/bash
# ── violet-chaton : binaires GitHub ───────────────────────────────────────────
source "$(dirname "$0")/lib.sh"

BIN="$HOME/.local/bin"
ensure_dir "$BIN"

# Récupère le dernier tag d'un dépôt GitHub via la redirection web (sans API → pas de rate limit)
github_latest_tag() {
    curl -sL -o /dev/null -w "%{url_effective}" \
        "https://github.com/$1/releases/latest" 2>/dev/null \
        | sed 's|.*/tag/||' | tr -d '\r\n'
}

install_binary() {
    local name="$1"
    local url="$2"
    local extract="$3"   # "tar:fichier", "zip:fichier", "direct", "tar-dir:dir/fichier"

    step "Téléchargement de $name..."

    local tmp=$(mktemp -d)
    local archive="$tmp/archive"

    if ! curl -sL "$url" -o "$archive"; then
        fail "$name — échec du téléchargement"
        rm -rf "$tmp"
        return 1
    fi

    case "$extract" in
        tar:*)
            local file="${extract#tar:}"
            tar xf "$archive" -C "$tmp" 2>/dev/null
            local found; found=$(find "$tmp" -maxdepth 3 -name "$file" -type f | head -1)
            [ -n "$found" ] && mv "$found" "$BIN/$name" && chmod +x "$BIN/$name"
            ;;
        tar-dir:*)
            local path="${extract#tar-dir:}"
            tar xf "$archive" -C "$tmp" 2>/dev/null && \
            cp "$tmp/$path" "$BIN/$name" && chmod +x "$BIN/$name"
            ;;
        zip:*)
            local file="${extract#zip:}"
            unzip -o "$archive" -d "$tmp" 2>/dev/null && \
            find "$tmp" -name "$file" -exec cp {} "$BIN/$name" \; && chmod +x "$BIN/$name"
            ;;
        direct)
            cp "$archive" "$BIN/$name" && chmod +x "$BIN/$name"
            ;;
    esac

    rm -rf "$tmp"

    if [ -x "$BIN/$name" ]; then
        ok "$name"
    else
        fail "$name — installation échouée"
    fi
}

section "Installation des binaires manuels"

# lazygit
if has_cmd lazygit; then
    ok "lazygit (déjà installé)"
else
    LG_VER=$(github_latest_tag "jesseduffield/lazygit")
    if [ -z "$LG_VER" ]; then
        fail "lazygit — version introuvable"
    else
        install_binary "lazygit" \
            "https://github.com/jesseduffield/lazygit/releases/download/${LG_VER}/lazygit_${LG_VER#v}_linux_x86_64.tar.gz" \
            "tar:lazygit"
    fi
fi

# yazi
if has_cmd yazi; then
    ok "yazi (déjà installé)"
else
    install_binary "yazi" \
        "https://github.com/sxyazi/yazi/releases/latest/download/yazi-x86_64-unknown-linux-musl.zip" \
        "zip:yazi"
fi

# glow
if has_cmd glow; then
    ok "glow (déjà installé)"
else
    GLOW_VER=$(github_latest_tag "charmbracelet/glow")
    if [ -z "$GLOW_VER" ]; then
        fail "glow — version introuvable"
    else
        install_binary "glow" \
            "https://github.com/charmbracelet/glow/releases/download/${GLOW_VER}/glow_${GLOW_VER#v}_Linux_x86_64.tar.gz" \
            "tar-dir:glow_${GLOW_VER#v}_Linux_x86_64/glow"
    fi
fi

# tealdeer (tldr)
# La version n'est pas dans le nom du fichier → latest/download suffit, pas besoin de github_latest_tag
if [ -x "$BIN/tldr" ] && "$BIN/tldr" --version &>/dev/null; then
    ok "tldr (déjà installé)"
else
    install_binary "tldr" \
        "https://github.com/tealdeer-rs/tealdeer/releases/latest/download/tealdeer-linux-x86_64-musl" \
        "direct"
fi

# navi
if has_cmd navi; then
    ok "navi (déjà installé)"
else
    NAVI_VER=$(github_latest_tag "denisidoro/navi")
    if [ -z "$NAVI_VER" ]; then
        fail "navi — version introuvable"
    else
        install_binary "navi" \
            "https://github.com/denisidoro/navi/releases/download/${NAVI_VER}/navi-${NAVI_VER}-x86_64-unknown-linux-musl.tar.gz" \
            "tar:navi"
    fi
fi

# pipes.sh
if [ -x "$BIN/pipes.sh" ]; then
    ok "pipes.sh (déjà installé)"
else
    step "Téléchargement de pipes.sh..."
    curl -sL "https://raw.githubusercontent.com/pipeseroni/pipes.sh/master/pipes.sh" -o "$BIN/pipes.sh" && \
    chmod +x "$BIN/pipes.sh" && ok "pipes.sh" || fail "pipes.sh"
fi

section "starship (prompt)"
if has_cmd starship; then
    ok "starship (déjà installé)"
else
    step "Installation de starship..."
    _ts=$(mktemp)
    curl -sS https://starship.rs/install.sh -o "$_ts" 2>/dev/null && \
    sh "$_ts" --yes &>/dev/null && ok "starship" || fail "starship"
    rm -f "$_ts"
fi

section "atuin (historique shell)"
if has_cmd atuin; then
    ok "atuin (déjà installé)"
else
    step "Installation de atuin..."
    _ts=$(mktemp)
    curl --proto '=https' --tlsv1.2 -LsSf https://setup.atuin.sh -o "$_ts" 2>/dev/null && \
    sh "$_ts" &>/dev/null && ok "atuin" || fail "atuin"
    rm -f "$_ts"
fi

section "fastfetch (system info)"
if has_cmd fastfetch; then
    ok "fastfetch (déjà installé)"
else
    step "Téléchargement de fastfetch (.deb)..."
    tmp=$(mktemp -d)
    if curl -sL "https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb" \
            -o "$tmp/fastfetch.deb"; then
        sudo dpkg -i "$tmp/fastfetch.deb" &>/dev/null && \
        ok "fastfetch" || fail "fastfetch — échec dpkg -i"
    else
        fail "fastfetch — échec du téléchargement"
    fi
    rm -rf "$tmp"
fi

section "zinit (gestionnaire de plugins zsh)"
if [ ! -d "$HOME/.local/share/zinit/zinit.git" ]; then
    step "Installation de zinit..."
    mkdir -p "$HOME/.local/share/zinit"
    git clone https://github.com/zdharma-continuum/zinit "$HOME/.local/share/zinit/zinit.git" -q && \
    ok "zinit" || fail "zinit"
else
    ok "zinit (déjà installé)"
fi

section "Mise à jour du cache tldr"
step "Téléchargement des pages..."
if "$BIN/tldr" --update 2>/dev/null || { sleep 3 && "$BIN/tldr" --update 2>/dev/null; }; then
    ok "Cache tldr mis à jour"
else
    warn "Échec mise à jour tldr — relancer manuellement : tldr --update"
fi

# ── Nerd Fonts ─────────────────────────────────────────────────────────────────
section "Nerd Fonts (JetBrainsMono NL + 0xProto)"
FONTS_DIR="$HOME/.local/share/fonts/NerdFonts"
ensure_dir "$FONTS_DIR"

install_font() {
    local name="$1"
    local url="$2"
    local marker="$3"   # nom d'un fichier font attendu après install
    if [ -f "$FONTS_DIR/$marker" ]; then
        ok "$name (déjà installée)"
        return
    fi
    step "Téléchargement de $name..."
    local tmp=$(mktemp -d)
    if curl -sL "$url" -o "$tmp/font.zip"; then
        unzip -o "$tmp/font.zip" -d "$tmp/extracted" '*.ttf' '*.otf' &>/dev/null
        find "$tmp/extracted" -type f \( -name "*.ttf" -o -name "*.otf" \) \
            -exec cp {} "$FONTS_DIR/" \;
        ok "$name"
    else
        fail "$name — échec du téléchargement"
    fi
    rm -rf "$tmp"
}

install_font "JetBrainsMono NL" \
    "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip" \
    "JetBrainsMonoNLNerdFont-Regular.ttf"
install_font "0xProto" \
    "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/0xProto.zip" \
    "0xProtoNerdFont-Regular.ttf"

step "Mise à jour du cache de polices (fc-cache)..."
fc-cache -f "$FONTS_DIR" &>/dev/null && ok "Cache polices" || warn "fc-cache échoué"

# ── candy-icons ────────────────────────────────────────────────────────────────
section "candy-icons (thème d'icônes)"
ICONS_DIR="$HOME/.local/share/icons"
ensure_dir "$ICONS_DIR"

if [ -d "$ICONS_DIR/candy-icons-master" ]; then
    ok "candy-icons (déjà installé)"
else
    step "Téléchargement de candy-icons..."
    tmp=$(mktemp -d)
    if curl -sL "https://github.com/EliverLara/candy-icons/archive/refs/heads/master.zip" \
            -o "$tmp/candy.zip"; then
        unzip -o "$tmp/candy.zip" -d "$tmp/extracted" &>/dev/null
        mv "$tmp/extracted/candy-icons-master" "$ICONS_DIR/candy-icons-master"
        ok "candy-icons"
    else
        fail "candy-icons — échec du téléchargement"
    fi
    rm -rf "$tmp"
fi

step "Mise à jour du cache icônes (gtk-update-icon-cache)..."
gtk-update-icon-cache -f "$ICONS_DIR/candy-icons-master" &>/dev/null && \
    ok "Cache icônes mis à jour" || warn "gtk-update-icon-cache échoué"

# ── uv ─────────────────────────────────────────────────────────────────────────
section "uv (gestionnaire Python + uvx)"
if has_cmd uv; then
    ok "uv (déjà installé)"
else
    step "Installation de uv..."
    _ts=$(mktemp)
    curl -LsSf https://astral.sh/uv/install.sh -o "$_ts" 2>/dev/null && \
    sh "$_ts" &>/dev/null && ok "uv (uvx inclus)" || fail "uv"
    rm -f "$_ts"
fi
