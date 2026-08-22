#!/usr/bin/env bash
#
# Fiducai — install the skills into an agent harness.
#
#   ./install.sh                    # detect the harness and ask
#   ./install.sh --target DIR       # install into a specific skills directory
#   ./install.sh --project          # install into ./.agents/skills of the current project
#   ./install.sh --link             # symlink instead of copy (good for development)
#   ./install.sh --list             # show what would be installed, change nothing
#
# Fiducai is not tied to any particular harness: a skill is a directory with a
# SKILL.md, and installing means putting that directory where your agent looks
# for skills. This script only saves you the copying.
#
# Known skill directories, as of August 2026:
#   Claude Code   ~/.claude/skills    .claude/skills
#   Codex         ~/.codex/skills     .codex/skills
#   Gemini CLI    ~/.gemini/skills    .gemini/skills
# Codex and Gemini CLI also read ~/.agents/skills and ./.agents/skills, which is
# what --project uses.

set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"

TARGET=""
MODE="copy"
LIST_ONLY=0

die() { printf 'fiducai: %s\n' "$1" >&2; exit 1; }

while [ $# -gt 0 ]; do
    case "$1" in
        --target) TARGET="${2:-}"; shift 2 ;;
        --project) TARGET="$PWD/.agents/skills"; shift ;;
        --link) MODE="link"; shift ;;
        --list) LIST_ONLY=1; shift ;;
        # Print the header block, however long it happens to be, rather than a
        # hard-coded line range that silently truncates when the header grows.
        -h|--help)
            awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
            exit 0 ;;
        *) die "option inconnue : $1" ;;
    esac
done

[ -d "$SOURCE_DIR" ] || die "dossier skills/ introuvable — lancer depuis le dépôt"

SKILLS=()
while IFS= read -r dir; do SKILLS+=("$dir"); done < <(
    find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -type d | sort
)
[ ${#SKILLS[@]} -gt 0 ] || die "aucun skill trouvé dans $SOURCE_DIR"

if [ "$LIST_ONLY" -eq 1 ]; then
    echo "Skills disponibles :"
    for dir in "${SKILLS[@]}"; do
        name=$(basename "$dir")
        desc=$(sed -n 's/^description: *//p' "$dir/SKILL.md" | head -1 | cut -c1-90)
        printf '  %-20s %s…\n' "$name" "$desc"
    done
    exit 0
fi

# Work out where to install if the caller did not say.
#
# Each harness has its own directory, and `~/.agents/skills` is a shared
# convention that several of them also read. We only offer a harness-specific
# path when its configuration directory already exists, so the list reflects
# what is actually installed on this machine.
if [ -z "$TARGET" ]; then
    CANDIDATES=()
    LABELS=()

    add_candidate() {   # add_candidate <path> <label>
        CANDIDATES+=("$1")
        LABELS+=("$2")
    }

    [ -d "$HOME/.claude" ] && add_candidate "$HOME/.claude/skills" "Claude Code"
    [ -d "$HOME/.codex" ] && add_candidate "$HOME/.codex/skills" "Codex"
    [ -d "$HOME/.gemini" ] && add_candidate "$HOME/.gemini/skills" "Gemini CLI"
    [ -d "$HOME/.agents" ] && add_candidate "$HOME/.agents/skills" \
        "convention partagée (Codex, Gemini CLI)"
    add_candidate "$PWD/.agents/skills" "ce projet uniquement"

    echo "Où installer les skills Fiducai ?"
    i=1
    for candidate in "${CANDIDATES[@]}"; do
        printf '  %d) %-28s %s\n' "$i" "$candidate" "— ${LABELS[$((i - 1))]}"
        i=$((i + 1))
    done
    printf 'Choix [1] : '
    read -r choice || choice=""
    choice="${choice:-1}"

    # Validate before indexing: bash treats a non-numeric answer as 0, and
    # index -1 would silently select the *last* candidate instead of failing.
    case "$choice" in
        ''|*[!0-9]*) die "choix invalide : $choice" ;;
    esac
    [ "$choice" -ge 1 ] && [ "$choice" -le ${#CANDIDATES[@]} ] \
        || die "choix invalide : $choice"

    TARGET="${CANDIDATES[$((choice - 1))]}"
fi

mkdir -p "$TARGET"

for dir in "${SKILLS[@]}"; do
    name=$(basename "$dir")
    destination="$TARGET/$name"

    if [ -e "$destination" ] || [ -L "$destination" ]; then
        printf '  %s existe déjà — remplacer ? [y/N] ' "$name"
        read -r answer || answer=""
        case "$answer" in
            y|Y) rm -rf "$destination" ;;
            *) echo "  $name : ignoré"; continue ;;
        esac
    fi

    if [ "$MODE" = "link" ]; then
        ln -s "$dir" "$destination"
        echo "  $name : lien symbolique créé"
    else
        cp -R "$dir" "$destination"
        echo "  $name : copié"
    fi
done

cat <<EOF

Installé dans : $TARGET

Les deux skills fonctionnent ensemble — 'vaud-tax-return' consulte
'swiss-tax-basics' installé à côté de lui. Gardez-les au même endroit.

Pour commencer, demandez simplement à votre agent :
  « aide-moi à remplir ma déclaration d'impôts vaudoise »

Fiducai prépare un brouillon à relire.
EOF
