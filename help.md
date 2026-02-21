# violet-chaton — référence des commandes

---

## Navigation & fichiers

| Commande | Alias | Description |
|---|---|---|
| `ls` | `eza --icons --git` | Listing coloré avec icônes |
| `ll` | `eza -l --git` | Listing long avec infos git |
| `lt` | `eza --tree` | Arborescence en arbre |
| `cd <dossier>` | zoxide | Navigation intelligente (mémorise les dossiers visités) |
| `cd <partiel>` | zoxide | Saute vers le dossier le plus probable — ex: `cd doc` → `~/Documents` |
| `<nom_dossier>` | AUTO_CD | Entrer dans un dossier sans taper `cd` |
| `yazi` | — | Explorateur de fichiers TUI (clavier) |
| `nemo` | — | Explorateur de fichiers GUI |
| `fd <pattern>` | fdfind | Recherche de fichiers (remplace `find`) |

### yazi — raccourcis principaux
| Touche | Action |
|---|---|
| `h/j/k/l` ou flèches | Navigation |
| `Entrée` | Ouvrir / entrer dans le dossier |
| `Espace` | Sélectionner |
| `y` | Copier |
| `d` | Couper |
| `p` | Coller |
| `r` | Renommer |
| `D` | Supprimer |
| `q` | Quitter |

---

## Visualisation

| Commande | Alias | Description |
|---|---|---|
| `cat <fichier>` | batcat | Affichage avec coloration syntaxique, sans pager |
| `bat <fichier>` | batcat | Comme cat avec numéros de lignes et pager |
| `glow <fichier.md>` | — | Rendu Markdown dans le terminal |
| `man <commande>` | tldr | Pages de manuel simplifiées (remplace man) |
| `tldr <commande>` | — | Exemples pratiques d'une commande |
| `fetch` | — | Affiche les infos système avec le logo violet-chaton |

---

## Recherche

| Commande | Description |
|---|---|
| `grep <pattern> <fichier>` | Recherche dans un fichier (--color=auto actif par défaut) |
| `rg <pattern>` | Recherche dans les fichiers (ripgrep, remplace grep) |
| `fd <pattern>` | Recherche de fichiers (remplace find) |
| `fzf` | Fuzzy finder interactif (pipe ou seul) |

### fzf — raccourcis clavier
| Touche | Action |
|---|---|
| `Ctrl+G` | Recherche fuzzy d'un **fichier** dans `$HOME` (aperçu batcat) |
| `Ctrl+F` | Recherche fuzzy d'un **dossier** dans `$HOME` |
| `Ctrl+R` | Recherche dans l'**historique** (via atuin) |

---

## Git

| Commande | Alias | Description |
|---|---|---|
| `lg` | lazygit | Interface TUI complète pour git |
| `git diff` | — | Affichage amélioré par git-delta (couleurs, side-by-side) |
| `gh pr create` | — | Créer une pull request depuis le terminal |
| `gh issue list` | — | Lister les issues du dépôt courant |
| `gh auth login` | — | S'authentifier sur GitHub |

### lazygit — raccourcis principaux
| Touche | Action |
|---|---|
| `1/2/3/4/5` | Changer de panneau (status/branches/commits/stash/reflog) |
| `Espace` | Stage / unstage un fichier |
| `c` | Commit |
| `p` | Push |
| `P` | Pull |
| `b` | Gérer les branches |
| `z` | Undo |
| `q` | Quitter |

### git-delta — navigation dans les diffs
| Touche | Action |
|---|---|
| `n` | Hunk suivant |
| `N` | Hunk précédent |
| `q` | Quitter |

---

## Monitoring & système

| Commande | Alias | Description |
|---|---|---|
| `btop` | — | Moniteur système interactif (CPU, RAM, réseau, disque) |
| `disk` | ncdu | Analyse de l'espace disque interactif |
| `ncdu` | — | Idem (nom original) |

---

## Historique shell (atuin)

| Commande / Touche | Description |
|---|---|
| `Ctrl+R` | Recherche dans l'historique avec atuin (fuzzy, filtré par dossier/host) |
| `atuin search <terme>` | Recherche dans l'historique en ligne de commande |
| `atuin stats` | Statistiques sur les commandes les plus utilisées |
| `atuin sync` | Synchroniser l'historique entre machines (compte requis) |
| `atuin register` | Créer un compte atuin pour la synchronisation |

