# 💜 Financeiro do Casal

Controle de receitas e despesas pelo Telegram. Você manda uma mensagem tipo `Pizza 89`, o bot classifica e salva. O dashboard mostra tudo.

## 1. Instalar Python 3.12 (macOS)

```bash
brew install python@3.12
```

## 2. Instalar o uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Feche e reabra o terminal depois.

## 3. Criar o Bot do Telegram

1. No Telegram, procure por **@BotFather**.
2. Envie `/newbot` e siga as instruções (nome + username).
3. Ele te dará um **token** (algo como `123456:ABC-DEF...`). Guarde.
4. Abra uma conversa com o seu bot e envie qualquer mensagem para ativá-lo.

## 4. Configurar o .env

```bash
cp .env.example .env
```

Edite o `.env` e cole seu token:

```
TELEGRAM_TOKEN=123456:ABC-DEF...
```

## 5. Instalar dependências

```bash
uv venv
uv pip install -r requirements.txt
```

## 6. Executar

```bash
uv run main.py
```

Isso liga o bot **e** o dashboard ao mesmo tempo.

## 7. Abrir o Dashboard

Acesse no navegador: **http://localhost:8000**

## 8. Testar

No Telegram, envie ao seu bot:

```
Pizza 89
```

Resposta esperada:

```
✅ Lançamento registrado
Tipo: Despesa
Descrição: Pizza
Categoria: Alimentação
Subcategoria: Fast Food
Valor: R$ 89,00
```

Depois envie:

```
Recebi salário 15000
```

Recarregue o dashboard e veja receita, despesa e saldo atualizados.

## Adicionar categorias

Edite `categorias.py` e adicione uma linha no dicionário. Exemplo:

```python
"spotify": ("Lazer", "Streaming"),
```

## Estrutura

```
financeiro-ai/
├── main.py          # liga bot + dashboard
├── bot.py           # trata mensagens do Telegram
├── database.py      # SQLite + tabela Lancamentos
├── categorias.py    # dicionário de categorias
├── parser.py        # extrai tipo, descrição e valor
├── dashboard.py     # rotas e consultas do painel
├── templates/       # dashboard.html
├── static/          # style.css
├── requirements.txt
├── .env.example
└── financeiro.db    # criado automaticamente
```

Uso pessoal, só para o casal. Sem login, sem nuvem, sem complicação.
