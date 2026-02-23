# violet-chaton — setup automatique

Environnement terminal complet aux couleurs violet-chaton, pensé pour Pop!_OS / Ubuntu avec COSMIC Desktop.
(Bonus thème Vesktop / Discord)

---

## Démarrage rapide

```bash
bash install.sh
```

Un menu s'affiche. Choisis **1** pour une installation complète.

---

## Prérequis

- **Distribution :** Debian, Ubuntu, Pop!_OS (ou dérivé apt)
- **Droits :** compte avec `sudo`
- **Connexion internet** (téléchargement des binaires)
- **Outils de base :**

```bash
sudo apt install -y curl git unzip
```

> Pour COSMIC Desktop : Pop!_OS 24.04 ou supérieur.

---

## Ce que fait le script — étape par étape

### Étape 1 — Paquets apt (`01-packages-apt.sh`)

Installe les outils via le gestionnaire de paquets système :

| Outil            | Rôle |
|------------------|------|
| `zsh`            | Shell principal (remplace bash) |
| `eza`            | Remplacement de `ls` avec icônes et couleurs |
| `bat`            | Remplacement de `cat` avec coloration syntaxique |
| `fd-find`        | Remplacement de `find`, plus rapide et intuitif |
| `fzf`            | Fuzzy finder — recherche floue de fichiers et dossiers |
| `zoxide`         | Remplacement de `cd` avec mémoire des dossiers fréquents |
| `git-delta`      | Pager git avec diff coloré côte à côte |
| `vivid`          | Générateur de LS_COLORS |
| `ripgrep`        | Remplacement de `grep`, très rapide |
| `ncdu`           | Analyse d'espace disque en TUI |
| `thefuck`        | Correction automatique de la dernière commande ratée |
| `lolcat`         | Arc-en-ciel sur n'importe quel output |
| `cbonsai`        | Bonsaï ASCII animé |
| `chafa`          | Affichage d'images dans le terminal (logo fastfetch) |
| `cava`           | Visualiseur audio animé |
| `btop`           | Moniteur système en TUI |
| `nemo`           | Explorateur de fichiers GUI |
| `jq`             | Processeur JSON en ligne de commande |
| `vivaldi-stable` | Navigateur — dépôt officiel ajouté automatiquement |
| `gh`             | CLI GitHub (auth, PR, issues) — dépôt officiel ajouté automatiquement |
| `cmatrix`        | Pluie de caractères style Matrix |
| `toilet`         | Texte en gros ASCII art coloré (bannières dans le terminal) |
| `w3m`            | Navigateur web en mode texte dans le terminal |
| `jp2a`           | Conversion d'images JPEG/PNG en ASCII art |
| `qalc`           | Calculatrice CLI — unités, conversions, expressions complexes |
| `waybar`         | Barre de statut Wayland 3-pills glassmorphism |
| `wob`            | Overlay volume/luminosité animé |
| `wofi`           | Launcher d'applications et menu power |
| `brightnessctl`  | Contrôle de la luminosité rétroéclairage |
| `playerctl`      | Contrôle MPRIS (lecture/pause, titre en cours) |
| `wireplumber`    | Gestionnaire audio PipeWire (`wpctl`) |
| `python3-gi`     | Bindings Python GTK3 (popups volume/luminosité) |
| `gir1.2-gtk-3.0` | Introspection GTK3 pour Python |
| `gir1.2-gtklayershell-0.1` | Layer-shell Wayland pour popups GTK flottants |

Définit aussi **zsh comme shell par défaut** via `chsh`.

---

### Étape 2 — Binaires manuels (`02-packages-manual.sh`)

Télécharge les versions les plus récentes depuis GitHub et les installe dans `~/.local/bin/` :

| Outil        | Rôle |
|--------------|------|
| `lazygit`    | Interface git complète en TUI (`lg`) |
| `yazi`       | Gestionnaire de fichiers en TUI |
| `glow`       | Rendu Markdown dans le terminal |
| `tldr`       | Man pages simplifiées avec exemples (tealdeer) |
| `navi`       | Cheatsheets interactives |
| `pipes.sh`   | Animation de tuyaux dans le terminal |
| `fastfetch`  | Infos système au démarrage du terminal — `.deb` depuis GitHub |
| `uv` / `uvx` | Gestionnaire de paquets Python ultra-rapide — script officiel astral.sh |

