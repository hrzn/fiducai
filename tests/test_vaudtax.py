"""Tests for the `.vaudtax` tooling.

The synthetic fixture in `build_fixture.py` is consistent by construction, so
every check is exercised by deriving a deliberately broken variant from it. That
keeps the repository free of committed broken binaries and makes each test state
plainly which defect it is about.
"""

from __future__ import annotations

import zipfile

import build_fixture
from conftest import codes

# --------------------------------------------------------------------------- #
# Identifier validation
# --------------------------------------------------------------------------- #

def test_iban_checksum(vt):
    good = build_fixture.IBAN_VALID_VECTOR
    spaced = " ".join(good[i:i + 4] for i in range(0, len(good), 4)).lower()

    assert vt.iban_is_valid(good)
    assert vt.iban_is_valid(spaced), "casse et espaces tolérées"
    assert not vt.iban_is_valid(build_fixture.IBAN_INVALID_VECTOR), "clé fausse"
    assert not vt.iban_is_valid(build_fixture.IBAN_TOO_SHORT_VECTOR)
    assert not vt.iban_is_valid("")


def test_avs_checksum(vt):
    assert vt.avs_is_valid(build_fixture.AVS_VALID_VECTOR)
    assert vt.avs_is_valid(build_fixture.AVS_VALID_VECTOR_UNSEPARATED), \
        "séparateurs facultatifs"
    assert not vt.avs_is_valid(build_fixture.AVS_INVALID_VECTOR), "clé fausse"
    assert not vt.avs_is_valid(build_fixture.AVS_WRONG_PREFIX_VECTOR), \
        "ne commence pas par 756"
    assert not vt.avs_is_valid(build_fixture.AVS_TRUNCATED_VECTOR)


def test_fixture_identifiers_are_valid(vt):
    """The generator must produce identifiers that pass the checks."""
    assert vt.iban_is_valid(build_fixture.IBAN_A)
    assert vt.avs_is_valid(build_fixture.AVS_1)


# --------------------------------------------------------------------------- #
# Archive handling
# --------------------------------------------------------------------------- #

def test_roundtrip_preserves_entries(vt, fixture_path, tmp_path):
    """unpack -> pack must reproduce every entry, in order, with identical CRCs."""
    work = tmp_path / "work"
    repacked = tmp_path / "repacked.vaudtax"

    vt.cmd_unpack(_args(source=str(fixture_path), dest=str(work), force=False))
    vt.cmd_pack(_args(source=str(work), dest=str(repacked)))

    with zipfile.ZipFile(fixture_path) as before, zipfile.ZipFile(repacked) as after:
        assert [i.filename for i in before.infolist()] == \
               [i.filename for i in after.infolist()]
        assert [i.CRC for i in before.infolist()] == [i.CRC for i in after.infolist()]


def test_unpack_writes_manifest(vt, fixture_path, tmp_path):
    work = tmp_path / "work"
    vt.cmd_unpack(_args(source=str(fixture_path), dest=str(work), force=False))
    assert (work / vt.MANIFEST).exists()


def test_pack_refuses_invalid_xml(vt, fixture_path, tmp_path):
    import pytest

    work = tmp_path / "work"
    vt.cmd_unpack(_args(source=str(fixture_path), dest=str(work), force=False))
    xml = next(work.glob("*.xml"))
    xml.write_text(xml.read_text(encoding="utf-8").replace("</vaudTaxData>", ""),
                   encoding="utf-8")

    with pytest.raises(SystemExit):
        vt.cmd_pack(_args(source=str(work), dest=str(tmp_path / "out.vaudtax")))


def test_pack_backs_up_existing_target(vt, fixture_path, tmp_path):
    work = tmp_path / "work"
    target = tmp_path / "target.vaudtax"
    target.write_bytes(b"ancien contenu")

    vt.cmd_unpack(_args(source=str(fixture_path), dest=str(work), force=False))
    vt.cmd_pack(_args(source=str(work), dest=str(target)))

    assert (tmp_path / "target.vaudtax.bak").read_bytes() == b"ancien contenu"


# --------------------------------------------------------------------------- #
# The namespace / tag-collision trap
# --------------------------------------------------------------------------- #

