# Fiducai — notes for agents

Fiducai is a collection of **skills**: directories under `skills/`, each with a
`SKILL.md` whose front matter carries a `name` and a `description`. Nothing here
is specific to one harness. If you are an agent working *in* this repository,
read on. If you are looking for a skill to *use*, load `skills/*/SKILL.md`.

## Layout

```
skills/swiss-tax-basics/     canton-agnostic Swiss tax knowledge (FR)
skills/vaud-tax-return/      the VaudTax skill (FR), incl. scripts/vaudtax.py
                             and chiffres-cles-vd.md, the Vaud figures
tests/                       pytest suite + synthetic fixture generator
scripts/                     repository guards (PII, skill metadata) and git hooks
docs/                        cantonal landscape
```

Language convention: **English** for code, comments, tests and contributor
documentation; **French** for skill content and anything a user reads, because
the tax software and the source documents are French.

## Hard rules

1. **No real tax data, ever.** No `.vaudtax`, no PDF, no IBAN, no AVS number, no
   real name. `scripts/check_no_pii.py` enforces this in CI and as a pre-commit
   hook; do not weaken it to make a commit pass. If you need an example, extend
   `tests/build_fixture.py`.
2. **Never invent a tax figure.** Every amount or threshold must trace to an
   official source, with a consultation date, recorded in the sources table of
   the skill it belongs to. A number you remember is not a source.
3. **Keep cantonal figures in the cantonal skill.** `swiss-tax-basics` holds
   only what is identical Switzerland-wide — essentially the pillar 3a ceilings.
   Deduction ceilings, thresholds, scales and wealth-tax rules are cantonal and
   live in that canton's skill (`chiffres-cles-vd.md` for Vaud). Putting a Vaud
   figure in the shared skill is how the next canton inherits a wrong number.
4. **Never re-serialise the VaudTax XML** with a parser. `ElementTree` rewrites
   every tag with an `ns0:` prefix. Edit it as text; that is why `vaudtax.py`
   only unpacks and repacks.
5. **The fixture stays consistent.** `tests/fixtures/exemple.vaudtax` must pass
   `check` with zero errors. Test a new check by deriving a broken variant
   in-test via the `make_variant` fixture, not by breaking the base file.

## Working on the tooling

```bash
uv sync --group dev                     # or: pip install pytest ruff
uv run pytest -q
uv run ruff check .
uv run scripts/check_no_pii.py
uv run scripts/check_skills.py
uv run tests/build_fixture.py           # regenerate the fixture after editing it
```

Everything also works with a plain `python3` in place of `uv run`; CI exercises
both paths deliberately.

`vaudtax.py` is deliberately a **single stdlib-only file** living inside the
skill, so a skill directory can be copied anywhere and still work. Do not turn
it into a package or give it dependencies.

It carries a [PEP 723](https://peps.python.org/pep-0723/) header
(`requires-python = ">=3.9"`, no dependencies) so that `uv run --script` can
provision an interpreter on a machine with no Python — the common case on
Windows. Keep that header valid: the `uv` CI job runs the script through it, and
`SKILL.md` step 3 tells the agent to try `uv run --script` before `python3`.

## Adding a canton

1. `skills/<canton>-tax-return/` with `SKILL.md`, `references/`, and `scripts/`
   if the canton's format needs tooling.
2. Reuse `swiss-tax-basics` for anything not canton-specific rather than
   duplicating it — and do not add cantonal figures to it.
3. Put the canton's per-year figures in its own
   `references/chiffres-cles-<ct>.md`, with a sources table carrying
   consultation dates. `vaud-tax-return/references/chiffres-cles-vd.md` is the
   model to copy.
4. Update `docs/cantons.md`.

Check first whether the canton's software lets you **export the return as a file
and import it back**. That, not whether it runs in a browser, is what decides
whether a skill can fill anything in: VaudTax is a web service and still
round-trips a `.vaudtax` file. Where no such round-trip exists, a skill can
still gather documents, compute thresholds and produce a worksheet to type in —
see `docs/cantons.md`.
