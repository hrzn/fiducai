#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Read/write helpers for VaudTax `.vaudtax` tax-return files.

A `.vaudtax` file is a ZIP archive containing:
  - one data XML: `CTB<id>_PF<year>_<gesdemRef>_<date>.xml`
  - the supporting PDFs, stored under `doc<timestamp>` keys

This script never rewrites the XML itself. It only takes it out of the archive
(`unpack`), puts it back (`pack`), and offers read-only views (`dump`, `diff`,
`check`, `ereleves`). Edits are made by hand on the extracted XML, which avoids
any accidental re-serialisation by a parser -- ElementTree would rewrite every
tag with an `ns0:` prefix and reflow the indentation.

Standard library only, Python 3.9+, so that the skill directory can simply be
copied around. The PEP 723 header above lets `uv run --script` provision an
interpreter on a machine that has no Python at all; `python3 vaudtax.py` keeps
working unchanged where one is available.

User-facing output is in French, matching the language of VaudTax itself.
Comments and docstrings are in English, matching the rest of the repository.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

NS = "http://www.vd.ch/fiscalite/vaudtax"
NSB = f"{{{NS}}}"

MANIFEST = ".fiducai-manifest.json"

# Natural keys used to pair repeated elements between two years. Without them a
# newly inserted account would shift every subsequent comparison by one.
KEYS = {
    "etatTitres": ["iban", "numCompte", "etablissement"],
    "activiteSalarieeRevenus": ["employeur"],
    "enfants": ["firstName"],
    "interetsDettes": ["creancier"],
    "relevesFiscauxBancaires": ["designation"],
    "actionPartSociale": ["designation"],
    "fraisMedicaux": ["etabliPar", "datePaiement"],
    "fraisEntretienImmeuble": ["maitreEtat"],
    "autresRevenusTouteNatureList": ["genre"],
    "fraisPerfectionnementFormations": ["description"],
    "biensImmobiliers": ["numParcelle"],
    "fraisRepas": ["noLigne"],
    "fraisTransport": ["noLigne"],
    "menuPrefs": ["menuId"],
    "documents": ["filename"],
    "piecesJustificatives": ["id"],
    "piecesJustificativesObligatoires": ["id"],
    "piecesJustificativesFacultatives": ["id"],
    "workingPeriodInterruptions": ["dateDebut"],
}

# Interface-only sections: no fiscal meaning, pure noise in a diff.
NOISE = {"userProfil", "guidedNav"}

# Fields that legitimately change every year, or that are internal bookkeeping.
VOLATILE = {"trackingIndex", "reference", "key", "fileSize", "identifiantEReleve"}

# Pillar 3a annual ceilings, in CHF, per fiscal year: (employee affiliated to a
# pension fund, self-employed without one). Sourced from the ESTV/AFC and from
# the canton's own deduction tables -- see
# ../../swiss-tax-basics/references/chiffres-cles.md, which carries the URLs and
# the consultation dates, and keep the two in sync.
# A year that is absent simply disables the check rather than guessing.
PILIER3A_CEILINGS: dict = {
    2024: (7056, 35280),
    2025: (7258, 36288),
    2026: (7258, 36288),
}

SEVERITY_ORDER = {"error": 0, "warning": 1}


def local(tag: str) -> str:
    return tag.replace(NSB, "")


def sections(root: ET.Element, tag: str) -> list:
    """Top-level sections carrying this name.

    Essential: `guidedNav/displayedSubForms` holds display booleans whose tags
    reuse section names (`etatTitres`, `immeubles`, `enfants`, ...). A plain
    `root.iter()` would pick those up and corrupt every count.
    """
    return [c for c in root if c.tag == NSB + tag]


def chf(value: float) -> str:
    return f"{value:,.0f}".replace(",", "'")


def text_of(elem, tag: str) -> str:
    value = elem.findtext(NSB + tag)
    return value.strip() if value else ""


# --------------------------------------------------------------------------- #
# Identifier validation
# --------------------------------------------------------------------------- #

def iban_is_valid(iban: str) -> bool:
    """ISO 13616 mod-97 check."""
    cleaned = re.sub(r"\s+", "", iban).upper()
    if not re.fullmatch(r"[A-Z]{2}[0-9A-Z]{13,32}", cleaned):
        return False
    rotated = cleaned[4:] + cleaned[:4]
    digits = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rotated)
    return int(digits) % 97 == 1


