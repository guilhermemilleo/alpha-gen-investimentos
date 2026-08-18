# Fontes de Dados — Alpha-Gen (v3.0 — Coleta via Firecrawl)

> **Regra de ouro:** toda coleta de dados passa pela skill `firecrawl`. Nunca usar `WebSearch` nativo do Claude, nunca fazer scraping manual fora do firecrawl.

---

## Ordem de Tentativas (obrigatória para todo dado)

| Ordem | Ação |
|---|---|
| 1ª | Buscar/raspar a **fonte preferencial** (tabela abaixo) via firecrawl |
| 2ª | Se não encontrar: firecrawl faz **busca livre** na internet |
| 3ª | Se ainda assim não encontrar: **perguntar ao usuário** (fail-loud) |

Nunca pular a 1ª tentativa. Nunca perguntar ao usuário sem esgotar as duas primeiras.

---

## Fontes Preferenciais por Tipo de Dado

| # | Tipo | Fonte preferencial | Domínio |
|---|------|---------------------|---------|
| 1 | Ações e FIIs brasileiros | Investidor10 | `investidor10.com.br` |
| 2 | Criptomoedas | CoinMarketCap | `coinmarketcap.com` |
| 3 | Macro Brasil (Selic, IPCA, Focus, USD/BRL) | Banco Central do Brasil | `bcb.gov.br` |
| 4 | Macro internacional (Treasuries, VIX, WTI, Brent, ouro, DXY) | Yahoo Finance | `finance.yahoo.com` |

Se a fonte preferencial não tiver o dado (página não traz o campo, ativo não listado, etc.), o firecrawl tenta busca livre na internet antes de qualquer pergunta ao usuário.

---

## Mapa Campo → Fonte Preferencial

### Macro Brasil — bcb.gov.br

| Campo | Onde buscar |
|-------|-------------|
| Selic meta (atual) | Série SGS 432 (API BCB) |
| IPCA mensal (últimos 12) | Série SGS 433 (API BCB) |
| USD/BRL PTAX venda | Série SGS 1 (API BCB) |
| Relatório Focus (medianas anuais: IPCA, PIB, Selic) | Olinda — Expectativas de Mercado Anuais (API BCB) |

### Macro Internacional — finance.yahoo.com

| Campo | Ticker Yahoo Finance |
|-------|-----------------------|
| Treasury 10Y EUA | `^TNX` |
| VIX | `^VIX` |
| WTI Crude Oil | `CL=F` |
| Brent Oil | `BZ=F` |
| Ouro | `GC=F` |
| DXY (Dollar Index) | `DX-Y.NYB` |
| USD/BRL (cross-check) | `USDBRL=X` |

### Ações Brasileiras — Investidor10

URL padrão: `https://investidor10.com.br/acoes/[ticker-em-minusculas]/`

Campos: Preço atual, P/L, P/VP, Dividend Yield, ROE, ROIC, Dív. líquida/EBITDA, Margem Líquida, LPA, VPA, Liquidez média diária.

### FIIs — Investidor10

URL padrão: `https://investidor10.com.br/fiis/[ticker-em-minusculas]/`

Campos: Preço atual, P/VP, Dividend Yield, Últ. Rendimento, Vacância, Liq. méd. diária, Val. patrim. p/cota, Nº de Cotistas.

**Limitação conhecida:** o Investidor10 não traz de forma padronizada WAULT, cap rate detalhado, rating de CRIs, concentração de inquilino, indexação dos CRIs. Para esses campos: tentar busca livre via firecrawl (ex: relatório gerencial do fundo) antes do fail-loud.

### Criptomoedas — CoinMarketCap

URL padrão: `https://coinmarketcap.com/currencies/[slug]/` (ex: `bitcoin`, `ethereum`, `solana`)

Campos: Preço USD, variação 24h/7d/30d, Market Cap, Volume 24h, ATH, Fear & Greed Index.

---

## Quando um Campo Está Faltante (fail-loud — regra rígida)

🚨 **Pedir manualmente é OBRIGATÓRIO, não opcional.** Marcar como indisponível só é aceito se o usuário **explicitamente** disser "marca como indisponível" depois de ser perguntado.

1. Tentativa 1 (fonte preferencial via firecrawl): falhou.
2. Tentativa 2 (busca livre via firecrawl): falhou.
3. **Perguntar ao usuário**, exatamente neste formato:

   > "🔍 Dado faltante: não encontrei [CAMPO] de [TICKER/INDICADOR] nem na fonte preferencial nem em busca livre via firecrawl. Pode me informar o valor manualmente para eu prosseguir? (Se preferir marcar como indisponível, me avise — anoto nota 5 + ⚠️ para o fator afetado.)"

4. **Aguardar resposta antes de continuar.** Nunca improvisar, nunca chutar.
5. **Registrar a falha em `./historico/_missing_data_log.md`** (pasta atual), incluindo em qual tentativa o dado faltou (formato em `skills/analise-aporte/SKILL.md`).

---

## Dados que NÃO Precisam de Busca em Tempo Real

- Pesos ARCA (25% cada — definido no sistema)
- Fórmulas de score (`sistema-score-v7.md`)
- Multiplicadores de ciclo (sempre lidos de `./historico/checklist-ciclo.md`, na pasta atual)
- Perfil do investidor (definido no README do plugin)
