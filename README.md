# FiducAI 🇨🇭🤖🇨🇭

**Agent skills for Swiss tax returns.** Point your favorite AI assistant at a folder of documents and a half-empty tax file, and get back a filled-in draft, a list of
what's missing, and a paper trail explaining how numbers were obtained.


> ⚠️
> **FiducAI is not tax advice, and it is not a tax advisor.** You must verify its outputs as it will likely get things wrong. It might contain plain bugs, too.

> ⚠️
> **Users are responsible for the privacy of their data.**
> You should ensure that your model provider (if any) respects the confidentiality of your data (e.g. that it doesn't train on it).
> [Disclaimer](#disclaimer).

---

## What it does today

| Skill | What it's for |
|---|---|
| **`vaud-tax-return`** | Fills a VaudTax `.vaudtax` file (canton of Vaud) from your documents. Checks it, compares it against last year, and reports what it did. Carries the Vaud figures: deduction ceilings, thresholds, scales. |
| **`swiss-tax-basics`** | Canton-agnostic Swiss tax knowledge: how to reason about deductions and their traps, federal pillar 3a ceilings, securities and wealth, real estate. Sourced, with consultation dates. |

Both are in **French**, because VaudTax is, and because the documents you'll
feed it most often are. The repository, code and contributor docs are in English.

Do you want to extend it other cantons? Or improve it in any other way? PRs are welcome!

## What it will not do

- Submit your return. That stays a manual step in the cantonal software.
- Attach your supporting documents. Also manual, also on purpose.
- Invent a number. If a figure has no source, it becomes a question, not a
  value. This is the single rule everything else is built around.
- Replace a professional in some complicated cases — self-employment, inheritance, cross-border situations, or any other situation that's not handled well today.

## Install

You need an agent harness that supports skills — Claude Code, Codex and Gemini
CLI all read the same `SKILL.md` format — and a way to run a Python script. The
script itself has **no dependencies**: standard library only, Python 3.9+.

**[uv](https://docs.astral.sh/uv/) is the recommended way**, and the only one
that works if you don't already have Python: uv is a single binary that
provisions an interpreter for you.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Already have Python 3.9+? You can skip uv entirely — everything works with
plain `python3` too.

Then:

```bash
git clone https://github.com/hrzn/fiducai.git
cd fiducai
./install.sh
```

On Windows, `install.sh` needs a bash shell (Git Bash or WSL). Without one, copy
the folders manually as shown below — that's all the installer does.

The installer asks where to put the skills and copies them there. Useful flags:
`--target DIR`, `--project` (install into `./.agents/skills`), `--link`
(symlink, for development), `--list` (show what would be installed).

Or just copy the directories yourself — a skill is a folder with a `SKILL.md`:

```bash
cp -R skills/* ~/.claude/skills/       # Claude Code
cp -R skills/* ~/.codex/skills/        # Codex
cp -R skills/* ~/.gemini/skills/       # Gemini CLI
cp -R skills/* ~/.agents/skills/       # shared convention (Codex, Gemini CLI)
```

Use `.claude/`, `.codex/` or `.gemini/` inside a project instead of `~/` to
install for that project only.

**Keep both skills together**: `vaud-tax-return` reads `swiss-tax-basics` as a
sibling.

## Use

Ask your agent, in plain French or English, for instance:

> aide-moi à remplir ma déclaration d'impôts 2025

It will ask you for what it needs. There are four inputs, and it reads nothing
else — no rummaging around in neighbouring folders:

| Input | Required | What it is |
|---|---|---|
| A starting `.vaudtax` | yes | Produced **by VaudTax itself**, via "reprendre l'année précédente". The gesdem reference in the filename ties it to your file at the canton and cannot be fabricated. |
| A documents folder | yes | Your PDFs for the year. No naming convention imposed. |
| `profil-fiscal.md` | no | Your stable personal facts — see below. |
| Last year's `.vaudtax` | no | Enables the year-on-year comparison and sanity checks. |

You get back a draft `.vaudtax` (with a `.bak` of the original) plus a report
folder: what documents are missing, where every value came from, what changed
since last year, and what's still open.

### Your personal profile

No generic skill can guess that your employer produces a separate annex to the salary certificate, or that you settled on a particular method for deducting your corporate yacht (yes, that can happen).

That lives in a `profil-fiscal.md` you keep **on your own machine**, next to
your documents. Copy
[the template](skills/vaud-tax-return/assets/profil-fiscal-modele.md) and fill
in what applies in ordinary prose. The skill reads it if you
give it, offers to create it if you don't, and proposes additions to it at the
end of every run, so it gets better each year.

A document always wins over the profile. If they disagree, you're told.

## Data privacy

Fiducai runs locally through your agent. It has no server, no telemetry and no
account. Your documents go wherever your agent already sends them to, so make sure you're fine with that.

For the repository itself, `scripts/check_no_pii.py` runs as a pre-commit hook
and in CI, and refuses IBANs, AVS/AHV numbers, tax files and PDFs, to prevent accidental commits of personal information.

## Contributing

Contributions are more than welcome, especially for **other cantons**. See [CONTRIBUTING.md](CONTRIBUTING.md)
and [docs/cantons.md](docs/cantons.md) for the lay of the land (spoiler: Swiss
cantonal tax software is gloriously fragmented, and every canton is its own
little adventure).

```bash
git config core.hooksPath scripts/git-hooks   # enable the no-PII hook. do this.
uv sync --group dev
uv run pytest -q
uv run ruff check .
```

`uv.lock` pins the dev tools, so your ruff agrees with CI's. No uv? `pip install
pytest ruff` and run them directly — the skills themselves stay dependency-free
either way.

Tests run against a **synthetic** declaration built by
[`tests/build_fixture.py`](tests/build_fixture.py). Each check is tested by deriving a deliberately broken variant from it.

## Disclaimer

Fiducai is provided **as is**, without warranty of any kind, under the
[Apache License 2.0](LICENSE). It does not constitute tax, legal or financial
advice, and using it creates no advisory relationship of any kind with anyone.

Tax rules change, cantonal practice varies, and this software may be wrong or
out of date. **Every figure it produces must be verified against your own
documents and, where it matters, with a qualified professional.** Only the tax
authority decides what your return should say.

Fiducai is an independent project. It is **not affiliated with, endorsed by, or
supported by** any Swiss federal, cantonal or communal tax administration, nor
by the publishers of VaudTax or any other cantonal tax software. Those names
are used only to describe what these tools interoperate with.

Users are responsible for the privacy/confidentiality of their data.