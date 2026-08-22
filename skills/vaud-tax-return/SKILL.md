---
name: vaud-tax-return
description: Pré-remplit une déclaration d'impôts vaudoise (fichier .vaudtax) à partir d'un fichier de départ produit par VaudTax et d'un dossier de documents. Produit une checklist des pièces manquantes, un rapport de traçabilité, un comparatif avec l'année précédente et une liste de questions ouvertes. À utiliser quand quelqu'un veut préparer, remplir, compléter, vérifier ou relire sa déclaration d'impôts vaudoise. Vaud / VaudTax Swiss tax return.
---

# Déclaration d'impôts vaudoise

Compléter un fichier `.vaudtax` à partir des documents fournis.

> **Avertissement à rappeler à l'utilisateur au début et à la fin du travail.**
> Ce skill prépare un **brouillon** que la personne doit relire et valider. Ce
> n'est pas un conseil fiscal, et il n'engage personne. Rien n'est transmis à
> l'administration : le dépôt reste une action manuelle dans VaudTax.

## Entrées

Ce skill travaille sur ce qu'on lui donne, et **rien d'autre**. Il ne parcourt
pas les dossiers voisins, ne cherche pas les déclarations des années passées et
ne lit pas les notes personnelles qui traînent à côté.

| Entrée | Requis | Rôle |
|---|---|---|
| Fichier `.vaudtax` de départ | oui | le fichier à compléter |
| Dossier de documents | oui | les pièces de l'année, lues récursivement |
| `profil-fiscal.md` | non | faits personnels stables (voir plus bas) |
| `.vaudtax` de l'année précédente | non | active le comparatif `diff` |

**Demander les chemins manquants plutôt que les deviner.** Si le fichier de
l'année précédente n'est pas fourni, le signaler : c'est le contrôle le plus
efficace du lot, et son absence doit apparaître dans le rapport.

Les rapports sont écrits dans un dossier de sortie indiqué par l'utilisateur, à
défaut `rapport/` à côté du fichier de travail.

## Périmètre

**Ce skill écrit uniquement des valeurs** — montants, dates, libellés — dans le
XML de la déclaration. Il ne joint **aucun** justificatif : les pièces sont
attachées à la main dans l'interface VaudTax. Ne jamais modifier les sections
`piecesJustificatives*`, `userProfil` ni `guidedNav`.

Deux tâches restent **à faire dans VaudTax**, jamais ici :

- **l'import des eRelevés bancaires** — VaudTax lit les codes-barres des PDF et
  remplit lui-même les comptes (étape 4) ;
- **l'ajout des justificatifs**.

Le skill intervient donc *après* l'import des eRelevés, pour compléter ce que
celui-ci ne couvre pas.

## Prérequis — le point de départ

Le fichier de travail doit avoir été produit **par VaudTax lui-même**, via la
fonction « reprendre l'année précédente ». Ne jamais fabriquer un `.vaudtax` en
copiant le XML de l'année précédente et en changeant `fiscalPeriod` : la
référence gesdem lie le fichier au dossier du canton et ne peut pas être
inventée.

Si ce fichier n'existe pas encore, s'arrêter et demander à l'utilisateur de le
créer dans VaudTax d'abord.

## Règle cardinale

**Ne jamais inventer un chiffre.** Chaque valeur écrite provient d'un document
identifié (fichier + page), ou est demandée à l'utilisateur. Une valeur dont la
source est incertaine va dans les questions ouvertes, pas dans le XML.

Reporter un montant de l'année précédente faute de mieux n'est acceptable que
pour des données réellement stables (estimation fiscale d'un immeuble, numéro de
parcelle, numéro AVS), et doit alors être signalé comme tel dans la traçabilité.

## Le profil personnel

Aucun skill générique ne peut connaître la situation d'une personne : quels
comptes existent et qui s'en occupe, un plan d'actionnariat, un bien dans un
autre canton, les méthodes retenues les années précédentes, les questions encore
ouvertes.

Ces faits vivent dans un fichier `profil-fiscal.md` que l'utilisateur garde chez
lui, **hors de tout dépôt public**. Un modèle est fourni :
[`assets/profil-fiscal-modele.md`](assets/profil-fiscal-modele.md).

- S'il est fourni, le lire à l'étape 1.
- S'il n'existe pas, **proposer de le créer** à partir du modèle, et le remplir
  au fil du travail avec ce qu'on apprend.
