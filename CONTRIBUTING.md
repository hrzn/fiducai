# Contributing to Fiducai

Contributions welcome — especially from people who have just finished their own
tax return and are still annoyed about some specific thing. That annoyance is
exactly the raw material this project runs on.

## The one rule that matters

**Never commit real tax data.** No `.vaudtax` or equivalent, no PDF, no real
IBAN, AVS number, name, address or amount. Not "anonymised" ones either —
redaction is how leaks happen, because you have to catch every trace.

Enable the guard before you do anything else:

```bash
git config core.hooksPath scripts/git-hooks
```

It runs `scripts/check_no_pii.py` on every commit, and CI runs it again on every
pull request. If you hit a false positive, add the path to `ALLOWED_PREFIXES` in
that script — don't disable the check.

If you need an example that looks realistic, add it to
`tests/build_fixture.py`, which is the one place allowed to contain
identifier-shaped strings. Everything in it is generated or invented.

## Setup

```bash
git clone https://github.com/hrzn/fiducai.git
cd fiducai
git config core.hooksPath scripts/git-hooks

uv sync --group dev          # pytest + ruff, pinned by uv.lock
uv run pytest -q
uv run ruff check .
uv run scripts/check_no_pii.py
uv run scripts/check_skills.py
```

[uv](https://docs.astral.sh/uv/) is recommended — it pins the dev tools via
`uv.lock`, so your ruff agrees with CI's, and it can provision a Python
interpreter on a machine that has none. Without uv, `pip install pytest ruff`
and run everything with `python3` instead; both paths are tested in CI.

Python 3.9+. The skills themselves have **no dependencies** and must stay that
way: `pytest` and `ruff` are for development only. `vaudtax.py` carries a
[PEP 723](https://peps.python.org/pep-0723/) header so it can also be run
standalone with `uv run --script`, which is how a user without Python runs it.

If you add a dev dependency, run `uv sync --group dev` and commit the updated
`uv.lock`.

## Language

English for code, comments, tests, README and these docs. French for skill
content and anything a user reads — the cantonal software and the taxpayer's
documents are in French, and precision in the fiscal vocabulary matters more
than reach.

A German-language canton will need its skill content in German. That is fine and
expected; keep the repository scaffolding in English.

## Adding or changing a tax figure

Every amount, ceiling, rate or threshold must come from an **official source**:
the cantonal tax administration, the AFC/ESTV, the Conférence suisse des impôts.
Not a bank's blog, not a comparison site, and definitely not memory.

When you add one:

1. put it in the **right skill**. A cantonal figure — deduction ceiling, rate,
   threshold, scale — belongs to that canton's skill, e.g.
   `skills/vaud-tax-return/references/chiffres-cles-vd.md`. Only figures that
   are identical Switzerland-wide, such as the pillar 3a ceilings, go in
   `skills/swiss-tax-basics/references/chiffres-cles.md`. When in doubt, assume
   it is cantonal: almost everything is;
2. state it **per fiscal year**, never as "the current amount";
3. add the source, with a **consultation date**, to the sources table of the
   same skill;
4. if the tooling relies on it (like the 3a ceiling in `vaudtax.py`), update both
   and say so in the comment.

Figures that change annually are a maintenance burden by nature. Stating the
year and the source is what makes them safe to keep.

## Adding a canton

Read `docs/cantons.md` first — cantonal tax software is fragmented, and the
first thing to establish is whether the canton lets you **export the return as a
file and import it back after editing**. For instance, Vaudtax produces a `.vaudtax` file.

If no such round-trip exists, a skill can still help a lot — gathering
documents, checking thresholds, explaining rubrics, producing a worksheet to
type in — but it cannot fill anything in, and its `SKILL.md` should say so
plainly.

Then see the "Adding a canton" section of [AGENTS.md](AGENTS.md).

Reverse-engineering a cantonal file format is legitimate — these are files the
software hands to *you*, about *your* data. But: never commit a real one, do not
copy text out of the software's own documentation, and be explicit in your
references about what is observed behaviour rather than specification. Formats
change between versions without notice.

## Testing

Every check in `vaudtax.py` has a test that derives a deliberately broken
variant from the synthetic fixture and asserts that exactly the right code
fires. Please keep that pattern: it documents what each check is for far better
than a comment does.

The base fixture must stay **consistent** — `check` on it reports zero errors.
Regenerate it with `python3 tests/build_fixture.py` after editing the generator.

## Pull requests

Small and focused beats large and comprehensive. Say what you verified and how,
and if you tested against your own real declaration, say that too — just don't
attach it.

## Tone

Fiducai takes tax law seriously and itself much less so. Keep user-facing text
clear and light; keep the warnings unambiguous. Someone is going to file a real
tax return based on this, and the disclaimer is not decoration.

## Licence

By contributing you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE), like the rest of the project.
