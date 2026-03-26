#!/usr/bin/env python3
"""
Générateur de diagramme EER au format DOT.
Lit model/diagram_model.yaml et produit un fichier .dot stylé (notation EER académique).

Usage:
    python tools/generate_er_dot.py [--out-dir DIR] [--svg] [--png]

Résultat: build/diagramme_er.dot (+ .svg et .png si demandé)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML requis: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = REPO_ROOT / "model" / "diagram_model.yaml"
ER_CONFIG_DIR = REPO_ROOT / "er_config"
DEFAULT_OUT_DIR = REPO_ROOT / "build"
OUTPUT_BASENAME = "diagramme_er"


def _parse_attribut_string(s: str) -> dict:
    """Convertit une chaîne 'PK idUtilisateur', 'email (UQ)', etc. en dict."""
    s = s.strip()
    attr = {"nom": s}
    # Préfixes PK, FK
    if s.startswith("PK,FK "):
        attr = {"nom": s[6:].strip(), "pk": True, "fk": True}
    elif s.startswith("PK "):
        attr = {"nom": s[3:].strip(), "pk": True}
    elif s.startswith("FK "):
        attr = {"nom": s[3:].strip(), "fk": True}
    # Suffixes entre parenthèses
    if " (" in attr["nom"] and ")" in attr["nom"]:
        nom, suffix = attr["nom"].rsplit(" (", 1)
        suffix = suffix.rstrip(")")
        attr["nom"] = nom.strip()
        if suffix == "UQ":
            attr["uq"] = True
        elif suffix == "derive":
            attr["derive"] = True
        elif suffix == "derive/coherent":
            attr["derive"] = True
            attr["coherent"] = True
        elif suffix == "derivee":
            attr["derivee"] = True
        else:
            attr["qualif"] = suffix
    return attr


def _load_from_er_config() -> dict:
    """Charge le modèle depuis er_config/ (format legacy)."""
    entites_data = yaml.safe_load((ER_CONFIG_DIR / "entites.yaml").read_text(encoding="utf-8"))
    relations_data = yaml.safe_load((ER_CONFIG_DIR / "relations.yaml").read_text(encoding="utf-8"))
    notes_data = yaml.safe_load((ER_CONFIG_DIR / "notes.yaml").read_text(encoding="utf-8"))

    entites = {}
    for nom, config in entites_data.get("entites", {}).items():
        attributs = config.get("attributs", [])
        entites[nom] = {
            "attributs": [
                _parse_attribut_string(a) if isinstance(a, str) else a
                for a in attributs
            ]
        }

    return {
        "metadata": {"title": "Plateforme de resumes de cours - Modele ER"},
        "entites": entites,
        "relations": relations_data.get("relations", []),
        "liens_notes": relations_data.get("liens_notes", []),
        "notes": notes_data.get("notes", {}),
    }


def load_model() -> dict:
    if MODEL_PATH.exists():
        with open(MODEL_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)
    if ER_CONFIG_DIR.exists():
        return _load_from_er_config()
    raise FileNotFoundError(f"Modèle introuvable: {MODEL_PATH} ou {ER_CONFIG_DIR}")


def attribut_to_str(attr: dict) -> str:
    """Convertit un attribut structuré en chaîne pour affichage."""
    nom = attr.get("nom", str(attr))
    parts = []
    if attr.get("pk"):
        parts.append("PK")
    if attr.get("fk"):
        parts.append("FK")
    if attr.get("uq"):
        parts.append("UQ")
    if attr.get("derive"):
        parts.append("derive")
    if attr.get("derivee"):
        parts.append("derivee")
    if attr.get("coherent"):
        parts.append("coherent")
    if attr.get("qualif"):
        parts.append(f"({attr['qualif']})")
    if parts:
        return f"{' '.join(parts)} {nom}"
    return nom


def format_attribut_html(attr: dict) -> str:
    """Retourne le HTML d'une cellule pour un attribut (soulignement si PK)."""
    nom = attr.get("nom", str(attr))
    extras = []
    if attr.get("fk"):
        extras.append("FK ")
    if attr.get("uq"):
        extras.append("(UQ) ")
    if attr.get("derive") and attr.get("coherent"):
        extras.append("(derive/coherent) ")
    elif attr.get("derive"):
        extras.append("(derive) ")
    if attr.get("derivee"):
        extras.append("(derivee) ")
    if attr.get("qualif"):
        extras.append(f"({attr['qualif']}) ")
    suffix = " ".join(extras).strip()
    display = f"{nom} {suffix}".strip()
    if attr.get("pk"):
        return f'<TD><U>{display}</U></TD>'
    return f'<TD>{display}</TD>'


def build_entity_html(name: str, attributs: list) -> str:
    """Construit le label HTML Graphviz pour une entité EER (PK soulignées)."""
    rows = [
        f'<TR><TD COLSPAN="1" BGCOLOR="#E8F0FE" BORDER="1" SIDES="B" PORT="header">'
        f'<B>{name}</B></TD></TR>'
    ]
    for attr in attributs:
        rows.append(f"<TR>{format_attribut_html(attr)}</TR>")
    table = (
        '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4" '
        'STYLE="ROUNDED" BGCOLOR="#E8F0FE" COLOR="#4A90E2">'
        + "".join(rows)
        + "</TABLE>"
    )
    return f'<{table}>'