Installe également :
- **starship** et **atuin** via leurs scripts officiels
- **zinit** (gestionnaire de plugins zsh) via git clone
- **Nerd Fonts** — JetBrainsMono NL et 0xProto, vers `~/.local/share/fonts/NerdFonts/`
- **candy-icons** — thème d'icônes, vers `~/.local/share/icons/candy-icons-master/`

> **nomachine** — à installer manuellement depuis [nomachine.com](https://www.nomachine.com/download) (comme VSCode et Vesktop)

Met à jour le cache des pages tldr et le cache de polices (`fc-cache`).

---

### Étape 3 — Déploiement des configs et thèmes (`03-deploy-configs.sh`)

Copie les fichiers de config et thèmes aux bons emplacements.

Avant chaque déploiement, les fichiers existants sont sauvegardés dans :
```
~/.config/violet-chaton-backups/YYYYMMDD-HHMMSS/
```
Le chemin exact est affiché à la fin du script si des fichiers ont été sauvegardés.

**Configs shell :**
- `~/.zshrc` — configuration zsh complète
- `~/.bashrc` — configuration bash minimale (PATH + `exec zsh`)
- `~/.gitconfig` — git avec delta comme pager

> `user.name` et `user.email` présents dans le gitconfig existant sont **automatiquement préservés** après le déploiement.

**Configs outils :**
- `~/.config/starship.toml` — prompt 2 lignes violet-chaton
- `~/.config/bat/config` — thème violet-chaton, style header
- `~/.config/btop/btop.conf` — moniteur avec thème violet-chaton
- `~/.config/fastfetch/config.jsonc` — modules système + logo chafa
- `~/.config/atuin/config.toml` — historique fuzzy, colonnes, thème
- `~/.config/lazygit/config.yml` — couleurs violet-chaton + delta
- `~/.config/yazi/yazi.toml` — config gestionnaire de fichiers
- `~/.config/glow/glow.yml` — style markdown dark

**Thèmes CLI :**
- `~/.config/bat/themes/violet-chaton.tmTheme`
- `~/.config/btop/themes/violet-chaton.theme`
- `~/.config/atuin/themes/violet-chaton.toml`
- `~/.config/cava/config`
- `~/.config/yazi/theme.toml`
- `~/.config/vesktop/themes/violet-chaton.theme.css` — Vesktop natif (toujours déployé)
- `~/.var/app/dev.vencord.Vesktop/config/vesktop/themes/` — Vesktop Flatpak (si installé)

**GTK3 et Nemo :**
- `~/.config/gtk-3.0/gtk.css` — thème GTK3 violet-chaton (Nemo et applications GTK)
- Nemo défini comme gestionnaire de fichiers par défaut (`xdg-mime`)
- Préférences Nemo appliquées via `gsettings` : vue icônes, miniatures, zoom standard
- Thème d'icônes **candy-icons** activé via `gsettings`

**COSMIC Desktop (entièrement automatique) :**
- `~/.config/cosmic/com.system76.CosmicTheme.Dark/v1/` — palette violet-chaton complète
- `~/.config/cosmic/com.system76.CosmicTheme.Light/v1/` — palette violet-chaton (mode clair)
- `~/.config/cosmic/com.system76.CosmicTheme.Mode/v1/is_dark` — mode sombre activé
- `~/.config/cosmic/com.system76.CosmicTerm/v1/` — police JetBrains Mono, couleurs, profil
- `~/.config/cosmic/com.system76.CosmicTk/v1/` — icônes candy-icons, polices UI 0xProto

**Waybar — island floating 3 pills :**
- `~/.config/waybar/config` — modules left/center/right
- `~/.config/waybar/style.css` — glassmorphism, bordures roses, animations
- `~/.config/waybar/cava-waybar.cfg` — config CAVA dédié waybar
- `~/.config/waybar/scripts/` — tous les scripts (gpu, network, power-profile, cava, wob, popups GTK)
- `~/.config/autostart/waybar.desktop` — démarrage automatique avec COSMIC
- `~/.config/autostart/wob.desktop` — démarrage automatique de l'overlay wob

**Wofi — launcher + menu power :**
- `~/.config/wofi/config` — configuration wofi
- `~/.config/wofi/style.css` — thème violet-chaton (launcher apps)
- `~/.config/wofi/power-style.css` — thème violet-chaton (menu power)

**wob — overlay volume/luminosité :**
- `~/.config/wob.ini` — couleurs violet-chaton, position bas de l'écran

**Système (avec sudo) :**
- `/etc/sudoers.d/waybar-power-profile` — changement de profil énergie sans mot de passe
- `/etc/udev/rules.d/90-platform-profile.rules` — permissions groupe `video` sur platform_profile

**Vivaldi (avec pause de sécurité) :**
- Si Vivaldi n'a pas encore été lancé, le script s'arrête et demande de le démarrer une fois
- Le thème **Rice Violet-Chaton** est ensuite injecté directement dans `~/.config/vivaldi/Default/Preferences`

Reconstruit également le **cache bat** pour activer le thème de coloration syntaxique.

---

## Étapes manuelles après installation

### zinit — premier démarrage

Au premier lancement de zsh, zinit télécharge automatiquement les plugins :
- `zsh-autosuggestions` — suggestions en gris au fil de la frappe
- `zsh-syntax-highlighting` — coloration des commandes en temps réel
- `zsh-completions` — complétion étendue

Cela peut prendre quelques secondes lors du tout premier démarrage.

### Polices — vérification

Si les icônes ne s'affichent pas correctement dans le terminal, forcer la reconstruction du cache de polices :

```bash
fc-cache -f -v
```

Puis sélectionner **JetBrainsMono NL Nerd Font** dans les préférences du terminal.

### atuin — synchronisation (optionnel)

atuin peut synchroniser l'historique entre machines. Pour activer la sync :

```bash
atuin register   # créer un compte
atuin sync       # synchroniser
```

Sans compte, atuin fonctionne en local uniquement.

---

## Log d'installation

Chaque installation génère un fichier log horodaté :

```
~/violet-chaton-install-YYYYMMDD-HHMMSS.log
```

En cas d'erreur, consulter ce fichier pour identifier l'étape qui a échoué.

---

## Troubleshooting

### Icônes ne s'affichent pas

- Vérifier que la police **JetBrainsMono NL Nerd Font** est sélectionnée dans le terminal
- Relancer `fc-cache -f` puis rouvrir le terminal

### zinit ne se lance pas

- Vérifier que `~/.local/share/zinit/zinit.git/zinit.zsh` existe
- Relancer le script d'installation étape 3

### Injection Vivaldi échoue

- Lancer Vivaldi une première fois, le fermer complètement, puis relancer `bash install.sh` → option 4

### Thème bat ne s'applique pas

```bash
bat cache --build
```

### candy-icons ne s'affiche pas dans Nemo

```bash
gtk-update-icon-cache ~/.local/share/icons/candy-icons-master
gsettings set org.gnome.desktop.interface icon-theme 'candy-icons-master'
```

### Waybar ne démarre pas

```bash
waybar &   # tester manuellement, lire les erreurs
pkill -SIGUSR2 waybar   # recharger la config à chaud
```

### Popups volume/luminosité ne s'ouvrent pas

Vérifier que les dépendances Python sont installées :
```bash
python3 -c "import gi; gi.require_version('GtkLayerShell', '0.1'); print('OK')"
```

### Profil énergie ne change pas au clic

Vérifier que la règle sudoers et les permissions udev sont en place :
```bash
ls -la /sys/firmware/acpi/platform_profile   # doit être g+w groupe video
cat /etc/sudoers.d/waybar-power-profile
```

---

## Raccourcis configurés

| Raccourci      | Action |
|----------------|--------|
| `Ctrl+R`       | Historique atuin (fuzzy search) |
| `Ctrl+G`       | Rechercher un fichier (fzf) |
| `Ctrl+F`       | Naviguer vers un dossier (fzf) |
| `Ctrl+Space`   | Accepter la suggestion autosuggestions |
| `→`            | Accepter la suggestion mot par mot |

---

## Alias configurés

| Alias    | Commande réelle |
|----------|-----------------|
| `ls`     | `eza --icons --git --group-directories-first` |
| `ll`     | `eza -l --icons --git` |
| `lt`     | `eza --tree --icons` |
| `cat`    | `batcat --paging=never` |
| `bat`    | `batcat` |
| `fd`     | `fdfind` |
| `man`    | `tldr` |
| `lg`     | `lazygit` |
| `rg`     | `rg --color=always` |
| `disk`   | `ncdu` |
| `fetch`  | `fastfetch` avec logo chafa |
| `pipes`  | `pipes.sh` |
| `cd`     | `zoxide` (avec mémoire) |
| `fuck`   | correction auto thefuck |
| `grep`   | `grep --color=auto` |

---

## Structure du dossier INSTALL/

```
INSTALL/
├── install.sh                    script principal — menu interactif
├── scripts/
│   ├── lib.sh                    couleurs et fonctions partagées
│   ├── 01-packages-apt.sh        installation apt + Vivaldi
│   ├── 02-packages-manual.sh     binaires GitHub + Nerd Fonts + candy-icons
│   └── 03-deploy-configs.sh      configs, thèmes, COSMIC, Vivaldi
├── configs/                      copies des fichiers de configuration
│   ├── zshrc
│   ├── bashrc
│   ├── gitconfig
│   ├── starship.toml
│   ├── bat.conf
│   ├── btop.conf
│   ├── fastfetch.jsonc
│   ├── atuin.toml
│   ├── lazygit.yml
│   ├── yazi.toml
│   ├── glow.yml
│   ├── autostart/
│   │   ├── waybar.desktop           démarrage automatique waybar
│   │   └── wob.desktop              démarrage automatique wob
│   ├── waybar/
│   │   ├── config                   modules 3-pills
│   │   ├── cava-waybar.cfg          config CAVA dédiée waybar
│   │   └── scripts/                 gpu, network, power-profile, cava, wob, popups GTK
│   ├── wofi/
│   │   └── config                   config wofi
│   └── wob/
│       └── wob.ini                  overlay volume/luminosité
├── assets/
│   └── violet-chaton-logo.png    logo fastfetch (1024×1024)
└── themes/                       tous les fichiers de thème violet-chaton
    ├── violet-chaton-bat.tmTheme
    ├── violet-chaton-btop.theme
    ├── violet-chaton-atuin.toml
    ├── violet-chaton-cava.conf
    ├── violet-chaton-yazi.toml
    ├── violet-chaton-gtk.css            thème GTK3 (Nemo + applications GTK)
    ├── violet-chaton-ls-colors.sh
    ├── violet-chaton-vivaldi.json       thème Rice Violet-Chaton pour Vivaldi
    ├── violet-chaton.theme.css          thème Discord/Vesktop compilé
    ├── violet-chaton-waybar.css         CSS 3-pills glassmorphism
    ├── violet-chaton-wofi.css           thème wofi launcher
    ├── violet-chaton-wofi-power.css     thème wofi menu power
    ├── cosmic/                          configs COSMIC déployées automatiquement
    │   ├── com.system76.CosmicTheme.Dark/v1/
    │   ├── com.system76.CosmicTheme.Light/v1/
    │   ├── com.system76.CosmicTheme.Mode/v1/
    │   ├── com.system76.CosmicTerm/v1/
    │   └── com.system76.CosmicTk/v1/
    └── violet-chaton-discord-theme/     sources SCSS du thème (gitignored)
```

---

## Mettre à jour les configs

Après avoir modifié un fichier de config sur ta machine, re-copier vers INSTALL/ :

```bash
# Exemple : mettre à jour la config starship
cp ~/.config/starship.toml ~/Documents/config-violet-chaton/INSTALL/configs/starship.toml

# Mettre à jour les configs COSMIC
cp ~/.config/cosmic/com.system76.CosmicTerm/v1/* \
   ~/Documents/config-violet-chaton/INSTALL/themes/cosmic/com.system76.CosmicTerm/v1/

# Mettre à jour la config ou le CSS waybar
cp ~/.config/waybar/config \
   ~/Documents/config-violet-chaton/INSTALL/configs/waybar/config
cp ~/.config/waybar/style.css \
   ~/Documents/config-violet-chaton/INSTALL/themes/violet-chaton-waybar.css

# Mettre à jour un script waybar
cp ~/.config/waybar/scripts/power-profile.sh \
   ~/Documents/config-violet-chaton/INSTALL/configs/waybar/scripts/power-profile.sh
```

---

## Palette violet-chaton

| Rôle       | Hex       |
|------------|-----------|
| Background | `#261537` |
| BG medium  | `#341c4a` |
| BG high    | `#3d2454` |
| Pink       | `#ff79c6` |
| Purple     | `#e79cfe` |
| Cyan       | `#8be9fd` |
| Text       | `#f8f8f2` |
| Muted      | `#6c7086` |
| Overlay    | `#9399b2` |
| Success    | `#a6e3a1` |
| Warning    | `#f9e2af` |
| Danger     | `#f38ba8` |
