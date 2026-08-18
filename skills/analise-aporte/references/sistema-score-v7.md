# Sistema de Score Alpha-Gen v7.0 — Referência Técnica

Fonte de verdade técnica. Contém todas as fórmulas, pesos e regras operacionais.

---

## Seção 01 — Arquitetura: Duas Camadas

**Score Ajustado Final = Score da Classe × Multiplicador de Convicção**

- **Camada 1 (Score da Classe):** qualidade intrínseca do ativo, escala 0–10
- **Camada 2 (Multiplicador de Convicção):** posicionamento no ciclo de longo prazo, escala 0,5–1,5
- O Score Ajustado Final é o ÚNICO número comparável entre classes diferentes
- Pode ultrapassar 10,0 quando Multiplicador >1,0 e Score alto — sinaliza oportunidade excepcional

---

## Seção 02 — Scores por Classe

### A — AÇÕES
`Score Ações = (A×0,15)+(B×0,15)+(C×0,20)+(D×0,15)+(E×0,10)+(F×0,05)+(G×0,20)`

| Fator | Peso | Critério |
|-------|------|----------|
| [A] Margem de Segurança | 15% | >30% = 9–10; <5% = 1–2; negativa = 0–1 + flag ⚠️ |
| [B] Qualidade do Negócio/Gestão | 15% | Moat, track record, previsibilidade. **REGRA:** resultado líquido negativo no último trimestre → nota máxima 4,0 (declarar obrigatoriamente) |
| [C] Assimetria Risco/Retorno | 20% | Ratio >3:1 = alto; <1,5:1 = baixo |
| [D] Independência do Macro | 15% | Tese intrínseca = alto; dependente de corte de juros/câmbio = baixo |
| [E] Pensamento de 2º Nível | 10% | Non-consensus fundamentado = alto; já precificado pelo mercado = baixo |
| [F] Geração de Fluxo (DY/JCP) | 5% | Peso baixo — melhores ações reinvestem |
| [G] Saúde Financeira | 20% | Média simples de G.1+G.2+G.3+G.4 |

**Sub-fatores de [G]:**
- [G.1] ROE: >20%=9–10; 15–20%=7–8; 10–15%=5–6; 5–10%=3–4; <5% ou negativo=0–2
- [G.2] ROIC: >15%=9–10; 10–15%=7–8; 7–10%=5–6; 4–7%=3–4; <4%=0–2
- [G.3] Dívida/EBITDA: <1×=9–10; 1–2×=7–8; 2–3×=5–6; 3–4×=3–4; >4×=0–2
- [G.4] P/L atual vs. P/L histórico 5 anos: 30%+ abaixo=9–10; ±10%=5–6; 30%+ acima=0–2
- **BANDEIRA VERMELHA:** 2+ sub-fatores com nota ≤2 → fator [G] capado em 3,0

---

### R — FIIs
`Score FIIs = (A×0,15)+(B×0,30)+(C×0,15)+(D×0,15)+(E×0,10)+(F×0,15)`

| Fator | Peso | Critério |
|-------|------|----------|
| [A] Margem de Segurança (P/VP + DY) | 15% | >30%=9–10; 20–30%=7–8; 15–20%=6–7; 10–15%=4–5; 5–10%=2–3; <5%=0–1; negativa=0+⚠️. Ajuste: P/VP<0,90 e margem>15% → +1; P/VP>1,0 → -1 |
| [B] Qualidade/Previsibilidade FCX | 30% | Comparar DY vs. CDI LÍQUIDO (CDI × 0,85 para PF). DY>CDI liq+4pp=9–10; +2–4pp=8; +0–2pp=7; ≈CDI liq=6; -0,5–2pp=4–5; <CDI liq-2pp=2–3. Ajuste: DY estruturalmente sustentável → +1; risco de redução → -1 |
| [C] Qualidade da Gestão/Portfólio | 15% | Track record, diversificação, qualidade dos ativos |
| [D] Assimetria Risco/Retorno | 15% | Upside P/VP + DY vs. risco de vacância/inadimplência |
| [E] Independência do Ciclo de Juros | 10% | Contextualizar exposição ao ciclo — não penalização |
| [F] Métricas Operacionais | 15% | Ver sub-fatores abaixo |

