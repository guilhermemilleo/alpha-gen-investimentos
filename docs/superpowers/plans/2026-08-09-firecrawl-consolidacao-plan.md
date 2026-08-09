# Consolidação em Skill Única + Coleta via Firecrawl — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduzir o plugin `alpha-gen-investimentos` a uma única skill (`analise-aporte`), removendo o script Python de scraping e substituindo toda a coleta de dados por chamadas à skill `firecrawl`, com Investidor10/CoinMarketCap/BCB/Yahoo Finance como fontes preferenciais e busca livre do firecrawl como fallback antes do fail-loud.

**Architecture:** Este é um plugin de conteúdo/instruções para o Claude Code (skills em Markdown), não uma aplicação com testes automatizados. As "tarefas" são edições de arquivos Markdown/JSON e remoção de arquivos obsoletos; a "verificação" de cada tarefa é feita por inspeção do conteúdo final e por comandos de busca (`grep`) que confirmam a ausência de referências obsoletas e a presença do conteúdo novo, além de validação de JSON onde aplicável.

**Tech Stack:** Markdown (skills e references), JSON (`plugin.json`). Nenhuma dependência de runtime — a skill final não usa Python nem requer instalação de pacotes.

## Global Constraints

- Spec de referência: `docs/superpowers/specs/2026-08-09-firecrawl-consolidacao-design.md`.
- Toda coleta de dados passa a ser feita via a skill `firecrawl` — nunca `WebSearch` nativo, nunca scraping via script.
- Ordem de fallback obrigatória por dado: fonte preferencial via firecrawl → busca livre via firecrawl → perguntar ao usuário (fail-loud). Nunca pular etapas, nunca estimar/chutar.
- Fontes preferenciais: `investidor10.com.br` (ações/FIIs), `coinmarketcap.com` (cripto), `bcb.gov.br` (macro Brasil), `finance.yahoo.com` (macro internacional).
- A skill deve verificar, antes de qualquer coleta, se a skill `firecrawl` está disponível no ambiente; se não estiver, parar e instruir a instalação.
- `skills/analise-aporte/references/html-output.md` e `skills/analise-aporte/references/sistema-score-v7.md` não são alterados neste plano — não têm menções a fontes de dados que precisem mudar.
- `historico/` (relatórios e cache antigo) não é apagado neste plano.
- Não criar cache em disco. Nenhum script Python de **coleta de dados** pode sobrar ou ser recriado. (Exceção explícita: a leitura da planilha Excel do usuário no Cenário C continua podendo usar a skill `xlsx` ou `pandas`/`openpyxl` via Bash — isso é leitura de arquivo local do usuário, não coleta de dados de mercado.)
- Vocabulário morto a eliminar de todo Markdown do plugin: "whitelist", "4 fontes", "Status Invest"/"statusinvest", "coletar_dados.py", "parser", "`_missing`" como retorno de script. Cada task que toca um arquivo é responsável por limpar esses termos nele.

**Fato verificado (2026-08-09):** os padrões de URL do Investidor10 usados neste plano foram confirmados ao vivo — `https://investidor10.com.br/acoes/petr4/` e `https://investidor10.com.br/fiis/hglg11/` respondem e expõem os campos listados na Task 2 (ações: P/L, P/VP, DY, ROE, ROIC, Dív. líq./EBITDA, liquidez média diária; FIIs: P/VP, DY, último rendimento, vacância, liquidez diária, valor patrimonial por cota, nº de cotistas).

---

### Task 1: Remover skills obsoletas e scripts Python

**Files:**
- Delete: `skills/analise-rapida/` (pasta inteira, incluindo `SKILL.md`)
- Delete: `skills/atualizar-ciclo/` (pasta inteira, incluindo `SKILL.md`)
- Delete: `skills/analise-aporte/scripts/` (pasta inteira: `coletar_dados.py`, `requirements.txt`)
- Delete: `scripts/` na raiz do plugin (pasta inteira: `coletar_dados.py`, `requirements.txt` — duplicata da anterior)

**Interfaces:**
- Consumes: nada (é a primeira tarefa, apenas remove arquivos).
- Produces: repositório sem as pastas acima. Tarefas seguintes assumem que essas pastas não existem mais.

- [ ] **Step 1: Remover as pastas**

```bash
git rm -r "skills/analise-rapida" "skills/atualizar-ciclo" "skills/analise-aporte/scripts" "scripts"
```

- [ ] **Step 2: Verificar que as pastas sumiram**

Run: `ls skills/ && ls .`
Expected: `skills/` lista apenas `analise-aporte/`; a raiz do plugin não tem mais pasta `scripts/`.

- [ ] **Step 3: Confirmar que nenhum arquivo Python sobrou no plugin**

Run: `find . -iname "*.py" -not -path "./.git/*"`
Expected: sem saída (nenhum match).

Nota: referências TEXTUAIS a `coletar_dados.py` ainda existem em `SKILL.md`, `README.md`, `regras-cenarios.md`, `melhorias-profissionais.md` neste ponto — elas são removidas nas Tasks 3–7 e verificadas na Task 8. Não tentar limpá-las aqui.

- [ ] **Step 4: Limpar entradas Python obsoletas do `.gitignore`**

O `.gitignore` tem entradas que só faziam sentido com o script Python. Remover estas três linhas:

```
__pycache__/
*.pyc
.pytest_cache/
```

Manter todas as demais linhas do arquivo intactas — inclusive `historico/cache_dados/`, já que os arquivos de cache antigos permanecem no disco e devem continuar ignorados.

- [ ] **Step 5: Verificar o `.gitignore`**

