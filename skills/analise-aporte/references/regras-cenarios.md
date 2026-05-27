# Regras Comportamentais dos Cenários — Alpha-Gen

Este arquivo define as regras de comportamento RÍGIDAS e ABSOLUTAS para cada cenário.
Inconsistência entre sessões é o principal problema a resolver. Seguir estas regras sem desvio.

---

## CENÁRIO A — Finclass Otimizada

### O QUE É
Identificar os melhores ativos do universo Finclass para o aporte, usando apenas o Score Ajustado Final como critério de alocação.

### REGRAS ABSOLUTAS (sem exceção)

**REGRA A-1: Universo exclusivo**
Apenas ativos presentes na Carteira Finclass. Nenhum ativo externo, mesmo que tenha score mais alto.

**REGRA A-2: Score Ajustado é o único árbitro**
A alocação do aporte segue estritamente o ranking por Score Ajustado Final. Nenhum outro fator define quanto vai para cada ativo.

**REGRA A-3: PROIBIÇÃO ABSOLUTA de ARCA no Cenário A**
- ❌ PROIBIDO verificar desvio de classe ARCA
- ❌ PROIBIDO priorizar ativo por classe estar subrepresentada
- ❌ PROIBIDO rejeitar ativo porque "já tem muito de uma classe"
- ❌ PROIBIDO ajustar alocação para "balancear" o portfólio
- ✅ CORRETO: se os 3 maiores scores forem todos FIIs, alocar nos 3 FIIs

**REGRA A-4: Verificação de carteira atual primeiro**
Antes de sugerir ativos novos, verificar se aportar nos ativos de maior Score já em carteira não é superior. Critério para ativo novo entrar: Score Ajustado >0,5 acima do melhor ativo já em carteira, OU tese atual comprometida por evento qualitativo.

**REGRA A-5: Prioridade a preço teto**
Verificar se o preço atual está abaixo do preço teto Finclass. Acima do preço teto: sinalizar com ⚠️ mas incluir na análise (o Score Ajustado é o árbitro, não o preço teto).

### COMO DISTRIBUIR O APORTE NO CENÁRIO A
1. Calcular Score Ajustado Final de todos os ativos Finclass
2. Ordenar por Score decrescente
3. Verificar ativos já em carteira com score alto (prioridade)
4. Selecionar top 3-5 ativos (evitar fragmentar demais o aporte)
5. Distribuir proporcionalmente ao Score: ativo com Score 9,0 recebe mais do que Score 7,5
6. Respeitar tetos de concentração (Score <8,0 → máx 20% do patrimônio; 8,0-8,9 → máx 30%; ≥9,0 → máx 40%)

---

## CENÁRIO B — ARCA Otimizada

### O QUE É
Alocar o aporte nas classes ARCA mais subrepresentadas, usando ativos Finclass como universo.

### REGRAS ABSOLUTAS

**REGRA B-1: ARCA primeiro, sempre**
O Cenário B começa OBRIGATORIAMENTE pelo diagnóstico ARCA:
- Calcular % atual de cada classe (Ações / FIIs / Caixa+RF / Alternativos)
- Calcular desvio de cada classe vs. 25% alvo
- Identificar as classes mais distantes do alvo (abaixo de 25%)
- Aplicar o Multiplicador de Convicção como ponderador (classe favorável tem prioridade sobre classe desfavorável mesmo que o desvio seja igual)

**REGRA B-2: Universo Finclass dentro da classe selecionada**
Após identificar qual(is) classe(s) recebe(m) o aporte, selecionar os melhores ativos Finclass daquela classe por Score Ajustado Final.

**REGRA B-3: Fallback quando não há ativo Finclass adequado**
Se a classe mais subrepresentada não tiver ativo Finclass com Score Ajustado >7,0: mover para a próxima classe mais subrepresentada. Se nenhuma classe tiver ativo com Score >7,0 E Ratio >2:1: acionar Fallback RF (aportar em CDB ou Tesouro IPCA+).