**Sub-fatores de [F] — FIIs de Tijolo:**
- [F.1] Vacância (peso 35%): <5%=9–10; 5–10%=7–8; 10–20%=4–6; 20–30%=2–3; >30%=0–1
- [F.2] Cap Rate vs. setor (peso 25%): acima média=7–10; na média=5–6; abaixo=2–4
- [F.3] WAULT (peso 25%): >7a=9–10; 5–7a=7–8; 3–5a=5–6; 1–3a=3–4; <1a=0–2
- [F.4] Concentração maior inquilino (peso 15%): <15%=9–10; 15–25%=7–8; 25–40%=4–6; 40–60%=2–3; >60%=0–1

**Sub-fatores de [F] — FIIs de Papel:**
- [F.1] Inadimplência (peso 35%): <1%=9–10; 1–3%=7–8; 3–5%=4–6; >5%=0–3
- [F.2] Rating médio CRIs (peso 30%): AA+/AAA=9–10; A=7–8; BBB=5–6; BB ou abaixo=0–4
- [F.3] Indexação vs. ciclo (peso 20%): aderente ao momento=7–10; neutro=5–6; contrária=2–4
- [F.4] Concentração maior devedor (peso 15%): <5%=9–10; 5–10%=7–8; 10–20%=4–6; >20%=0–3

**Regra obrigatória [F]:** declarar os valores numéricos dos sub-fatores na justificativa. Nunca usar "vacância elevada" sem o número. Dado não disponível → nota 5 + flag ⚠️

---

### C — RENDA FIXA
`Score RF = (A×0,20)+(B×0,25)+(C×0,15)+(D×0,20)+(E×0,05)+(F×0,15)`

| Fator | Peso | Critério |
|-------|------|----------|
| [A] Retorno Real Líquido Ajustado | 20% | Taxa nominal - IPCA - IR. Retorno real >5% a.a. = alto |
| [B] Segurança e Previsibilidade | 25% | Risco de crédito, garantias FGC, liquidez. RF soberana = máximo |
| [C] Risco e Liquidez de Resgate | 15% | Liquidez de resgate antecipado. Tesouro = alta liquidez. CDB com carência = baixo |
| [D] Geração de Fluxo de Caixa | 20% | Cupons, juros. Incluir reinvestimento |
| [E] Custo de Oportunidade vs. RV | 5% | Tiebreaker apenas |
| [F] Risco de Duration | 15% | Ver abaixo |

**Fator [F] — Risco de Duration:**
- Duration <3a = nota 8–10; 3–10a = 6–8; 10–20a = 4–6; 20–40a = 2–4; >40a = 0–2
- Ajuste pelo ciclo: Selic em queda confirmada → +2; em pico estável → +1; em base estável → -1; em alta → -2
- **REGRA MTM obrigatória:** posição RF longa (duration >10a) representando >30% do patrimônio → calcular e declarar impacto MTM em +1pp, +2pp, +3pp nas taxas longas

---

### A — ALTERNATIVOS
`Score Alts = (A×0,30)+(B×0,20)+(C×0,25)+(D×0,15)+(E×0,10)`

| Fator | Peso | Critério |
|-------|------|----------|
| [A] Assimetria Retorno (Up/Down) | 30% | Ratio >4:1 = máximo. Apenas quando assimetria excepcional |
| [B] Descorrelação com Carteira | 20% | Reduz volatilidade total? Ativo que sobe quando ações caem = alto |
| [C] Risco e Drawdown Histórico | 25% | Volatilidade, drawdown máximo, velocidade de recuperação |
| [D] Solidez da Tese de LP | 15% | Fundamento intrínseco (adoção, escassez) vs. especulação/momentum |
| [E] Pensamento de 2º Nível | 10% | Bear market com Fear & Greed <30 + tese intacta = oportunidade |

---

## Seção 03 — Multiplicador de Convicção de Ciclo