Run: `grep -n "pycache\|pyc\|pytest" .gitignore`
Expected: sem saída (nenhum match) — código de saída 1.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "Remove skills analise-rapida e atualizar-ciclo, e script de scraping Python"
```

---

### Task 2: Reescrever `skills/analise-aporte/references/fontes-dados.md`

**Files:**
- Modify (reescrita completa): `skills/analise-aporte/references/fontes-dados.md`

**Interfaces:**
- Consumes: nada além do design da spec (fontes preferenciais + fallback).
- Produces: documento de referência que `SKILL.md` (Task 3) vai citar como `references/fontes-dados.md`. O nome do arquivo não muda.

- [ ] **Step 1: Substituir todo o conteúdo do arquivo**

Usar Write para substituir o conteúdo inteiro de `skills/analise-aporte/references/fontes-dados.md` por:

```markdown
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
5. **Registrar a falha em `historico/_missing_data_log.md`**, incluindo em qual tentativa o dado faltou (formato em `skills/analise-aporte/SKILL.md`).

---

## Dados que NÃO Precisam de Busca em Tempo Real

- Pesos ARCA (25% cada — definido no sistema)
- Fórmulas de score (`sistema-score-v7.md`)
- Multiplicadores de ciclo (sempre lidos de `historico/checklist-ciclo.md`)
- Perfil do investidor (definido no README do plugin)
```

- [ ] **Step 2: Verificar que não sobrou nenhuma menção às fontes antigas**

Run: `grep -n "Status Invest\|statusinvest\|coletar_dados\|whitelist estrita\|4 fontes" "skills/analise-aporte/references/fontes-dados.md"`
Expected: sem saída (nenhum match) — o comando retorna código de saída 1.

- [ ] **Step 3: Commit**

```bash
git add "skills/analise-aporte/references/fontes-dados.md"
git commit -m "Reescreve fontes-dados.md para coleta via firecrawl (Investidor10/CoinMarketCap/BCB/Yahoo)"
```

---

### Task 3: Reescrever `skills/analise-aporte/SKILL.md`

**Files:**
- Modify (reescrita completa): `skills/analise-aporte/SKILL.md`

**Interfaces:**
- Consumes: `references/fontes-dados.md` (Task 2, já reescrito), `references/regras-cenarios.md` (citado, atualizado na Task 4), `references/sistema-score-v7.md` e `references/html-output.md` (inalterados).
- Produces: a única skill do plugin, com frontmatter `name: analise-aporte` e `description` cobrindo as frases-gatilho de aporte completo e de atualização de ciclo (mas não as de `analise-rapida`, que foi removida sem substituto).

- [ ] **Step 1: Substituir todo o conteúdo do arquivo**

Usar Write para substituir o conteúdo inteiro de `skills/analise-aporte/SKILL.md` por (o bloco abaixo usa cerca de 4 crases porque o conteúdo contém blocos de código aninhados — copiar tudo entre as cercas de 4 crases):

````markdown
---
name: analise-aporte
description: >
  Execute análise completa de investimentos pelo framework Alpha-Gen para decisão de aporte,
  incluindo a atualização do Checklist de Ciclo (multiplicadores de convicção ARCA).
  Acionar quando o usuário disser: "executar alpha-gen", "análise de aporte", "onde aportar",
  "análise mensal", "qual ativo comprar", "fazer análise de investimento", "análise alpha-gen",
  "iniciar sessão alpha-gen", "tenho R$X para aportar", "vou aportar R$X este mês",
  "me recomende ativos", "quais ativos comprar agora", "análise da carteira",
  "atualizar ciclo", "atualizar checklist", "revisar multiplicadores", "update do ciclo",
  "multiplicadores estão corretos?", "revisão de ciclo", "novo checklist",
  "quero revisar os multiplicadores", "ciclo macro mudou", "atualizar análise macro".
---

# Análise de Aporte — Framework Alpha-Gen (v3.0 — Coleta via Firecrawl)

Você é um Senior Equity Research Analyst e Estrategista Macro com filosofia Howard Marks (Oaktree Capital). Comunicação direta, técnica, sem introduções genéricas. Missão: levar o usuário ao patrimônio de R$1.000.000 pelo caminho de maior eficiência composta — priorizando consistência, controle de risco e margem de segurança sobre velocidade bruta.

**Princípio central:** "Não é o que você compra, é o quanto você paga." — Howard Marks

---

## ⚠️ ETAPA 0 — Gate de Instalação do Firecrawl (obrigatória, antes de tudo)

Toda coleta de dados desta skill depende da skill `firecrawl`. Antes de qualquer outra etapa:

1. Verificar se a skill `firecrawl` está disponível no ambiente atual (deve aparecer na listagem de skills carregadas nesta sessão).
2. **Se NÃO estiver disponível:** parar a execução imediatamente e informar ao usuário, literalmente:
   > "Esta skill depende da skill **firecrawl** para toda a coleta de dados, e ela não está instalada neste ambiente. Instale o plugin/skill Firecrawl (marketplace de plugins do Claude Code) e rode a análise novamente."
   Não seguir para nenhuma etapa de coleta enquanto isso não for resolvido.
3. **Se estiver disponível:** prosseguir normalmente para a Etapa 1.

---

## ⚠️ REGRAS ABSOLUTAS DE COLETA DE DADOS — Leia ANTES de qualquer busca

**Toda coleta de dados acontece através da skill `firecrawl`.** Para cada dado necessário, seguir esta ordem de tentativas — nunca pular etapas:

| Ordem | Ação |
|---|---|
| 1ª | Buscar/raspar a fonte preferencial via firecrawl |
| 2ª | Se não encontrar: firecrawl faz busca livre na internet |
| 3ª | Se ainda assim não encontrar: perguntar ao usuário (fail-loud) |

### Fontes Preferenciais

| Tipo | Fonte preferencial |
|---|---|
| Ações e FIIs brasileiros | `investidor10.com.br` |
| Criptomoedas | `coinmarketcap.com` |
| Macro Brasil (Selic, IPCA, Focus, USD/BRL) | `bcb.gov.br` |
| Macro internacional (Treasuries, VIX, WTI, Brent, ouro) | `finance.yahoo.com` |

Detalhes de campos e URLs em `references/fontes-dados.md`.

### O QUE É PROIBIDO

- ❌ **PROIBIDO usar `WebSearch` nativo do Claude em qualquer etapa.** Toda busca — preferencial ou livre — passa pela skill `firecrawl`.
- ❌ **PROIBIDO pular a fonte preferencial** e ir direto para busca livre.
- ❌ **PROIBIDO perguntar ao usuário sem antes esgotar as 2 tentativas via firecrawl** (fonte preferencial + busca livre).
- ❌ **PROIBIDO estimar / chutar / usar "média do setor"** para campos faltantes.

### Quando um Campo Está Faltante (regra fail-loud — REFORÇADA)

🚨 **Pedir manualmente é OBRIGATÓRIO, não opcional.** Marcar como indisponível com nota 5 + ⚠️ só é aceito se o usuário **explicitamente** disser "marca como indisponível" depois de ser perguntado.

Sequência rígida:

1. Buscar a fonte preferencial via firecrawl. Falhou.
2. Firecrawl faz busca livre na internet. Falhou.
3. **PERGUNTAR ao usuário** literalmente neste formato:
   > "🔍 Dado faltante: não encontrei **[CAMPO]** de **[TICKER]** nem na fonte preferencial nem em busca livre via firecrawl. Pode me informar o valor manualmente para eu prosseguir? (Se preferir marcar como indisponível, me avise — anoto nota 5 + ⚠️.)"
4. **Aguardar resposta antes de continuar.** Nunca improvisar, nunca chutar.
5. **Registrar o evento no log de falhas** (ver abaixo) — isso é o que vai permitir identificar padrões e melhorar o plugin.

### Log de Dados Faltantes

Para cada sessão, manter um log persistente em `historico/_missing_data_log.md` com formato:

```markdown
## Sessão YYYY-MM-DD HH:MM

