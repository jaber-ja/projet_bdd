# Plateforme de résumés de cours – Modèle ER

Schéma entité-association pour la plateforme de gestion des résumés, évaluations et points.

## Génération du diagramme

```bash
pip install -r requirements.txt   # PyYAML
make build                        # Nécessite Graphviz (brew install graphviz)
```

Alternative avec venv :
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python tools/generate_er_dot.py --out-dir build --svg --png
```

Sortie : `build/diagramme_er.dot`, `build/diagramme_er.svg`, `build/diagramme_er.png`

Voir [docs/MAINTENANCE_DIAGRAMME.md](docs/MAINTENANCE_DIAGRAMME.md) pour modifier le modèle.