| Multiplicador | Temperatura | Indicadores Típicos |
|---------------|-------------|---------------------|
| 1,3–1,5 | Excepcional | Pessimismo excessivo, valuations historicamente baixos |
| 1,1–1,2 | Favorável | Catalisadores confirmados, valuations razoáveis |
| 0,9–1,0 | Neutro | Nem pessimismo nem otimismo excessivos |
| 0,7–0,8 | Desfavorável | Valuations elevados, otimismo acima do histórico |
| 0,5–0,6 | Adverso Severo | Euforia, valuations extremos |

**Regra de Estabilidade (OBRIGATÓRIA):** Multiplicador não muda mais de 0,2 entre sessões consecutivas sem evento de ciclo relevante (crash confirmado, reversão estrutural, mudança de política monetária de longo prazo). Se mudar >0,2, declarar o evento que motivou.

---

## Seção 04 — Interpretação do Score Ajustado Final

| Score | Nível | Ação | Teto de Concentração |
|-------|-------|------|----------------------|
| 8,0–10,0+ | Alta Convicção | Posição estrutural — overweight justificado | Até 40% do patrimônio |
| 6,0–7,9 | Conv. Moderada | Boa relação risco/retorno — alocar normalmente | Até 30% |
| 4,0–5,9 | Conv. Baixa | Assimetria fraca — apenas se complementar | Até 20% |
| <4,0 | Descartar | Upside não compensa risco | Zero — considerar venda |

---

## Seção 05 — Distinção Carry vs. Margem de Segurança

**CARRY:** DY de FIIs, cupons de RF, dividendos. O que o ativo paga enquanto você espera. Renda durante a espera — não proteção contra erro de avaliação.

**MARGEM DE SEGURANÇA:** Distância entre preço pago e valor intrínseco. Proteção contra erro de avaliação.

**REGRA:** Carry NUNCA substitui Margem de Segurança. Usar DY como "margem adicional" só é permitido como EXCEÇÃO TÁTICA declarada explicitamente — conta como filtro reprovado.

---

## Seção 06 — Cálculo do Valor Intrínseco

**Ações:** P/L médio histórico do setor × LPA estimado próximos 12 meses. Alternativa: DCF com FCF × (1/(WACC-g)), g=5–8% a.a. Usar sempre o método mais conservador disponível.

**FIIs:** VI = DY anual últimos 12 meses / Taxa alvo. Taxa alvo: FIIs papel = CDI+1,5–2%; FIIs tijolo = CDI+2,5–3,5%.

**RF:** "Barato" quando taxa atual > média histórica de spread. Tesouro IPCA+: atrativo acima de IPCA+6,5%; caro abaixo de IPCA+5,5%.

**Alternativos:** Range baseado em ciclos anteriores. Declarar como range, não valor pontual.

---

## Seção 07 — Regras de Alocação e Gestão

- **Prioridade ao que já existe:** aportar em ativos em carteira antes de buscar novos. Critério novo ativo: diferença de Score >0,5 OU tese comprometida por evento qualitativo
- **Fallback RF:** se nenhum ativo RV/alts tiver Score >7,0 E Ratio >2:1 → Renda Fixa Tática
- **Tetos de concentração:** inegociáveis (ver Seção 04)
- **Sinalização de deterioração:** Score <6,0 → sinalizar para possível substituição

---

## Seção 08 — Semáforo de Saúde da Carteira

| Cor | Critério | Ação |
|-----|----------|------|
| 🟢 VERDE | Score ≥7,0 E Ratio ≥2:1 E sem gatilho ativo | MANTER — tese intacta |
| 🟡 AMARELO | Score 5,0–6,9 OU Ratio 1,5–2,0 OU gatilho em monitoramento | MONITORAR |
| 🔴 VERMELHO | Score <5,0 OU Ratio <1,5 OU gatilho qualitativo ativo | URGENTE — considerar venda |

**Regra de Variação de Score (OBRIGATÓRIA):** variação >1,0 ponto vs. sessão anterior → declarar: "▲/▼ Score variou X,X pontos vs. sessão anterior. Fator que mudou: [identificar fator e razão]"

---

## Seção 09 — Filtros de Howard Marks

