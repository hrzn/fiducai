# Cas particuliers

Situations qui reviennent souvent et que le remplissage naïf traite mal. Pour
les montants et les seuils vaudois, ainsi que leurs sources, voir
[`chiffres-cles-vd.md`](chiffres-cles-vd.md).

> Ce document décrit des pratiques observées et des règles publiées. Il ne
> remplace pas une décision de l'autorité. Quand un point reste ouvert, il va
> dans les questions ouvertes de la déclaration et dans le profil personnel — il
> ne se tranche pas silencieusement.

## Immeuble situé dans un autre canton

Le cas typique : domicile dans le canton de Vaud, résidence secondaire ailleurs.

**Côté vaudois**, l'immeuble se déclare normalement dans la déclaration VD, avec
sa commune de situation et son `sigleCanton`. Vaud procède ensuite à une
**répartition intercantonale** : la fortune immobilière et son rendement
reviennent au canton de situation, mais Vaud les retient pour déterminer le
**taux** applicable au reste du revenu et de la fortune. Rien de particulier à
saisir — VaudTax s'en charge à partir de `communeFiscale`. **Ne pas** omettre
l'immeuble sous prétexte qu'il est taxé ailleurs.

**Côté du canton de situation**, une déclaration distincte est en principe à
déposer, avec ses propres formulaires et délais. Elle est **hors périmètre de ce
skill** — ce n'est pas un fichier `.vaudtax` — mais elle doit être rappelée dans
les livrables de fin de travail, car elle est facile à oublier une fois la
déclaration vaudoise bouclée.

Un immeuble acquis en cours d'année n'appelle évidemment pas de déclaration dans
le canton de situation pour les années antérieures à l'acquisition.

## Valeur locative : deux méthodes de saisie

VaudTax accepte deux manières de renseigner la valeur locative d'un bien occupé
par son propriétaire :

1. `isImmeubleOccupeSuisse=true` avec `nombreJoursOccupation` — VaudTax calcule
   lui-même la valeur locative, au prorata des jours d'occupation ;
2. `isAutresRendementsImmobiliers=true` avec `autresRendementsImmobiliers`
   portant le montant annuel communiqué par la commune, et
   `isImmeubleOccupeSuisse=false`.

Les deux se rencontrent. La seconde est plus explicite quand la commune a
communiqué une valeur locative brute annuelle précise ; porter alors la mention
correspondante dans le champ libre `nature`.

**Ne pas changer de méthode d'une année à l'autre sans raison** : un écart
inexpliqué entre deux exercices attire l'attention. La méthode retenue et sa
justification vont dans le profil personnel.

## Frais et taxes communales

Sur une facture communale, tout n'est pas déductible. Se déduisent en général
les taxes liées à l'exploitation du bien — taxe de base eau, location de
compteur, épuration, ordures. Ne se déduisent pas l'impôt foncier ni la taxe de
séjour.

Ventiler la facture ligne par ligne et documenter le total retenu ; ne jamais
reporter le montant global.

## Entretien contre plus-value

Les travaux vont en `fraisEntretienImmeuble`, une ligne par facture, avec le
booléen `plusValue`.

- **Entretien** (déductible) : remplacement à l'identique, réparation,
  ramonage, peinture, révision de chauffage, maçonnerie de réfection.
- **Plus-value** (non déductible du revenu) : extension, équipement nouveau,
  montée en gamme notable.

Un poêle remplacé à l'identique est de l'entretien ; le même remplacement par un
modèle nettement supérieur comporte une part de plus-value. Conserver les
factures de plus-value : elles réduiront l'impôt sur les gains immobiliers à la
revente.

Ne pas oublier l'alternative du **forfait** sur la valeur locative, souvent plus
avantageuse les années sans gros travaux — et qui dispense de justificatifs.

## Hypothèque

Intérêts payés et solde de la dette au 31.12 figurent sur l'attestation du
créancier. Ils vont **aux deux endroits** : `interetsDettes` et
`biensImmobiliers` (`interetsPassifsImmeuble`, `detteImmeuble`). Oubli fréquent,
que `vaudtax.py check` détecte.

Ne jamais reconstituer le solde par une formule d'amortissement contractuelle
sans le vérifier contre l'attestation : amortissements extraordinaires et
renouvellements de tranche faussent le calcul.

## Participations d'employé et actions non cotées

Se déclarent en `actionPartSociale`, avec le pays de la société.

Points de vigilance :