- **Précédence : un document l'emporte toujours sur le profil.** Le profil donne
  des faits stables, du contexte et des conventions retenues — jamais un montant
  que porte aussi un document. Une contradiction entre les deux se **signale**,
  elle ne se résout pas en silence.
- À la fin du travail, **proposer les ajouts** au profil : faits confirmés,
  conventions choisies, questions soulevées. C'est ainsi qu'il devient utile
  d'année en année.

## Connaissances de fond

Les **montants vaudois** — plafonds, franchises, barèmes, avec leurs sources —
sont dans [`references/chiffres-cles-vd.md`](references/chiffres-cles-vd.md), ici
même.

Pour ce qui ne dépend pas du canton, lire au besoin le skill
**`swiss-tax-basics`**, installé à côté de celui-ci :
`references/deductions.md` (comment raisonner sur les déductions),
`references/titres-et-fortune.md`, `references/immobilier.md`, et
`references/chiffres-cles.md` pour les plafonds fédéraux du pilier 3a.

## Déroulé

### 1. Cadrage

Établir les entrées ci-dessus et demander celles qui manquent. Déterminer
l'année N. Lire le profil personnel s'il existe.

Lire les références de ce skill : [`references/format-vaudtax.md`](references/format-vaudtax.md),
[`references/champs-xml.md`](references/champs-xml.md),
[`references/documents-attendus.md`](references/documents-attendus.md),
[`references/cas-particuliers.md`](references/cas-particuliers.md).

### 2. Inventaire et documents manquants

Lister le dossier de documents et le confronter à `documents-attendus.md`.
Produire `00_documents_manquants.md` : pièces attendues et absentes, avec la
démarche pour les obtenir lorsqu'elle est connue. Par exemple commander un relevé fiscal payant, télécharger les eRelevés, réclamer à l'employeur l'annexe au certificat de salaire, etc.

**Présenter cette liste à l'utilisateur avant de continuer.** Il vaut mieux
récupérer les pièces manquantes maintenant que remplir à moitié.

### 3. Déballage

**Déterminer d'abord comment lancer le script**, une fois pour toutes, et le
retenir pour la suite. Essayer dans cet ordre :

```bash
uv run --script <chemin>/vaudtax.py --help    # 1er choix : uv fournit l'interpréteur
python3 <chemin>/vaudtax.py --help            # 2e choix
python  <chemin>/vaudtax.py --help            # 3e choix (Windows)
```

Le script n'a **aucune dépendance** : n'importe lequel des trois convient. Si
aucun ne fonctionne, **s'arrêter ici** et indiquer à l'utilisateur d'installer
uv, qui ne requiert pas de Python préalable :