Aplicar obrigatoriamente no Veredito. Responder com valores calculados, não texto qualitativo.

| # | Filtro | Aprovado quando |
|---|--------|----------------|
| 1 | Margem de Segurança | Margem média ponderada dos ativos do cenário ≥15%. Carry/DY NÃO substitui |
| 2 | Assimetria Favorável | Ratio médio ponderado ≥2,5:1 |
| 3 | Temperatura do Ciclo | Multiplicador médio ponderado ≥1,0 (ciclo neutro a favorável) |
| 4 | Risco de Duration | Duration total ponderada ≤15 anos OU stress test <15% em +2pp |

**Regra de Rating Máximo:** cenário que falhar em 2+ filtros → Rating de Convicção máximo 7/10.

---

## Seção 10 — Projeção de Meta R$1.000.000

```
FV = PV × (1+r)^n + PMT × [(1+r)^n - 1] / r

FV = R$1.000.000 (meta)
PV = patrimônio atual
r  = retorno mensal (retorno anual / 12)
n  = meses até a meta (calcular iterativamente)
PMT = aporte mensal fixo
```

Premissas: Ações 18% a.a. | FIIs 12% a.a. | RF/Caixa 13% a.a. | Alternativos 20% a.a.

---

## Seção 11 — Checklist de Ciclo

Gerar quando `./historico/checklist-ciclo.md` (pasta atual) não existir. Salvar após geração.

**Indicadores por classe:**
- Ações: P/L médio Ibovespa vs. histórico 10a (barato <10x, caro >18x); fluxo estrangeiro B3 (30d); volume IPOs
- FIIs: P/VP médio setorial vs. histórico (desconto estrutural <0,90, prêmio >1,10); spread DY vs. NTN-B (atrativo >2%)
- RF: spread IPCA+ atual vs. média 5 anos; inclinação da curva de juros; posição no ciclo Copom
- Alternativos: Fear & Greed cripto (oportunidade <25, cautela >75); ouro vs. ATH; VIX atual vs. média histórica

---

## Seção 12 — Protocolo de Execução

Última seção obrigatória do relatório. Cobre TODOS os ativos em carteira.

Colunas: Prioridade | Ação | Ativo | Valor/Referência | Prazo | Motivo resumido

Labels fixas de prioridade:
- 🔴 URGENTE: venda com gatilho ativo OU stop acionado OU Score <4,0
- 🟢 EXECUTAR: compras recomendadas desta sessão
- 🟢 MANTER: ativos com semáforo verde sem ação requerida
- 🟡 MONITORAR: gatilho em observação, semáforo amarelo
- 🔵 PRÓX. SESSÃO: ação adiada por timing ou evento pendente

---

## Seção 13 — 10 Seções Obrigatórias do Relatório HTML

Ordem exata:
1. **Cabeçalho** — data, patrimônio, aporte, meta, reserva, versão
2. **Panorama Macro** — tabela de dados em tempo real + Multiplicadores com justificativa
3. **Checklist de Ciclo** — comparativo com sessão anterior OU novo gerado
4. **Semáforo de Saúde** — todos os ativos com 🟢🟡🔴 + Score Ajustado + variações
5. **Diagnóstico Crítico** — desvio ARCA, gatilhos, stops, Ratio, margens negativas
6. **Ranking Finclass** — 100% dos ativos; top 10 com breakdown completo
7. **Tabelas dos 3 Cenários** — A, B, C com todas as colunas obrigatórias
8. **Veredito Alpha-Gen** — cenário recomendado, ratings, filtros Marks
9. **Projeção de Meta** — meses por cenário, fórmula explícita, premissas
10. **Protocolo de Execução** — todos os ativos em carteira com prioridade

**Colunas obrigatórias nas tabelas dos 3 cenários:**
Ativo | Classe | Valor (R$) | Preço Atual | VI Est. | Método VI | Margem Seg. (%) | Carry (%) | Preço Alvo | Stop Loss | Gatilho Qualitativo | Upside (%) | Ratio Assim. | Sc. Classe | Mult. | Sc. Ajustado | Justificativa
