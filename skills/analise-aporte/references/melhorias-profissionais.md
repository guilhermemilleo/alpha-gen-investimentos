# Melhorias Profissionais Propostas — Alpha-Gen v2.1+

> **Status:** este é um documento de **propostas para revisão do usuário**, não regras ativas do sistema. O score em produção continua sendo o da Seção 02 de `sistema-score-v7.md`. As propostas aqui são gaps identificados ao revisar o framework contra o que sell-side equity research, gestoras de FIIs (Kinea, RBR, Capitânia) e research de cripto (Glassnode, Coin Metrics) usam profissionalmente.
>
> A ideia é o usuário escolher quais incorporar — algumas custam zero implementação (mexer no peso), outras exigem capturar um dado novo na coleta via firecrawl.
>
> **Notação:** 🟢 alta prioridade, sem custo · 🟡 média, exige campo novo · 🔴 baixa, exige fonte que nem as preferenciais nem a busca livre do firecrawl cobrem de forma confiável.

---

## 1. AÇÕES — gaps no score atual

### 🟢 1.1 EV/EBITDA além de P/L
**Problema:** o fator [G.4] usa apenas P/L vs. P/L histórico. P/L distorce em empresas alavancadas, com prejuízo contábil pontual ou capital-intensivas (mineração, energia, telecom). Sell-side usa EV/EBITDA como múltiplo dominante nesses casos.

**Proposta:** desdobrar [G.4] em dois sub-fatores:
- [G.4a] P/L atual vs. histórico 5 anos — peso 60% do [G.4]
- [G.4b] EV/EBITDA atual vs. histórico — peso 40% do [G.4]

**Investidor10 cobre EV/EBITDA?** Sim — já está na página de cada ação. Custo: incluir esse campo na extração via firecrawl.

### 🟢 1.2 Free Cash Flow Yield
**Problema:** o sistema mede lucro contábil (LPA, ROE) mas não fluxo de caixa real. Empresa pode ter lucro alto e queimar caixa (capex, capital de giro). Buffett pesa FCF acima de lucro contábil.

**Proposta:** adicionar fator [H] Geração de Caixa — peso 5% (tirar de [F] DY que está superdimensionado em 5%).
- FCF Yield = FCF últimos 12m / Market Cap
- >8% = 9–10 · 5–8% = 7–8 · 3–5% = 5–6 · 1–3% = 3–4 · <1% ou negativo = 0–2

**Investidor10 cobre?** Indiretamente (FCO, Capex). Pode calcular: FCF = FCO − Capex. Adicionar à extração via firecrawl.

### 🟡 1.3 Crescimento de Receita (CAGR 3 anos)
**Problema:** ROE/ROIC altos em empresa que não cresce = armadilha de valor. Faltam métricas de growth.

**Proposta:** adicionar fator [I] Crescimento Composto — peso 5%.
- CAGR receita 3 anos: >15% = 9–10 · 8–15% = 7–8 · 3–8% = 5–6 · 0–3% = 3–4 · negativo = 0–2

**Investidor10 cobre?** Tem histórico de receita anual. Custo: a busca via firecrawl precisa capturar a tabela histórica, não só o valor atual.

### 🟢 1.4 Dívida Líquida em STRESS, não só nominal
**Problema:** [G.3] usa Dívida/EBITDA atual. Em momento de queda de EBITDA (recessão), o ratio explode. Marks recomenda fazer stress: "se EBITDA cair 30%, ainda passa?"

**Proposta:** dentro de [G.3], calcular também Dívida/EBITDA com EBITDA −30%. Se em stress > 5×, capar [G.3] em 4,0 (mesmo que o nominal seja bom).

**Custo:** zero — fórmula derivada, não precisa novo dado.

### 🟡 1.5 Diluição via SBC (Stock-Based Compensation)
**Problema:** especialmente em tech e small caps, SBC dilui o acionista mesmo com "lucro recorrente". Não captado em nenhum fator.

