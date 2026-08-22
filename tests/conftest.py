"""Shared test helpers.

`vaudtax.py` deliberately lives inside the skill directory (so that a skill can
be copied around on its own) rather than in an installable package, so it is
loaded here by path.
"""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "vaud-tax-return" / "scripts" / "vaudtax.py"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_fixture  # noqa: E402


def _load_module():
    spec = importlib.util.spec_from_file_location("vaudtax", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vaudtax = _load_module()


@pytest.fixture(scope="session")
def vt():
    """The vaudtax module under test."""
    return vaudtax


@pytest.fixture
def fixture_path(tmp_path):
    """A freshly built, consistent synthetic declaration."""
    return build_fixture.build(tmp_path / "exemple.vaudtax")


@pytest.fixture
def make_variant(tmp_path):
    """Build a deliberately broken copy of the fixture.

    Takes a list of (old, new) literal replacements applied to the XML text.
    Editing the XML as text is exactly what the skill itself does, so the
    variants exercise the same code path a real edit would.
    """
    counter = {"n": 0}

    def _make(replacements, name=None):
        counter["n"] += 1
        source = build_fixture.build(tmp_path / f"base{counter['n']}.vaudtax")
        target = tmp_path / (name or f"variant{counter['n']}.vaudtax")

        with zipfile.ZipFile(source) as zf:
            entries = [(i.filename, zf.read(i.filename)) for i in zf.infolist()]

        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, payload in entries:
                if filename.endswith(".xml"):
                    text = payload.decode("utf-8")
                    for old, new in replacements:
                        assert old in text, f"motif absent du gabarit : {old!r}"
                        text = text.replace(old, new)
                    payload = text.encode("utf-8")
                zf.writestr(filename, payload)
        return target

    return _make


def codes(problems):
    return {p["code"] for p in problems}
