#!/bin/bash
# ── violet-chaton : paquets apt ───────────────────────────────────────────────
source "$(dirname "$0")/lib.sh"

PACKAGES=(
    zsh
    eza
    bat
    fd-find
    fzf
    zoxide
    git-delta
    vivid
    ripgrep
    ncdu
    thefuck
    lolcat
    cbonsai
    chafa
    jq
    libgtk-3-bin
    adw-gtk3
    nemo
    nemo-fileroller
    # fastfetch → installé via .deb GitHub (voir 02-packages-manual.sh)
    cava
    btop
    # atuin  → installé via son propre script (voir 02-packages-manual.sh)
    # starship → installé via son propre script (voir 02-packages-manual.sh)
    # ── Waybar + launcher + dépendances ──────────────────────────────────────
    waybar
    wob
    wofi
    brightnessctl
    playerctl
    wireplumber
    python3-gi
    gir1.2-gtk-3.0
    gir1.2-gtklayershell-0.1
    # ── Fun & utils ──────────────────────────────────────────────────────────
    cmatrix
    toilet
    w3m
    jp2a
    qalc
)

section "Installation des paquets apt"

step "Mise à jour des dépôts..."
sudo apt update -qq 2>/dev/null && ok "Dépôts mis à jour" || { fail "Échec apt update" ; exit 1; }

for pkg in "${PACKAGES[@]}"; do
    if dpkg -s "$pkg" &>/dev/null; then
        ok "$pkg (déjà installé)"
    else
        step "Installation de $pkg..."
        if sudo apt install -y "$pkg" -qq 2>/dev/null; then
            ok "$pkg"
        else
            fail "$pkg — vérifier le nom du paquet"
        fi
    fi
done

section "Vivaldi (navigateur)"
if dpkg -s vivaldi-stable &>/dev/null; then
    ok "vivaldi-stable (déjà installé)"
else
    step "Ajout du dépôt Vivaldi..."
    curl -fsSL https://repo.vivaldi.com/archive/linux_signing_key.pub \
        | sudo gpg --dearmor -o /usr/share/keyrings/vivaldi-browser.gpg 2>/dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/vivaldi-browser.gpg arch=$(dpkg --print-architecture)] \
https://repo.vivaldi.com/archive/deb/ stable main" \
        | sudo tee /etc/apt/sources.list.d/vivaldi.list &>/dev/null && \
    sudo apt update -qq 2>/dev/null && ok "Dépôt ajouté" || { fail "Dépôt Vivaldi — échec" ; }

    step "Installation de vivaldi-stable..."
    sudo apt install -y vivaldi-stable -qq 2>/dev/null && \
    ok "vivaldi-stable" || fail "vivaldi-stable"
fi

section "GitHub CLI (gh)"
if dpkg -s gh &>/dev/null; then
    ok "gh (déjà installé)"
else
    step "Ajout du dépôt GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null && \
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        | sudo tee /etc/apt/sources.list.d/github-cli.list &>/dev/null && \
    sudo apt update -qq 2>/dev/null && ok "Dépôt ajouté" || { fail "Dépôt gh — échec" ; }

    step "Installation de gh..."
    sudo apt install -y gh -qq 2>/dev/null && \
    ok "gh" || fail "gh"
fi

section "Configuration du shell par défaut"
if [ "$SHELL" != "/usr/bin/zsh" ]; then
    step "Passage à zsh..."
    chsh -s /usr/bin/zsh && ok "zsh défini comme shell par défaut" || warn "Échec chsh — à faire manuellement"
else
    ok "zsh déjà défini comme shell par défaut"
fi
