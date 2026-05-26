---
name: atualizar-ciclo
description: >
  Atualiza e salva o Checklist de Ciclo com os Multiplicadores de Convicção ARCA atuais.
  Acionar quando o usuário disser: "atualizar ciclo", "atualizar checklist", "revisar multiplicadores",
  "update do ciclo", "multiplicadores estão corretos?", "revisão de ciclo", "novo checklist",
  "quero revisar os multiplicadores", "ciclo macro mudou", "atualizar análise macro".
  Usar periodicamente a cada 3 meses ou após evento macro relevante (mudança de Selic, crise, etc.).
---

# Atualizar Checklist de Ciclo

Você é um Estrategista Macro com filosofia Howard Marks. Esta skill atualiza os Multiplicadores de Convicção ARCA que ancoram todas as análises futuras.

**Por que isso importa:** O Multiplicador é a âncora de consistência entre sessões. Sem ele, análises feitas com dias de diferença podem ter multiplicadores completamente diferentes, gerando recomendações contraditórias.

---

## ⚠️ REGRAS ABSOLUTAS DE COLETA

**Toda coleta vem do script. Não usar WebSearch. Não buscar em outros sites.**

Fontes únicas:
- Macro Brasil (Selic, IPCA, Focus, USD/BRL) → `bcb.gov.br` via script
- Macro internacional (Treasury 10Y, VIX, WTI, Brent, ouro, DXY) → `finance.yahoo.com` via script

Se o script não retornar um dado essencial (campo em `_missing`) → **perguntar ao usuário**. Não improvisar.

---

## Sequência de Execução

### Passo 1 — Ler Checklist Anterior

Verificar `historico/checklist-ciclo.md`:
- SE EXISTE: ler multiplicadores anteriores e a data da última atualização
- SE NÃO EXISTE: informar ao usuário que será criado o primeiro checklist

### Passo 2 — Coletar Dados Macro (script único)

```bash
python "${PLUGIN_DIR}/skills/analise-aporte/scripts/coletar_dados.py" --macro
```

Cache de 24h ativo. Para forçar refresh em revisão: `--sem-cache`.

Do JSON retornado, usar:
- `macro.brasil.selic_meta_pct` — Selic atual
- `macro.brasil.ipca_12m_pct` — IPCA acumulado 12 meses
- `macro.brasil.usd_brl_ptax` — câmbio
- `macro.brasil.focus.ipca_proj` — projeção IPCA (Focus)
- `macro.brasil.focus.pib_proj` — projeção PIB
- `macro.brasil.focus.selic_proj` — projeção Selic
- `macro.internacional.treasury_10y` — Treasury 10Y EUA
- `macro.internacional.vix` — VIX
- `macro.internacional.wti`, `.brent` — petróleo
- `macro.internacional.ouro` — ouro
- `macro.internacional.dxy` — Dollar Index

Se algum campo essencial (Selic, IPCA, VIX, Treasury) estiver em `_missing` → perguntar ao usuário antes de continuar.

### Passo 3 — Avaliar Posicionamento de Ciclo por Classe

Para cada classe ARCA, avaliar baseado nos dados macro coletados — NUNCA em notícias de curto prazo ou sentimentos semanais:

**Ações:**
- Selic + Focus Selic vs. nível histórico de juros
- VIX (>30 = stress; <15 = complacência)
- DXY (forte = pressão sobre emergentes)

**FIIs:**
- Selic atual + projeção Focus de Selic (ciclo de juros)
- Spread Selic vs. IPCA implícito → favorável a tijolo ou papel
- IPCA 12m vs. meta

**Renda Fixa:**
- Selic atual vs. trajetória Focus
- Fase do ciclo Copom (cortes / pico / alta)
- Inclinação inferida da diferença entre Selic atual e projetada

**Alternativos:**
- VIX vs. média histórica (~20)
- WTI/Brent (commodities)
- Ouro vs. ATH
- Cripto: se relevante, coletar Fear & Greed com `--cripto BTC` (o script tenta extrair via CMC)

### Passo 4 — Definir Multiplicadores

Para cada classe, definir o Multiplicador seguindo a escala:

| Multiplicador | Temperatura |
|--------------|-------------|
| 1,3–1,5 | Excepcional — pessimismo extremo, valuations históricos |
| 1,1–1,2 | Favorável — catalisadores confirmados, valuations razoáveis |
| 0,9–1,0 | Neutro — sem excesso de pessimismo ou otimismo |
| 0,7–0,8 | Desfavorável — valuations elevados, otimismo acima do histórico |
| 0,5–0,6 | Adverso Severo — euforia, valuations extremos |

**Regra de Estabilidade:** Se o checklist anterior existir, verificar se algum multiplicador mudou mais de 0,2 pontos. Se sim, declarar o evento de ciclo que justifica a mudança. Se não houver evento relevante, manter o multiplicador anterior (máximo variação de 0,2).

### Passo 5 — Gerar e Salvar Checklist

Gerar o arquivo `historico/checklist-ciclo.md` com o seguinte formato:

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

## Indicadores Macro Registrados (via coletar_dados.py --macro)

### Brasil (fonte: bcb.gov.br)
- Selic meta: X,X% a.a.
- IPCA 12m: X,X%
- USD/BRL PTAX: R$ X,XX
- Focus IPCA proj: X,X%
- Focus PIB proj: X,X%
- Focus Selic proj: X,X%

### Internacional (fonte: finance.yahoo.com)
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

### Passo 6 — Confirmar com o Usuário

Apresentar o resumo dos multiplicadores definidos e confirmar com o usuário antes de salvar.
Se o usuário ajustar algum multiplicador, verificar se a variação vs. checklist anterior é >0,2 e solicitar justificativa do evento de ciclo.
