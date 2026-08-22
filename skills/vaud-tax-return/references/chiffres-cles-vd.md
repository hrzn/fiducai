# Chiffres clés vaudois, par période fiscale

> **Toujours vérifier l'année.** Ces montants changent, et pas tous en même
> temps. Avant de les utiliser, confirmer qu'ils correspondent bien à la période
> fiscale traitée — un montant repris de l'année précédente est l'erreur la plus
> courante et la plus coûteuse. Les sources et leurs dates de consultation sont
> en fin de document.

Montants en francs, pour l'**impôt cantonal vaudois**. Les codes sont ceux de la
déclaration vaudoise.

Pour ce qui ne dépend pas du canton — plafonds fédéraux du pilier 3a, principes
de déduction, titres et fortune, immobilier — voir le skill `swiss-tax-basics`,
en particulier [`references/chiffres-cles.md`](../../swiss-tax-basics/references/chiffres-cles.md).

## Déductions vaudoises

| Code | Déduction | 2025 | 2024 |
|---|---|---|---|
| 140 | Frais de déplacement, voiture | 0.70/km jusqu'à 15 000 km, puis 0.35/km | idem |
| 150 | Frais de repas | 3 200/an ; 1 600 avec cantine ou participation de l'employeur | idem |
| 150 | Résidence hors du domicile | 6 400/an (midi + soir) ; 4 800 avec cantine ou participation à midi | idem |
| 160 | Autres frais professionnels | 3 % du revenu net, min. 2 000, max. 4 000 | idem |
| 165 | Frais pour activité accessoire | 20 % du revenu net, min. 800, max. 2 400 | idem |
| 235 | Double activité des conjoints | max. 1 700 | idem |
| 300 | Assurance-maladie | 5 000 seul · 9 900 couple · 1 300 par enfant | 4 900 · 9 800 · 1 300 |
| 310 | Prévoyance individuelle liée (3a) | 7 258 / 36 288 | 7 056 / 35 280 |
| 480 | Intérêts de capitaux d'épargne | 1 600 seul · 3 300 couple · 300 par enfant | idem |
| 490 | Frais d'administration des titres | 1.5 ‰ des titres déclarés sous code 410 | idem |
| 495 | Mises dans les loteries | 5 % de chaque gain, max. 5 000 par gain | idem |
| 618 | Frais de perfectionnement et de formation | max. 12 000 par contribuable de 20 ans et plus | idem |
| 620 | Versements aux partis politiques | max. 10 100 | idem |
| 660 | Déduction sociale pour le logement | max. **6 800** | max. 6 700 |
| 670 | Frais de garde | max. **15 200** par enfant de moins de 14 ans | max. 15 000 |
| 680 | Personne à charge | 3 400 si l'aide annuelle atteint ce montant | idem |
| 695 | Contribuable modeste | 17 000 de base + 5 700 conjoint / 3 200 famille monoparentale + 3 500 par enfant | 16 800 + 5 600 / 3 200 + 3 500 |
| 710 | Frais médicaux | part excédant **5 %** du revenu intermédiaire (code 700) | idem |
| 720 | Dons | max. 20 % du revenu intermédiaire (code 700) | idem |
| 725 | Déduction famille | 1 300 couple · 2 800 famille monoparentale · 1 000 par enfant | idem |

« idem » signifie que le montant 2024 est identique à celui de 2025.

Le code 310 reprend le plafond **fédéral** du pilier 3a : il est identique dans
tous les cantons. C'est celui que `vaudtax.py check` contrôle.

## Frais d'entretien d'immeuble (code 540)

Forfait ou frais effectifs, au choix, et le choix peut changer d'une année à
l'autre :

| Situation | Forfait |
|---|---|
| Immeuble de plus de 20 ans, occupé par le propriétaire | 30 % de la valeur locative |
| Immeuble de moins de 20 ans, occupé par le propriétaire | 20 % de la valeur locative |
| Immeuble de plus de 20 ans, mis en location | 20 % du revenu net de l'immeuble |
| Immeuble de moins de 20 ans, mis en location | 10 % du revenu net de l'immeuble |

Immeuble avec un état locatif supérieur à 150 000 : frais effectifs, ou forfait
calculé sur un état locatif de 150 000. Identique en 2024 et 2025.

## Déduction sociale pour le logement (code 660) — le calcul

Ce n'est pas un simple plafond, c'est une différence. La déduction vaut :

> loyer net annuel sans les charges (ou valeur locative du logement principal)
> **moins** 20 % du revenu net déclaré sous code 650

Le loyer pris en compte est lui-même plafonné, pour 2025 :

- 11 100 pour une personne célibataire, veuve, séparée ou divorcée ;
- 13 700 pour un couple marié ou en partenariat enregistré, ainsi que pour un
  parent seul tenant un ménage indépendant avec un enfant à charge ;
- **+ 3 700 par enfant** dont l'entretien complet est assuré.

Et la déduction finale ne peut pas dépasser **6 800** (2025).

Conséquence pratique : si le loyer est nettement inférieur à 20 % du revenu net,
la déduction est nulle et il est inutile de renseigner la rubrique. Si l'on est
proche du seuil, il faut le montant exact du loyer annuel sans les charges.

Exemple officiel, couple avec deux enfants (maximum déterminant 21 100) :

| Revenu net (code 650) | 60 000 | 80 000 | 70 000 |
|---|---|---|---|
| Loyer annuel | 22 000 | 18 000 | 12 000 |
| 20 % du code 650 | −12 000 | −16 000 | −14 000 |
| Différence | 9 100 | 2 000 | 0 |
| **Déduction accordée** | **6 800** (plafond) | **2 000** | **0** |

