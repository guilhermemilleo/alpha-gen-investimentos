# Fontes de Dados — Alpha-Gen (v2.0 — Whitelist Estrita)

> **Regra de ouro:** apenas as 4 fontes desta página podem ser consultadas. Qualquer dado que não estiver disponível nelas → **parar e perguntar ao usuário**. Não navegar em outros sites, não usar WebSearch, não improvisar.

---

## As 4 Fontes Permitidas

| # | Fonte | Domínio único | Uso |
|---|-------|---------------|-----|
| 1 | **Status Invest** | `statusinvest.com.br` | Ações e FIIs brasileiros (todos os dados) |
| 2 | **CoinMarketCap** | `coinmarketcap.com` | Criptomoedas (todos os dados) |
| 3 | **Banco Central do Brasil** | `bcb.gov.br` (API SGS/Olinda) | Macro Brasil (Selic, IPCA, Focus, USD/BRL) |
| 4 | **Yahoo Finance** | `finance.yahoo.com` (via lib `yfinance`) | Macro EUA/internacional (Treasuries, VIX, WTI, Brent, ouro, DXY) |

**Importante:** as 4 são acessadas pelo script `scripts/coletar_dados.py` em batch. NÃO buscar diretamente via web_fetch a menos que o script falhe — e ainda assim apenas as URLs exatas mapeadas nesta página.

---

## Mapa Campo → Fonte → URL Exata

### Macro Brasil — bcb.gov.br (API SGS, retorna JSON)

| Campo | Endpoint |
|-------|----------|
| Selic meta (atual) | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json` |
| IPCA mensal (últimos 12) | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/12?formato=json` |
| USD/BRL PTAX venda | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json` |
| Relatório Focus (medianas anuais) | `https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais?$top=20&$orderby=Data%20desc&$format=json` |

### Macro Internacional — Yahoo Finance (via lib `yfinance`)

| Campo | Ticker yfinance |
|-------|-----------------|
| Treasury 10Y EUA | `^TNX` |
| VIX | `^VIX` |
| WTI Crude Oil | `CL=F` |
| Brent Oil | `BZ=F` |
| Ouro | `GC=F` |
| DXY (Dollar Index) | `DX-Y.NYB` |
| USD/BRL (cross-check) | `USDBRL=X` |

### Ações Brasileiras — Status Invest

URL única: `https://statusinvest.com.br/acoes/[ticker-em-minusculas]`

Campos extraídos: Preço atual, P/L, P/VP, Dividend Yield, ROE, ROIC, Dív. líquida/EBITDA, M. Líquida, LPA, VPA, Liquidez média diária.

### FIIs — Status Invest

URL única: `https://statusinvest.com.br/fundos-imobiliarios/[ticker-em-minusculas]`

Campos extraídos: Preço atual, P/VP, Dividend Yield, Últ. Rendimento, Vacância, Liq. méd. diária, Val. patrim. p/cota, Nº de Cotistas.

**Limitação conhecida do Status Invest para FIIs:** não traz WAULT, cap rate detalhado, rating de CRIs, concentração de inquilino, indexação dos CRIs. Esses sub-fatores ficam sob a regra de **dado indisponível**: o script marca em `_missing`, a skill pergunta ao usuário (ou aceita marcar como indisponível → nota 5 + flag ⚠️, conforme `sistema-score-v7.md` Seção 02-R).

### Criptomoedas — CoinMarketCap

URL única: `https://coinmarketcap.com/currencies/[slug]/` (ex: `bitcoin`, `ethereum`, `solana`)

Campos extraídos: Preço USD, variação 24h/7d/30d, Market Cap, Volume 24h, ATH, Fear & Greed Index.

---

## Regras de Comportamento da Coleta

### O QUE FAZER

1. Sempre chamar `scripts/coletar_dados.py` PRIMEIRO. Ele cuida das 4 fontes em batch e devolve JSON estruturado.
2. Cache de 24h ativo por padrão (`historico/cache_dados/`). Dado fresco não refaz request.
3. Se um campo voltar `null` no JSON, ele estará listado no array `_missing` — tratar conforme regra de dado indisponível.

### O QUE NÃO FAZER

- ❌ **PROIBIDO** usar `WebSearch` em qualquer etapa de coleta de dados.
- ❌ **PROIBIDO** consultar Fundamentus, Investidor10, Investing.com, BTG, XP, TradingView, Suno, Empiricus, Reuters, Bloomberg, ou qualquer outro site não listado nesta página.
- ❌ **PROIBIDO** "tentar uma fonte alternativa" se a fonte primária falhar. A regra é binária: a fonte mapeada acima ou nada.
- ❌ **PROIBIDO** estimar valores faltantes ("aproximadamente 12%", "média do setor", "vou usar valor de referência").
- ❌ **PROIBIDO** chamar `web_fetch` para domínios fora da whitelist.

### Quando um Campo Está Faltante (regra única — REFORÇADA v2.1)

🚨 **Default na v2.1: pedir manualmente é OBRIGATÓRIO.** Marcar como indisponível só vale se o usuário pedir explicitamente após ser perguntado.

1. O script já tentou nas fontes desta página. Falhou.
2. **Perguntar ao usuário** explicitamente, exatamente neste formato:

   > "🔍 Dado faltante: não encontrei [CAMPO] de [TICKER/INDICADOR] no [FONTE]. Pode me informar o valor manualmente para eu prosseguir? (Se preferir marcar como indisponível, me avise — anoto nota 5 + ⚠️ para o fator afetado.)"

3. **Aguardar resposta antes de continuar.** Nunca improvisar, nunca buscar em outra fonte, nunca chutar.
4. **Registrar a falha em `historico/_missing_data_log.md`** (formato em `skills/analise-aporte/SKILL.md`). Isso permite identificar campos que falham repetidamente e melhorar o plugin no futuro.

### Cache

- TTL padrão: 24h
- Localização: `historico/cache_dados/`
- Para forçar refresh: passar flag `--sem-cache` ao script
- Macro: refresh recomendado a cada análise (mas cache de 24h aceito)
- Ativos: cache de 24h aceito (preço pode variar intra-dia, mas fundamentais não mudam)

---

## Dados que NÃO precisam de busca em tempo real

- Pesos ARCA (25% cada — definido no sistema)
- Fórmulas de score (`sistema-score-v7.md`)
- Multiplicadores de ciclo (sempre lidos de `historico/checklist-ciclo.md`)
- Perfil do investidor (definido no README do plugin)
