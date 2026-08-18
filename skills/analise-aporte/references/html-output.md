# Template de Saída HTML — Alpha-Gen v8.0

Visual renovado: dark mode premium, tipografia refinada, menos neon, mais legível.
Gerar HTML autocontido (sem dependências externas). Todo CSS em <style> no <head>.

## Paleta de Cores (Renovada)

```css
:root {
  --bg:        #08090e;   /* fundo principal — quase preto */
  --bg2:       #0e1118;   /* cards */
  --bg3:       #141720;   /* linhas alternadas, sub-cards */
  --bg4:       #1a1f2e;   /* hover */
  --border:    #1e2535;   /* bordas suaves */
  --border2:   #28334a;   /* bordas de destaque */

  --text:      #e2e8f0;   /* texto principal */
  --text2:     #8899aa;   /* texto secundário */
  --text3:     #4a5568;   /* texto terciário / placeholders */

  --accent:    #38bdf8;   /* azul céu — destaque primário */
  --accent2:   #0284c7;   /* azul mais escuro */
  --gold:      #f59e0b;   /* âmbar / labels */
  --green:     #10b981;   /* Score alto / Verde */
  --green2:    #059669;
  --red:       #ef4444;   /* Score baixo / Urgente */
  --orange:    #f97316;   /* Score moderado-baixo */
  --purple:    #a78bfa;   /* RF / detalhes */

  --mono: 'Courier New', 'Lucida Console', monospace;
  --sans: -apple-system, 'Segoe UI', Arial, sans-serif;
}
```

## CSS Base

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 14px;
  line-height: 1.65;
  max-width: 1140px;
  margin: 0 auto;
  padding: 24px 20px 80px;
}
h1 { font-size: 26px; color: #fff; font-weight: 600; letter-spacing: -0.5px; }
h2 {
  font-size: 11px;
  color: var(--accent);
  letter-spacing: 2.5px;
  text-transform: uppercase;
  margin: 36px 0 14px;
  border-bottom: 1px solid var(--border2);
  padding-bottom: 10px;
  font-family: var(--mono);
}
h3 { font-size: 13px; color: var(--gold); margin: 18px 0 8px; font-weight: 600; }
p { margin-bottom: 10px; font-size: 13px; color: var(--text2); line-height: 1.7; }

.tag {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--accent);
  letter-spacing: 3px;
  text-transform: uppercase;
}

.card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
  margin-bottom: 14px;
}

.alert {
  border-left: 3px solid var(--gold);
  background: rgba(245,158,11,0.07);
  padding: 10px 14px;
  border-radius: 0 8px 8px 0;
  margin: 12px 0;
  font-size: 12px;
  color: var(--text2);
}
.alert-red   { border-color: var(--red);   background: rgba(239,68,68,0.07); }
.alert-green { border-color: var(--green); background: rgba(16,185,129,0.07); }
.alert-blue  { border-color: var(--accent); background: rgba(56,189,248,0.06); }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-bottom: 16px;
}
th {
  background: var(--bg3);
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text3);
  letter-spacing: 1px;
  text-transform: uppercase;
  padding: 9px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}
td {
  padding: 9px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
  color: var(--text2);
}
tr:hover td { background: var(--bg3); }

.score-high   { font-family: var(--mono); font-weight: 700; color: var(--green); }
.score-mod    { font-family: var(--mono); font-weight: 700; color: var(--gold); }
.score-low    { font-family: var(--mono); font-weight: 700; color: var(--orange); }
.score-disc   { font-family: var(--mono); font-weight: 700; color: var(--red); }

.badge {
  display: inline-block;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}
.badge-high { background: rgba(16,185,129,0.15); color: var(--green); border: 1px solid rgba(16,185,129,0.3); }
.badge-mod  { background: rgba(245,158,11,0.12); color: var(--gold); border: 1px solid rgba(245,158,11,0.3); }
.badge-low  { background: rgba(249,115,22,0.12); color: var(--orange); border: 1px solid rgba(249,115,22,0.3); }
.badge-disc { background: rgba(239,68,68,0.12); color: var(--red); border: 1px solid rgba(239,68,68,0.3); }
.badge-blue { background: rgba(56,189,248,0.10); color: var(--accent); border: 1px solid rgba(56,189,248,0.2); }

.formula {
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: 8px;
  padding: 12px 16px;
  font-family: var(--mono);
  font-size: 12px;
  color: var(--accent);
  margin: 12px 0;
  white-space: pre-wrap;
  line-height: 1.8;
}

.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
.grid4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; }
@media(max-width:700px) { .grid2,.grid3,.grid4 { grid-template-columns: 1fr; } }

.section-num {
  display: inline-block;
  background: var(--accent2);
  color: #fff;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 8px;
}

.class-badge {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
  display: inline-block;
}
.acoes { background: rgba(56,189,248,0.15); color: var(--accent); border: 1px solid rgba(56,189,248,0.3); }
.fiis  { background: rgba(16,185,129,0.15); color: var(--green); border: 1px solid rgba(16,185,129,0.3); }
.rf    { background: rgba(167,139,250,0.15); color: var(--purple); border: 1px solid rgba(167,139,250,0.3); }
.alts  { background: rgba(245,158,11,0.12); color: var(--gold); border: 1px solid rgba(245,158,11,0.3); }