def avs_is_valid(avs: str) -> bool:
    """Swiss AVS/AHV number: 756.XXXX.XXXX.XC, EAN-13 check digit."""
    digits = re.sub(r"\D", "", avs)
    if len(digits) != 13 or not digits.startswith("756"):
        return False
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(digits[:12]))
    return (10 - total % 10) % 10 == int(digits[12])


# --------------------------------------------------------------------------- #
# Archive access
# --------------------------------------------------------------------------- #

def xml_member(zf: zipfile.ZipFile) -> str:
    names = [n for n in zf.namelist() if n.lower().endswith(".xml")]
    if len(names) != 1:
        sys.exit(f"attendu 1 XML dans l'archive, trouvé {len(names)}: {names}")
    return names[0]


def load_tree(path: Path):
    """Load the XML from a `.vaudtax` file or from an already unpacked folder."""
    if path.is_dir():
        xmls = sorted(path.glob("*.xml"))
        if len(xmls) != 1:
            sys.exit(f"attendu 1 XML dans {path}, trouvé {len(xmls)}")
        return ET.parse(xmls[0]), xmls[0].name
    with zipfile.ZipFile(path) as zf:
        name = xml_member(zf)
        with zf.open(name) as fh:
            return ET.parse(fh), name


def cmd_unpack(args) -> int:
    src, dest = Path(args.source), Path(args.dest)
    if dest.exists() and any(dest.iterdir()) and not args.force:
        sys.exit(f"{dest} existe et n'est pas vide (utiliser --force)")
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as zf:
        zf.extractall(dest)
        name = xml_member(zf)
        # Record the original entry order and compression so that `pack` can
        # rebuild a byte-comparable archive instead of guessing.
        manifest = {
            "source": src.name,
            "entries": [
                {"name": i.filename, "compress_type": i.compress_type}
                for i in zf.infolist()
            ],
        }
    (dest / MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    attached = len([p for p in dest.iterdir()
                    if p.is_file() and not p.name.startswith(".")]) - 1
    print(f"déballé   : {dest}")
    print(f"XML       : {dest / name}")
    print(f"documents : {attached} justificatifs joints (ne pas toucher)")
    return 0


def cmd_pack(args) -> int:
    src, dest = Path(args.source), Path(args.dest)
    xmls = sorted(src.glob("*.xml"))
    if len(xmls) != 1:
        sys.exit(f"attendu 1 XML dans {src}, trouvé {len(xmls)}")

    # The XML must still parse, otherwise VaudTax will reject the file.
    try:
        ET.parse(xmls[0])
    except ET.ParseError as exc:
        sys.exit(f"XML invalide ({exc}) — corriger avant de reconstruire l'archive")

    present = {p.name: p for p in src.iterdir()
               if p.is_file() and not p.name.startswith(".")}

    # Replay the original entry order when we know it; fall back to sorting.
    order = []
    manifest_path = src / MANIFEST
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["entries"]:
            if entry["name"] in present:
                order.append((present.pop(entry["name"]), entry["compress_type"]))
        for name in sorted(present):
            order.append((present[name], zipfile.ZIP_DEFLATED))
    else:
        order = [(present[n], zipfile.ZIP_DEFLATED) for n in sorted(present)]

    if dest.exists():
        backup = dest.with_suffix(dest.suffix + ".bak")
        shutil.copy2(dest, backup)
        print(f"sauvegarde: {backup}")

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, compress_type in order:
            zf.write(path, path.name, compress_type=compress_type)

    print(f"écrit     : {dest} ({len(order)} entrées)")
    print("Ouvrir le fichier dans VaudTax pour valider avant toute autre étape.")
    return 0


# --------------------------------------------------------------------------- #
# Read-only views
# --------------------------------------------------------------------------- #

def render(elem: ET.Element, depth: int = 0) -> None:
    text = (elem.text or "").strip()
    print("  " * depth + local(elem.tag) + (f" = {text}" if text else ""))
    for child in elem:
        render(child, depth + 1)


def cmd_dump(args) -> int:
    tree, name = load_tree(Path(args.source))
    print(f"# {name}\n")
    wanted = set(args.section or [])
    for child in tree.getroot():
        tag = local(child.tag)
        if wanted and tag not in wanted:
            continue
        if not wanted and not args.all and tag in NOISE:
            continue
        render(child)
    return 0


def flatten(elem: ET.Element, prefix: str, acc: dict) -> None:
    """Flatten an element into path -> value, disambiguating repetitions."""
    counters: dict = defaultdict(int)
    for child in elem:
        tag = local(child.tag)
        if tag in VOLATILE:
            continue
        key = None
        for candidate in KEYS.get(tag, []):
            value = child.findtext(NSB + candidate)
            if value and value.strip():
                key = value.strip()
                break
        if key is None and sum(1 for c in elem if local(c.tag) == tag) > 1:
            counters[tag] += 1
            key = f"#{counters[tag]}"
        path = f"{prefix}/{tag}" + (f"[{key}]" if key else "")
        text = (child.text or "").strip()
        if text:
            acc[path] = text
        flatten(child, path, acc)


def flat_map(path: Path):
    tree, name = load_tree(path)
    acc: dict = {}
    flatten(tree.getroot(), "", acc)
    acc = {k: v for k, v in acc.items()
           if not any(k.startswith(f"/{n}") for n in NOISE)}
    return acc, name


def cmd_diff(args) -> int:
    old, old_name = flat_map(Path(args.previous))
    new, new_name = flat_map(Path(args.current))
    print(f"# Comparatif\n- précédent : {old_name}\n- courant   : {new_name}\n")

    removed = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))
    changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
    identical = sorted(k for k in set(old) & set(new) if old[k] == new[k])

    def money_delta(a: str, b: str) -> str:
        try:
            fa, fb = float(a.replace(" ", "")), float(b.replace(" ", ""))
        except ValueError:
            return ""
        if fa == 0:
            return "  (nouveau montant)"
        return f"  ({fb - fa:+.0f}, {100 * (fb - fa) / abs(fa):+.1f}%)"

    print(f"## Modifiés ({len(changed)})\n")
    for key in changed:
        print(f"- `{key}`\n  {old[key]} → {new[key]}{money_delta(old[key], new[key])}")

    print(f"\n## Absents cette année ({len(removed)})\n")
    for key in removed:
        print(f"- `{key}` (valait {old[key]})")

    print(f"\n## Nouveaux cette année ({len(added)})\n")
    for key in added:
        print(f"- `{key}` = {new[key]}")

    # A monetary amount identical to the franc two years running is nearly
    # always a value that was never updated, not a coincidence.
    frozen = [k for k in identical if re.fullmatch(r"-?\d+(\.\d+)?", old[k])
              and float(old[k]) not in (0.0, 1.0)
              and not re.search(r"iban|numCompte|avs|numeroValeur|numParcelle|"
                                r"numeroOfs|anneeConstruction|coefficient",
                                k, re.IGNORECASE)]
    print(f"\n## Montants inchangés depuis l'an dernier ({len(frozen)})\n")
    print("À passer en revue : un montant identique au franc près d'une année sur")
    print("l'autre est le plus souvent un oubli de mise à jour.\n")
    for key in sorted(frozen):
        print(f"- `{key}` = {old[key]}")
    return 0