| Ticker | Campo | Estágio que falhou | Resolução |
|--------|-------|---------------------|-----------|
| KNCR11 | WAULT | fonte preferencial + busca livre | manual: 5,8 anos |
| MXRF11 | Rating CRIs | fonte preferencial + busca livre | indisponível (nota 5 + ⚠️) |
| BTC | Fear & Greed | fonte preferencial | manual: 42 |
```

**Por que isso importa:** se o mesmo campo do mesmo ticker falhar em 3+ sessões seguidas, é sinal estrutural — nem a fonte preferencial nem a busca livre cobrem o dado, e o usuário deve decidir entre (a) aceitar o gap como permanente, (b) sempre fornecer aquele campo manualmente, ou (c) ajustar a fonte preferencial daquele tipo de dado.

Anexar o log ao relatório HTML como Seção 4.5 (Diagnóstico de Coleta) quando houver ≥1 entrada na sessão. Se o log mostrar reincidência (mesmo campo + ticker em ≥3 sessões), destacar no relatório com alerta âmbar.

---

## Dados Necessários Antes de Iniciar

Confirme que possui:
1. **Valor do aporte** — perguntar se não informado
2. **Minha Carteira** — arquivo Excel ou tabela (ativos, % na carteira, preço médio, patrimônio total)
3. **Carteira Finclass** — arquivo Excel ou tabela (ativos recomendados, % alvo, preço teto, classe)
4. Verificar `historico/` por arquivo `AlphaGen_*.html` mais recente (histórico da sessão anterior)
5. Verificar `historico/checklist-ciclo.md` (âncora dos multiplicadores)

Se carteira ou Finclass não forem enviados, solicite antes de continuar.

---

## Sequência de Execução — OBRIGATÓRIA

### ETAPA 1 — Coleta de Dados Macro (via firecrawl)

Buscar via firecrawl, seguindo a ordem de tentativas (fonte preferencial → busca livre → fail-loud):

- **Brasil** (fonte preferencial `bcb.gov.br`): Selic meta, IPCA 12m, USD/BRL PTAX, Focus (IPCA proj, PIB proj, Selic proj)
- **Internacional** (fonte preferencial `finance.yahoo.com`): Treasury 10Y, VIX, WTI, Brent, ouro, DXY

Se algum campo essencial (Selic, IPCA, VIX, Treasury) não for encontrado nem na fonte preferencial nem em busca livre → aplicar fail-loud.

### ETAPA 2 — Checklist de Ciclo

**Passo 2.1 — Ler Checklist Anterior**

Verificar `historico/checklist-ciclo.md`:
- **SE EXISTE:** ler multiplicadores anteriores e a data da última atualização
- **SE NÃO EXISTE:** informar ao usuário que será criado o primeiro checklist

**Passo 2.2 — Avaliar Posicionamento de Ciclo por Classe**

Usando os dados macro da Etapa 1, avaliar cada classe ARCA — NUNCA em notícias de curto prazo ou sentimentos semanais:

- **Ações:** Selic + Focus Selic vs. nível histórico de juros; VIX (>30 = stress; <15 = complacência); DXY (forte = pressão sobre emergentes)
- **FIIs:** Selic atual + projeção Focus de Selic (ciclo de juros); spread Selic vs. IPCA implícito; IPCA 12m vs. meta
- **Renda Fixa:** Selic atual vs. trajetória Focus; fase do ciclo Copom (cortes/pico/alta); inclinação inferida da diferença entre Selic atual e projetada
- **Alternativos:** VIX vs. média histórica (~20); WTI/Brent (commodities); ouro vs. ATH; cripto — se relevante, coletar Fear & Greed via firecrawl (fonte preferencial CoinMarketCap)

**Passo 2.3 — Definir Multiplicadores**

Para cada classe, definir o Multiplicador seguindo a escala:

| Multiplicador | Temperatura |
|--------------|-------------|
| 1,3–1,5 | Excepcional — pessimismo extremo, valuations históricos |
| 1,1–1,2 | Favorável — catalisadores confirmados, valuations razoáveis |
| 0,9–1,0 | Neutro — sem excesso de pessimismo ou otimismo |
| 0,7–0,8 | Desfavorável — valuations elevados, otimismo acima do histórico |
| 0,5–0,6 | Adverso Severo — euforia, valuations extremos |

**Regra de Estabilidade:** se o checklist anterior existir, verificar se algum multiplicador mudou mais de 0,2 pontos. Se sim, declarar o evento de ciclo que justifica a mudança. Se não houver evento relevante, manter o multiplicador anterior (máximo variação de 0,2).

**Passo 2.4 — Comparar com Sessão Anterior**

- **SE EXISTE checklist anterior:** comparar com macro desta sessão, aplicar a regra de estabilidade, exibir tabela comparativa no relatório (Seção 3)
- **SE NÃO EXISTE:** gerar novo checklist conforme Seção 11 de `references/sistema-score-v7.md`

**Passo 2.5 — Gerar e Salvar Checklist**

Gerar/atualizar `historico/checklist-ciclo.md` com o formato:

```markdown
# Checklist de Ciclo — Alpha-Gen
Data de geração: [DATA]
Próxima revisão sugerida: [DATA + 3 meses]

