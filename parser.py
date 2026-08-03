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


def _num(bruto):
    limpo = bruto.rstrip(".,").replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


# "5x de 370" / "em 5 vezes de 370"  → 370 é o valor de CADA parcela
_PARC_DE = re.compile(r"(?:em\s+)?(\d{1,2})\s*(?:x|vezes)\s+de\s+r?\$?\s*([\d.,]+)", re.I)
# "5x" / "em 5 vezes" (sem "de")  → o outro número do texto é o TOTAL
_PARC_X = re.compile(r"(?:em\s+)?(\d{1,2})\s*(?:x|vezes)\b", re.I)


def _parcela(t):
    """Detecta parcelamento. Retorna (n, valor_parcela_ou_None, texto_sem_parcela)."""
    m = _PARC_DE.search(t)
    if m:
        n = int(m.group(1))
        return n, _num(m.group(2)), (t[:m.start()] + " " + t[m.end():])
    m = _PARC_X.search(t)
    if m:
        n = int(m.group(1))
        return n, None, (t[:m.start()] + " " + t[m.end():])
    return 1, None, t


def parse(texto):
    CATEGORIAS, RECEITAS = get_maps()
    t = texto.lower().strip()

    # Parcelamento? "5x de 370" (valor por parcela) ou "370 5x" (valor total ÷ n)
    parcelas, valor_parc, t_sem = _parcela(t)
    if parcelas > 1 and valor_parc is not None:
        valor = valor_parc                       # valor de cada parcela, informado direto
    elif parcelas > 1:
        achou = _valor(t_sem)                     # total nos outros números → divide
        if not achou:
            return None
        valor = round(achou[0] / parcelas, 2)
    else:
        achou = _valor(t)
        if not achou:
            return None
        valor = achou[0]

    # Descrição = texto sem número, sem R$/$, sem "Nx/vezes", sem ligação e sem pontuação.
    descricao = re.sub(r"\d[\d.,]*", "", texto)
    descricao = re.sub(r"r\$|\$", "", descricao, flags=re.I)
    descricao = re.sub(r"\bparcelad[oa]s?\b|\bvezes\b|\bx\b", " ", descricao, flags=re.I)
    descricao = re.sub(r"\b(por|reais|real|no|na|de|em|um|uma)\b", "", descricao, flags=re.I)
    descricao = re.sub(r"[,;:.!?]+", " ", descricao)
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
                "parcelas": parcelas,
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
        "parcelas": parcelas,
    }