- **Réclamer à l'employeur l'annexe au certificat de salaire** donnant la valeur
  des titres au 31.12 et la durée de blocage. C'est elle qui justifie la valeur
  retenue, et elle arrive rarement spontanément — la demander **avant** de
  remplir la rubrique.
- Les titres **bloqués** ouvrent droit à un abattement lié à la durée du blocage,
  et un actionnaire **minoritaire** peut bénéficier d'un abattement
  supplémentaire (circulaire 28 de la Conférence suisse des impôts). Ces
  abattements ne s'appliquent pas d'office : il faut les demander et les
  justifier.
- Les **options non exercées** se portent en général sur une ligne « pour
  mémoire », avec un cours et une valeur fiscale nuls.
- Sans numéro de valeur ni ISIN, la pratique observée est d'indiquer `0`.
- Conversion en francs : utiliser le cours au 31.12 publié par
  [ICTax](https://www.ictax.admin.ch/), pas un cours trouvé ailleurs.

## Fonds de placement

Le plus simple et le plus fiable est de **commander le relevé fiscal** auprès de
la banque ou du courtier. Il se saisit alors en `relevesFiscauxBancaires`
(code 410) : un libellé et quelques montants. Le coût du relevé est déductible
sous `fraisAdministrationTitres`.

À défaut, les données fiscales d'un fonds — rendement imposable, part soumise à
l'impôt anticipé — se trouvent sur ICTax par numéro de valeur. Un simple extrait
de dépôt ne suffit pas : la variation de valeur du fonds n'est pas le rendement
imposable.

## Frais médicaux : calculer avant de saisir

Seule la part excédant **5 % du revenu intermédiaire** est déductible, et il
s'agit du reste à charge après remboursement.

Conséquence opérationnelle : faire le calcul **d'abord**. Si le total à charge
est nettement en dessous du seuil, ne pas remplir la rubrique du tout — cela
évite de rassembler des justificatifs pour rien, et allège le dossier. Le
signaler dans le rapport, pour qu'on ne prenne pas cette absence pour un oubli.

Les frais liés à un **handicap** relèvent d'un régime distinct : entièrement
déductibles, sans franchise. Ne pas les confondre.

## Déduction sociale pour le logement : idem

La déduction vaut la différence entre le loyer annuel net sans charges (ou la
valeur locative) et 20 % du revenu net, elle-même plafonnée. Le calcul complet
est dans [`chiffres-cles-vd.md`](chiffres-cles-vd.md).

Si le loyer est nettement inférieur à 20 % du revenu net, la déduction est nulle
et la rubrique reste vide. Si l'on est proche du seuil, demander le montant
exact du loyer annuel sans les charges — une estimation ne suffit pas.

## Frais de garde et répartition entre parents

La déduction est plafonnée **par enfant** : ventiler un montant global.

Quand deux parents assument les frais, l'autorité peut attendre une répartition
par moitié. Un **accord écrit** entre les parents permet d'attribuer une autre
clé, y compris 100 % à l'un d'eux. Sans accord, ne pas présumer : poser la
question et noter la réponse dans le profil personnel.

## Cotisations professionnelles

Les cotisations à une association professionnelle ou à un syndicat ne vont
**pas** en `fraisPerfectionnementFormations`, réservée aux frais directement
liés à un cursus ou à une mise à niveau : cours, écolages, matériel d'étude,
frais d'examens.

Elles relèvent des **autres frais professionnels**, couverts par le forfait de
3 % du revenu net (bornes dans [`chiffres-cles-vd.md`](chiffres-cles-vd.md)).
Elles ne se déduisent donc
en plus que si l'ensemble des frais effectifs dépasse ce forfait — ce qui est
rare.

## Reprise de l'année précédente : ce qui est conservé

| Conservé | Non conservé |
|---|---|
| identité des contribuables et des enfants | **tous les montants** |
| structure : rubriques et catégories activées | les justificatifs PDF |
| listes d'éléments : comptes, employeurs, immeuble | les dates propres à l'exercice |

Le fichier de départ est donc un **squelette** : la structure est en place, les
valeurs sont à saisir. Un `check` initial qui signale des montants manquants est
normal, c'est le point de départ attendu.

Corollaire important pour la relecture : une valeur qui apparaîtrait
**inchangée** par rapport à l'an dernier ne peut pas venir d'un report
automatique. Soit elle est légitimement stable, soit elle a été saisie par
erreur depuis un document de l'année précédente. `vaudtax.py diff` les liste
dans une section dédiée.
