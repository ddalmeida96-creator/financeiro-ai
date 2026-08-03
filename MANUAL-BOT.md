# Manual do Bot — Financeiro AI

Guia rápido do que dá pra fazer pelo Telegram.

## Registrar um gasto ou receita (texto livre)

Só mandar a mensagem, sem comando. O bot entende e lança sozinho.

- `Pizza 89` → despesa de R$ 89
- `Mercado 240,50`
- `Salário 6000` → entra como receita
- `Uber 32`

Ele responde com o resumo (tipo, categoria, valor) e o **número** do lançamento, pra você poder apagar depois.

## Registrar por áudio 🎙️

Manda uma mensagem de voz falando o gasto, tipo "pizza oitenta e nove" ou "mercado duzentos e quarenta". O bot transcreve, mostra o que entendeu e lança direto — igual ao texto. Se transcrever errado, é só usar `/apagar`.

## Compra parcelada 💳

Coloque o número de vezes com **`Nx`** ou **`N vezes`** que o bot cria uma parcela por mês (uma agora, as outras nos próximos meses).

- `Tênis Juliana em 5x de 370` → 5 parcelas de R$370 (total R$1.850). O **370 é o valor de cada parcela**.
- `Notebook 2000 5x` → sem o "de", o **2000 é o total** → 5x de R$400.
- `Sofá em 12 vezes de 300` → funciona por extenso também (bom pra áudio).

Cada mês mostra só a parcela daquele mês — igual à fatura do cartão. As parcelas futuras **não** entram no saldo/patrimônio de hoje; entram quando o mês chega. Pra cancelar a compra inteira, use `/apagar` no número da 1ª parcela (apaga todas de uma vez).

## Lista de compras 🛒

Comece a mensagem (texto **ou** áudio) com **"lista de compras"** e o bot põe os itens na lista em vez de lançar como gasto.

- `lista de compras leite, ovos, pão` → adiciona os 3 itens
- `lista de compra café e açúcar` → separa por vírgula ou "e"
- `lista de compras` (sozinho) → o bot **responde com a lista atual**

A lista também aparece na aba **Compras** do dashboard, onde dá pra marcar e apagar.

## Comandos

| Comando | O que faz |
|---|---|
| `/ultimos` | Mostra os 8 últimos lançamentos com seus números. |
| `/apagar <nº>` | Apaga um lançamento. Ex.: `/apagar 12` |
| `/fixas` | Lista as contas e receitas fixas do mês: pendentes e já lançadas. |
| `/pagar <nº>` | Marca uma fixa como paga/recebida (cria o lançamento do mês). Ex.: `/pagar 3` |
| `/cofrinho` | Mostra os cofrinhos com saldo + resumo de patrimônio (conta, cofrinhos, bens, total). |
| `/aportar <nº> <valor>` | Faz um aporte num cofrinho. Ex.: `/aportar 1 500` |
| `/lista` | Mostra a lista de compras atual. |
| `/comprei <nº>` | Marca um item da lista como comprado. Ex.: `/comprei 3` |
| `/limpar` | Remove da lista os itens já comprados. |

## Dicas

- O **número** que aparece nas respostas é o que você usa nos comandos (`/apagar`, `/pagar`, `/aportar`).
- Valor com vírgula funciona: `240,50` ou `240.50`.
- `/pagar` é seguro: se a fixa já foi lançada no mês, ele avisa e não duplica.
- Um aporte pelo bot entra também como despesa do mês (igual ao dashboard).
