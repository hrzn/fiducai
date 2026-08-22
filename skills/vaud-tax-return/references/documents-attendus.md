# Documents attendus → champs XML

Ce tableau sert deux usages : établir la **checklist des pièces manquantes** au
début du travail, et savoir où va chaque document une fois rassemblé.

Il est organisé par **type de document**, pas par nom de fichier : les dossiers
sont nommés différemment par chacun, et c'est le contenu qui compte. Quand
l'appartenance d'un document est ambiguë, le demander plutôt que le supposer.

## Pièces obligatoires selon l'ACI

L'administration cantonale exige que ces pièces soient jointes à la déclaration
(état 2025) :

- certificat de salaire de **tous** les employeurs ;
- pour un indépendant : bilan et compte de résultat signés, ou état des actifs
  et passifs avec relevé des recettes et dépenses, plus le questionnaire pour
  indépendant ;
- eRelevé fiscal bancaire ;
- relevés bancaires des valeurs fiscales des titres ;
- justificatifs originaux des gains de loterie ayant subi l'impôt anticipé ;
- attestations officielles des versements au 3e pilier A ;
- attestations de rachat au 2e pilier **dès CHF 10 000** ;
- justificatifs des frais de garde des enfants par des tiers.

Facultatives, mais à tenir à disposition : rachats 2e pilier inférieurs à
CHF 10 000, justificatifs d'entretien d'immeuble, frais médicaux et dentaires,
décomptes de frais bancaires et postaux.

## Revenus

| Document | Champs |
|---|---|
| Certificat de salaire, un par employeur et par personne | `activiteSalarieeRevenus` : `salaireNet` (ch. 11), `cotisationOrdinaire` (ch. 10), `tauxActivite`, booléens des ch. 13/15 |
| Certificat pour une activité accessoire | `autresRevenusTouteNatureList` ou un second `activiteSalarieeRevenus` selon la nature |
| Attestation de rentes, indemnités, allocations | rubriques de revenus correspondantes |

## Comptes bancaires — un `etatTitres` par compte

| Document | Champs |
|---|---|
| **eRelevé fiscal** (PDF à code-barres) | à importer **dans VaudTax** : remplit seul `soldeCompteCHF`, `rendementNonSoumisIA`, `iban`, `nomEreleve`, `identifiantEReleve` |
| Relevé ou attestation de fin d'année sans code-barres | saisie manuelle : solde au 31.12, intérêts, IBAN, devise |
| Relevé fiscal d'un courtier | `relevesFiscauxBancaires` (code 410) **et** les comptes espèces associés |

Règles constantes : **déclarer tous les comptes**, y compris à solde nul ;
comptes joints en `CTB1_CTB2` ; comptes d'une seule personne en `CTB1` ou
`CTB2`.

À vérifier au tout début du travail, établissement par établissement :

1. cet établissement fournit-il un eRelevé fiscal ?
2. si oui, est-il gratuit et téléchargeable, ou **payant et à commander à
   l'avance** ? Le délai peut être de plusieurs semaines, et le coût est
   déductible sous `fraisAdministrationTitres`.
3. si non, quel document tient lieu de relevé fiscal ?

`python3 $S ereleves <fichier>` liste ce qui est déjà importé et ce qui reste à
faire.

## Titres et participations

| Document | Champs |
|---|---|
| Relevé fiscal bancaire | `relevesFiscauxBancaires` : rendements et valeurs fiscales, ventilés IA / IES / USA |
| Relevé de plan d'actionnariat salarié (*account summary*) | `actionPartSociale` : nombre de parts au 01.01 et au 31.12, cours, valeur fiscale |
| Annexe au certificat de salaire pour les participations | valeur au 31.12, durée de blocage, abattements éventuels |
| Extrait de dépôt sans données fiscales | insuffisant : les valeurs fiscales se prennent sur [ICTax](https://www.ictax.admin.ch/) |

## Prévoyance et assurances

| Document | Champs |
|---|---|
| Attestations 3a, **une par contrat et par personne** | `formesReconnuesPrevoyanceIndividuelleContribuable1` / `…2` — la **somme** par personne |
| Attestation de rachat 2e pilier | `rachat2emePilierContribuable1` / `…2` |
| Attestations fiscales d'assurance maladie, base et complémentaires, pour chaque membre du ménage | `montantPrimesBrutes` (somme du ménage) |
| Décision de subside | `montantSubsides` |

## Enfants

| Document | Champs |
|---|---|
| Attestation de frais de garde (crèche, maman de jour) | `enfants[…]/enfFraisGarde` |
| Attestation d'accueil parascolaire | idem, **à cumuler** par enfant |

Ventiler par enfant selon les attestations ; en cas de montant global, demander
la répartition. Ne retenir que la part « garde » à l'exclusion des repas et de
l'entretien.

## Immeuble

| Document | Champs |
|---|---|
| Communication de la valeur locative | `autresRendementsImmobiliers` ou `nombreJoursOccupation` — cf. `cas-particuliers.md` |
| Attestation hypothécaire au 31.12 | `interetsDettes` (`interets`, `detteMontant`) **et** `biensImmobiliers` (`interetsPassifsImmeuble`, `detteImmeuble`) |
| Extrait de cadastre / estimation fiscale | `estimationFiscale`, `numParcelle`, `anneeConstruction` |
| Prime d'assurance du bâtiment | `taxesPrimesImpots/primesAssuranceDM`, `primesAssuranceRC` |
| Facture communale (eau, épuration, ordures) | `taxesOrdures` — **ventiler, tout n'est pas déductible** |
| Factures d'entretien | une ligne `fraisEntretienImmeuble` par facture, avec `plusValue` |

## Frais médicaux

| Document | Champs |
|---|---|
| Factures de médecin, dentiste, pharmacie, hôpital | une ligne `fraisMedicaux` par facture |
| Décomptes de l'assurance | déterminent `montantACharge`, le reste à charge réel |

Calculer d'abord le seuil de 5 % du revenu : en dessous, ne rien saisir.

## Formation et frais professionnels

| Document | Champs |
|---|---|
| Factures de cours, écolages, frais d'examens | `fraisPerfectionnementFormations` |
| Cotisations à une association professionnelle ou un syndicat | **pas** ici : relèvent des autres frais professionnels, donc du forfait |

## Acomptes

| Document | Champs |
|---|---|
| Décompte ou récapitulatif des acomptes versés dans l'année | `acomptes/acomptesPayes` |

## Documents administratifs — sans effet sur le XML

Quittances de demande de délai, brouillons de déclaration, décisions de taxation
d'années antérieures, factures finales, archives compressées. Ne pas les traiter
comme des sources de données ; ils peuvent en revanche renseigner utilement sur
des points restés en suspens.

## Documents à obtenir de tiers

Quand une partie des pièces dépend de quelqu'un d'autre — conjoint, employeur,
banque —, produire la demande **au début** du travail, sous forme de liste
qu'on peut transmettre telle quelle. Typiquement, pour un conjoint :

- certificat(s) de salaire ;
- attestation fiscale d'assurance maladie, base et complémentaires ;
- attestation(s) de versement au 3e pilier A ;
- relevés ou eRelevés des comptes dont il ou elle s'occupe ;
- frais médicaux éventuels ;
- frais professionnels ou de perfectionnement éventuels.

Le profil personnel (`profil-fiscal.md`) est l'endroit où noter qui s'occupe de
quoi, pour ne pas refaire cette répartition chaque année.
