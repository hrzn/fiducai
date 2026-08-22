# Référence des champs XML

Relevé sur des déclarations réelles, sans garantie d'exhaustivité : une rubrique
jamais utilisée n'apparaît pas ici. Les montants sont des **entiers CHF** sauf
mention contraire ; rendements, cours et taux portent des décimales.

Les correspondances avec les codes officiels de la déclaration (140, 310, 660…)
sont indiquées quand elles sont établies — voir
[`chiffres-cles-vd.md`](chiffres-cles-vd.md) pour les plafonds associés.

## Identité — stable d'une année sur l'autre

```
identification            communeFiscale (nomOfficiel, numeroOfs, sigleCanton), etatCivil
taxpayerPersonalData1     contribuable 1
taxpayerPersonalData2     contribuable 2 (couple)
  lastName, firstName, avs, birthDate, civility, profession
representative            mandataire éventuel
```

Repris tel quel par VaudTax. **Ne rien y toucher**, sauf changement d'adresse,
d'état civil ou de profession. `isContribuable1` ailleurs dans le fichier
renvoie à `taxpayerPersonalData1`.

## Revenus salariés

```
activiteSalarieeRevenus          (un par employeur et par contribuable)
  employeur, type=PRINCIPAL, tauxActivite
  dateDebut, dateFin             (bornes de la période fiscale)
  salaireNet                     ← certificat de salaire, chiffre 11
  cotisationOrdinaire            ← certificat de salaire, chiffre 10 (LPP)
  transportGratuit, contributionFraisRepas, fraisForfaitaire,
  contributionPerfectionnement, droitParticipation    (booléens, chiffres 13/15)
  isContribuable1
workingPeriodInterruptions       dateDebut, dateFin, reason
```

Les cases 13 et 15 du certificat de salaire pilotent les booléens : elles
déterminent notamment si les frais de repas sont réduits de moitié.

## Frais professionnels

```
fraisRepas        noLigne, fraisRepasType, nbJours, dateDebut, isContribuable1
fraisTransport    noLigne, moyenTransport, domicile, lieuTravail,
                  nbJours, nbKilometres, isForfait
autresFraisEtFraisActiviteSalarialeAccessoire
                  contribuable1 / contribuable2 :
                    autresFraisDeductionType=FORFAIT, autresFraisFraisForfaitaires
fraisPerfectionnementFormations
                  datePaiement, description, montant, isContribuable1
```