## Multiplicadores de Convicção ARCA

| Classe | Multiplicador | Temperatura | Justificativa |
|--------|--------------|-------------|---------------|
| Ações | X,X | [label] | [justificativa baseada em ciclo de longo prazo] |
| FIIs | X,X | [label] | [justificativa] |
| RF/Caixa | X,X | [label] | [justificativa] |
| Alternativos | X,X | [label] | [justificativa] |

## Indicadores Macro Registrados (via firecrawl)

### Brasil (fonte preferencial: bcb.gov.br)
- Selic meta: X,X% a.a.
- IPCA 12m: X,X%
- USD/BRL PTAX: R$ X,XX
- Focus IPCA proj: X,X%
- Focus PIB proj: X,X%
- Focus Selic proj: X,X%

### Internacional (fonte preferencial: finance.yahoo.com)
- Treasury 10Y: X,XX%
- VIX: XX,X
- WTI: USD XX,XX
- Brent: USD XX,XX
- Ouro: USD X.XXX,XX
- DXY: XXX,X

## Comparativo com Sessão Anterior
[Se existia checklist anterior: tabela com multiplicadores anteriores vs. atuais e variações]
[Se não existia: "Primeiro checklist gerado"]

## Eventos de Ciclo Registrados
[Lista de eventos macro relevantes que motivaram mudanças >0,2 desde o último checklist]
```

**Passo 2.6 — Confirmar com o Usuário**

Apresentar o resumo dos multiplicadores definidos e confirmar com o usuário antes de salvar. Se o usuário ajustar algum multiplicador, verificar se a variação vs. checklist anterior é >0,2 e solicitar justificativa do evento de ciclo.

### ETAPA 3 — Diagnóstico da Carteira (busca em batch via firecrawl)

Coletar TODOS os ativos da carteira do usuário via firecrawl, seguindo a ordem de tentativas:
- Ações/FIIs → fonte preferencial `investidor10.com.br`
- Cripto → fonte preferencial `coinmarketcap.com`

Após coletar:
- Para cada ativo: recalcular Score Ajustado Final (Score da Classe × Multiplicador de Convicção)
- Aplicar Semáforo 🟢🟡🔴 conforme Seção 08 de `references/sistema-score-v7.md`
- Calcular desvio de cada classe ARCA vs. 25% alvo
- Verificar gatilhos qualitativos e stops
- Para campos não encontrados (nem fonte preferencial, nem busca livre) → aplicar fail-loud
- Declarar variação de score >1,0 ponto vs. sessão anterior com o fator responsável

### ETAPA 4 — Ranking Completo Finclass

Coletar via firecrawl TODA a Carteira Finclass (mesma ordem de tentativas da Etapa 3).

- Cobertura 100% obrigatória: calcular Score Ajustado Final para TODOS
- Top 10 scores: incluir breakdown completo por fator (A até G conforme a classe)
- Demais ativos: todas as colunas obrigatórias sem breakdown
- Para campos não encontrados → aplicar fail-loud

### ETAPA 5 — Três Cenários de Aporte

Seguir RIGOROSAMENTE as regras comportamentais de `references/regras-cenarios.md`.

**CENÁRIO A — Finclass Otimizada (regras absolutas):**
- Universo exclusivo: ativos da Carteira Finclass
- Árbitro único: Score Ajustado Final — nenhum outro critério influencia a alocação
- **PROIBIDO** qualquer consideração de balanceamento ARCA
- Distribuir aporte proporcional ao Score Ajustado entre os top ativos
- Verificar prioridade para ativos já em carteira (regra de Seção 07)

**CENÁRIO B — ARCA Otimizada:**
- Identificar classe(s) ARCA mais subrepresentadas (desvio vs. 25%)
- Dentro das classes identificadas, selecionar melhores ativos Finclass por Score Ajustado
- Se classe subrepresentada não tiver ativo Finclass com Score >7,0: próxima classe mais subrepresentada
- Universo: apenas ativos Finclass (igual ao A, mas com filtro ARCA aplicado primeiro)

**CENÁRIO C — Alpha-Gen Livre (universo trazido pelo usuário via Excel):**

🚨 **COMPORTAMENTO OBRIGATÓRIO:** Antes de gerar o Cenário C, parar a execução e perguntar literalmente:

> "Quer anexar uma planilha Excel com os ativos para análise do Cenário C?
>  • **Sim** → me envia o arquivo (uma coluna com os tickers, ex: PRIO3, VALE3, BTC, KNCR11).
>  • **Não** → vou gerar o relatório apenas com os Cenários A e B."

Conforme a resposta:

- **Usuário anexa Excel:** ler a planilha (usar a skill `xlsx` ou `pandas`/`openpyxl` via Bash). Extrair coluna de tickers. Se ambíguo qual coluna usar → perguntar antes de coletar. Em seguida: dividir tickers por classe (ações/FIIs vs. cripto) e coletar via firecrawl (Investidor10/CoinMarketCap conforme classe). Aplicar todas as regras C-1 a C-6 de `references/regras-cenarios.md`.
- **Usuário diz Não / agora não / pular:** **não gerar Cenário C**. Pular direto para ETAPA 6. No relatório, omitir a tabela do Cenário C e declarar no Veredito: "Cenário C não foi gerado nesta sessão — usuário optou por não submeter universo livre."
- **Resposta ambígua:** repetir a pergunta uma vez. Se ainda ambíguo → tratar como Não.

Detalhes do Cenário C quando ativo:
- Universo: união dos tickers da planilha do usuário (qualquer classe) + opcionalmente ativos da Carteira Finclass que o usuário marcar para entrar no C
- Filtro de liquidez obrigatório: volume médio diário ≥ 10× o valor do aporte no ativo
- Pelo menos 1 tese genuinamente non-consensus (nomear, identificar e justificar). Se nenhum ativo passar no Teste de Segundo Nível → declarar ausência no relatório, não inventar.
- Tickers não encontrados nem na fonte preferencial nem em busca livre via firecrawl → aplicar fail-loud (perguntar manualmente) OU excluir declarando o motivo.

### ETAPA 6 — Veredito e Filtros de Howard Marks

Aplicar os 4 filtros obrigatórios (Seção 09 de `references/sistema-score-v7.md`):
1. Margem de Segurança média ponderada ≥ 15%
2. Ratio médio ponderado ≥ 2,5:1
3. Multiplicador médio ponderado ≥ 1,0
4. Duration total ponderada da carteira pós-aporte ≤ 15 anos

Cenário que falhar em 2+ filtros: Rating de Convicção máximo 7/10. Declarar quais falharam.

### ETAPA 7 — Projeção de Meta R$1.000.000

`FV = PV × (1+r)^n + PMT × [(1+r)^n - 1] / r`

Premissas: Ações 18% a.a. | FIIs 12% a.a. | RF 13% a.a. | Alternativos 20% a.a.
Exibir nota obrigatória sobre premissas não garantidas.

### ETAPA 8 — Protocolo de Execução

Tabela com TODOS os ativos em carteira (cobertura total obrigatória):
Prioridade 🔴 URGENTE | 🟢 EXECUTAR | 🟢 MANTER | 🟡 MONITORAR | 🔵 PRÓX. SESSÃO

### ETAPA 9 — Geração e Salvamento

1. Gerar relatório HTML completo seguindo `references/html-output.md` (10 seções obrigatórias em ordem)
2. Salvar como `historico/AlphaGen_[DATA].html` na pasta do plugin
3. Se novo Checklist de Ciclo foi gerado ou atualizado: salvar em `historico/checklist-ciclo.md`

---

## Regras de Consistência

- Multiplicadores: posicionamento de CICLO DE LONGO PRAZO — nunca dados macro semanais
- Variação de multiplicador entre sessões: máximo 0,2 sem evento de ciclo declarado
- Margem de Segurança: NUNCA substituída por argumento de Carry ou DY
- Score variando >1,0 ponto: declarar fator responsável obrigatoriamente
- Reserva de emergência R$6.000: fora da carteira, jamais incluir em análises de aporte
- Toda coleta de dados usa a skill `firecrawl` — sem cache em disco; cada sessão busca os dados no momento do uso
````

- [ ] **Step 2: Verificar que não sobrou nenhuma menção ao script Python, cache em disco ou fontes antigas**

Run: `grep -n "coletar_dados.py\|Status Invest\|statusinvest\|Cache de 24h\|--sem-cache\|pip install\|whitelist\|4 fontes" "skills/analise-aporte/SKILL.md"`
Expected: sem saída (nenhum match) — código de saída 1.

Nota: o arquivo novo cita `historico/_missing_data_log.md` (nome de arquivo de log, que permanece) — isso é esperado e não deve ser removido.

- [ ] **Step 3: Verificar que o frontmatter YAML é válido e contém `name: analise-aporte`**

Run: `head -20 "skills/analise-aporte/SKILL.md"`
Expected: bloco `---`/`---` no topo do arquivo com `name: analise-aporte` e `description: >` seguido de texto cobrindo tanto frases de "análise de aporte" quanto de "atualizar ciclo".

- [ ] **Step 4: Commit**

```bash
git add "skills/analise-aporte/SKILL.md"
git commit -m "Reescreve SKILL.md: coleta via firecrawl, gate de instalação e checklist de ciclo absorvido"
```

---

### Task 4: Atualizar `skills/analise-aporte/references/regras-cenarios.md`

**Files:**
- Modify: `skills/analise-aporte/references/regras-cenarios.md`

**Interfaces:**
- Consumes: nada novo — apenas substitui menções pontuais ao script/fontes antigas por firecrawl/Investidor10.
- Produces: arquivo citado por `SKILL.md` (Task 3) na ETAPA 5 e no Cenário C.

- [ ] **Step 1: Editar a linha da tabela de REGRA C-0**

Old string:
```
| Anexa Excel agora | Ler tickers, coletar dados via `coletar_dados.py`, executar Cenário C |
```

New string:
```
| Anexa Excel agora | Ler tickers, coletar dados via firecrawl (Investidor10/CoinMarketCap conforme classe), executar Cenário C |
```

- [ ] **Step 2: Editar a REGRA C-4 (filtro de liquidez)**

Old string:
```
- Verificar volume médio diário negociado (Status Invest para ações/FIIs; CoinMarketCap para cripto)
```

New string:
```
- Verificar volume médio diário negociado (Investidor10 para ações/FIIs; CoinMarketCap para cripto — ambos via firecrawl)
```

- [ ] **Step 3: Editar a REGRA C-6 inteira (título e corpo)**

Old string:
```
### REGRA C-6: Cobertura pelas 4 fontes
Se algum ticker da planilha não for coberto pelas 4 fontes da whitelist (ex: ação americana sem BDR, ETF estrangeiro, ouro físico):
1. Declarar explicitamente no relatório: "Ticker X não coberto pelas 4 fontes da whitelist v2.0."
2. Pedir ao usuário os dados manualmente (regra fail-loud), OU
3. Excluir do Cenário C declarando o motivo no Veredito.

