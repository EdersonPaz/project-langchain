#!/usr/bin/env python
"""Sincroniza arquivos de documentação para a pasta docs/ e remove da raiz."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
FILES = ["STRUCTURE_OPTIONS.md", "TOKEN_OPTIMIZATION.md"]


def sync_docs():
    DOCS.mkdir(parents=True, exist_ok=True)
    moved = []

    for filename in FILES:
        src = ROOT / filename
        dst = DOCS / filename

        if src.exists():
            with src.open("rb") as f_src, dst.open("wb") as f_dst:
                f_dst.write(f_src.read())
            src.unlink()
            moved.append(filename)
            print(f"✅ Moveu {filename} -> docs/")
        elif dst.exists():
            print(f"ℹ️ {filename} já existe em docs/ (sem ação)")
        else:
            print(f"⚠️ {filename} não encontrado em root nem docs/")

    if moved:
        print("\nSincronização concluída. Arquivos removidos da raiz e colocados em docs/.")
    else:
        print("\nNenhuma movimentação necessária. Verifique os arquivos manualmente.")


if __name__ == "__main__":
    sync_docs()
