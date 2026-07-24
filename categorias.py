# Palavra-chave -> (Categoria, Subcategoria) para DESPESAS.
# Adicionar novas categorias = adicionar uma linha aqui.
CATEGORIAS = {
    # Alimentação - Fast Food
    "pizza": ("Alimentação", "Fast Food"),
    "mcdonalds": ("Alimentação", "Fast Food"),
    "mc donalds": ("Alimentação", "Fast Food"),
    "burger": ("Alimentação", "Fast Food"),
    "outback": ("Alimentação", "Fast Food"),
    "habibs": ("Alimentação", "Fast Food"),
    "hut": ("Alimentação", "Fast Food"),
    "lanche": ("Alimentação", "Fast Food"),
    # Alimentação - Supermercado
    "mercado": ("Alimentação", "Supermercado"),
    "condor": ("Alimentação", "Supermercado"),
    "muffato": ("Alimentação", "Supermercado"),
    "festval": ("Alimentação", "Supermercado"),
    "carrefour": ("Alimentação", "Supermercado"),
    "atacadao": ("Alimentação", "Supermercado"),
    # Vestuário - Calçados
    "nike": ("Vestuário", "Calçados"),
    "adidas": ("Vestuário", "Calçados"),
    "centauro": ("Vestuário", "Calçados"),
    # Transporte - Combustível
    "shell": ("Transporte", "Combustível"),
    "posto": ("Transporte", "Combustível"),
    "ipiranga": ("Transporte", "Combustível"),
    "abasteci": ("Transporte", "Combustível"),
    "gasolina": ("Transporte", "Combustível"),
    # Transporte - Aplicativos
    "uber": ("Transporte", "Aplicativos"),
    "99": ("Transporte", "Aplicativos"),
    # Saúde
    "farmacia": ("Saúde", "Farmácia"),
    "farmácia": ("Saúde", "Farmácia"),
    "panvel": ("Saúde", "Farmácia"),
    "droga raia": ("Saúde", "Farmácia"),
    "drogaria": ("Saúde", "Farmácia"),
    # Lazer
    "cinema": ("Lazer", "Cinema"),
    "netflix": ("Lazer", "Streaming"),
    "spotify": ("Lazer", "Streaming"),
}

# Palavra-chave -> Subcategoria para RECEITAS.
# Se qualquer uma aparecer na frase, Tipo = Receita.
RECEITAS = {
    "salario": "Salário",
    "salário": "Salário",
    "comissao": "Comissão",
    "comissão": "Comissão",
    "bonus": "Bônus",
    "bônus": "Bônus",
    "pix recebido": "PIX",
    "recebi pix": "PIX",
    "cliente pagou": "Cliente",
    "pagamento recebido": "Pagamento",
    "dividendos": "Dividendos",
    "cashback": "Cashback",
    "rendimento": "Rendimento",
    "reembolso": "Reembolso",
    "estorno": "Estorno",
    "venda": "Venda",
    "aluguel recebido": "Aluguel",
    "recebi": "Outros",
}