# --------------------------------------------------------------------------- #
# Consistency checks
# --------------------------------------------------------------------------- #

def _problem(problems: list, severity: str, code: str, message: str) -> None:
    problems.append({"severity": severity, "code": code, "message": message})


def collect_checks(path: Path):
    """Run every check. Returns (name, notes, problems)."""
    tree, name = load_tree(path)
    root = tree.getroot()
    problems: list = []
    notes: list = []

    period = root.findtext(NSB + "fiscalPeriod")
    notes.append(f"période fiscale : {period}")

    immeubles = sections(root, "biensImmobiliers")

    # --- dates consistent with the fiscal period ---------------------------- #
    if period and period.isdigit():
        dated = [("fraisMedicaux", "datePaiement", e)
                 for e in sections(root, "fraisMedicaux")]
        dated += [("fraisEntretienImmeuble", "dateFacture", e)
                  for immo in immeubles for e in immo.iter(NSB + "fraisEntretienImmeuble")]
        dated += [("fraisPerfectionnementFormations", "datePaiement", e)
                  for e in sections(root, "fraisPerfectionnementFormations")]
        for tag, field, elem in dated:
            value = elem.findtext(NSB + field) or ""
            if value[:4] and value[:4] != period:
                label = (text_of(elem, "etabliPar") or text_of(elem, "maitreEtat")
                         or text_of(elem, "description") or "?")
                _problem(problems, "error", "date-hors-periode",
                         f"{tag} « {label} » : {field}={value} hors période {period}")

        for elem in sections(root, "activiteSalarieeRevenus"):
            employeur = text_of(elem, "employeur") or "?"
            for field in ("dateDebut", "dateFin"):
                value = text_of(elem, field)
                if value[:4] and value[:4] != period:
                    _problem(problems, "warning", "periode-emploi",
                             f"activiteSalarieeRevenus « {employeur} » : "
                             f"{field}={value} hors période {period}")

    # --- securities: every account needs a balance -------------------------- #
    total = 0.0
    comptes = sections(root, "etatTitres")
    for elem in comptes:
        solde = elem.findtext(NSB + "soldeCompteCHF")
        label = text_of(elem, "etablissement") or text_of(elem, "iban") or "?"
        if solde is None or not solde.strip():
            _problem(problems, "error", "solde-manquant",
                     f"etatTitres « {label} » : soldeCompteCHF manquant")
        else:
            total += float(solde)
    notes.append(f"{len(comptes)} comptes, total soldes = {chf(total)} CHF")

    # --- duplicate accounts ------------------------------------------------- #
    # Importing an eReleve into a file carried over from N-1 creates a second
    # line next to the one already listed. Discriminate on (IBAN, account
    # number, currency): one IBAN legitimately carries several currencies.
    seen: dict = defaultdict(list)
    for elem in comptes:
        iban = text_of(elem, "iban").replace(" ", "")
        if not iban:
            continue
        devise = elem.find(NSB + "devise/" + NSB + "label")
        seen[(iban, text_of(elem, "numCompte"),
              devise.text if devise is not None else "")].append(
                  text_of(elem, "etablissement") or "?")
    for (iban, _, _), labels in sorted(seen.items()):
        if len(labels) > 1:
            _problem(problems, "error", "compte-doublon",
                     f"compte {iban} déclaré {len(labels)} fois ({', '.join(labels)}) — "
                     f"doublon probable entre une saisie reprise de N-1 et un "
                     f"eRelevé importé")

    # --- IBAN checksums ----------------------------------------------------- #
    for elem in comptes:
        iban = text_of(elem, "iban")
        if iban and not iban_is_valid(iban):
            label = text_of(elem, "etablissement") or "?"
            _problem(problems, "error", "iban-invalide",
                     f"etatTitres « {label} » : IBAN {iban} ne passe pas le "
                     f"contrôle mod-97 (chiffre erroné ?)")

    # --- eReleve provenance -------------------------------------------------- #
    ereleves = sum(1 for e in comptes if e.findtext(NSB + "identifiantEReleve"))
    notes.append(f"dont {ereleves} importés par eRelevé, "
                 f"{len(comptes) - ereleves} saisis à la main")
    if period and period.isdigit():
        for elem in comptes:
            ident = elem.findtext(NSB + "identifiantEReleve")
            if ident and period not in ident:
                label = text_of(elem, "etablissement") or "?"
                _problem(problems, "error", "ereleve-perime",
                         f"etatTitres « {label} » : identifiantEReleve {ident} ne "
                         f"mentionne pas {period} — eRelevé de l'année précédente "
                         f"importé par mégarde ?")

    # --- AVS numbers --------------------------------------------------------- #
    for elem in root.iter(NSB + "avs"):
        value = (elem.text or "").strip()
        if value and not avs_is_valid(value):
            _problem(problems, "warning", "avs-invalide",
                     f"numéro AVS {value} ne passe pas le contrôle de clé")

    # --- salaries ------------------------------------------------------------ #
    for elem in sections(root, "activiteSalarieeRevenus"):
        employeur = text_of(elem, "employeur") or "?"
        net = elem.findtext(NSB + "salaireNet")
        if not net:
            _problem(problems, "error", "salaire-manquant",
                     f"activiteSalarieeRevenus « {employeur} » : salaireNet manquant")
        else:
            notes.append(f"salaire net {employeur} : {chf(float(net))} CHF")

    # --- pillar 3a ceiling ---------------------------------------------------- #
    if period and period.isdigit() and int(period) in PILIER3A_CEILINGS:
        employee_cap, _ = PILIER3A_CEILINGS[int(period)]
        for assurance in sections(root, "primesEtCotisationsAssurance"):
            for n in ("1", "2"):
                field = f"formesReconnuesPrevoyanceIndividuelleContribuable{n}"
                value = text_of(assurance, field)
                if value and float(value) > employee_cap:
                    _problem(problems, "warning", "plafond-3a",
                             f"{field} = {chf(float(value))} dépasse le plafond "
                             f"salarié {chf(employee_cap)} de {period} — vérifier "
                             f"le statut (indépendant sans 2e pilier ?)")

    # --- mortgage interest must appear in two places -------------------------- #
    immo_interets = [i.findtext(NSB + "interetsPassifsImmeuble") for i in immeubles]
    for elem in sections(root, "interetsDettes"):
        if text_of(elem, "isGageImmobGarantie") != "true":
            continue
        interets = elem.findtext(NSB + "interets")
        if interets and interets not in [v for v in immo_interets if v]:
            _problem(problems, "error", "interets-hypothecaires",
                     f"intérêts hypothécaires {interets} déclarés dans interetsDettes "
                     f"mais absents de biensImmobiliers/interetsPassifsImmeuble "
                     f"(valeurs vues : {immo_interets})")

    # --- duplicate trackingIndex within one element type ---------------------- #
    for tag in {local(c.tag) for c in root}:
        indexes = [c.findtext(NSB + "trackingIndex") for c in sections(root, tag)
                   if c.findtext(NSB + "trackingIndex")]
        dupes = {i for i in indexes if indexes.count(i) > 1}
        if dupes:
            _problem(problems, "error", "trackingindex-doublon",
                     f"{tag} : trackingIndex dupliqué(s) {sorted(dupes)}")

    # --- attachments referenced by the XML must exist in the ZIP -------------- #
    if path.is_file():
        with zipfile.ZipFile(path) as zf:
            members = set(zf.namelist())
        referenced = {e.findtext(NSB + "key") for e in root.iter(NSB + "documents")}
        referenced.discard(None)
        for key in sorted(referenced - members):
            _problem(problems, "error", "justificatif-absent",
                     f"justificatif référencé « {key} » absent de l'archive")
        orphans = members - referenced - {n for n in members if n.endswith(".xml")}
        for key in sorted(orphans):
            notes.append(f"pièce présente mais non référencée : {key}")

    problems.sort(key=lambda p: SEVERITY_ORDER.get(p["severity"], 9))
    return name, notes, problems


