#!/usr/bin/env python3
"""Validate the skills in `skills/`.

A skill is a directory containing a `SKILL.md` whose YAML front matter carries a
`name` and a `description`. Agent harnesses decide whether to load a skill from
that description alone, so a vague or missing one makes the skill invisible.

Checks performed:
  - front matter present, with `name` and `description`
  - `name` matches the directory name
  - `description` long enough to be discriminating, short enough to be loaded
  - every relative markdown link resolves to a file that exists

    python3 scripts/check_skills.py

Exit code 1 means at least one skill is malformed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

MIN_DESCRIPTION = 80
MAX_DESCRIPTION = 1024

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_front_matter(text: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    data = {}
    key = None
    for line in block.splitlines():
        if not line.strip():
            continue
        match = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if match:
            key = match.group(1)
            data[key] = match.group(2).strip()
        elif key:                      # folded continuation line
            data[key] += " " + line.strip()
    return data


def check_skill(directory: Path) -> list:
    problems = []
    skill_file = directory / "SKILL.md"

    if not skill_file.exists():
        return [f"{directory.name}: SKILL.md manquant"]

    text = skill_file.read_text(encoding="utf-8")
    front = parse_front_matter(text)

    if front is None:
        return [f"{directory.name}: front matter YAML absent ou mal fermé"]

    name = front.get("name")
    description = front.get("description")

    if not name:
        problems.append(f"{directory.name}: champ `name` manquant")
    elif name != directory.name:
        problems.append(
            f"{directory.name}: `name: {name}` ne correspond pas au dossier")

    if not description:
        problems.append(f"{directory.name}: champ `description` manquant")
    elif len(description) < MIN_DESCRIPTION:
        problems.append(
            f"{directory.name}: description trop courte ({len(description)} car.) — "
            f"le harnais choisit d'après elle, il lui faut des mots-clés concrets")
    elif len(description) > MAX_DESCRIPTION:
        problems.append(
            f"{directory.name}: description trop longue ({len(description)} car.)")

    # Relative links must resolve: a dangling reference means the agent will
    # look for guidance that is not there.
    for markdown in directory.rglob("*.md"):
        for target in LINK.findall(markdown.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            resolved = (markdown.parent / target.split("#")[0]).resolve()
            if not resolved.exists():
                relative = markdown.relative_to(ROOT)
                problems.append(f"{relative}: lien cassé vers `{target}`")

    return problems


def main() -> int:
    if not SKILLS.is_dir():
        print("aucun dossier skills/")
        return 1

    directories = sorted(d for d in SKILLS.iterdir() if d.is_dir())
    if not directories:
        print("aucun skill trouvé")
        return 1

    problems = []
    for directory in directories:
        problems.extend(check_skill(directory))

    if problems:
        print("check_skills : problèmes détectés.\n")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(f"check_skills : {len(directories)} skills valides "
          f"({', '.join(d.name for d in directories)}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
