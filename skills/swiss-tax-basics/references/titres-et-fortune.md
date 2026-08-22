# Titres, comptes et fortune mobilière

## La règle de base

Tout se déclare : chaque compte bancaire ou postal, y compris ceux dont le solde
est nul ou dérisoire, y compris les comptes de garantie de loyer, y compris les
comptes joints. Un compte oublié ressort tôt ou tard, et son absence coûte plus
cher que le peu d'impôt qu'il aurait généré.

On déclare la situation **au 31 décembre** : solde à cette date, et rendements
encaissés pendant l'année.

## Le relevé fiscal électronique (eRelevé, eCH-0196)

C'est de loin la meilleure source, et il faut la privilégier systématiquement.

Un eRelevé fiscal est un PDF que la banque produit spécifiquement pour la
déclaration, porteur d'un code-barres qui encode l'ensemble des données dans le
format normalisé [eCH-0196](https://www.ech.ch/fr/ech/ech-0196/2.2.0). Les
logiciels fiscaux cantonaux savent le lire et remplissent les rubriques seuls :
solde, rendements, valeurs fiscales, identifiant du compte.

Conséquences pratiques :

- **L'import se fait dans le logiciel fiscal**, jamais en recopiant le PDF à la
  main. Une extraction manuelle est moins fiable et perd la traçabilité.
- Un compte rempli par import **appartient au logiciel**. Le modifier à la main
  crée une incohérence qui sera écrasée au prochain import, ou pire, coexistera
  avec lui.
- L'import **renomme** souvent le compte avec la dénomination officielle de la
  banque. Les libellés personnels disparaissent : c'est normal.
- Certains relevés fiscaux sont **payants** et se commandent à l'avance, parfois
  plusieurs semaines. À vérifier au tout début du travail, pas au moment de
  remplir. Leur coût est déductible au titre des frais d'administration de
  titres.

L'identifiant du code-barres contient la **date d'arrêté** (par exemple
`…20251231`). C'est le moyen de vérifier qu'on a bien importé l'eRelevé de
l'année en cours : les noms de fichiers d'une année sur l'autre sont presque
identiques, et l'import du mauvais millésime est une erreur classique.

Écosystème open source autour de cette norme, utile quand la banque ou le
courtier ne fournit pas d'eRelevé :

- [`vroonhof/opensteuerauszug`](https://github.com/vroonhof/opensteuerauszug) —
  génère et contrôle des relevés eCH-0196 depuis des exports bancaires ;
- [`aurelschwitter/ibkr-to-etax`](https://github.com/aurelschwitter/ibkr-to-etax)
  — convertit un export Interactive Brokers en relevé eCH-0196 ;
- [`BrunoEberhard/open-ech-taxstatement`](https://github.com/BrunoEberhard/open-ech-taxstatement)
  — éditeur de relevés eCH-0196.

Fiducai ne réimplémente pas ces outils.

## Valeurs fiscales : ICTax

Pour les titres, la valeur à déclarer n'est pas le cours de bourse choisi au
hasard : c'est la **valeur fiscale** publiée par l'Administration fédérale des
contributions dans [ICTax](https://www.ictax.admin.ch/). ICTax donne, par numéro
de valeur ou ISIN et par année :

- le cours fiscal au 31.12 ;
- le traitement des distributions (soumises ou non à l'impôt anticipé) ;
- les **cours de conversion des devises** au 31.12, à utiliser pour convertir un
  compte ou un titre en francs.

Utiliser ICTax plutôt qu'un taux trouvé ailleurs : c'est la référence que
l'autorité utilisera elle-même.

Pour les fonds de placement, la donnée fiscale n'est pas la variation de valeur
mais le **rendement imposable** calculé par le fonds, que ICTax publie. C'est la
raison pour laquelle un relevé fiscal bancaire vaut mieux qu'un simple extrait
de dépôt.

## Impôt anticipé

L'impôt anticipé (35 %) prélevé sur les rendements suisses est **récupéré** via
la déclaration : c'est un des rares endroits où bien remplir rapporte
directement de l'argent. Encore faut-il que les rendements concernés soient
déclarés dans la bonne colonne — soumis ou non soumis à l'impôt anticipé. Les
eRelevés font cette ventilation seuls.

Les retenues étrangères (par exemple sur des dividendes américains) suivent un
régime différent, avec leurs propres rubriques.

## Ce qui n'est pas de la fortune imposable

Les avoirs de **2e pilier** (caisse de pension) et de **3e pilier A** ne sont
pas soumis à l'impôt sur la fortune et ne se déclarent pas comme tels. Seules
les **cotisations** de l'année se déduisent du revenu.
