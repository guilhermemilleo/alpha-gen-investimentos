# Alpha-Gen Investimentos — v3.0

Plugin de análise e consultoria de investimentos pessoal baseado no framework Alpha-Gen v7.0, filosofia Howard Marks / Oaktree Capital.

**Novidade da v3.0:** o plugin passou a ter uma única skill — `analise-aporte` — e toda a coleta de dados é feita através da skill `firecrawl`, com Investidor10 (ações/FIIs) e CoinMarketCap (cripto) como fontes preferenciais, BCB e Yahoo Finance para dados macro, e busca livre do firecrawl como fallback antes de perguntar ao usuário. O script Python de scraping e o cache em disco da v2.x foram removidos.

## Skill Disponível

### `/analise-aporte`
Análise completa para decisão de aporte mensal — inclui também a atualização do Checklist de Ciclo (multiplicadores de convicção ARCA), que antes era uma skill separada.

**Uso:** Informe o valor disponível para aporte + envie os arquivos "Minha Carteira" e "Carteira Finclass". Também pode ser acionada só para revisar os multiplicadores de ciclo, dizendo por exemplo "atualizar ciclo" ou "revisar multiplicadores".

---

## Arquitetura de Coleta de Dados

### Pré-requisito: skill `firecrawl`

A skill `analise-aporte` depende da skill `firecrawl` para toda a coleta de dados. Antes de qualquer busca, ela verifica se o `firecrawl` está instalado no ambiente; se não estiver, para a execução e instrui a instalação antes de continuar.

### Fontes Preferenciais

| Tipo | Fonte preferencial |
|---|---|
| Ações e FIIs brasileiros | `investidor10.com.br` |
| Criptomoedas | `coinmarketcap.com` |
| Macro Brasil (Selic, IPCA, Focus, USD/BRL) | `bcb.gov.br` |
| Macro internacional (Treasuries, VIX, WTI, Brent, ouro, DXY) | `finance.yahoo.com` |

### Ordem de Tentativas por Dado

1. Buscar/raspar a fonte preferencial via firecrawl
2. Se não encontrar: firecrawl faz busca livre na internet
3. Se ainda assim não encontrar: perguntar ao usuário (fail-loud)

Detalhes em `skills/analise-aporte/references/fontes-dados.md`.

### Fail-Loud (regra rígida, mantida da v2.x)

Se nem a fonte preferencial nem a busca livre do firecrawl encontrarem um dado, a skill **PERGUNTA AO USUÁRIO** o valor manualmente, ou aceita marcar como indisponível (nota 5 + flag ⚠️ na regra do sistema). **Nunca estima, nunca chuta.**

---

## Estrutura de Arquivos

```
alpha-gen-investimentos/
├── skills/
│   └── analise-aporte/            # Única skill do plugin
│       ├── SKILL.md
│       └── references/
│           ├── fontes-dados.md             # Fontes preferenciais + regra de fallback via firecrawl
│           ├── sistema-score-v7.md
│           ├── regras-cenarios.md
│           ├── html-output.md
│           └── melhorias-profissionais.md  # Gaps + propostas para revisão do usuário
├── historico/                     # Relatórios gerados
│   ├── AlphaGen_YYYY-MM-DD.html
│   └── checklist-ciclo.md
└── README.md
```

## Perfil do Investidor

- **Meta:** R$1.000.000 por eficiência composta
- **Perfil:** Agressivo de longo prazo
- **Metodologia ARCA:** Ações | FIIs | Caixa/RF | Alternativos (25% cada como referência)
- **Reserva de emergência:** R$6.000 (fora da carteira — nunca aportar)

## Changelog

### v3.0 (esta versão)
- **Skill única:** `analise-rapida` e `atualizar-ciclo` foram removidas; a lógica de checklist de ciclo foi absorvida como etapa interna de `analise-aporte`
- **Coleta via Firecrawl:** o script Python `coletar_dados.py` e o cache em disco de 24h foram removidos. Toda coleta agora é feita pela skill `firecrawl`
- **Fontes preferenciais atualizadas:** Investidor10 substitui Status Invest para ações/FIIs; CoinMarketCap continua para cripto; BCB e Yahoo Finance continuam para macro
- **Fallback de busca livre:** se a fonte preferencial não tiver o dado, o firecrawl busca livremente na internet antes de perguntar ao usuário (fail-loud continua sendo o último recurso)
- **Gate de instalação:** a skill verifica se o `firecrawl` está disponível antes de iniciar qualquer coleta e instrui a instalação caso não esteja

### v2.1
- Cenário C reformulado: universo vindo de planilha Excel anexada pelo usuário
- Fail-loud reforçado: pedir dado manualmente virou default obrigatório
- Log persistente de dados faltantes (`historico/_missing_data_log.md`)
- Nova referência `melhorias-profissionais.md`

### v2.0
- Coleta de dados via script Python em batch (consumo de tokens drasticamente menor)
- Whitelist estrita de 4 fontes (BCB, Yahoo Finance, Status Invest, CoinMarketCap)
- Cache 24h em disco compartilhado entre skills
- Fail-loud: campos faltantes geram pergunta ao usuário, sem improviso

### v1.0
- Versão inicial com framework Alpha-Gen v7.0
- Coleta via WebSearch/web_fetch livre (descontinuada na v2.0)