Nunca buscar em outras fontes para preencher o gap.
```

New string:
```
### REGRA C-6: Cobertura via Firecrawl
Se algum ticker da planilha não for encontrado nem na fonte preferencial (Investidor10/CoinMarketCap) nem na busca livre do firecrawl (ex: ação americana sem BDR, ETF estrangeiro, ouro físico):
1. Declarar explicitamente no relatório: "Ticker X não coberto pelas fontes disponíveis via firecrawl."
2. Pedir ao usuário os dados manualmente (regra fail-loud), OU
3. Excluir do Cenário C declarando o motivo no Veredito.

A busca livre do firecrawl já foi tentada antes de chegar a este ponto — não há uma "próxima fonte" a tentar além dela.
```

- [ ] **Step 4: Editar o passo 3 de "COMO SELECIONAR ATIVOS NO CENÁRIO C"**

Old string:
```
3. Coletar dados via `coletar_dados.py --ativos ... --cripto ...` (split por classe)
```

New string:
```
3. Coletar dados via firecrawl (Investidor10 para ações/FIIs, CoinMarketCap para cripto — split por classe)
```

- [ ] **Step 5: Editar a nota introdutória do Cenário C (menção remanescente à whitelist)**

Old string:
```
> Na v2.1 o Cenário C deixou de "varrer o mercado" e passou a operar **somente sobre os tickers que o usuário decide submeter**. Isso elimina recomendações arbitrárias e mantém o sistema 100% dentro da whitelist das 4 fontes.
```

New string:
```
> O Cenário C não "varre o mercado": ele opera **somente sobre os tickers que o usuário decide submeter**. Isso elimina recomendações arbitrárias e mantém o universo sob controle do usuário, mesmo com o firecrawl podendo buscar livremente os dados de cada ticker.
```

- [ ] **Step 6: Verificar que não sobrou nenhuma menção ao script ou às fontes antigas**

Run: `grep -n "coletar_dados.py\|Status Invest\|statusinvest\|4 fontes\|whitelist" "skills/analise-aporte/references/regras-cenarios.md"`
Expected: sem saída (nenhum match) — código de saída 1.

- [ ] **Step 7: Commit**

```bash
git add "skills/analise-aporte/references/regras-cenarios.md"
git commit -m "Atualiza regras-cenarios.md para coleta via firecrawl"
```

---

### Task 5: Atualizar terminologia em `skills/analise-aporte/references/melhorias-profissionais.md`

**Files:**
- Modify: `skills/analise-aporte/references/melhorias-profissionais.md`

**Interfaces:**
- Consumes: nada novo — documento de propostas futuras, ajuste é só de terminologia (script/parser/Status Invest → firecrawl/Investidor10).
- Produces: nenhuma outra tarefa depende deste arquivo.

- [ ] **Step 1: Editar linha 5 (introdução)**

Old string:
```
> A ideia é o usuário escolher quais incorporar — algumas custam zero implementação (mexer no peso), outras exigem dado novo no script (`coletar_dados.py`).
```

New string:
```
> A ideia é o usuário escolher quais incorporar — algumas custam zero implementação (mexer no peso), outras exigem capturar um dado novo na coleta via firecrawl.
```

- [ ] **Step 2: Editar item 1.1 (EV/EBITDA)**

Old string:
```
**Status Invest cobre EV/EBITDA?** Sim — já está na página de cada ação. Custo: adicionar 1 campo no parser do `coletar_dados.py`.
```

New string:
```
**Investidor10 cobre EV/EBITDA?** Sim — já está na página de cada ação. Custo: incluir esse campo na extração via firecrawl.
```

- [ ] **Step 3: Editar item 1.2 (FCF Yield)**

Old string:
```
**Status Invest cobre?** Indiretamente (FCO, Capex). Pode calcular: FCF = FCO − Capex. Adicionar no parser.
```

New string:
```
**Investidor10 cobre?** Indiretamente (FCO, Capex). Pode calcular: FCF = FCO − Capex. Adicionar à extração via firecrawl.
```

- [ ] **Step 4: Editar item 1.3 (Crescimento de Receita)**

Old string:
```
**Status Invest cobre?** Tem histórico de receita anual. Custo: parser precisa ler tabela histórica, não só "current".
```

New string:
```
**Investidor10 cobre?** Tem histórico de receita anual. Custo: a busca via firecrawl precisa capturar a tabela histórica, não só o valor atual.
```

- [ ] **Step 5: Editar item 1.5 (SBC)**

Old string:
```
**Cobertura:** Status Invest tem nº de ações. Custo: parser lê histórico.
```

New string:
```
**Cobertura:** Investidor10 tem nº de ações. Custo: a busca via firecrawl precisa capturar o histórico.
```

- [ ] **Step 6: Editar item 2.1 (Dividend Coverage Ratio)**

Old string:
```
**Status Invest cobre?** Parcialmente — relatórios gerenciais mensais têm FFO mas não estão na página padrão. Provavelmente vai cair em `_missing` → manual. **Mas é um dos campos mais importantes.**
```

New string:
```
**Investidor10 cobre?** Parcialmente — relatórios gerenciais mensais têm FFO mas não estão na página padrão. Provavelmente vai exigir busca livre via firecrawl ou pergunta manual. **Mas é um dos campos mais importantes.**
```

- [ ] **Step 7: Editar item 2.2 (Alavancagem)**

Old string:
```
**Cobertura:** Status Invest tem "Patrimônio Líquido" mas não traz LTV direto. Buscar em relatório gerencial → fail-loud manual.
```

New string:
```
**Cobertura:** Investidor10 tem "Patrimônio Líquido" mas não traz LTV direto. Buscar em relatório gerencial via busca livre do firecrawl → fail-loud manual se não encontrar.
```

- [ ] **Step 8: Editar item 4.1 (MVRV Z-Score)**

Old string:
```
**Cobertura:** CoinMarketCap **não** tem MVRV. Glassnode tem (fora da whitelist). Alternativa: deixar fail-loud → manual nas sessões de checklist trimestral.
```

New string:
```
**Cobertura:** CoinMarketCap **não** tem MVRV. Glassnode tem — fora das fontes preferenciais, mas o firecrawl pode tentar buscar livremente. Alternativa: deixar fail-loud → manual nas sessões de checklist trimestral.
```

- [ ] **Step 9: Editar item 4.2 (NVT Ratio)**

Old string:
```
**Cobertura:** CoinMarketCap não traz. Fail-loud → manual ou desistir do fator.
```

New string:
```
**Cobertura:** CoinMarketCap não traz. O firecrawl pode tentar busca livre (ex: sites especializados em on-chain); se não achar, fail-loud → manual ou desistir do fator.
```

- [ ] **Step 10: Editar item 4.3 (% supply em exchanges)**

Old string:
```
**Cobertura:** Glassnode/CryptoQuant — fora da whitelist.
```

New string:
```
**Cobertura:** Glassnode/CryptoQuant — fora das fontes preferenciais; o firecrawl pode tentar busca livre nesses sites antes do fail-loud.
```

- [ ] **Step 11: Editar item 4.4 (SoV vs. produtiva)**

Old string:
```
**Custo:** documentar — sem dado novo para BTC. Para ETH/SOL: TVL via DefiLlama (fora da whitelist) → fail-loud manual.
```

New string:
```
**Custo:** documentar — sem dado novo para BTC. Para ETH/SOL: TVL via DefiLlama (fora das fontes preferenciais) → firecrawl tenta busca livre, senão fail-loud manual.
```

- [ ] **Step 12: Editar item 5.1 (matriz de correlação)**

Old string:
```
**Custo:** Yahoo Finance tem dados — script precisa calcular. Médio.
```

New string:
```
**Custo:** Yahoo Finance tem dados — a coleta via firecrawl precisa buscar as séries e o cálculo é feito depois. Médio.
```

- [ ] **Step 13: Editar o passo 4 da seção "Próximos passos sugeridos"**

Old string:
```
4. Sistema atualiza `sistema-score-v7.md` e `coletar_dados.py` conforme escolha
```

New string:
```
4. Sistema atualiza `sistema-score-v7.md` e as instruções de coleta via firecrawl em `SKILL.md`/`fontes-dados.md` conforme escolha
```

- [ ] **Step 14: Editar a linha de notação (menção remanescente à whitelist)**

Old string:
```
> **Notação:** 🟢 alta prioridade, sem custo · 🟡 média, exige campo novo · 🔴 baixa, exige fonte externa fora da whitelist.
```

New string:
```
> **Notação:** 🟢 alta prioridade, sem custo · 🟡 média, exige campo novo · 🔴 baixa, exige fonte que nem as preferenciais nem a busca livre do firecrawl cobrem de forma confiável.
```

- [ ] **Step 15: Editar o item 1.6 (earnings revisions — menção remanescente à whitelist)**

Old string:
```
**Proposta:** NÃO incorporar agora — exige fonte externa (Bloomberg, Refinitiv, Reuters) fora da whitelist. Manter como nota mental.
```

New string:
```
**Proposta:** NÃO incorporar agora — exige fonte paga (Bloomberg, Refinitiv, Reuters) que o firecrawl não consegue acessar de forma confiável. Manter como nota mental.
```

- [ ] **Step 16: Verificar que não sobrou vocabulário morto no arquivo**

Run: `grep -n "Status Invest\|statusinvest\|parser\|coletar_dados.py\|whitelist" "skills/analise-aporte/references/melhorias-profissionais.md"`
Expected: sem saída (nenhum match) — código de saída 1.

- [ ] **Step 17: Commit**

```bash
git add "skills/analise-aporte/references/melhorias-profissionais.md"
git commit -m "Atualiza terminologia de melhorias-profissionais.md para firecrawl/Investidor10"
```

---

### Task 6: Atualizar `.claude-plugin/plugin.json`

**Files:**
- Modify: `.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: nada.
- Produces: metadados do plugin lidos pelo Claude Code ao carregar o plugin.

