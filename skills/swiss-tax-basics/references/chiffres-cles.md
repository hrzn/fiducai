# Chiffres clés fédéraux, par période fiscale

> **Toujours vérifier l'année.** Ces montants changent, et pas tous en même
> temps. Avant de les utiliser, confirmer qu'ils correspondent bien à la période
> fiscale traitée — un montant repris de l'année précédente est l'erreur la plus
> courante et la plus coûteuse. Les URL et les dates de consultation sont dans
> [`sources.md`](sources.md).

Ce fichier ne contient que ce qui vaut **partout en Suisse**. Les montants
cantonaux — plafonds de déduction, barèmes, impôt sur la fortune — vivent dans
le skill du canton concerné : pour Vaud, `vaud-tax-return`,
`references/chiffres-cles-vd.md`.

## Pilier 3a — plafonds fédéraux

| Période | Affilié à un 2e pilier | Sans 2e pilier |
|---|---|---|
| 2026 | 7 258 | 20 % du revenu net, au max. 36 288 |
| 2025 | 7 258 | 20 % du revenu net, au max. 36 288 |
| 2024 | 7 056 | 20 % du revenu net, au max. 35 280 |

Le montant déductible est le **cumul** des attestations de la personne pour
l'année, plafonné. Chaque conjoint a son propre plafond : deux attestations de
7 258 dans un couple sont normales, une attestation de 14 516 pour une seule
personne ne l'est pas.

Les plafonds sont indexés et restent donc identiques plusieurs années de suite ;
2026 est inchangé par rapport à 2025. Ils sont fixés au niveau fédéral et repris
tels quels par les cantons — c'est le seul chiffre de ce fichier sur lequel un
outil peut s'appuyer sans savoir dans quel canton il travaille, et c'est celui
que contrôle `vaudtax.py check`.

## Ce qui est fédéral et ce qui ne l'est pas

Utile pour savoir où chercher un chiffre, et pour ne pas transposer d'un canton
à l'autre une valeur qui ne s'y applique pas.

| Élément | Niveau |
|---|---|
| Plafonds du pilier 3a | **fédéral**, identique partout |
| Rachats de 2e pilier | déductibles partout ; modalités fédérales |
| Impôt anticipé (35 %) et sa récupération | **fédéral** |
| Valeurs fiscales des titres (ICTax) | **fédéral** |
| Impôt fédéral direct (IFD) : barème et déductions | **fédéral**, mais avec ses propres montants, distincts des montants cantonaux |
| Impôt sur la **fortune** | **cantonal et communal uniquement** — il n'existe pas d'impôt fédéral sur la fortune |
| Plafonds de frais de garde, frais médicaux, logement, frais professionnels | **cantonaux** — et l'IFD a en plus ses propres plafonds |
| Barèmes, coefficients, quotient familial ou splitting | **cantonaux** |
| Valeur locative : principe | fédéral ; **le montant** est fixé par le canton de situation |

Conséquence pratique : une déclaration sert simultanément l'IFD et l'impôt
cantonal, et le revenu imposable n'est pas le même pour les deux. Le logiciel
fiscal calcule les deux assiettes seul — mais c'est ce qui explique qu'un même
montant saisi une fois apparaisse avec deux plafonds différents.

## Où trouver les chiffres cantonaux

Chaque canton publie son propre tableau de déductions et ses propres
instructions, en général au début de l'année qui suit la période fiscale. Le
skill du canton concerné doit les citer avec leur date de consultation.

Ne jamais transposer un montant d'un canton à un autre, même quand la déduction
porte le même nom : les plafonds diffèrent, et les codes de rubrique aussi.
