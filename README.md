# Alpha-Gen Investimentos — v2.1

Plugin de análise e consultoria de investimentos pessoal baseado no framework Alpha-Gen v7.0, filosofia Howard Marks / Oaktree Capital.

**Novidade da v2.0:** coleta de dados em batch via script Python (4 fontes estritas, cache 24h, fail-loud). Reduz drasticamente o consumo de tokens em relação à v1.0 (que fazia busca livre via WebSearch/web_fetch).

## Skills Disponíveis

### `/analise-aporte`
Análise completa para decisão de aporte mensal. Coleta toda a base de dados via `scripts/coletar_dados.py` no início e gera relatório HTML em `historico/`.

**Uso:** Informe o valor disponível para aporte + envie os arquivos "Minha Carteira" e "Carteira Finclass".

### `/analise-rapida`
Análise pontual de um ativo ou pergunta específica. Usa o mesmo script (com cache compartilhado).

**Uso:** Faça a pergunta diretamente. Ex: "Vale aumentar posição em PRIO3?" ou "Qual o score atual de TRXF11?"

### `/atualizar-ciclo`
Atualiza o Checklist de Ciclo (multiplicadores ARCA). Coleta dados macro via `--macro` no script.

**Uso:** Execute periodicamente (recomendado: a cada 3 meses ou após evento macro relevante).

---

## Arquitetura de Coleta de Dados

### As 4 Fontes Estritas (whitelist)

| Tipo | Fonte única |
|---|---|
| Macro Brasil (Selic, IPCA, Focus, USD/BRL) | `bcb.gov.br` (API SGS/Olinda) |
| Macro internacional (Treasuries, VIX, WTI, Brent, ouro, DXY) | `finance.yahoo.com` (via `yfinance`) |
| Ações + FIIs brasileiros | `statusinvest.com.br` |
| Criptomoedas | `coinmarketcap.com` |

**Nenhuma outra fonte é consultada.** Sem WebSearch, sem Fundamentus, sem Investidor10, sem BTG/XP, sem Investing.com. Detalhes em `skills/analise-aporte/references/fontes-dados.md`.

### Script de Coleta

`skills/analise-aporte/scripts/coletar_dados.py` — comando único, três modos:

```bash
# Macro completo (BCB + Yahoo Finance)
python skills/analise-aporte/scripts/coletar_dados.py --macro

# Ações e FIIs em batch
python skills/analise-aporte/scripts/coletar_dados.py --ativos PETR4,HGLG11,VALE3

# Criptomoedas
python skills/analise-aporte/scripts/coletar_dados.py --cripto BTC,ETH,SOL

# Combinado
python skills/analise-aporte/scripts/coletar_dados.py --macro --ativos PETR4,HGLG11 --cripto BTC

# Forçar refresh (ignora cache)
python skills/analise-aporte/scripts/coletar_dados.py --macro --sem-cache
```

Saída: JSON estruturado em stdout. Logs em stderr.

### Cache

- TTL: 24h
- Localização: `historico/cache_dados/`
- Compartilhado entre as 3 skills — mesma sessão não refaz request

### Fail-Loud (regra rígida)

Se o script não conseguir um dado nas 4 fontes, o campo volta `null` e aparece em `_missing` no JSON. A skill **PERGUNTA AO USUÁRIO** o valor manualmente, ou aceita marcar como indisponível (nota 5 + flag ⚠️ na regra do sistema). **Nunca improvisa, nunca busca em outras fontes.**

### Instalação das Dependências

```bash
pip install --break-system-packages -r skills/analise-aporte/scripts/requirements.txt
```

Dependências mínimas: `requests`, `beautifulsoup4`, `lxml`, `yfinance`.

---

## Estrutura de Arquivos

```
alpha-gen-investimentos/
├── skills/
│   ├── analise-aporte/            # Skill principal de aporte mensal
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── coletar_dados.py   # Script único de coleta em batch
│   │   │   └── requirements.txt
│   │   └── references/
│   │       ├── fontes-dados.md             # Whitelist estrita das 4 fontes
│   │       ├── sistema-score-v7.md
│   │       ├── regras-cenarios.md
│   │       ├── html-output.md
│   │       └── melhorias-profissionais.md  # NOVO v2.1 — gaps + propostas
│   ├── analise-rapida/            # Skill de consulta pontual
│   │   └── SKILL.md
│   └── atualizar-ciclo/           # Skill de atualização do checklist macro
│       └── SKILL.md
├── historico/                     # Relatórios + cache de dados
│   ├── AlphaGen_YYYY-MM-DD.html
│   ├── checklist-ciclo.md
│   └── cache_dados/
└── README.md
```

## Perfil do Investidor

- **Meta:** R$1.000.000 por eficiência composta
- **Perfil:** Agressivo de longo prazo
- **Metodologia ARCA:** Ações | FIIs | Caixa/RF | Alternativos (25% cada como referência)
- **Reserva de emergência:** R$6.000 (fora da carteira — nunca aportar)

## Changelog

### v2.1 (esta versão)
- **Cenário C reformulado:** universo agora vem de planilha Excel anexada pelo usuário, não mais "varredura das 4 fontes". Pergunta obrigatória de abertura: anexa Excel ou pula Cenário C
- **Fail-loud reforçado:** pedir dado manualmente virou DEFAULT obrigatório. Marcar como indisponível só com confirmação explícita do usuário
- **Log persistente de dados faltantes** (`historico/_missing_data_log.md`): registra todo gap por sessão para identificar padrões estruturais de falha das fontes
- **Nova referência `melhorias-profissionais.md`:** análise de gaps no score atual frente ao que sell-side, gestoras de FIIs e research de cripto usam, com 25+ propostas categorizadas por prioridade e custo
- Inconsistências removidas: referências a Investidor10/BTG/XP no Cenário C foram eliminadas (haviam sobrado da v1.0)

### v2.0
- Coleta de dados via script Python em batch (consumo de tokens drasticamente menor)
- Whitelist estrita de 4 fontes (BCB, Yahoo Finance, Status Invest, CoinMarketCap)
- Cache 24h em disco compartilhado entre skills
- Fail-loud: campos faltantes geram pergunta ao usuário, sem improviso
- Cenário C ajustado: universo restrito ao que as 4 fontes cobrem
- WebSearch e fontes alternativas explicitamente proibidas

### v1.0
- Versão inicial com framework Alpha-Gen v7.0
- Coleta via WebSearch/web_fetch livre (descontinuada na v2.0)