**REGRA B-4: Exceção de Diversificação Intrassetorial**
Permitida com declaração explícita "EXCEÇÃO DE DIVERSIFICAÇÃO INTRASSETORIAL" na justificativa.
Gate de DY para FIIs: se novo FII tiver DY mais de 3pp abaixo de FII da mesma sub-classe já em carteira, calcular custo de oportunidade composto em 10 anos e apresentar ao usuário antes de recomendar.

### COMO DISTRIBUIR O APORTE NO CENÁRIO B
1. Mapear desvio ARCA atual
2. Identificar top 1-2 classes subrepresentadas × Multiplicador de Convicção
3. Dentro dessas classes, ranquear ativos Finclass por Score
4. Distribuir o aporte para os top 2-3 ativos das classes selecionadas
5. Se o desvio for pequeno (<5%), aceitar qualquer classe — usar Score como desempate

---

## CENÁRIO C — Alpha-Gen Livre (universo trazido pelo usuário)

### O QUE É
Identificar oportunidades fora da Carteira Finclass, dentro de um universo de ativos **fornecido pelo usuário via planilha Excel**. Pelo menos uma tese deve ser genuinamente non-consensus.

> Na v2.1 o Cenário C deixou de "varrer o mercado" e passou a operar **somente sobre os tickers que o usuário decide submeter**. Isso elimina recomendações arbitrárias e mantém o sistema 100% dentro da whitelist das 4 fontes.

### REGRA C-0: Pergunta Obrigatória de Abertura (NOVA — v2.1)

Antes de gerar o Cenário C, **o sistema PRECISA perguntar ao usuário**, com este texto literal:

> "Quer anexar uma planilha Excel com os ativos para análise do Cenário C?
>  • **Sim** → me envia o arquivo (uma coluna com os tickers, ex: PRIO3, VALE3, BTC, KNCR11).
>  • **Não** → vou gerar o relatório apenas com os Cenários A e B."

Comportamento conforme resposta:

| Resposta | Comportamento |
|----------|---------------|
| Anexa Excel agora | Ler tickers, coletar dados via `coletar_dados.py`, executar Cenário C |
| Não / agora não / pular | **Não gerar Cenário C.** Relatório final terá apenas Cenários A e B. Declarar no Veredito: "Cenário C não foi gerado nesta sessão — usuário optou por não submeter universo livre." |
| Resposta ambígua | Repetir a pergunta uma vez. Se ainda ambíguo: tratar como "Não". |

### REGRA C-1: Composição do Universo do Cenário C

O universo do Cenário C é a **união** entre:
1. Ativos da planilha Excel fornecida pelo usuário (qualquer classe: ações BR, FIIs, cripto, ETFs/BDRs, RF)
2. *Opcional:* ativos da Carteira Finclass que o usuário marcar explicitamente para entrar no Cenário C (default: NÃO entram — Finclass é universo do A e B)

**Não existe** "buscar ativo no mercado por conta própria". O analista trabalha apenas com o que o usuário trouxe.

### REGRA C-2: Formato esperado da planilha Excel

A skill deve aceitar variações razoáveis. Mínimo: uma coluna com os tickers. Colunas opcionais:

| Coluna | Obrigatória? | Uso |
|--------|--------------|-----|
| `Ticker` ou `Ativo` | ✅ Sim | Identificador (PRIO3, KNCR11, BTC, etc.) |
| `Classe` | Não | Se omitido, inferir pelo ticker (Seção "Identificação por ticker") |
| `Tese` ou `Observação` | Não | Texto livre do usuário sobre por que está olhando esse ativo |
| `Preço alvo manual` | Não | Sobrescreve o cálculo de VI da Seção 06 do score |
| `Stop manual` | Não | Sobrescreve cálculo automático de stop |

Se a planilha tiver formato diferente (ex: tickers em linha única separados por vírgula): aceitar e extrair. **Em caso de dúvida sobre qual coluna é o ticker → perguntar ao usuário antes de coletar dados.**