def test_sections_ignores_guided_nav_booleans(vt, fixture_path):
    """`guidedNav/displayedSubForms` reuses section tag names.

    A naive `root.iter("etatTitres")` would pick up the display boolean and
    report five accounts instead of four.
    """
    tree, _ = vt.load_tree(fixture_path)
    root = tree.getroot()

    assert len(vt.sections(root, "etatTitres")) == 4
    assert len(list(root.iter(vt.NSB + "etatTitres"))) == 5, \
        "le gabarit doit contenir le booléen d'affichage homonyme"


# --------------------------------------------------------------------------- #
# Checks: the fixture is clean, each variant trips exactly one check
# --------------------------------------------------------------------------- #

def test_fixture_has_no_errors(vt, fixture_path):
    _, _, problems = vt.collect_checks(fixture_path)
    assert [p for p in problems if p["severity"] == "error"] == []


def test_multicurrency_same_iban_is_not_a_duplicate(vt, fixture_path):
    """One IBAN legitimately carries several currencies at a broker."""
    _, _, problems = vt.collect_checks(fixture_path)
    assert "compte-doublon" not in codes(problems)


def test_duplicate_account_detected(vt, make_variant):
    """Same IBAN, same account number, same currency: a real duplicate."""
    variant = make_variant([("<label>USD</label>", "<label>CHF</label>"),
                            ("<id>3</id>", "<id>1</id>")])
    _, _, problems = vt.collect_checks(variant)
    assert "compte-doublon" in codes(problems)


def test_invalid_iban_detected(vt, make_variant):
    broken = build_fixture.IBAN_A[:-1] + str((int(build_fixture.IBAN_A[-1]) + 1) % 10)
    variant = make_variant([(build_fixture.IBAN_A, broken)])
    _, _, problems = vt.collect_checks(variant)
    assert "iban-invalide" in codes(problems)


def test_invalid_avs_detected(vt, make_variant):
    broken = build_fixture.AVS_1[:-1] + str((int(build_fixture.AVS_1[-1]) + 1) % 10)
    variant = make_variant([(build_fixture.AVS_1, broken)])
    _, _, problems = vt.collect_checks(variant)
    assert "avs-invalide" in codes(problems)


def test_stale_ereleve_identifier_detected(vt, make_variant):
    """The classic trap: last year's eRelevé imported into this year's file."""
    variant = make_variant([("CH00900000100000002_20251231",
                             "CH00900000100000002_20241231")])
    _, _, problems = vt.collect_checks(variant)
    assert "ereleve-perime" in codes(problems)


def test_missing_balance_detected(vt, make_variant):
    variant = make_variant([("<soldeCompteCHF>18450</soldeCompteCHF>",
                             "<soldeCompteCHF></soldeCompteCHF>")])
    _, _, problems = vt.collect_checks(variant)
    assert "solde-manquant" in codes(problems)


def test_missing_salary_detected(vt, make_variant):
    variant = make_variant([("<salaireNet>95000</salaireNet>", "")])
    _, _, problems = vt.collect_checks(variant)
    assert "salaire-manquant" in codes(problems)


def test_mortgage_interest_must_appear_in_both_places(vt, make_variant):
    """Declared under interetsDettes but not carried onto the property."""
    variant = make_variant([("<interetsPassifsImmeuble>4200</interetsPassifsImmeuble>",
                             "<interetsPassifsImmeuble>3900</interetsPassifsImmeuble>")])
    _, _, problems = vt.collect_checks(variant)
    assert "interets-hypothecaires" in codes(problems)


def test_duplicate_tracking_index_detected(vt, make_variant):
    variant = make_variant([("<trackingIndex>2</trackingIndex>\n        "
                             "<employeur>Autre Employeur Exemple</employeur>",
                             "<trackingIndex>1</trackingIndex>\n        "
                             "<employeur>Autre Employeur Exemple</employeur>")])
    _, _, problems = vt.collect_checks(variant)
    assert "trackingindex-doublon" in codes(problems)


def test_out_of_period_date_detected(vt, make_variant):
    variant = make_variant([("<datePaiement>2025-03-08</datePaiement>",
                             "<datePaiement>2024-03-08</datePaiement>")])
    _, _, problems = vt.collect_checks(variant)
    assert "date-hors-periode" in codes(problems)


def test_out_of_period_employment_is_a_warning(vt, make_variant):
    variant = make_variant([("<dateFin>2025-12-31</dateFin>",
                             "<dateFin>2024-12-31</dateFin>")])
    _, _, problems = vt.collect_checks(variant)
    matching = [p for p in problems if p["code"] == "periode-emploi"]
    assert matching and all(p["severity"] == "warning" for p in matching)


