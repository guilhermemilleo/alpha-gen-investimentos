# Design — Consolidação em Skill Única + Coleta via Firecrawl

Data: 2026-08-09

## Contexto

O plugin `alpha-gen-investimentos` (v2.1.0) hoje tem 3 skills (`analise-aporte`,
`analise-rapida`, `atualizar-ciclo`) e coleta dados via um script Python
(`skills/analise-aporte/scripts/coletar_dados.py`) que faz scraping direto de
4 fontes fixas (Status Invest, CoinMarketCap, BCB, Yahoo Finance), com cache
de 24h em disco (`historico/cache_dados/`).

O usuário quer:
1. Apenas 1 skill: análise completa de aporte.
2. Toda a coleta de dados feita via a skill `firecrawl` (instalável
   separadamente). Se não estiver instalada no momento de uso, a skill deve
   parar e instruir a instalação antes de prosseguir.
3. Fonte preferencial: Investidor10 para ações/FIIs, CoinMarketCap para
   cripto. Se não encontrar nesses sites (nem no fallback de macro), o
   Firecrawl pode buscar livremente na internet.

## Decisões (confirmadas com o usuário)

- A lógica de "Checklist de Ciclo" (multiplicadores de convicção ARCA), hoje
  em `atualizar-ciclo/SKILL.md`, é absorvida como etapa interna da skill
  única — tanto no fluxo padrão de aporte quanto acionável isoladamente
  pelas mesmas frases-gatilho de antes ("atualizar ciclo", "revisar
  multiplicadores" etc.), agora cobertas pela description da skill única.
- Dados macro (Selic, IPCA, Focus, Treasury, VIX, WTI, Brent, ouro, DXY)
  mantêm BCB e Yahoo Finance como fonte preferencial (via firecrawl), com o
  mesmo fallback de busca livre.
- O script Python e o cache em disco são removidos por completo. Não há mais
  camada de cache — cada coleta é feita via firecrawl no momento do uso.
- "Firecrawl instalada" = a skill/plugin `firecrawl` aparece na listagem de
  skills disponíveis do ambiente atual. Se não aparecer, a skill para e
  instrui o usuário a instalar antes de prosseguir (não tenta rodar
  onboarding sozinha).
- Ordem de fallback por dado: fonte preferencial (via firecrawl) → busca
  livre do firecrawl → só então pergunta ao usuário (fail-loud). Nunca
  estima/chuta.

## Arquitetura

### Skills

- Remove `skills/analise-rapida/` e `skills/atualizar-ciclo/` inteiras.
- Única skill remanescente: `skills/analise-aporte/`.
- `description` do `SKILL.md` único passa a cobrir as frases-gatilho das 3
  skills antigas (análise de aporte, consulta pontual de ativo, atualização
  de ciclo).

### Coleta de dados

Remove `skills/analise-aporte/scripts/` (`coletar_dados.py`,
`requirements.txt`) e a pasta duplicada `scripts/` na raiz do plugin. Toda
coleta passa a ser uma chamada à skill `firecrawl` dentro das instruções da
skill principal.

**Etapa 0 — Gate de instalação do Firecrawl (nova, obrigatória):**
1. Verificar se a skill `firecrawl` está disponível no ambiente.
2. Se não estiver: parar e instruir a instalação antes de prosseguir.
3. Se estiver: seguir normalmente.

**Fluxo de coleta por tipo de dado:**

| Tipo | 1ª tentativa | 2ª tentativa | 3ª tentativa |
|---|---|---|---|
| Ações e FIIs BR | `investidor10.com.br` via firecrawl | Busca livre via firecrawl | Perguntar ao usuário |
| Criptomoedas | `coinmarketcap.com` via firecrawl | Busca livre via firecrawl | Perguntar ao usuário |
| Macro Brasil | `bcb.gov.br` via firecrawl | Busca livre via firecrawl | Perguntar ao usuário |
| Macro internacional | `finance.yahoo.com` via firecrawl | Busca livre via firecrawl | Perguntar ao usuário |

Regra fail-loud mantida (pergunta explícita ao usuário, nunca estima), mas
agora só dispara depois que a fonte preferencial **e** a busca livre do
firecrawl falharem. O log `historico/_missing_data_log.md` continua sendo
mantido, registrando em qual estágio o dado faltou.

### Arquivos afetados

**Removidos:**
- `skills/analise-rapida/`
- `skills/atualizar-ciclo/`
- `skills/analise-aporte/scripts/`
- `scripts/` (raiz)

**Mantidos sem alteração de conteúdo:**
- `skills/analise-aporte/references/html-output.md`
- `skills/analise-aporte/references/sistema-score-v7.md`
- `historico/` (incluindo `cache_dados/*.json` antigos, que ficam órfãos mas
  não são apagados nesta mudança)

**Reescritos:**
- `skills/analise-aporte/SKILL.md`
- `skills/analise-aporte/references/fontes-dados.md`
- `skills/analise-aporte/references/regras-cenarios.md` (remove menções a
  `coletar_dados.py` / Status Invest)
- `skills/analise-aporte/references/melhorias-profissionais.md` (ajuste de
  terminologia: script/parser/Status Invest → firecrawl/Investidor10)
- `.claude-plugin/plugin.json` (bump para 3.0.0 — quebra de arquitetura)
- `README.md`

## Fora de escopo

- Não há mudança nas fórmulas de score, regras dos 3 cenários (A/B/C), nem
  no template HTML de saída — apenas na camada de coleta de dados e na
  estrutura de skills.
- Não apaga o histórico de relatórios/cache existente em `historico/`.