```
macOS / Linux : curl -LsSf https://astral.sh/uv/install.sh | sh
Windows       : powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Ne pas tenter de contourner l'absence d'interpréteur en analysant le XML à la
main : les contrôles sont l'essentiel de la valeur de ce skill.

Dans la suite, `$S` désigne la commande retenue.

```bash
$S unpack travail.vaudtax /tmp/declN
$S check  travail.vaudtax --year N
```

**Vérifier que `fiscalPeriod` vaut bien N.**

Un `check` initial qui signale des montants manquants est normal : le fichier
repris de l'année précédente est un squelette. Voir `cas-particuliers.md`,
« Reprise de l'année précédente ».

### 4. eRelevés — étape VaudTax, avant d'écrire

```bash
$S ereleves /tmp/declN
```

La commande sépare les comptes déjà importés (ils portent `identifiantEReleve`)
de ceux saisis à la main, et signale les identifiants dont la date d'arrêté ne
correspond pas à l'année N — le cas typique étant l'import par mégarde du PDF de
l'an dernier, dont le nom de fichier est très proche.

**Règles :**

- **Ne jamais écrire dans un compte porteur d'`identifiantEReleve`.** Il
  appartient à VaudTax ; toute saisie manuelle sera écrasée au prochain import,
  ou pire, coexistera avec lui.
- Si des comptes attendus n'apparaissent pas comme importés, **rendre la main à
  l'utilisateur** : lui indiquer quels eRelevés télécharger et importer dans
  VaudTax, puis reprendre le travail sur le fichier ré-enregistré.
- L'import **renomme** les comptes avec le nom officiel de la banque ; les
  libellés personnels disparaissent. C'est normal, ne pas les rétablir.
- L'import peut créer un **doublon** à côté de la ligne reprise de l'année
  précédente. `check` les détecte ; c'est la ligne **sans**
  `identifiantEReleve` qu'il faut supprimer.

Seuls les comptes listés comme « saisis manuellement » sont à remplir à l'étape
suivante.

### 5. Lecture des documents

Lire les PDF avec l'outil de lecture de fichiers. Pour chaque valeur extraite,
noter la source (fichier, page) — elle alimentera la traçabilité.

**Extraire d'abord, écrire ensuite** : constituer la table complète des valeurs
avant de toucher au XML, ce qui permet de repérer les incohérences en amont.

Calculer à ce stade les **franchises** qui décident si une rubrique doit être
remplie du tout : frais médicaux (5 % du revenu), déduction pour le logement
(20 % du revenu net). Cf. `references/chiffres-cles-vd.md`.

### 6. Écriture

Éditer le XML extrait **comme du texte**. Ne pas le re-sérialiser avec un
parseur XML : cela réécrirait toutes les balises avec un préfixe `ns0:`.

Ordre conseillé, du plus sûr au plus délicat :

1. `activiteSalarieeRevenus` (certificats de salaire)
2. `etatTitres` — **uniquement les comptes sans `identifiantEReleve`** — et
   `fraisAdministrationTitres`
3. `primesEtCotisationsAssurance` (3a, primes maladie)
4. `enfants/enfFraisGarde`
5. `biensImmobiliers` + `interetsDettes`
6. `actionPartSociale` et `relevesFiscauxBancaires`
7. `fraisMedicaux`, `fraisPerfectionnementFormations`
8. `autoMoto`, `acomptes`, `autresRevenusTouteNatureList`

Mettre à jour `dateDebut` / `dateFin` sur les périodes : elles portent encore
l'année précédente. Insérer tout nouvel élément **au contact de ses semblables**
et lui attribuer un `trackingIndex` non utilisé pour ce type.

Pour les sections sans objet, laisser `isInitialized=false` plutôt que de les
supprimer.

### 7. Contrôles

```bash
$S check /tmp/declN --year N
$S diff  annee_precedente.vaudtax /tmp/declN   # si disponible
```

Traiter **chaque** anomalie du `check`, et lire les avertissements.

Passer le `diff` en revue ligne à ligne : c'est le filet de sécurité principal.
Chercher les variations inexpliquées, les postes disparus, et surtout la section
**« Montants inchangés depuis l'an dernier »** — un montant identique au franc
près d'une année sur l'autre est presque toujours un oubli de mise à jour.

Si aucun fichier de l'année précédente n'a été fourni, **le dire explicitement**
dans le rapport : ce contrôle n'a pas pu être fait.

### 8. Reconstruction

```bash
$S pack /tmp/declN travail.vaudtax
```

Une sauvegarde `.bak` est créée automatiquement. **Demander à l'utilisateur
d'ouvrir le fichier dans VaudTax pour valider** avant toute autre étape : la vérification est indispensable.

### 9. Livrables

Écrire dans le dossier de rapport :

| Fichier | Contenu |
|---|---|
| `00_documents_manquants.md` | produit à l'étape 2, y compris les eRelevés à commander ou importer |
| `01_tracabilite.md` | chaque valeur écrite, sa source (fichier + page), son statut : extrait d'un document / confirmé par l'utilisateur / donnée stable reportée |
| `02_comparatif.md` | sortie de `diff` commentée, ou la mention que l'année précédente n'était pas disponible |
| `03_questions_ouvertes.md` | points incertains, à trancher ou à poser à un professionnel |
| `04_profil_propose.md` | ajouts proposés au `profil-fiscal.md` |

La traçabilité est le livrable qui compte : elle doit permettre de contrôler la
déclaration sans rouvrir les PDF.

Y rappeler également les démarches **hors** fichier `.vaudtax` restant à faire :
joindre les justificatifs dans l'interface, déposer la déclaration, et le cas
échéant **déposer la déclaration du canton où se trouve un immeuble**.

## Interaction avec l'utilisateur

Poser les questions **groupées**, pas au fil de l'eau. Traiter d'abord tout ce
qui ne dépend pas d'une réponse, puis soumettre les points en suspens en un seul
lot.
