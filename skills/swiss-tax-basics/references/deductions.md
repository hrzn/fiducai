# Déductions — principes et pièges

Ce document explique *comment raisonner* sur les déductions. Il ne donne aucun
montant : les plafonds fédéraux sont dans
[`chiffres-cles.md`](chiffres-cles.md), et les plafonds cantonaux dans le skill
du canton concerné — pour Vaud, `vaud-tax-return`,
`references/chiffres-cles-vd.md`.

Les seuils cités ici à titre d'exemple (5 % pour les frais médicaux, 20 % pour
le logement) sont ceux de Vaud : **vérifier ceux du canton traité**.

## Trois niveaux d'impôt, trois jeux de règles

Une déclaration suisse sert simultanément l'**impôt fédéral direct**, l'**impôt
cantonal** et l'**impôt communal**. Le revenu imposable n'est pas le même pour
les trois : certaines déductions existent au niveau cantonal et pas au niveau
fédéral, et les plafonds diffèrent. Le logiciel fiscal calcule les deux
assiettes seul, mais cela explique pourquoi un même montant saisi une fois
apparaît avec deux plafonds différents.

Le pilier 3a fait exception : son plafond est fédéral et repris tel quel partout.

## Forfait contre frais effectifs

Beaucoup de rubriques offrent le choix entre un forfait et les frais réellement
justifiés — frais professionnels, entretien d'immeuble, frais de véhicule. Deux
règles :

1. **Calculer les deux** et retenir le plus favorable. Le forfait est souvent
   plus avantageux qu'on ne le croit, et il dispense de justificatifs.
2. Le choix se fait **par année**, et pour l'ensemble de la rubrique : on ne
   peut pas cumuler le forfait et quelques frais effectifs choisis.

Corollaire utile : si les frais effectifs sont nettement inférieurs au forfait,
il est inutile de rassembler les justificatifs correspondants.

## Les franchises rendent certaines rubriques inutiles

Plusieurs déductions ne s'appliquent qu'au-delà d'un seuil calculé sur le
revenu : les frais médicaux au-delà d'un pourcentage du revenu, la déduction
pour le logement au titre de la part du loyer qui dépasse une fraction du revenu
net. Les pourcentages sont **cantonaux** (à Vaud : 5 % et 20 %).

Il faut donc **calculer le seuil avant de saisir quoi que ce soit**. Si le total
est largement en dessous, la déduction sera nulle : ne pas remplir la rubrique,
ne pas rassembler les pièces, et le signaler dans le rapport plutôt que de
laisser croire à un oubli. Si l'on est proche du seuil, il faut au contraire le
montant exact, pas une estimation.

## Cotisations professionnelles : la confusion classique

- Les **frais de perfectionnement et de formation** couvrent exclusivement ce
  qui se rattache à un cursus ou à une mise à niveau professionnelle : frais de
  cours, écolages, matériel d'étude, frais d'examens.
- Les **cotisations à une association professionnelle ou à un syndicat** n'en
  font pas partie. Elles relèvent des **autres frais professionnels**, couverts
  par un forfait — et ne sont donc déductibles en plus que si l'ensemble des
  autres frais professionnels effectifs dépasse ce forfait, ce qui est rare.
  Le forfait est cantonal (à Vaud : 3 % du revenu net, entre deux bornes).

Ranger une cotisation syndicale dans les frais de formation est une erreur
fréquente, et visible pour l'autorité.

## Frais de garde

Seul le **coût de la garde** est déductible : crèche, maman de jour, accueil
parascolaire. Les frais d'entretien facturés sur la même attestation —
nourriture, tâches ménagères — ne le sont pas, et les attestations les
mélangent souvent. Lire l'attestation ligne par ligne.

La déduction est plafonnée **par enfant**, ce qui suppose de ventiler un montant
global entre les enfants. Quand plusieurs personnes assument les frais, la
répartition entre elles peut être discutée par l'autorité ; un accord écrit
entre les parents est ce qui permet de la justifier.

## Assurance maladie

La déduction porte sur les primes de l'ensemble du ménage — assurance de base et
complémentaires, pour les deux conjoints et pour les enfants à charge — sous
déduction des subsides reçus. Elle est **plafonnée à un montant forfaitaire**,
qui est en pratique atteint dès qu'on assure une famille : le montant exact des
primes n'a alors qu'une importance limitée, mais il faut quand même le
renseigner correctement.

## Ce qui n'est pas déductible

Erreurs récurrentes, à écarter d'emblée :

- les impôts eux-mêmes (impôt sur le revenu, impôt foncier) ;
- les amortissements de dette — seuls les **intérêts** le sont ;
- les dépenses d'entretien courant du ménage ;
- les primes d'assurance ménage et RC privée ;
- les frais de déplacement au-delà du plafond, ou lorsque l'employeur les
  rembourse ;
- les dépenses de plus-value sur un immeuble (à conserver pour l'impôt sur les
  gains immobiliers).

## Une déduction n'est pas un gain

Une déduction de 1 000 francs ne fait pas économiser 1 000 francs d'impôt, mais
1 000 × le taux marginal — souvent entre 20 % et 35 % en Suisse selon le revenu
et la commune. Cela a une conséquence pratique : passer une heure à chercher un
justificatif de 50 francs n'a pas de sens, alors que vérifier un plafond de
prévoyance en a beaucoup.