**Proposta:** flag qualitativa em [B] Qualidade — se #ações outstanding cresceu >3% a.a. nos últimos 3 anos: -1 em [B] obrigatório.

**Cobertura:** Investidor10 tem nº de ações. Custo: a busca via firecrawl precisa capturar o histórico.

### 🔴 1.6 Earnings revisions / consenso analistas
**Problema:** revisões de consenso (analistas subindo ou cortando estimativas) são um dos sinais mais potentes em equity research quantitativo (modelo de Piotroski + revisões).

**Proposta:** NÃO incorporar agora — exige fonte paga (Bloomberg, Refinitiv, Reuters) que o firecrawl não consegue acessar de forma confiável. Manter como nota mental.

---

## 2. FIIs — gaps no score atual

### 🟢 2.1 Dividend Coverage Ratio
**Problema:** o score atual mede DY (quanto distribui) mas não cobre se o FII está distribuindo MAIS do que gera. Em FIIs de tijolo é comum distribuir lucro contábil acima do FFO real (queimando caixa do fundo).

**Proposta:** adicionar sub-fator [F.5] Cobertura de Distribuição — peso 15% dentro de [F].
- Cobertura = (FFO 12m − Capex) / Distribuído 12m
- >1,2× = 9–10 · 1,0–1,2× = 7–8 · 0,9–1,0× = 5–6 · 0,8–0,9× = 3–4 · <0,8× = 0–1 + ⚠️ obrigatória

**Investidor10 cobre?** Parcialmente — relatórios gerenciais mensais têm FFO mas não estão na página padrão. Provavelmente vai exigir busca livre via firecrawl ou pergunta manual. **Mas é um dos campos mais importantes.**

### 🟢 2.2 Alavancagem (LTV / Dívida/GAV)
**Problema:** o score atual não pesa alavancagem do FII. FIIs alavancados (LTV >30%) têm risco amplificado em ciclo de juros alto.

**Proposta:** desdobrar [F.4] (concentração maior inquilino) → criar [F.4a] Concentração inquilino (peso 8%) e [F.4b] LTV/Dívida (peso 7%).
- LTV <10% = 9–10 · 10–20% = 7–8 · 20–30% = 5–6 · 30–40% = 3–4 · >40% = 0–2 + ⚠️

**Cobertura:** Investidor10 tem "Patrimônio Líquido" mas não traz LTV direto. Buscar em relatório gerencial via busca livre do firecrawl → fail-loud manual se não encontrar.

### 🟢 2.3 Qualidade da Receita: aluguel vs. financeiro
**Problema:** muitos FIIs de tijolo melhoram DY temporariamente vendendo imóvel ou rolando receita financeira (aplicações). Score não distingue receita recorrente (aluguel) de não-recorrente.

**Proposta:** adicionar dentro de [C] Qualidade da Gestão:
- "% receita 12m vinda de aluguel" — campo informativo no breakdown. Se <80%: -1 em [C].

**Cobertura:** Relatório gerencial → manual provavelmente.

### 🟢 2.4 Vacância Projetada (não só atual)
**Problema:** [F.1] usa vacância spot. Mas contratos vencendo nos próximos 12 meses sem renovação encaminhada são vacância latente. Sell-side de FIIs (Kinea, RBR) sempre olha "vacância projetada 12m" além da spot.

**Proposta:** dentro de [F.1], criar [F.1a] Vacância spot (peso 60%) e [F.1b] Vacância projetada 12m (peso 40%). Se [F.1b] > 15% e spot < 10%: capar [F.1] em 5,0.

**Cobertura:** relatório gerencial → manual.

### 🟡 2.5 P/VP por classe: tijolo vs. papel vs. híbrido vs. desenvolvimento
**Problema:** o sistema trata P/VP igual para todos. Mas FII de papel naturalmente roda P/VP ≈1,00 (marca a mercado), enquanto tijolo pode ficar abaixo de 0,80 sem ser barato real (vacância estrutural).

