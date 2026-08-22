# Immobilier

## Valeur locative

Un bien immobilier que l'on occupe soi-même produit un revenu fiscal fictif, la
**valeur locative** : le loyer que l'on percevrait en le louant. Elle s'ajoute
au revenu imposable. En contrepartie, les intérêts hypothécaires et les frais
d'entretien sont déductibles.

La valeur locative est fixée par le canton où se trouve l'immeuble, pas par
celui du domicile. Elle est en général communiquée par écrit au propriétaire.
Quand le bien n'est occupé qu'une partie de l'année, ou acquis en cours d'année,
il faut savoir si le canton attend un prorata ou la valeur annuelle complète —
c'est une question à poser plutôt qu'à deviner, et la réponse doit être notée
pour les années suivantes afin de ne pas changer de méthode sans raison.

> La valeur locative fait l'objet de réformes politiques récurrentes au niveau
> fédéral. Vérifier ce qui s'applique à la période fiscale traitée.

## Immeuble situé dans un autre canton

Cas fréquent : domicile dans un canton, résidence secondaire dans un autre.

**Dans le canton de domicile**, l'immeuble se déclare normalement, avec sa
commune de situation. Ne pas l'omettre sous prétexte qu'il est imposé ailleurs.
Le canton procède ensuite à une **répartition intercantonale** : la fortune
immobilière et son rendement reviennent au canton de situation, mais le canton
de domicile les retient pour déterminer le **taux** applicable au reste du
revenu et de la fortune. Le logiciel s'en charge à partir de la commune indiquée.

**Dans le canton de situation**, une déclaration distincte est en principe à
déposer. C'est une démarche séparée, avec ses propres formulaires et délais,
très facile à oublier une fois la déclaration principale bouclée. Elle doit être
rappelée explicitement dans les livrables de fin de travail.

Le même raisonnement vaut pour un immeuble à l'étranger, avec une répartition
internationale à la place.

## Entretien ou plus-value

Distinction centrale, et source d'erreur constante :

- **Entretien** : ce qui maintient le bien en état — remplacement à
  l'identique, réparation, ramonage, peinture, révision de chauffage.
  **Déductible.**
- **Plus-value** : ce qui améliore le bien ou en augmente la valeur — extension,
  équipement nouveau, montée en gamme. **Non déductible** du revenu, mais à
  conserver précieusement : ces frais réduiront l'impôt sur les gains
  immobiliers lors d'une vente future.

Un poêle remplacé par un poêle équivalent est de l'entretien ; le même
remplacement par un modèle nettement supérieur comporte une part de plus-value.
Certaines factures sont mixtes et se ventilent.

Les investissements d'**économie d'énergie** bénéficient souvent d'un traitement
favorable et peuvent être déductibles même lorsqu'ils augmentent la valeur du
bien : vérifier la pratique du canton concerné.

## Forfait ou frais effectifs

La plupart des cantons laissent le choix, **année par année**, entre un forfait
calculé sur la valeur locative et les frais effectifs justifiés. Le réflexe est
de calculer les deux et de retenir le plus favorable : une année sans travaux
appelle le forfait, une année de gros entretien appelle les frais effectifs.

Les taux du forfait sont cantonaux ; pour Vaud, voir `vaud-tax-return`,
`references/chiffres-cles-vd.md`.

## Taxes communales

Toutes les taxes figurant sur une facture communale ne sont pas déductibles. En
règle générale :

- déductibles : les taxes liées à l'entretien et à l'exploitation du bien
  (épuration, ordures, eau) ;
- non déductibles : l'impôt foncier et la taxe de séjour.

Ventiler la facture ligne par ligne, ne pas déduire le total.

## Dette hypothécaire et intérêts

Deux montants distincts, tous deux fournis par le créancier au 31.12 :

- les **intérêts payés** pendant l'année, déductibles du revenu ;
- le **solde de la dette** au 31.12, déductible de la fortune.

Ne jamais reconstituer le solde par une formule d'amortissement contractuelle
sans le vérifier contre l'attestation : les amortissements extraordinaires, les
changements de tranche et les renouvellements faussent le calcul.

Dans la plupart des logiciels, ces montants doivent être saisis **à deux
endroits** — dans la rubrique des dettes et intérêts, et sur la fiche de
l'immeuble. L'oubli de l'un des deux est fréquent ; `vaudtax.py check` le
détecte pour Vaud.

## Assurances

Les primes d'assurance du bâtiment (incendie, dégâts d'eau, RC immeuble) sont en
principe déductibles au titre des charges de l'immeuble. L'assurance ménage et
la RC privée ne le sont pas : elles relèvent des primes d'assurance de la
personne.