## Frais médicaux (code 710) — la franchise de 5 %

Seule la part qui **excède 5 % du revenu intermédiaire** (code 700) est
déductible, et il s'agit des frais réellement restés à charge après
remboursement de l'assurance.

Sont admis : frais de médecin, de dentiste, d'oculiste, frais pharmaceutiques
sur prescription, et le coût des mesures usuelles et nécessaires (prothèse
dentaire, lunettes, etc.).

Corollaire opérationnel : si le total des frais à charge est nettement inférieur
à 5 % du revenu, la déduction est nulle. Le calcul se fait avant de saisir quoi
que ce soit, et avant de rassembler les justificatifs.

**Les frais liés à un handicap sont un régime distinct** : entièrement
déductibles, **sans franchise**, pour une personne handicapée au sens de la loi
sur l'égalité pour les handicapés. Ne pas les confondre avec les frais médicaux
ordinaires.

## Frais de garde (code 670)

Max. 15 200 par enfant de moins de 14 ans révolus vivant dans le même ménage
(2025 ; 15 000 en 2024). Seul le **coût de la garde** est déductible — crèche,
maman de jour, accueil parascolaire — à l'exclusion des frais d'entretien
(nourriture, tâches ménagères) souvent facturés sur la même attestation.

## Fortune

L'impôt sur la fortune est **purement cantonal et communal** : il n'existe pas au
niveau fédéral.

- Barème cantonal : la fortune nette n'est pas imposée en dessous de **60 000**
  (120 000 pour un couple ou un partenariat enregistré vivant en ménage commun),
  2025.
- **Objets mobiliers (code 440)** : en règle générale 30 % de la valeur
  d'assurance incendie, avec une déduction de 60 000.
- **Autos, motos, bateaux, collections, œuvres d'art (code 430)** : la valeur
  imposable est la **valeur vénale**, c'est-à-dire la valeur de marché. Certains
  praticiens l'approchent par un amortissement forfaitaire du prix d'achat ;
  c'est une estimation, pas la règle. Pour un objet de collection dont la valeur
  monte, l'amortissement donne un résultat faux.
- **Assurances-vie (code 435)** : valeur de rachat au 31.12, attestée par
  l'assureur. Les assurances risque pur n'en ont pas. Les avoirs de 2e pilier et
  de 3e pilier A **ne sont pas** soumis à l'impôt sur la fortune et ne se
  déclarent pas ici.

## Coefficients

L'impôt calculé au barème est l'**impôt cantonal de base (100 %)**. Le montant
réellement dû s'obtient en le multipliant par le coefficient cantonal annuel
(**155.0 % en 2025**) et par le coefficient communal, qui varie d'une commune à
l'autre.

## Quotient familial (code 810)

Vaud détermine le taux par **quotient familial** — d'autres cantons utilisent le
splitting ou un barème distinct pour les couples. Le revenu déterminant pour le
**taux** est le revenu imposable divisé par le total des parts au 31 décembre :

| Situation | Parts |
|---|---|
| Célibataire, veuf, divorcé, imposé séparément | 1,0 |
| Époux / partenaires enregistrés en ménage commun | 1,8 |
| Parent seul tenant un ménage indépendant avec un enfant à charge | 1,3 |
| Par enfant mineur, en apprentissage ou aux études | 0,5 |

Le concubinage ne donne pas droit à la part de 1,3. La réduction est plafonnée
(« blocage du quotient familial »).

## Sources

Les chiffres ci-dessus proviennent des documents suivants, et d'aucune autre
source. En les mettant à jour, mettre aussi à jour la date de consultation : elle
indique au lecteur suivant à quel point le chiffre peut avoir vieilli.

| Source | Éditeur | Consulté le | Utilisé pour |
|---|---|---|---|
| [Tableau des principales déductions vaudoises 2025](https://www.vd.ch/fileadmin/user_upload/organisation/dfin/aci/fichiers_pdf/Tableau_des_d%C3%A9ductions_2025.pdf) | ACI, État de Vaud | 2026-08-03 | tous les montants 2025 |
| [Tableau des principales déductions vaudoises 2024](https://www.vd.ch/fileadmin/user_upload/organisation/dfin/aci/fichiers_pdf/Tableau_des_d%C3%A9ductions_2024.pdf) | ACI, État de Vaud | 2026-08-03 | tous les montants 2024 |
| [Instructions générales 2025 (21001_2025.pdf)](https://www.vd.ch/fileadmin/user_upload/organisation/dfin/aci/fichiers_pdf/21001_2025.pdf) | ACI, État de Vaud | 2026-08-03 | règles des codes 430, 435, 440, 660, 710 ; liste des pièces obligatoires |
| [Les déductions](https://www.vd.ch/etat-droit-finances/impots/impots-pour-les-individus/les-deductions) | État de Vaud | 2026-08-03 | page d'entrée, liens vers les tableaux annuels |
| [Formulaires, directives, lois et barèmes](https://www.vd.ch/etat-droit-finances/impots/formulaires-directives-et-baremes) | État de Vaud | 2026-08-03 | où trouver les éditions suivantes |

L'État de Vaud publie chaque année un nouveau « Tableau des principales
déductions » et de nouvelles « Instructions générales », en général au début de
l'année qui suit la période fiscale.

Ces documents donnent des montants et des règles générales, pas des réponses à
des situations particulières. Une pratique cantonale, une circulaire de la
Conférence suisse des impôts ou une décision de taxation peuvent préciser ou
contredire une lecture naïve du tableau. En cas de doute, la question va dans
les questions ouvertes de la déclaration, pas dans une valeur inventée.
