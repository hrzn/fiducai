#!/usr/bin/env python3
"""Refuse to let real tax data into a public repository.

Fiducai is built from people's actual tax returns, so the failure mode is
obvious: someone pastes a real IBAN into an example, or commits a bank PDF they
were testing with. This script is the mechanical backstop. It runs as a
pre-commit hook and in CI.

It is deliberately blunt. False positives are cheap -- add an exception -- and a
leaked AVS number is not.

    python3 scripts/check_no_pii.py            # scan the working tree
    python3 scripts/check_no_pii.py --staged   # scan what is about to be committed

Exit code 1 means: do not commit this.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Paths whose content is synthetic by construction and may legitimately contain
# identifier-shaped strings.
ALLOWED_PREFIXES = (
    "tests/fixtures/",
    "tests/build_fixture.py",
    "scripts/check_no_pii.py",
)

# Files that must never be committed, whatever their content.
FORBIDDEN_SUFFIXES = (
    ".vaudtax", ".vstax", ".getax", ".tax",
    ".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff",
    ".xlsx", ".xls", ".csv", ".zip",
)

FORBIDDEN_NAMES = ("profil-fiscal.md", "profil_fiscal.md")

# Content patterns. Each is (code, human-readable reason, compiled regex).
PATTERNS = [
    (
        "iban",
        "IBAN suisse ou liechtensteinois",
        re.compile(r"\b(?:CH|LI)\d{2}[ ]?(?:\d{4}[ ]?){4}\d\b"),
    ),
    (
        "avs",
        "numéro AVS (756.xxxx.xxxx.xx)",
        re.compile(r"\b756[.\s]?\d{4}[.\s]?\d{4}[.\s]?\d{2}\b"),
    ),
    (
        "email",
        "adresse e-mail",
        re.compile(r"\b[\w.+-]+@(?!example\.(?:com|org)\b)[\w-]+\.[a-zA-Z]{2,}\b"),
    ),
    (
        "phone",
        "numéro de téléphone suisse",
        re.compile(r"(?:\+41|\b0)(?:[ .]?\d{2})(?:[ .]?\d{3})(?:[ .]?\d{2}){2}\b"),
    ),
    (
        "gesdem",
        "nom de fichier VaudTax réel (CTB<id>_PF<année>_…)",
        re.compile(r"\bCTB(?!99999999\b)\d{6,}_PF\d{4}_"),
    ),
]

TEXT_SUFFIXES = {".md", ".py", ".txt", ".yml", ".yaml", ".json", ".toml",
                 ".sh", ".xml", ".cfg", ".ini", ".html"}


def tracked_files(staged: bool) -> list:
    if staged:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    else:
        cmd = ["git", "ls-files"]
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line.strip()]


def is_allowed(relpath: str) -> bool:
    return any(relpath.startswith(p) for p in ALLOWED_PREFIXES)


def scan(staged: bool) -> int:
    findings = []

    for relpath in tracked_files(staged):
        path = ROOT / relpath
        name = Path(relpath).name.lower()

        if name in FORBIDDEN_NAMES:
            findings.append((relpath, 0, "profil personnel",
                             "un profil fiscal ne se commite jamais"))
            continue

        if not is_allowed(relpath) and relpath.lower().endswith(FORBIDDEN_SUFFIXES):
            findings.append((relpath, 0, "type de fichier interdit",
                             "document ou déclaration : ne se commite pas"))
            continue

        if is_allowed(relpath) or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if not path.exists():
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            for _code, reason, pattern in PATTERNS:
                match = pattern.search(line)
                if match:
                    findings.append((relpath, lineno, reason, match.group(0)))

    if not findings:
        print("check_no_pii : rien à signaler.")
        return 0

    print("check_no_pii : données personnelles probables — commit refusé.\n")
    for relpath, lineno, reason, detail in findings:
        where = f"{relpath}:{lineno}" if lineno else relpath
        print(f"  {where}\n      {reason} : {detail}")
    print("\nSi c'est un faux positif, ajouter le chemin à ALLOWED_PREFIXES dans")
    print("scripts/check_no_pii.py, ou reformuler l'exemple pour qu'il soit")
    print("manifestement fictif.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true",
                        help="ne scanner que les fichiers indexés (hook pre-commit)")
    args = parser.parse_args()
    return scan(args.staged)


if __name__ == "__main__":
    sys.exit(main())
