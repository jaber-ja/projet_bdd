# Génération du diagramme EER
# Prérequis: Python 3, PyYAML (pip install -r requirements.txt), Graphviz (dot)

.PHONY: build install clean

BUILD_DIR := build

install:
	pip install -r requirements.txt

# Générer diagramme_er.dot, .svg et .png dans build/
build:
	@mkdir -p $(BUILD_DIR)
	python3 tools/generate_er_dot.py --out-dir $(BUILD_DIR) --svg --png
	@echo "✓ Diagramme généré dans $(BUILD_DIR)/"

# Nettoyer les artefacts générés
clean:
	rm -rf $(BUILD_DIR)
