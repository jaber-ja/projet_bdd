# Modele relationnel - Plateforme de partage de resumes

Ce document presente le modele relationnel final de la partie 1, avec:
- les relations
- les cles primaires et etrangeres
- les contraintes d'unicite et de domaine
- les hypotheses de modelisation

## 1) Relations

### Utilisateurs et profil

- `Utilisateur(`**`idUtilisateur`**`, nomUtilisateur, email, dateInscription)`
  - PK: `idUtilisateur`
  - UQ: `email`

- `ProfilUtilisateur(`**`idUtilisateur`**`, pointsTotal, niveau, idTitreActif)`
  - PK: `idUtilisateur`
  - FK: `idUtilisateur -> Utilisateur(idUtilisateur)`
  - FK: `idTitreActif -> PossessionObjet(idPossession)` (nullable)

### Cours et annees academiques

- `Cours(`**`codeCours`**`, nomCours, faculte)`
  - PK: `codeCours`

- `AnneeAcademique(`**`idAnnee`**`, libelleAnnee, dateDebut, dateFin)`
  - PK: `idAnnee`
  - UQ: `libelleAnnee`

- `CoursAnnee(`**`codeCours, idAnnee`**`)`
  - PK: `(codeCours, idAnnee)`
  - FK: `codeCours -> Cours(codeCours)`
  - FK: `idAnnee -> AnneeAcademique(idAnnee)`

### Resumes et evaluations

- `Resume(`**`idResume`**`, idAuteur, codeCours, idAnnee, titre, description, datePublication, visibilite, noteMoyenne)`
  - PK: `idResume`
  - FK: `idAuteur -> Utilisateur(idUtilisateur)`
  - FK: `(codeCours, idAnnee) -> CoursAnnee(codeCours, idAnnee)`
  - `noteMoyenne` est un attribut derive (ou materialise si besoin technique)

- `EvaluationResume(`**`idEvaluateur, idResume`**`, note, commentaire, dateEvaluation)`
  - PK: `(idEvaluateur, idResume)`
  - FK: `idEvaluateur -> Utilisateur(idUtilisateur)`
  - FK: `idResume -> Resume(idResume)`

### Points et transactions

- `TransactionPoints(`**`idTransaction`**`, idUtilisateur, typeTransaction, nbPoints, dateTransaction, motif, sourceType, sourceId)`
  - PK: `idTransaction`
  - FK: `idUtilisateur -> Utilisateur(idUtilisateur)`
  - `sourceType` identifie l'origine metier (`publication`, `evaluation`, `achat`, `ajustement`)

### Boutique et cosmetiques

- `ObjetCosmetique(`**`idObjet`**`, nom, description, prixPoints, typeObjet)`
  - PK: `idObjet`

- `AchatObjet(`**`idAchat`**`, idUtilisateur, idObjet, dateAchat, prixPointsPaye)`
  - PK: `idAchat`
  - FK: `idUtilisateur -> Utilisateur(idUtilisateur)`
  - FK: `idObjet -> ObjetCosmetique(idObjet)`

- `PossessionObjet(`**`idPossession`**`, idUtilisateur, idObjet, idAchat, dateObtention, estEquipe)`
  - PK: `idPossession`
  - FK: `idUtilisateur -> Utilisateur(idUtilisateur)`
  - FK: `idObjet -> ObjetCosmetique(idObjet)`
  - FK: `idAchat -> AchatObjet(idAchat)`

### Leaderboard

- `ClassementCourant(`**`idUtilisateur`**`, rang, pointsConstates, dateCalcul)`
  - PK: `idUtilisateur`
  - FK: `idUtilisateur -> Utilisateur(idUtilisateur)`

## 2) Contraintes d'integrite

## 2.1 Contraintes d'unicite

- `Utilisateur.email` est unique.
- `AnneeAcademique.libelleAnnee` est unique.
- `EvaluationResume(idEvaluateur, idResume)` est unique (une evaluation par utilisateur et par resume).
- `ClassementCourant(idUtilisateur)` est unique.

## 2.2 Contraintes de domaine

- `EvaluationResume.note` dans `[1..5]`.
- `Resume.visibilite` dans `{public, prive, restreint}`.
- `TransactionPoints.typeTransaction` dans `{gain, depense}`.
- `TransactionPoints.sourceType` dans `{publication, evaluation, achat, ajustement}`.
- `TransactionPoints.nbPoints > 0`.
- `ObjetCosmetique.prixPoints >= 0`.
- `ObjetCosmetique.typeObjet` dans `{badge, titre, theme}`.
- `AnneeAcademique.dateDebut < AnneeAcademique.dateFin`.

## 2.3 Contraintes metier

- Le `pointsTotal` de `ProfilUtilisateur` correspond a la somme signee des `TransactionPoints` de l'utilisateur.
- `Resume.noteMoyenne` est la moyenne des `EvaluationResume.note` associees.
- `ProfilUtilisateur.idTitreActif` est `NULL` ou refere une ligne de `PossessionObjet`:
  - appartenant au meme utilisateur
  - dont l'objet associe est de type `titre`
- Un utilisateur ne peut avoir qu'un seul titre actif a un instant donne (porte par l'unique FK `idTitreActif`).
- Un achat d'objet doit etre coherent avec une depense de points (tracee dans `TransactionPoints` avec `sourceType = achat`).
- `ClassementCourant.rang` est strictement positif.

## 3) Hypotheses de modelisation (justifiees)

- **Cours multi-annees**: un cours peut exister sur plusieurs annees academiques, d'ou `CoursAnnee`.
- **Titre actif unique**: seul le titre est activable dans le profil (pas d'obligation de badge actif).
- **Attributs techniques**: `idResume`, `idTransaction`, `idAchat`, `idPossession` sont des identifiants techniques.
- **Version de resume**: pas de versionnement dans ce modele (une ligne par resume).
- **Leaderboard courant**: seule la photo courante est conservee.
- **Transaction comme source de verite des points**: toute variation de points doit etre tracee dans `TransactionPoints`.