- [ ] **Step 1: Substituir o conteúdo do arquivo**

Usar Write para substituir o conteúdo inteiro de `.claude-plugin/plugin.json` por:

```json
{
  "name": "alpha-gen-investimentos",
  "version": "3.0.0",
  "description": "Analista e consultor de investimentos pessoal — framework Alpha-Gen (Howard Marks / ARCA) com coleta de dados via Firecrawl (Investidor10, CoinMarketCap, BCB, Yahoo Finance).",
  "author": { "name": "Guilherme" },
  "keywords": ["investimentos", "alpha-gen", "arca", "howard-marks", "fiis", "acoes", "renda-fixa", "cripto", "firecrawl"]
}
```

- [ ] **Step 2: Verificar que o JSON é válido**

Run: `node -e "JSON.parse(require('fs').readFileSync('.claude-plugin/plugin.json', 'utf8')); console.log('OK')"`
Expected: `OK` impresso, sem erro de parsing.

- [ ] **Step 3: Commit**

```bash
git add ".claude-plugin/plugin.json"
git commit -m "Bump plugin.json para v3.0.0 (skill única + coleta via firecrawl)"
```

---

### Task 7: Reescrever `README.md`

**Files:**
- Modify (reescrita completa): `README.md`

**Interfaces:**
- Consumes: conteúdo final de `SKILL.md` (Task 3) e `plugin.json` (Task 6) como referência do que documentar.
- Produces: documentação de topo do plugin — não é consumido por nenhuma skill em runtime.