**Proposta:** ajuste de bandas por classe:
- Tijolo: barato <0,85 · justo 0,85–1,00 · caro >1,00
- Papel: barato <0,97 · justo 0,97–1,03 · caro >1,03
- Desenvolvimento: barato <0,80 · justo 0,80–0,95 · caro >0,95

**Custo:** zero — ajuste na fórmula.

### 🟢 2.6 TIR projetada (não só DY)
**Problema:** DY mede só o cupom. Em FIIs de papel pré-fixados em IPCA+, a TIR completa (DY + apreciação até paridade) pode ser muito maior. O sistema deveria comparar TIR vs. NTN-B equivalente, não DY vs. CDI.

**Proposta:** para FIIs de papel com indexação IPCA+: usar TIR estimada (DY atual + duration × spread implícito) no fator [B] em vez de DY puro.

**Cobertura:** cálculo derivado — custo zero.

---

## 3. RENDA FIXA — gaps no score atual

### 🟢 3.1 Roll-down explícito
**Problema:** o sistema mede duration mas não decompõe retorno em carry vs. roll-down. Em curva ascendente, roll-down adiciona retorno relevante além do cupom.

**Proposta:** declarar no [D] Geração de Fluxo: "Retorno total esperado 12m = Carry + Roll-down + MTM esperado". Mostrar os 3 componentes separados na justificativa.

**Custo:** cálculo derivado — Yahoo Finance tem curva implícita.

### 🟡 3.2 Convexidade para durations longas
**Problema:** stress MTM linear (+1pp, +2pp, +3pp) ignora convexidade. Em Tesouro Renda+ 2065 (duration ~39 anos), convexidade adiciona ~5pp de proteção em +1pp e tira ~5pp em -1pp. O sistema subestima ganho em queda de juros.

**Proposta:** quando duration >20 anos, calcular MTM com fórmula completa: ΔP ≈ −D × Δy + 0,5 × C × (Δy)². Declarar convexidade (C) explicitamente.

**Custo:** fórmula — sem dado novo.

### 🟢 3.3 Real Yield líquido pós-IR (já existe, mas raramente fundamentado)
O sistema já tem "Retorno Real Líquido Ajustado" mas a justificativa muitas vezes não decompõe. Padronizar: sempre apresentar como "X% nominal − Y% IPCA Focus − Z% IR efetivo = W% real líquido".

**Custo:** zero — disciplina de formato.

---

## 4. ALTERNATIVOS (cripto) — gaps no score atual

### 🟢 4.1 MVRV Z-Score
**Problema:** o sistema usa Fear & Greed como indicador de ciclo, que é qualitativo. MVRV Z-Score (Market Value vs. Realized Value, normalizado) é o indicador quantitativo mais respeitado para identificar topos e fundos do ciclo do BTC.

**Proposta:** substituir Fear & Greed (ou complementar) por MVRV Z-Score em [C] Risco e Drawdown.
- MVRV Z >7 = topo histórico (multiplicador 0,5–0,6)
- 4–7 = euforia (0,7–0,8)
- 0–4 = neutro a favorável (0,9–1,1)
- -1 a 0 = fundo provável (1,2–1,4)
- < -1 = capitulação histórica (1,5)

**Cobertura:** CoinMarketCap **não** tem MVRV. Glassnode tem — fora das fontes preferenciais, mas o firecrawl pode tentar buscar livremente. Alternativa: deixar fail-loud → manual nas sessões de checklist trimestral.

### 🟢 4.2 NVT Ratio (Network Value to Transactions)
**Problema:** análogo a P/E para cripto — mede se valor da rede está esticado vs. uso real (volume de transações).

**Proposta:** adicionar como sub-fator informativo em [D] Solidez da Tese. NVT alto persistente = bolha; NVT baixo persistente = subavaliado.

**Cobertura:** CoinMarketCap não traz. O firecrawl pode tentar busca livre (ex: sites especializados em on-chain); se não achar, fail-loud → manual ou desistir do fator.