`fraisRepasType` : `HORS_DOMICILE_NORMAL` | `HORS_DOMICILE_CONTRIBUTION`
(le second quand l'employeur participe — chiffre 13.1.1 du certificat).
`moyenTransport` observé : `TRANSPORT_PUBLIC`.

`nbJours` correspond au nombre de jours de travail effectifs de l'année,
proportionnel au taux d'activité. Il n'y a pas de valeur « par défaut » : elle
se déduit du taux d'activité et de la durée d'emploi.

## Autres revenus

```
autresRevenusTouteNatureList     genre, montant, isContribuable1
```

`genre` observés : `ROYALTIES`, `AUTRES_PRESTATIONS_AVANTAGES_ARGENT`.

## Assurances et prévoyance

```
primesEtCotisationsAssurance
  montantPrimesBrutes                                  ← attestations LAMal du ménage
  montantSubsides
  formesReconnuesPrevoyanceIndividuelleContribuable1    ← 3a, cumul des attestations
  formesReconnuesPrevoyanceIndividuelleContribuable2
  rachat2emePilierContribuable1 / …2
  hasVerseCotisationsPrevoyanceProfessionnelleContribuable1 / …2
```

Le 3a est le **cumul** des attestations d'une même personne, plafonné par
personne. `vaudtax.py check` compare au plafond de l'année.

## État des titres — comptes bancaires

```
etatTitres                       (un par compte)
  contribuable                   CTB1 | CTB2 | CTB1_CTB2
  etablissement, iban, numCompte
  devise                         id (1=CHF, 3=USD, 4=EUR…), label, coefficient
  soldeCompteDevise              (si devise étrangère)
  coursMonetaire                 (cours au 31.12 — source ICTax)
  soldeCompteCHF                 ← solde au 31.12
  rendementNonSoumisIA           (décimal)
  rendementType                  NON | OUI_NON_SOUMIS_IA | OUI_SOUMIS_IA
  nomEreleve, identifiantEReleve (si eRelevé importé)
```

**La présence d'`identifiantEReleve` marque un compte rempli par l'import
eRelevé : ne jamais l'éditer à la main.** Seuls les comptes qui en sont dépourvus
relèvent de la saisie. Cf. `format-vaudtax.md` et `vaudtax.py ereleves`.

Un même IBAN peut porter plusieurs devises, chacune sur sa propre ligne : ce
n'est pas un doublon.

```
fraisAdministrationTitres/fraisEffectif    ← code 490, frais bancaires déductibles
```

## État des titres — titres et relevés

```
actionPartSociale
  designation, numeroValeur, country/iso2Id, typeImpotSoumis
  valeurNominaleInitiale                     (nb de parts au 01.01)
  infosImpotNational/valeurNominaleFinale    (nb de parts au 31.12)
  infosImpotNational/coursFiscalFinal        (cours unitaire CHF — ICTax)
  infosImpotNational/valeurFiscaleFinale     (= nb × cours, arrondi)

relevesFiscauxBancaires          (code 410 — relevé fiscal d'une banque)
  designation, numeroCompte
  revenusBrutsNonSoumisIA, valeurFiscaleFinaleNonSoumisIA
  revenusBrutsSoumisIES, valeurFiscaleFinaleSoumisIES, montantIES
  retenueSupUSA, revenusBrutsSoumisUSA, valeurFiscaleFinaleSoumisUSA, montantUSA
  nomEreleve, identifiantEReleve, documentReference
```

`numeroValeur` attend le numéro de valeur suisse ou l'ISIN. Quand le titre n'en
a pas — participation non cotée —, la pratique observée est d'indiquer `0`.

Les options non exercées se déclarent en général sur une ligne « pour mémoire »,
avec `coursFiscalFinal=0.00` et `valeurFiscaleFinale=0`.

## Immeuble

```
biensImmobiliers
  contribuable, partProprieteCtb1, partProprieteCtb2      (parts en %)
  communeFiscale (nomOfficiel, numeroOfs, sigleCanton), address, numParcelle
  batimentExiste, anneeConstruction, estimationFiscale
  typeImmeublePrivate, typeLogementPrincipal
  interetsPassifsImmeuble        ← intérêts hypothécaires de l'année
  detteImmeuble                  ← solde de la dette au 31.12
  isImmeubleOccupeSuisse, nombreJoursOccupation, surfaceHabitable
  isAutresRendementsImmobiliers, autresRendementsImmobiliers   ← valeur locative
  nature                         (texte libre — remarques à l'attention du fisc)
  taxesPrimesImpots/ primesAssuranceDM, primesAssuranceRC, taxesOrdures
  fraisEntretienImmeuble         (répété) dateFacture, maitreEtat, montant, plusValue
```

`sigleCanton` porte le canton de **situation** de l'immeuble, qui peut différer
de celui du domicile : c'est lui qui déclenche la répartition intercantonale.

Deux manières de renseigner la valeur locative coexistent — soit
`isImmeubleOccupeSuisse=true` avec `nombreJoursOccupation`, VaudTax calculant
lui-même, soit `isAutresRendementsImmobiliers=true` avec le montant annuel. Voir
`cas-particuliers.md`.

Le champ `plusValue` distingue l'entretien déductible de la plus-value qui ne
l'est pas.

## Dettes

```
interetsDettes                   (un par créancier)
  contribuable, isGageImmobGarantie, creancier, iban, numCompte
  interets, detteMontant
```

Les intérêts hypothécaires doivent figurer **aux deux endroits** :
`interetsDettes` **et** `biensImmobiliers/interetsPassifsImmeuble`.
`vaudtax.py check` signale l'oubli, qui est fréquent.

## Enfants et déductions sociales

```
enfants
  lastName, firstName, avs, birthDate, activite
  menageCommunAvecEnfant, menageCommunAvecAutreParent
  enfACharge, enfFraisGarde      ← frais de garde payés dans l'année (code 670)
deductionSocialeLogement/loyerAnnuelNetPayeSansCharge   ← code 660
```

`loyerAnnuelNetPayeSansCharge` : loyer annuel **sans les charges**. Ne le
renseigner que si la déduction a une chance d'être non nulle — voir le calcul
dans [`chiffres-cles-vd.md`](chiffres-cles-vd.md).

## Frais médicaux

```
fraisMedicaux                    (une ligne par facture)
  etabliPar, datePaiement, type, montantBrut, montantACharge
```

`type` : `MEDECIN` | `DENTISTE` | `PHARMACIE` | `HOPITAL`.
`montantACharge` = reste à charge réel après remboursement de l'assurance.
Seule la part dépassant 5 % du revenu est déductible : vérifier le seuil avant
de saisir quoi que ce soit.

## Divers

```
autoMoto/value                   ← valeur vénale des véhicules (code 430)
objetsMobiliers, numeraires, fraisResidence, complementRentePension,
successionHoirieDonation, prestationsEnCapital, activitesIndependantes
                                 ← isInitialized=false quand sans objet
acomptes/acomptesPayes           ← décimal, acomptes versés durant l'année
infosComplementairesIes          ← coordonnées bancaires pour remboursement
```

`autoMoto/value` est un **montant unique pour l'ensemble des véhicules** :
additionner s'il y en a plusieurs, et le préciser dans la traçabilité.

Laisser `isInitialized=false` sur les sections sans objet plutôt que de les
supprimer.

## Sections d'interface — ne pas éditer

`userProfil` (menus ouverts/fermés) et `guidedNav/displayedSubForms` (rubriques
affichées) n'ont aucun effet fiscal. VaudTax les met à jour seul.

Une exception utile : si une rubrique n'apparaît pas dans l'interface alors
qu'on vient d'y écrire des données, c'est que son booléen dans
`displayedSubForms` est à `false`.

## Justificatifs

```
piecesJustificativesObligatoires / piecesJustificativesFacultatives
  id, titleLabelKey, isRequired
  piecesJustificatives/ id, labelKey, canBeDeleted
    documents/ reference (UUID), filename, label, key (= entrée ZIP),
               mimeType, fileSize
```

**Hors périmètre de ce skill** : les pièces sont jointes à la main dans VaudTax.
Ne pas modifier ces sections. `check` vérifie seulement que chaque `key`
référencée existe bien dans l'archive.
