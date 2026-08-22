# Le format `.vaudtax`

Ce document décrit le format tel qu'il a été observé sur des déclarations
réelles. Il n'est pas une spécification officielle : l'État de Vaud ne publie
pas de schéma pour ce format, et rien ne garantit qu'il ne changera pas d'une
version de VaudTax à l'autre. Traiter ce qui suit comme une observation à
revérifier, pas comme un contrat.

## Structure de l'archive

Un `.vaudtax` est une **archive ZIP** (deflate, sans chiffrement ni signature)
contenant :

| Entrée | Rôle |
|---|---|
| `CTB<id>_PF<année>_<réfGesdem>_<date>.xml` | toutes les données de la déclaration |
| `doc<timestamp>` (une par pièce) | les justificatifs PDF joints |

Le nom du XML encode le numéro de contribuable, la période fiscale, une
référence dite « gesdem » et la date de sauvegarde.

**La référence gesdem change à chaque synchronisation avec le canton.** Elle ne
peut être ni inventée ni recopiée d'une année sur l'autre : elle lie le fichier
au dossier détenu par l'administration. C'est la raison pour laquelle on part
toujours d'un fichier produit par VaudTax lui-même — fonction « reprendre
l'année précédente » — et jamais d'un XML fabriqué de toutes pièces.

Il n'y a **ni somme de contrôle ni signature** dans l'archive : un XML modifié à
la main puis recompressé est accepté. Un cycle `unpack` → `pack` sans
modification reproduit les mêmes entrées avec des CRC identiques ; c'est vérifié
par la suite de tests.

## Racine XML

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<vaudTaxData xmlns="http://www.vd.ch/fiscalite/vaudtax">
```

Espace de noms par défaut, sans préfixe.

**Éditer le XML comme du texte**, jamais en le re-sérialisant avec un parseur :
`ElementTree` réécrirait toutes les balises avec un préfixe `ns0:` et
changerait l'indentation, produisant un diff illisible et un risque de rejet.
C'est pour cette raison que `vaudtax.py` se contente d'extraire et de
reconstruire l'archive, sans jamais réécrire le XML.

## Piège : les noms de balises sont réutilisés

`guidedNav/displayedSubForms` contient des **booléens d'affichage** dont les
balises portent le même nom que les sections de données :
`<etatTitres>true</etatTitres>`, `<immeubles>true</immeubles>`,
`<enfants>true</enfants>`…

Conséquence : `root.iter("etatTitres")` ramasse ce booléen et fausse tout
comptage. Toujours filtrer sur les **enfants directs de la racine** — c'est ce
que fait le helper `sections()` de `vaudtax.py`, et un test dédié protège ce
comportement.

## Ordre des éléments

Les sections apparaissent dans un ordre précis, et les éléments répétés
(`etatTitres`, `enfants`, …) sont contigus. En cas d'ajout, **insérer le nouvel
élément juste après ses semblables**, jamais en fin de fichier.

`trackingIndex` numérote les éléments au sein d'un même type et doit rester
unique par type ; `vaudtax.py check` le vérifie.

`unpack` enregistre l'ordre d'origine des entrées de l'archive dans un fichier
`.fiducai-manifest.json`, que `pack` rejoue. L'ordre semble sans importance pour
VaudTax, mais rien ne le garantit, et le préserver ne coûte rien.

## Provenance des comptes : les eRelevés

VaudTax sait importer des **eRelevés fiscaux bancaires** : des PDF porteurs d'un
code-barres qu'il décode pour remplir seul le compte. Cette opération n'est
possible que **dans l'interface VaudTax** — aucun script ne peut la remplacer.

Un compte ainsi rempli se reconnaît dans le XML à deux champs :

```xml
<nomEreleve>…_2026-01-07_E960_….pdf</nomEreleve>
<identifiantEReleve>CH…………………20251231</identifiantEReleve>
```

`identifiantEReleve` est le contenu du code-barres : numéro de clearing, numéro
de compte, puis **date d'arrêté**. Cette date permet de vérifier que c'est bien
l'eRelevé de l'année N qui a été importé, et non celui de l'an dernier — les
noms de fichiers sont très proches d'une année sur l'autre, et c'est une erreur
classique. `vaudtax.py check` et `vaudtax.py ereleves` la signalent tous deux.

Ces comptes appartiennent à VaudTax : **ne jamais les éditer à la main.** Une
saisie manuelle sera écrasée au prochain import.

Deux effets de bord à connaître :

- l'import **remplace le libellé** du compte par la dénomination officielle de
  la banque ; les libellés personnels disparaissent, c'est normal, ne pas les
  rétablir ;
- la reprise de l'année précédente conserve la **liste** des comptes (sans les
  montants) ; l'import peut donc créer une **seconde ligne** pour un compte déjà
  listé. `check` signale les doublons en discriminant sur (IBAN, numéro de
  compte, devise) — un même IBAN porte légitimement plusieurs devises chez un
  courtier. C'est la ligne **sans** `identifiantEReleve` qu'il faut supprimer.

## Contexte : les normes eCH

Le format `.vaudtax` est propriétaire, mais il existe deux normes suisses dans
son voisinage, utiles à connaître :

- [**eCH-0119**](https://www.ech.ch/fr/ech/ech-0119/4.0.0) — format XML
  d'échange des déclarations de personnes physiques, avec des extensions
  cantonales. `.vaudtax` ne s'y conforme pas, mais la structure des rubriques
  s'en rapproche.
- [**eCH-0196**](https://www.ech.ch/fr/ech/ech-0196/2.2.0) — le relevé fiscal
  électronique, c'est-à-dire précisément ce que VaudTax importe. Voir le skill
  `swiss-tax-basics`, `references/titres-et-fortune.md`, pour l'écosystème open
  source qui gravite autour.

## Le script

Aucune dépendance, bibliothèque standard uniquement, Python 3.9+. Le script
porte un en-tête [PEP 723](https://peps.python.org/pep-0723/), ce qui permet à
`uv` de fournir lui-même un interpréteur sur une machine qui n'en a aucune —
utile sous Windows, où Python est souvent absent.

```bash
# au choix, selon ce qui est disponible :
S="uv run --script skills/vaud-tax-return/scripts/vaudtax.py"
S="python3 skills/vaud-tax-return/scripts/vaudtax.py"

$S unpack   travail.vaudtax /tmp/decl      # extraire (+ manifeste)
$S dump     /tmp/decl                      # arbre lisible
$S dump     travail.vaudtax --section etatTitres biensImmobiliers
$S check    /tmp/decl --year 2025          # contrôles de cohérence
$S check    /tmp/decl --json               # sortie machine
$S ereleves /tmp/decl                      # importés vs saisis à la main
$S diff     annee_precedente.vaudtax /tmp/decl
$S pack     /tmp/decl travail.vaudtax      # reconstruire (.bak auto)
```

`unpack`, `dump`, `check`, `diff` et `ereleves` acceptent indifféremment un
`.vaudtax` ou un dossier déjà déballé.

`check` rend un code de sortie non nul en cas d'anomalie (`--strict` pour que
les simples avertissements comptent aussi).

`pack` refuse d'écrire si le XML n'est plus analysable, et sauvegarde
systématiquement la cible existante en `.bak`.

`diff` apparie les éléments répétés par **clé naturelle** (IBAN pour les
comptes, nom d'employeur pour les salaires, prénom pour les enfants…) et non par
position, ce qui rend la comparaison robuste à l'insertion d'une ligne. Il
ignore `trackingIndex`, les références de documents et les sections d'interface,
et met en évidence une catégorie à part : les **montants inchangés** depuis
l'année précédente.