def cmd_check(args) -> int:
    path = Path(args.source)
    name, notes, problems = collect_checks(path)

    tree, _ = load_tree(path)
    period = tree.getroot().findtext(NSB + "fiscalPeriod")
    if args.year and period != str(args.year):
        problems.insert(0, {
            "severity": "error", "code": "periode-inattendue",
            "message": f"fiscalPeriod={period} alors que l'année attendue "
                       f"est {args.year}"})

    if args.json:
        print(json.dumps({"file": name, "notes": notes, "problems": problems},
                         indent=2, ensure_ascii=False))
    else:
        print(f"# Contrôles — {name}\n")
        for note in notes:
            print(f"- {note}")
        errors = [p for p in problems if p["severity"] == "error"]
        warnings = [p for p in problems if p["severity"] == "warning"]
        print(f"\n## Anomalies ({len(errors)})\n")
        for problem in errors:
            print(f"- ⚠️  {problem['message']}")
        if not errors:
            print("- aucune")
        if warnings:
            print(f"\n## Points à vérifier ({len(warnings)})\n")
            for problem in warnings:
                print(f"- ℹ️  {problem['message']}")

    if any(p["severity"] == "error" for p in problems):
        return 1
    if args.strict and problems:
        return 1
    return 0


def cmd_ereleves(args) -> int:
    """Separate eReleve-imported accounts from hand-entered ones.

    An account filled by VaudTax's eReleve import carries `identifiantEReleve`
    (the barcode payload) and `nomEreleve`. Those accounts belong to VaudTax and
    must never be edited by hand.
    """
    tree, name = load_tree(Path(args.source))
    root = tree.getroot()
    period = root.findtext(NSB + "fiscalPeriod") or "?"

    imported, manual = [], []
    for elem in sections(root, "etatTitres"):
        entry = {
            "etablissement": text_of(elem, "etablissement") or "?",
            "reference": text_of(elem, "iban") or text_of(elem, "numCompte") or "—",
            "solde": text_of(elem, "soldeCompteCHF") or "—",
            "identifiant": text_of(elem, "identifiantEReleve"),
        }
        (imported if entry["identifiant"] else manual).append(entry)

    releves = [{"designation": text_of(e, "designation"),
                "importe": bool(text_of(e, "identifiantEReleve"))}
               for e in sections(root, "relevesFiscauxBancaires")]

    # A file carried over from N-1 keeps last year's identifiers -- a trap, as
    # the associated amounts would be last year's too.
    stale = [e for e in imported
             if period.isdigit() and period not in e["identifiant"]]

    if args.json:
        print(json.dumps({"file": name, "periode": period, "importes": imported,
                          "manuels": manual, "relevesFiscaux": releves,
                          "identifiantsPerimes": stale},
                         indent=2, ensure_ascii=False))
        return 0

    print(f"# eRelevés — {name} (période {period})\n")
    print(f"## Importés par VaudTax ({len(imported)}) — ne pas éditer à la main\n")
    for e in imported:
        print(f"- {e['etablissement']} · {e['reference']} · {e['solde']} CHF")
    if not imported:
        print("- aucun — l'import des eRelevés n'a probablement pas encore été fait")

    print(f"\n## Saisis manuellement ({len(manual)}) — à remplir depuis les documents\n")
    for e in manual:
        print(f"- {e['etablissement']} · {e['reference']} · {e['solde']} CHF")
    if not manual:
        print("- aucun")

    print(f"\n## Relevés fiscaux, code 410 ({len(releves)})\n")
    for r in releves:
        print(f"- {r['designation']} · "
              f"{'importé' if r['importe'] else 'saisi à la main'}")
    if not releves:
        print("- aucun")

    if stale:
        print(f"\n## ⚠️  Identifiants ne mentionnant pas {period} ({len(stale)})\n")
        print("Probablement repris de l'année précédente : les montants associés "
              "sont ceux de N-1. Ré-importer les eRelevés dans VaudTax.\n")
        for e in stale:
            print(f"- {e['etablissement']} · `{e['identifiant']}`")
    return 0