- [ ] **Step 1: Substituir todo o conteúdo do arquivo**

Usar Write para substituir o conteúdo inteiro de `README.md` por (o bloco abaixo usa cerca de 4 crases porque o conteúdo contém um bloco de código aninhado — copiar tudo entre as cercas de 4 crases):

````markdown
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
````

- [ ] **Step 2: Verificar que não sobrou nenhuma menção às skills/arquivos removidos (fora do changelog histórico)**

A seção `## Changelog` menciona de propósito a arquitetura antiga nas entradas v1.0/v2.0/v2.1 — isso é história correta e deve permanecer. A verificação cobre apenas o conteúdo ANTES do changelog:

Run: `sed -n '1,/^## Changelog/p' README.md | grep -n "analise-rapida\|atualizar-ciclo\|coletar_dados.py\|Status Invest\|statusinvest\|cache_dados\|requirements.txt\|whitelist\|4 fontes"`
Expected: sem saída (nenhum match) — código de saída 1.

- [ ] **Step 2b: Confirmar que o changelog documenta a v3.0**

Run: `grep -n "### v3.0" README.md`
Expected: uma linha com `### v3.0 (esta versão)`.

- [ ] **Step 3: Commit**

```bash
git add "README.md"
git commit -m "Reescreve README.md para v3.0 (skill única + coleta via firecrawl)"
```

