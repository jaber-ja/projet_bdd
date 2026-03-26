# Plateforme de resumes de cours - Modele ER

Schema entite-association pour la plateforme de gestion des resumes, evaluations et points.

## Generation du diagramme

```bash
pip install -r requirements.txt   # PyYAML
make build                        # Necessite Graphviz (brew install graphviz)
```

Alternative avec venv :
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python tools/generate_er_dot.py --out-dir build --svg --png
```

Sortie : `build/diagramme_er.dot`, `build/diagramme_er.svg`, `build/diagramme_er.png`

## Documentation

- Maintenance du diagramme: [docs/MAINTENANCE_DIAGRAMME.md](docs/MAINTENANCE_DIAGRAMME.md)
- Modele relationnel final: [docs/MODELE_RELATIONNEL.md](docs/MODELE_RELATIONNEL.md)