def _force_utf8_output() -> None:
    """Make the output survive a legacy Windows console code page.

    All user-facing text here is French and the check markers are emoji, so a
    cp1252 console would raise UnicodeEncodeError halfway through a report.
    Windows is also where the `uv run --script` path matters most, since it is
    where a system Python is least likely to exist.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:          # replaced by a test harness or a pipe
            continue
        # Already detached, or a stream that refuses re-encoding.
        with contextlib.suppress(ValueError, OSError):
            reconfigure(encoding="utf-8")


def main() -> int:
    _force_utf8_output()
    parser = argparse.ArgumentParser(
        description="Outils de lecture/écriture des fichiers .vaudtax",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("unpack", help="extraire un .vaudtax dans un dossier")
    p.add_argument("source")
    p.add_argument("dest")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_unpack)

    p = sub.add_parser("pack", help="reconstruire un .vaudtax depuis un dossier")
    p.add_argument("source")
    p.add_argument("dest")
    p.set_defaults(func=cmd_pack)

    p = sub.add_parser("dump", help="afficher l'arbre XML")
    p.add_argument("source")
    p.add_argument("--section", nargs="*", help="limiter à ces éléments racine")
    p.add_argument("--all", action="store_true", help="inclure userProfil/guidedNav")
    p.set_defaults(func=cmd_dump)

    p = sub.add_parser("diff", help="comparer deux déclarations")
    p.add_argument("previous")
    p.add_argument("current")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("ereleves",
                       help="comptes importés par eRelevé vs saisis à la main")
    p.add_argument("source")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_ereleves)

    p = sub.add_parser("check", help="contrôles de cohérence")
    p.add_argument("source")
    p.add_argument("--year", type=int)
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="code de sortie non nul aussi sur les avertissements")
    p.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