.stat-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  text-align: center;
}
.stat-value {
  font-family: var(--mono);
  font-size: 22px;
  font-weight: 700;
  color: var(--accent);
  display: block;
  margin: 4px 0;
}
.stat-label {
  font-size: 10px;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-family: var(--mono);
}

hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }
```

## Estrutura HTML — 10 Seções Obrigatórias

### Seção 1 — Cabeçalho

```html
<div style="border-bottom:1px solid var(--border2);padding-bottom:24px;margin-bottom:32px;">
  <div class="tag">Alpha-Gen · Framework de Investimentos · [DATA COMPLETA]</div>
  <h1 style="margin-top:8px;">⚡ Análise Alpha-Gen — [MÊS/ANO]</h1>
  <p style="font-size:13px;margin-top:4px;color:var(--text2);">Versão 7.0 · Filosofia Howard Marks / Oaktree Capital</p>
  <div class="grid4" style="margin-top:20px;">
    <div class="stat-card">
      <span class="stat-label">Patrimônio</span>
      <span class="stat-value">R$ XX.XXX</span>
    </div>
    <div class="stat-card">
      <span class="stat-label">Aporte</span>
      <span class="stat-value">R$ X.XXX</span>
    </div>
    <div class="stat-card">
      <span class="stat-label">Meta</span>
      <span class="stat-value">R$ 1M</span>
    </div>
    <div class="stat-card">
      <span class="stat-label">Reserva EM.</span>
      <span class="stat-value" style="color:var(--text3);">R$ 6.000</span>
    </div>
  </div>
</div>
```

### Seção 2 — Panorama Macro

Tabela de dados em tempo real + Tabela de Multiplicadores de Convicção com justificativas de ciclo (não de curto prazo).

### Seção 3 — Checklist de Ciclo

Comparativo sessão anterior vs. atual, OU novo checklist gerado. Data de geração + próxima revisão (+3 meses).

### Seção 4 — Semáforo de Saúde da Carteira

Tabela com todos os ativos: Ativo | Classe | % Carteira | Score Ajustado | Semáforo | Status | Variação Score

Para variações >1,0 ponto, inserir linha adicional: "▲/▼ Score variou X,X pontos — fator: [...]"

### Seção 5 — Diagnóstico Crítico

Cards ARCA com desvio de cada classe. Alertas de stops/gatilhos. Margens negativas com flag ⚠️. Ratio de Assimetria baixos. Stress test de Duration se aplicável.

### Seção 6 — Ranking Completo Finclass

Tabela com 100% dos ativos. Linhas de breakdown para top 10.

**Score colorido:**
- ≥8,0 → `<span class="score-high">`
- 6,0–7,9 → `<span class="score-mod">`
- 4,0–5,9 → `<span class="score-low">`
- <4,0 → `<span class="score-disc">`

### Seção 7 — Tabelas dos 3 Cenários

Três tabelas separadas com header colorido:
- Cenário A: borda azul (`var(--accent)`)
- Cenário B: borda verde (`var(--green)`)
- Cenário C: borda âmbar (`var(--gold)`)

Declarar no header de cada tabela qual regra se aplica:
- A: "Score Ajustado como árbitro absoluto. ARCA não considerado."
- B: "Classes ARCA subrepresentadas priorizadas. Universo Finclass."
- C: "Universo livre. Pelo menos 1 tese non-consensus obrigatória."

### Seção 8 — Veredito Alpha-Gen

Card com borda dourada. Incluir:
- Cenário recomendado + justificativa
- Rating de Convicção (1–10) com indicador visual
- 4 Filtros de Marks com valores calculados (✅ ou ❌ + número)
- Tese non-consensus (Cenário C)
- "O que Marks faria?" — resposta direta

### Seção 9 — Projeção de Meta

```html
<div class="formula">
FV = PV × (1+r)^n + PMT × [(1+r)^n - 1] / r

Patrimônio atual: R$ XX.XXX  |  Aporte: R$ X.XXX/mês
───────────────────────────────────────────────────
Cenário A: r=[X%/mês] → n=[X] meses ([X anos])
Cenário B: r=[X%/mês] → n=[X] meses ([X anos])
Cenário C: r=[X%/mês] → n=[X] meses ([X anos])
</div>
```

Nota obrigatória após a tabela.

### Seção 10 — Protocolo de Execução

Tabela final. Todos os ativos em carteira. Nenhum omitido.

Usar `style="color:var(--red)"` para 🔴, `style="color:var(--green)"` para 🟢, etc.

Se novo Checklist foi gerado, exibir box de salvamento no final:
```html
<div class="alert" style="margin-top:24px;font-size:13px;border-color:var(--accent);">
  💾 <strong>AÇÃO — Salvar Checklist de Ciclo:</strong><br>
  Checklist gerado nesta sessão. Para ancorar os multiplicadores na próxima análise,
  o arquivo foi salvo automaticamente em <code>./historico/checklist-ciclo.md</code>.
</div>
```

## Rodapé

```html
<hr>
<div style="text-align:center;padding:20px 0 0;color:var(--text3);font-size:11px;font-family:var(--mono);">
  Alpha-Gen v7.0 · Filosofia Howard Marks / Oaktree Capital · [DATA]<br>
  Análise para fins educacionais e de apoio à decisão. Não constitui recomendação profissional de investimentos.
</div>
```