> L'interface atuin affiche : code de sortie | durée | timestamp | commande.
> L'historique est partagé entre sessions et machines si atuin est configuré avec un compte.

---

## Correction & suggestions

| Commande / Touche | Description |
|---|---|
| `fuck` | Corrige la dernière commande ratée (thefuck) |
| `Ctrl+Space` | Accepte la suggestion automatique complète |
| `→` (flèche droite) | Accepte partiellement la suggestion (mot par mot) |
| `Tab` | Autocomplétion avec menu interactif |

> zsh corrige aussi automatiquement les petites typos de commandes (option `CORRECT`).

---

## Visuels & fun

| Commande | Description |
|---|---|
| `cava` | Visualiseur audio dans le terminal |
| `pipes` | Animation de tuyaux colorés |
| `cbonsai` | Bonsaï animé dans le terminal |
| `chafa <image>` | Affiche une image dans le terminal |
| `lolcat` | Colorie la sortie d'une commande en arc-en-ciel (ex: `ls \| lolcat`) |
| `cmatrix` | Pluie de caractères style Matrix |
| `toilet -f big <texte>` | Affiche du texte en gros ASCII art coloré |
| `jp2a <image.jpg>` | Convertit une image en ASCII art dans le terminal |
| `w3m <url>` | Navigue sur le web en mode texte depuis le terminal |

---

## Utilitaires

| Commande | Description |
|---|---|
| `qalc` | Calculatrice interactive (unités, conversions, ex: `150 EUR to USD`) |
| `jq <filtre> <fichier.json>` | Traite et formate du JSON en ligne de commande |
| `uv` | Gestionnaire de paquets Python ultra-rapide (remplace pip/venv) |
| `uvx <outil>` | Exécute un outil Python dans un environnement isolé temporaire |

---

## Cheat sheets interactifs

| Commande | Description |
|---|---|
| `navi` | Interface interactive de cheat sheets (chercher des exemples de commandes) |
| `tldr <commande>` | Résumé rapide d'une commande avec exemples |

---

## Prompt (starship)

Le prompt affiche automatiquement sur **2 lignes** :

**Ligne 1 :** OS | User@Host | Dossier courant | Branche git + état | Langage détecté + version | Durée dernière commande (si >2s) | RAM | Heure

**Ligne 2 :** Code de retour si erreur | Caractère `❯` (bleu ok / rouge erreur)

**État git affiché :**
| Symbole | Signification |
|---|---|
| `⇡N` | N commits en avance sur le remote |
| `⇣N` | N commits en retard |
| `?N` | N fichiers non trackés |
| `!N` | N fichiers modifiés |
| `+N` | N fichiers stagés |
| `✘N` | Conflits |

---

## Plugins zsh actifs

| Plugin | Effet |
|---|---|
| `zsh-autosuggestions` | Suggestions grises basées sur l'historique |
| `zsh-syntax-highlighting` | Coloration de la commande en cours de frappe |
| `zsh-completions` | Complétions supplémentaires pour de nombreux outils |
| `zinit` | Gestionnaire de plugins (chargement automatique au démarrage) |

---

## Coloration syntaxique du terminal

| Type | Couleur |
|---|---|
| Commandes | Cyan |
| Alias | Violet |
| Builtins zsh | Rose |
| Chaînes | Violet |
| Chemins | Blanc souligné |
| Erreurs / inconnu | Rouge gras |
| Commentaires | Gris italique |
| Globs (`*`, `?`) | Jaune |

---

## Options zsh actives

| Option | Effet |
|---|---|
| `AUTO_CD` | Entrer dans un dossier sans taper `cd` |
| `CORRECT` | Correction automatique des typos |
| `GLOB_DOTS` | Les fichiers cachés `.xxx` inclus dans les globs |
| `SHARE_HISTORY` | Historique partagé entre toutes les sessions zsh |
| `HIST_IGNORE_DUPS` | Ne pas enregistrer les doublons dans l'historique |
| `HIST_IGNORE_SPACE` | Les commandes précédées d'un espace ne sont pas enregistrées |
| `NO_BEEP` | Silence — pas de bip |