### REGRA C-3: Tese non-consensus obrigatória (mantida)
Obrigatório incluir pelo menos 1 ativo do universo do Cenário C com tese genuinamente non-consensus:
- Nomear explicitamente qual ativo é a tese non-consensus
- Justificar POR QUE o mercado está errado sobre ele
- Passar no Teste de Segundo Nível: "O mercado está errado sobre este ativo, e eu sei por quê?"
- Não confundir non-consensus com "ativo polêmico" — a tese precisa ser fundamentada

Se nenhum ativo do universo trazido passar no Teste de Segundo Nível: **declarar no relatório** que nenhuma tese non-consensus foi identificada e que o Cenário C apresentado é "convexidade de convicção alta sem non-consensus declarado". Não inventar non-consensus para cumprir tabela.

### REGRA C-4: Filtro de liquidez obrigatório (mantida)
Para cada ativo recomendado no Cenário C:
- Verificar volume médio diário negociado (Status Invest para ações/FIIs; CoinMarketCap para cripto)
- Volume ≥ 10× o valor do aporte alocado naquele ativo
- Declarar o volume na tabela antes de incluir
- Se o script não conseguir o volume: **aplicar fail-loud** (perguntar ao usuário). Não excluir silenciosamente.

### REGRA C-5: Mesmas métricas obrigatórias (mantida)
Todas as métricas obrigatórias se aplicam:
- Valor Intrínseco Estimado + Método VI
- Margem de Segurança (%)
- Carry Anualizado (%)
- Ratio de Assimetria
- Preço Alvo + Stop Loss
- Score Ajustado Final (usando a classe ARCA mais adequada)

### REGRA C-6: Cobertura pelas 4 fontes
Se algum ticker da planilha não for coberto pelas 4 fontes da whitelist (ex: ação americana sem BDR, ETF estrangeiro, ouro físico):
1. Declarar explicitamente no relatório: "Ticker X não coberto pelas 4 fontes da whitelist v2.0."
2. Pedir ao usuário os dados manualmente (regra fail-loud), OU
3. Excluir do Cenário C declarando o motivo no Veredito.

Nunca buscar em outras fontes para preencher o gap.

### COMO SELECIONAR ATIVOS NO CENÁRIO C
1. Confirmar com o usuário se quer anexar a planilha (REGRA C-0)
2. Se sim: ler a planilha → extrair tickers → confirmar parsing com o usuário se houver ambiguidade
3. Coletar dados via `coletar_dados.py --ativos ... --cripto ...` (split por classe)
4. Para campos `_missing`: aplicar fail-loud (perguntar ao usuário)
5. Calcular Score Ajustado Final de cada candidato
6. Filtrar por liquidez (regra C-4)
7. Verificar se algum passa no Teste de Segundo Nível
8. Selecionar 3-5 ativos: mix de alta convicção + tese non-consensus
9. Declarar qual é a tese non-consensus (ou declarar ausência conforme C-3)

---

## Regras Transversais (todos os cenários)

### Fallback RF
Se nenhum ativo de RV ou Alternativos tiver Score Ajustado >7,0 E Ratio >2:1 em qualquer cenário:
- Direcionar para Renda Fixa Tática: Tesouro IPCA+ ou CDB de alta liquidez
- Justificar a decisão explicitamente

### Tetos de Concentração (inegociáveis)
- Score Ajustado <8,0 → máximo 20% do patrimônio total
- Score Ajustado 8,0–8,9 → máximo 30% do patrimônio total
- Score Ajustado ≥9,0 → máximo 40% do patrimônio total

### Margem de Segurança Negativa
Quando o preço atual superar o VI estimado: declarar com flag ⚠️ o valor negativo exato. Nunca omitir com "—". Nunca substituir por argumento de DY/Carry.

### Risco de Duration Ponderado (especial para esta carteira)
A carteira atual tem ~65% em Tesouro Renda+ 2065 (duration ~39 anos). Calcular SEMPRE o Duration Total Ponderado pós-aporte e os 3 cenários de stress MTM (+1pp, +2pp, +3pp nas taxas longas).