### 🟢 4.3 % do supply em exchanges
**Problema:** indicador de pressão vendedora. Quando % do BTC em exchanges sobe, sinaliza que holders estão movendo para vender. Quando cai, sinaliza acumulação (custodiar self).

**Proposta:** adicionar como flag informativa, não fator de peso.

**Cobertura:** Glassnode/CryptoQuant — fora das fontes preferenciais; o firecrawl pode tentar busca livre nesses sites antes do fail-loud.

### 🟡 4.4 Distinção entre cripto store-of-value (BTC) e produtiva (ETH, SOL)
**Problema:** o sistema trata BTC e ETH com a mesma régua. BTC se valida por escassez (stock-to-flow); ETH/SOL se validam por adoção da camada de aplicação (TVL DeFi, volume de DEX, gas burned).

**Proposta:** dois sub-templates do score Alternativos:
- **Cripto SoV (BTC):** peso maior em [B] Descorrelação e [C] Drawdown, menor em [D] Tese (BTC é tese estabelecida)
- **Cripto produtiva (ETH, SOL, etc.):** peso maior em [D] (TVL, devs ativos, gas) e [E] (2º Nível)

**Custo:** documentar — sem dado novo para BTC. Para ETH/SOL: TVL via DefiLlama (fora das fontes preferenciais) → firecrawl tenta busca livre, senão fail-loud manual.

---

## 5. Gaps TRANSVERSAIS (todas as classes)

### 🟢 5.1 Matriz de correlação intra-carteira
**Problema:** ARCA mede balanceamento por classe macro, mas dois FIIs do mesmo segmento (ex: dois shoppings) são funcionalmente o mesmo ativo. O sistema não mede correlação real entre os ativos.

**Proposta:** adicionar Seção 5.5 ao relatório HTML: matriz de correlação 30d (retornos diários) entre os ativos da carteira. Yahoo Finance tem séries históricas. Sinalizar pares com correlação >0,8 como "concentração disfarçada".

**Custo:** Yahoo Finance tem dados — a coleta via firecrawl precisa buscar as séries e o cálculo é feito depois. Médio.

### 🟢 5.2 Concentração SETORIAL (não só ARCA)
**Problema:** ARCA mede 4 classes. Mas dentro de Ações, pode estar 70% em commodities (PETR4, VALE3, PRIO3) — concentração setorial enorme não capturada.

**Proposta:** adicionar à Seção 5 (Diagnóstico Crítico) tabela "Concentração por setor", com tetos sugeridos:
- Nenhum setor >40% das ações
- Nenhum subsegmento de FII >40% dos FIIs
- Cripto em altcoins ≤30% do bucket cripto

**Custo:** baixo — exige classificação setorial dos tickers (lookup table no plugin).

### 🟢 5.3 Position sizing via Kelly fracionário
**Problema:** o sistema usa "proporcional ao Score Ajustado" para distribuir o aporte, sem base teórica. Kelly fracionário (1/4 Kelly) é o padrão profissional para position sizing por convicção.

**Proposta:** dentro de cada cenário, declarar o "Kelly fracionário sugerido" por ativo:
- f = (p × b − q) / b, onde p = prob de acerto estimada (do Score), q = 1−p, b = Ratio de Assimetria
- Aplicar 1/4 desse f sobre o aporte

**Custo:** fórmula derivada — só apresentar como referência secundária na tabela.

### 🟢 5.4 Bear case obrigatório para ativos de Alta Convicção
**Problema:** psicologia. Quando o sistema diz "Alta Convicção", o usuário tende a entrar grande sem revisar. Forçar bear case explícito é a heurística do Charlie Munger ("invert, always invert").

**Proposta:** para todo ativo com Score Ajustado ≥8,0, exigir campo "Bear case" no breakdown: "O que precisa acontecer para essa tese quebrar?" — 2 linhas obrigatórias.

**Custo:** zero — disciplina de output.

