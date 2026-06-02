#!/usr/bin/env python3
"""
Scansiona la cartella immagini/ e genera manifest.json con la lista
esatta dei file per ogni progetto (foto e disegni, jpg e mp4).
Da eseguire dalla root della repo, oppure automaticamente via GitHub Action.
"""

import json
import os
import re
from pathlib import Path

IMMAGINI_DIR = Path("immagini")
OUTPUT_FILE  = Path("manifest.json")

def scan_project(slug_dir: Path) -> dict:
    slug = slug_dir.name
    foto    = []
    disegni = []

    # Raccoglie tutti i file jpg/mp4 nella cartella
    files = sorted(slug_dir.iterdir(), key=lambda f: f.name.lower())

    for f in files:
        if f.suffix.lower() not in (".jpg", ".jpeg", ".mp4"):
            continue
        name = f.stem.lower()

        # Determina il tipo (img o video)
        media_type = "video" if f.suffix.lower() == ".mp4" else "img"
        rel_path   = f"{IMMAGINI_DIR.name}/{slug}/{f.name}"

        # Classifica: anteprima, foto-N, disegno-N
        if "anteprima" in name:
            continue  # gestita separatamente
        elif re.search(r"-foto-\d+$", name):
            foto.append({"src": rel_path, "type": media_type})
        elif re.search(r"-disegno-\d+$", name):
            disegni.append({"src": rel_path, "type": media_type})

    # Anteprima: cerca jpg o png con "anteprima" nel nome
    anteprima = None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        candidate = slug_dir / f"{slug}-anteprima{ext}"
        if candidate.exists():
            anteprima = f"{IMMAGINI_DIR.name}/{slug}/{candidate.name}"
            break

    return {
        "foto":      foto,
        "disegni":   disegni,
        "anteprima": anteprima,
    }

def main():
    if not IMMAGINI_DIR.exists():
        print(f"Cartella '{IMMAGINI_DIR}' non trovata. Esegui dalla root della repo.")
        raise SystemExit(1)

    manifest = {}

    for slug_dir in sorted(IMMAGINI_DIR.iterdir()):
        if not slug_dir.is_dir():
            continue
        slug = slug_dir.name
        manifest[slug] = scan_project(slug_dir)
        foto_n    = len(manifest[slug]["foto"])
        disegni_n = len(manifest[slug]["disegni"])
        print(f"  {slug}: {foto_n} foto, {disegni_n} disegni")

    OUTPUT_FILE.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"\n✓ manifest.json generato con {len(manifest)} progetti.")

if __name__ == "__main__":
    main()
