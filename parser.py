import re
from catstore import get_maps


def _valor(texto):
    # Pega todos os números (aceita 15.000 / 89,90 / 89). Usa o último.
    nums = re.findall(r"\d[\d.,]*", texto)
    if not nums:
        return None
    bruto = nums[-1].rstrip(".,")
    limpo = bruto.replace(".", "").replace(",", ".")
    try:
        return float(limpo), bruto
    except ValueError:
        return None


def parse(texto):
    CATEGORIAS, RECEITAS = get_maps()
    t = texto.lower().strip()
    achou = _valor(t)
    if not achou:
        return None
    valor, bruto = achou

    # Descrição = texto sem o número final.
    descricao = re.sub(r"\d[\d.,]*", "", texto).strip()
    descricao = re.sub(r"\b(por|reais|r\$|no|na|de|um|uma)\b", "", descricao, flags=re.I)
    descricao = re.sub(r"\s+", " ", descricao).strip().capitalize() or "Lançamento"

    # Receita?
    for chave, sub in RECEITAS.items():
        if chave in t:
            # tenta subcategoria mais específica
            for c2, s2 in RECEITAS.items():
                if s2 != "Outros" and c2 in t:
                    sub = s2
                    break
            return {
                "tipo": "Receita",
                "descricao": descricao,
                "categoria": "Receita",
                "subcategoria": sub,
                "valor": valor,
            }

    # Despesa: procura categoria por palavra-chave.
    categoria, subcategoria = "Outros", "Outros"
    for chave, (cat, sub) in CATEGORIAS.items():
        if chave in t:
            categoria, subcategoria = cat, sub
            break

    return {
        "tipo": "Despesa",
        "descricao": descricao,
        "categoria": categoria,
        "subcategoria": subcategoria,
        "valor": valor,
    }
