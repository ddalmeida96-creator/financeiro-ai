# Manual do Bot — Financeiro AI

Guia rápido do que dá pra fazer pelo Telegram.

## Registrar um gasto ou receita (texto livre)

Só mandar a mensagem, sem comando. O bot entende e lança sozinho.

- `Pizza 89` → despesa de R$ 89
- `Mercado 240,50`
- `Salário 6000` → entra como receita
- `Uber 32`

Ele responde com o resumo (tipo, categoria, valor) e o **número** do lançamento, pra você poder apagar depois.

## Comandos

| Comando | O que faz |
|---|---|
| `/ultimos` | Mostra os 8 últimos lançamentos com seus números. |
| `/apagar <nº>` | Apaga um lançamento. Ex.: `/apagar 12` |
| `/fixas` | Lista as contas e receitas fixas do mês: pendentes e já lançadas. |
| `/pagar <nº>` | Marca uma fixa como paga/recebida (cria o lançamento do mês). Ex.: `/pagar 3` |
| `/cofrinho` | Mostra os cofrinhos com saldo + resumo de patrimônio (conta, cofrinhos, bens, total). |
| `/aportar <nº> <valor>` | Faz um aporte num cofrinho. Ex.: `/aportar 1 500` |

## Dicas

- O **número** que aparece nas respostas é o que você usa nos comandos (`/apagar`, `/pagar`, `/aportar`).
- Valor com vírgula funciona: `240,50` ou `240.50`.
- `/pagar` é seguro: se a fixa já foi lançada no mês, ele avisa e não duplica.
- Um aporte pelo bot entra também como despesa do mês (igual ao dashboard).