---

### Task 8: Verificação final de consistência

**Files:**
- Nenhum arquivo novo — apenas verificação de todo o repositório.

**Interfaces:**
- Consumes: resultado de todas as tasks anteriores.
- Produces: confirmação de que o plugin está internamente consistente antes de considerar a migração concluída.

- [ ] **Step 1: Confirmar que só existe uma skill**

Run: `ls skills/`
Expected: apenas `analise-aporte` listado.

- [ ] **Step 2: Confirmar ausência de qualquer artefato Python no plugin**

Run: `find . \( -iname "*.py" -o -iname "requirements.txt" \) -not -path "./.git/*"`
Expected: sem saída (nenhum match).

- [ ] **Step 3: Varredura final por vocabulário morto em todo o Markdown/JSON do plugin**

Run: `grep -rIn "coletar_dados\|Status Invest\|statusinvest\|whitelist\|4 fontes\|skills/analise-rapida\|skills/atualizar-ciclo" --include="*.md" --include="*.json" skills/ .claude-plugin/`
Expected: sem saída (nenhum match) — código de saída 1.

Run (README, ignorando o changelog histórico): `sed -n '1,/^## Changelog/p' README.md | grep -n "coletar_dados\|Status Invest\|statusinvest\|whitelist\|4 fontes\|analise-rapida\|atualizar-ciclo"`
Expected: sem saída (nenhum match) — código de saída 1.

Nota sobre o que É esperado permanecer e portanto NÃO deve ser "corrigido": (a) a frase "atualizar ciclo" (com espaço, sem hífen) na `description` do `SKILL.md` e no `README.md`, que é frase-gatilho; (b) `historico/_missing_data_log.md`, nome do arquivo de log que continua existindo; (c) as entradas v1.0/v2.0/v2.1 do changelog do README, que descrevem a arquitetura antiga por serem história.

- [ ] **Step 4: Confirmar que a skill principal referencia `firecrawl` como dependência**

Run: `grep -c "firecrawl" "skills/analise-aporte/SKILL.md"`
Expected: número maior que 5 (a palavra aparece várias vezes ao longo do arquivo — gate, regras de coleta, cada etapa de coleta).

- [ ] **Step 5: Revisar `git log` e `git status` para confirmar que todas as tasks foram commitadas**

Run: `git status && git log --oneline -10`
Expected: working tree limpo (`nothing to commit, working tree clean`) e os commits das Tasks 1–7 visíveis no histórico.

- [ ] **Step 6: Nenhum commit adicional nesta task** (é só verificação — se algo estiver pendente, corrigir e voltar para a task correspondente em vez de commitar aqui).