def test_missing_attachment_detected(vt, make_variant):
    variant = make_variant([("<key>doc1737000000000</key>",
                             "<key>doc1737000000999</key>")])
    _, _, problems = vt.collect_checks(variant)
    assert "justificatif-absent" in codes(problems)


def test_pillar_3a_ceiling(vt, make_variant):
    """Only meaningful once the ceiling table is populated from official sources."""
    import pytest

    if 2025 not in vt.PILIER3A_CEILINGS:
        pytest.skip("plafonds 3a non encore renseignés — cf. chiffres-cles.md")
    ceiling = vt.PILIER3A_CEILINGS[2025][0]
    variant = make_variant([
        ("<formesReconnuesPrevoyanceIndividuelleContribuable1>7258<",
         f"<formesReconnuesPrevoyanceIndividuelleContribuable1>{ceiling + 500}<")])
    _, _, problems = vt.collect_checks(variant)
    assert "plafond-3a" in codes(problems)


# --------------------------------------------------------------------------- #
# Exit codes
# --------------------------------------------------------------------------- #

def test_check_exit_codes(vt, fixture_path, make_variant, capsys):
    assert vt.cmd_check(_args(source=str(fixture_path), year=2025,
                              json=False, strict=False)) == 0

    assert vt.cmd_check(_args(source=str(fixture_path), year=2024,
                              json=False, strict=False)) == 1, \
        "une période inattendue est une erreur"

    warning_only = make_variant([("<dateFin>2025-12-31</dateFin>",
                                  "<dateFin>2024-12-31</dateFin>")])
    assert vt.cmd_check(_args(source=str(warning_only), year=2025,
                              json=False, strict=False)) == 0
    assert vt.cmd_check(_args(source=str(warning_only), year=2025,
                              json=False, strict=True)) == 1
    capsys.readouterr()


def test_force_utf8_output_survives_a_replaced_stream(vt, monkeypatch):
    """Must not explode when stdout has no reconfigure(), as under capture."""
    import io

    monkeypatch.setattr("sys.stdout", io.StringIO())
    monkeypatch.setattr("sys.stderr", io.StringIO())
    vt._force_utf8_output()


def test_check_json_output(vt, fixture_path, capsys):
    import json

    vt.cmd_check(_args(source=str(fixture_path), year=2025, json=True, strict=False))
    payload = json.loads(capsys.readouterr().out)
    assert set(payload) == {"file", "notes", "problems"}


def test_ereleves_json_output(vt, fixture_path, capsys):
    import json

    vt.cmd_ereleves(_args(source=str(fixture_path), json=True))
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["importes"]) == 1
    assert len(payload["manuels"]) == 3
    assert payload["identifiantsPerimes"] == []


# --------------------------------------------------------------------------- #
# diff
# --------------------------------------------------------------------------- #

def test_diff_pairs_accounts_by_iban_not_position(vt, fixture_path, make_variant,
                                                  capsys):
    """Inserting an account must not shift the whole comparison."""
    reordered = make_variant([("<soldeCompteCHF>32000</soldeCompteCHF>",
                               "<soldeCompteCHF>33000</soldeCompteCHF>")])
    vt.cmd_diff(_args(previous=str(fixture_path), current=str(reordered)))
    out = capsys.readouterr().out
    assert "32000 → 33000" in out
    assert "## Modifiés (1)" in out


def test_diff_flags_amounts_unchanged_since_last_year(vt, fixture_path, capsys):
    """The single most valuable signal: a figure nobody updated."""
    vt.cmd_diff(_args(previous=str(fixture_path), current=str(fixture_path)))
    out = capsys.readouterr().out
    assert "Montants inchangés depuis l'an dernier" in out
    assert "salaireNet" in out


def test_diff_ignores_interface_sections(vt, fixture_path, capsys):
    vt.cmd_diff(_args(previous=str(fixture_path), current=str(fixture_path)))
    out = capsys.readouterr().out
    assert "userProfil" not in out
    assert "guidedNav" not in out


# --------------------------------------------------------------------------- #

class _args:
    """Stand-in for the argparse namespace."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.__dict__.setdefault("section", None)
        self.__dict__.setdefault("all", False)
