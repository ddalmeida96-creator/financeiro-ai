"""Armazenamento editável de categorias/palavras-chave em JSON.
Semeado a partir de categorias.py na primeira execução. Persistido ao lado do banco
(no volume do Railway) para sobreviver a redeploys.
"""
import os
import json
from categorias import CATEGORIAS as _SEED_DESP, RECEITAS as _SEED_REC

DB_PATH = os.getenv("DB_PATH", "financeiro.db")
_DIR = os.path.dirname(os.path.abspath(DB_PATH))
_FILE = os.path.join(_DIR, "categorias.json")


def _seed():
    return {
        "despesas": {k: [c, s] for k, (c, s) in _SEED_DESP.items()},
        "receitas": dict(_SEED_REC),
    }


def load():
    if not os.path.exists(_FILE):
        save(_seed())
    try:
        with open(_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("despesas", {})
        data.setdefault("receitas", {})
        return data
    except Exception:
        d = _seed()
        save(d)
        return d


def save(data):
    try:
        os.makedirs(_DIR, exist_ok=True)
        with open(_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_maps():
    """Retorna (CATEGORIAS, RECEITAS) no formato usado pelo parser."""
    d = load()
    despesas = {k: (v[0], v[1]) for k, v in d["despesas"].items()}
    receitas = dict(d["receitas"])
    return despesas, receitas