### 🟢 5.5 Decision journal persistente
**Problema:** sem registro das justificativas usadas em decisões passadas, é impossível aprender com erros. Não há feedback loop.

**Proposta:** ao final de cada sessão, salvar `historico/decision_journal/YYYY-MM-DD.md` com:
- Cenário escolhido, ativos comprados, valores
- Tese resumida em 3 linhas por ativo
- Bear case esperado
- "O que vou monitorar nos próximos 90 dias para validar/invalidar a tese"

Na sessão seguinte, abrir o journal das últimas 12 semanas e marcar quais teses se confirmaram. Esse é o feedback loop que a maioria dos investidores PF não tem.

**Custo:** baixo — adicionar geração de arquivo MD ao final da ETAPA 9.

### 🟢 5.6 Range de VI (intervalo de confiança) em vez de valor pontual
**Problema:** o sistema atual cospe "VI = R$X,XX" como se fosse exato. Sell-side sempre apresenta range (cenário base / otimista / pessimista). Pontual transmite falsa precisão.

**Proposta:** mudar fórmula de VI para sempre apresentar como `VI: R$X,XX — R$Y,YY (mid R$Z,ZZ)`. Margem de Segurança calculada sobre o **mid** ou **pior caso conservador** (preferível).

**Custo:** zero — disciplina de formato.

### 🟡 5.7 Backtest light contra benchmark
**Problema:** sem comparação vs. benchmark (Ibovespa, IFIX, CDI), o usuário não sabe se está ganhando alfa ou só seguindo beta.

**Proposta:** novo campo no relatório (Seção 9, junto com projeção): "Performance vs. benchmark" — patrimônio atual vs. patrimônio se tivesse alocado tudo em IBOV/IFIX/CDI desde [primeira sessão registrada]. Yahoo Finance tem séries.

**Custo:** médio — precisa cache de patrimônio histórico do usuário.

---

## 6. Resumo Executivo — o que adotar primeiro

Se for adotar só 5 coisas (priorizei por ROI: impacto / esforço):

1. **🟢 5.4 Bear case obrigatório** — disciplina pura, custo zero, evita FOMO em alta convicção
2. **🟢 5.6 Range de VI** — elimina falsa precisão; padrão sell-side
3. **🟢 2.1 Dividend Coverage Ratio para FIIs** — fator mais importante que falta. Mesmo via fail-loud manual, vale incluir
4. **🟢 5.2 Concentração setorial além de ARCA** — fecha buraco real de risco que ARCA não enxerga
5. **🟢 5.5 Decision journal persistente** — único caminho para aprender com decisões passadas

Os outros (EV/EBITDA, FCF Yield, MVRV, correlação, Kelly) ficam para uma v2.2.

---

## 7. O que NÃO recomendo adotar

- ❌ Indicadores técnicos (RSI, MACD, médias móveis) — incompatíveis com filosofia Marks/Buffett. Buy-and-hold de longo prazo não opera por technicals.
- ❌ Stop-loss percentual fixo (ex: "stop em -15%") — destrói teses de valor que pioram antes de melhorar. Manter stop fundamentalista (gatilho qualitativo) como já está.
- ❌ Rebalanceamento mensal automático — gera custo e tira a vantagem do Score Ajustado dinâmico. Manter rebalanceamento por desvio ARCA >5pp como já está.
- ❌ Subscrições de research pago (Suno, Empiricus) — viola filosofia "pensamento de 2º nível": se você consome o mesmo research que o mercado, não tem edge.

---

## 8. Próximos passos sugeridos

1. Usuário lê este documento
2. Marca quais propostas adotar (1–5 prioritárias + opcionais)
3. Pedir nova sessão de customização do plugin: "Adota 5.4, 5.6 e 2.1 do `melhorias-profissionais.md`"
4. Sistema atualiza `sistema-score-v7.md` e as instruções de coleta via firecrawl em `SKILL.md`/`fontes-dados.md` conforme escolha
5. Versão sobe para v2.2