def build_entity_record(name: str, attributs: list) -> str:
    """Fallback: format record classique si HTML pose problème."""
    lines = [attribut_to_str(a) for a in attributs]
    label = "{" + name + "|" + "\\l".join(lines) + "\\l}"
    return f'label="{label}"'


def format_notes_label(lignes: list) -> str:
    return "\\l".join(lignes)


def validate_cardinality(c: str) -> bool:
    """Vérifie qu'une cardinalité a la forme (min,max)."""
    s = c.replace(" ", "").strip()
    return bool(re.match(r'^\(\d+,(\d+|n)\)$', s))


def next_output_version_dir(out_dir: Path) -> Path:
    """Retourne le prochain dossier de version: out_dir/vN."""
    pattern = re.compile(r"^v(\d+)$")
    max_version = 0
    for candidate in out_dir.iterdir():
        if not candidate.is_dir():
            continue
        match = pattern.match(candidate.name)
        if match:
            max_version = max(max_version, int(match.group(1)))
    return out_dir / f"v{max_version + 1}"


def build_dot(model: dict, use_html_labels: bool = True) -> str:
    """Construit le contenu DOT complet à partir du modèle."""
    meta = model.get("metadata", {})
    title = meta.get("title", "Modele ER")

    lines = [
        'digraph DiagrammeER {',
        '  graph [rankdir=LR, splines=ortho, overlap=false,',
        '         size="11.69,8.27!", ratio=fill, dpi=200,',
        '         margin=0.25, pad=0.25, nodesep=0.65, ranksep=1.10,',
        f'         labelloc="t", fontsize=20, fontname="Helvetica", label="{title}"];',
        '  node [fontname="Helvetica", fontsize=10];',
        '  edge [color="#555555", arrowsize=0.8, fontname="Helvetica", fontsize=9];',
        '',
    ]

    # --- Entités ---
    entites = model.get("entites", {})
    for nom, config in entites.items():
        attributs = config.get("attributs", [])
        if use_html_labels:
            html = build_entity_html(nom, attributs)
            lines.append(f'  {nom} [shape=plain, margin=0, label={html}];')
        else:
            lines.append(f'  {nom} [shape=record, style="rounded,filled", fillcolor="#E8F0FE", '
                        f'color="#4A90E2", {build_entity_record(nom, attributs)}];')

    lines.append("")

    # --- Notes (Contraintes, Hypothèses) ---
    notes = model.get("notes", {})
    for nom, config in notes.items():
        style = config.get("style", {})
        fill = style.get("fillcolor", "#FFF8E1")
        color = style.get("color", "#C9A227")
        shape = style.get("shape", "note")
        label = format_notes_label(config.get("lignes", []))
        lines.append(f'  {nom} [shape={shape}, fillcolor="{fill}", color="{color}", '
                    f'label="{label}"];')

    lines.append("")

    # --- Relations ---
    for r in model.get("relations", []):
        src, dst = r["source"], r["cible"]
        lbl = r.get("label", "")
        tail = r.get("taillabel", "(0,n)")
        head = r.get("headlabel", "(1,1)")
        if not validate_cardinality(tail):
            tail = "(0,n)"
        if not validate_cardinality(head):
            head = "(1,1)"
        dist = 1.6 if "EditionCours" in (src, dst) else 1.8
        opts = f'label="{lbl}", taillabel="{tail}", headlabel="{head}", labeldistance={dist}'
        lines.append(f'  {src} -> {dst} [{opts}];')

    # --- Liens pointillés vers notes ---
    for lnk in model.get("liens_notes", []):
        src, dst = lnk["source"], lnk["cible"]
        lines.append(f'  {src} -> {dst} [style=dashed, arrowhead=none, constraint=false];')

    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Génère le diagramme EER à partir du modèle YAML")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR,
                        help=f"Répertoire de sortie (défaut: {DEFAULT_OUT_DIR})")
    parser.add_argument("--svg", action="store_true", help="Générer aussi le SVG")
    parser.add_argument("--png", action="store_true", help="Générer aussi le PNG")
    parser.add_argument("--no-html", action="store_true",
                        help="Utiliser le format record au lieu des labels HTML (fallback)")
    args = parser.parse_args()

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    version_dir = next_output_version_dir(out_dir)
    version_dir.mkdir(parents=True, exist_ok=False)
    dot_path = version_dir / f"{OUTPUT_BASENAME}.dot"

    model = load_model()
    dot_content = build_dot(model, use_html_labels=not args.no_html)
    dot_path.write_text(dot_content, encoding="utf-8")
    print(f"✓ {OUTPUT_BASENAME}.dot généré: {dot_path}")

    for fmt, flag in [("svg", args.svg), ("png", args.png)]:
        if not flag:
            continue
        out_path = version_dir / f"{OUTPUT_BASENAME}.{fmt}"
        try:
            subprocess.run(
                ["dot", f"-T{fmt}", "-o", str(out_path), str(dot_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✓ {OUTPUT_BASENAME}.{fmt} généré: {out_path}")
        except FileNotFoundError:
            print("Graphviz (dot) non installé. Installez-le pour générer SVG/PNG.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Erreur Graphviz: {e.stderr}")
            sys.exit(1)


if __name__ == "__main__":
    main()
