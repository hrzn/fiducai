# Cantonal landscape

> [!NOTE]
> **This table is a starting point, not a reference.** It was assembled from
> public sources in August 2026 and has only been verified in depth for **Vaud**.
> Software names, file formats and especially the "round-trips a file?" column
> need confirmation by someone who actually files in that canton. Corrections
> very welcome — that is the most useful contribution you can make right now.

## The uncomfortable truth

There is a widespread belief that most cantons run more or less the same tax
software. **They don't.** Federal law sets the framework, but each canton
publishes its own application, with its own file format, its own rubric
numbering and its own practice. Even cantons whose products share a name
(`eTax.*`) ship distinct implementations.

So there is no shortcut to "support all of Switzerland". Each canton is a
separate piece of work — which is exactly why an open collection makes sense.

Two standards do exist in the neighbourhood, and are worth knowing:

- [**eCH-0119**](https://www.ech.ch/fr/ech/ech-0119/4.0.0) — an XML format for
  exchanging individual tax returns, with cantonal extensions. Cantonal formats
  do not necessarily conform to it, but it describes the same shape of data.
- [**eCH-0196**](https://www.ech.ch/fr/ech/ech-0196/2.2.0) — the electronic tax
  statement (*eRelevé* / *eSteuerauszug*), the barcode PDF your bank issues.
  This one **is** widely implemented, and it is the single highest-leverage
  thing to support: it is how securities and account data get in without
  retyping. There is already an open-source ecosystem around it (see
  `swiss-tax-basics/references/titres-et-fortune.md`).

## The question that actually matters

Not "is it a desktop program or a website?" — that turns out to be irrelevant.
**VaudTax is a web service, and it still hands you a `.vaudtax` file** you can
save, edit and load back in. That round-trip is the whole basis of this project.

So the question for each canton is narrower:

> Can you export the return as a file, and import it back after editing?

If yes, a skill can fill it in, whatever the interface looks like. If the
software only persists your data on the canton's own servers — as Bern's
TaxMe-Online appears to, saving as you move between sections and resuming in
place — then there is no file to edit, and a skill has to help differently.

That distinction is **unverified for almost every canton below**. Please don't
read the blanks as "no".

## By canton

| Canton | Software | Round-trips a file? | Fiducai |
|---|---|---|---|
| **VD** Vaud | VaudTax (web) | **yes** — `.vaudtax`, a ZIP holding one XML plus attachments | ✅ `vaud-tax-return` |
| **VS** Valais | VSTax | to verify | — |
| **GE** Genève | GeTax | to verify | — |
| **FR** Fribourg | FriTax | to verify | — |
| **NE** Neuchâtel | to verify | to verify | — |
| **JU** Jura | to verify | to verify | — |
| **BE** Berne | TaxMe-Online | to verify — persists server-side, export unclear | — |
| **ZH** Zurich | ZHprivateTax | to verify | — |
| **LU** Lucerne | eSteuern.LU | to verify | — |
| **SG** St-Gall | E-Tax SG | to verify | — |
| **TG** Thurgovie | eFisc | to verify | — |
| **AG** Argovie | eTax Aargau | to verify | — |
| **SO** Soleure | eTax Solothurn | to verify | — |
| **SZ** Schwyz | eTax.SZ | to verify | — |
| **ZG** Zoug | eTax.zug | to verify | — |
| others | — | — | contributions welcome |

## If a canton turns out not to round-trip a file

Then a skill cannot fill anything in — but it can still do most of the useful
work:

- build the checklist of documents to gather, and chase what is missing;
- read the documents and produce a **table of values with their sources**, ready
  to type in, rubric by rubric;
- compute the thresholds that decide whether a rubric is worth filling at all
  (medical costs, housing deduction);
- flag the classic errors and the year-on-year inconsistencies.

That is a perfectly good skill. It should just be honest in its `SKILL.md` about
producing a worksheet rather than a file.

Worth checking before concluding a canton is in this category: an export may
exist but be buried, named unhelpfully (*Sicherung*, *sauvegarde*, *Datenexport*),
or offered only at particular points in the flow. And even where the return
itself doesn't round-trip, **eCH-0196 tax statement import usually still works** —
that is the single most tedious part of a return, and it is worth supporting on
its own.

## Priorities

1. **Vaud**, deeper: more checks, more real-world round-trips.
2. **Valais**, because a Vaud resident with a holiday home there has to file in
   both, and the situation is common enough to be worth solving properly.
3. **eCH-0196** support in the shared toolkit, since it benefits every canton at
   once.
4. Anything a contributor actually files themselves — that beats any priority
   list, because they can test it.
