# Maintenance du diagramme EER

Ce guide décrit comment faire évoluer le modèle et régénérer le diagramme.

## Prérequis

- Python 3
- PyYAML : `pip install -r requirements.txt`
- Graphviz (commande `dot`) : [graphviz.org](https://graphviz.org/)

## Structure des fichiers

| Fichier | Rôle |
|---------|------|
| `model/diagram_model.yaml` | **Source canonique** du schéma (entités, relations, contraintes) |
| `tools/generate_er_dot.py` | Générateur YAML → DOT |
| `build/diagramme_er.dot` | Fichier DOT produit (artefact, ne pas éditer) |
| `build/diagramme_er.svg` | Diagramme SVG |
| `build/diagramme_er.png` | Diagramme PNG |

Les anciens fichiers `er_config/`, `diagramme_test.dot` et `generer_diagramme.py` restent pour compatibilité, mais la source officielle est désormais `model/diagram_model.yaml`.

## Modifier le modèle

1. Ouvrir `model/diagram_model.yaml`
2. Éditer selon les besoins :
   - **Entités** : section `entites`, attributs avec `nom`, `pk`, `fk`, `uq`, `derive`, `derivee`, `coherent`, `qualif`
   - **Relations** : section `relations`, avec `source`, `cible`, `label`, `taillabel`, `headlabel`
   - **Contraintes** : section `notes` (Contraintes, Hypotheses)
3. Régénérer : `make build` ou `python3 tools/generate_er_dot.py --out-dir build --svg --png`

## Format des cardinalités

Utiliser `(min,max)` avec `min` et `max` numériques ou `n` pour « plusieurs » :  
ex. `(0,n)`, `(1,1)`, `(1,n)`.

## Vérification de parité

Après modification du générateur, comparer le rendu avec l’ancien :

1. Toutes les entités du modèle doivent apparaître.
2. Toutes les relations et leurs cardinalités doivent être correctes.
3. Les contraintes et hypothèses doivent être lisibles en bas du diagramme.

## Fallback format record

Si les labels HTML provoquent des problèmes de rendu Graphviz :

```bash
python3 tools/generate_er_dot.py --out-dir build --no-html --svg --png
```

## Checklist avant commit

- [ ] Le modèle YAML est à jour et cohérent
- [ ] `make build` s’exécute sans erreur
- [ ] Le diagramme généré reflète les changements attendus
