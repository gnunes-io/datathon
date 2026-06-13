# Datathon FIAP × Passos Mágicos — CLAUDE.md

## Visão Geral

Projeto de datathon acadêmico desenvolvido para a ONG **Passos Mágicos** (Embu-Guaçu, SP).
Objetivo: identificar precocemente alunos em risco de **defasagem escolar** (≥ 1 ano) usando
os indicadores coletados pela ONG nos anos 2022–2024.

Quatro entregáveis:
1. `eda/` — Análise Exploratória de Dados (12 perguntas)
2. `model/` — Modelo preditivo binário exportado como `.pkl`
3. `streamlit_app/` — App de apoio à decisão para pedagogos
4. `bot/` — Chat com 3 personas (Guia do Aluno / Painel do Gestor / Radar de Risco)

---

## Estrutura de Diretórios

```
.
├── data/
│   ├── DATATHON - 2022.csv      # encoding=latin1, ~860 alunos
│   ├── DATATHON - 2023.csv      # encoding=latin1, ~1.014 alunos
│   └── DATATHON - 2024.csv      # encoding=latin1, ~1.156 alunos
├── eda/
│   └── EDA_PassosMagicos.ipynb  # 44 células, 12 perguntas + cohort + completude
├── model/
│   ├── modelo_preditivo.ipynb   # 25 células — treina e exporta o modelo
│   └── modelo_risco_defasagem.pkl
├── streamlit_app/
│   ├── app.py
│   └── requirements.txt
└── bot/
    ├── index.html               # SPA com Tailwind — 3 personas
    ├── api/chat.js              # Vercel Serverless Function → OpenAI
    ├── vercel.json
    └── package.json
```

---

## Domínio — Indicadores da ONG

Escala 0–10 para todos os indicadores:

| Sigla | Descrição | Disponível |
|-------|-----------|------------|
| IAN | Adequação de Nível | 2022–2024 |
| IDA | Desempenho Acadêmico (Mat/Port/Ing) | 2022–2024 |
| IEG | Engajamento (presença, participação) | 2022–2024 |
| IAA | Autoavaliação do aluno | 2022–2024 |
| IPS | Indicador Psicossocial | 2022–2024 |
| IPP | Indicador Psicopedagógico | **2023–2024 apenas** |
| IPV | Ponto de Virada | 2022–2024 |
| INDE | Índice de Desenvolvimento Educacional (síntese) | 2022–2024 |

**Pedras classificatórias** (baseadas no INDE):
- Quartzo: INDE < 5.5
- Ágata: 5.5 ≤ INDE < 7.0
- Ametista: 7.0 ≤ INDE < 8.5
- Topázio: INDE ≥ 8.5

**Target do modelo:** `Defasagem >= 1` (binário) — aluno cursando fase ≥ 1 ano abaixo do esperado.

**Quirks dos CSVs:**
- Encoding `latin1` — sempre usar `pd.read_csv(..., encoding='latin1')`
- Decimais com vírgula — usar `str.replace(',', '.')` antes de `float()`
- Colunas com sufixo de ano: `INDE 2022`, `Pedra 2023`, etc. — buscar com `[c for c in df.columns if 'INDE' in c]`
- IPP ausente em 2022 — forçar `df22['IPP'] = np.nan`
- Coluna de gênero pode ter grafias distintas: `'F'`, `'M'`, `'Feminino'`, `'Masculino'`

---

## Modelo Preditivo

**Split temporal (não aleatório):**
- Treino: 2022 + 2023 (1.874 registros, 2.9% positivos)
- Teste: 2024 (1.156 registros, 11.9% positivos)
- O shift de distribuição 2.9% → 11.9% é documentado — o `scale_pos_weight` do XGBoost foi calibrado para o treino.

**Algoritmos:** Random Forest + XGBoost (compara ambos, usa o melhor por AUC-ROC)

**Métricas reais (conjunto de teste 2024):**
- Random Forest AUC-ROC: 0.759
- XGBoost AUC-ROC: 0.737

**Threshold:** calibrado por **Fbeta (β=2)** — penaliza falso negativo 2× mais que falso positivo, adequado para triagem educacional.

**Features (18 total):**
- 9 diretas: IAN, IDA, IEG, IAA, IPS, IPP, IPV, INDE, Fase
- 9 derivadas: `ind_academico_medio`, `ind_psico_medio`, `gap_ian_fase`, `inde_x_ian`, `baixo_ida`, `baixo_ieg`, `fase_sq`, `genero_cod`, `pedra_ord`

**Payload exportado no `.pkl`:**
```python
{
    'pipeline':     Pipeline(imputer + model),
    'feature_cols': [...],   # lista exata de 18 features na ordem certa
    'threshold':    float,   # threshold ótimo Fbeta β=2
    'model_name':   str,
    'auc_roc':      float,
    'ref_means':    dict,    # médias reais do treino para IAN/IDA/IEG/IAA/IPS/IPV/INDE
    'train_years':  [2022, 2023],
    'test_year':    2024
}
```

**Patch de compatibilidade sklearn** (aplicado no carregamento do pkl):
```python
for _, step in payload['pipeline'].steps:
    if hasattr(step, 'statistics_') and not hasattr(step, '_fill_dtype'):
        step._fill_dtype = step.statistics_.dtype
```

---

## App Streamlit

**Rodar localmente:**
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

O app procura o modelo em `../model/modelo_risco_defasagem.pkl`. Gere o pkl executando o notebook `model/modelo_preditivo.ipynb` antes de rodar o app.

**3 abas:**
- **Avaliação Individual:** sliders para todos os 8 indicadores + Fase + Gênero + Pedra → probabilidade de risco + radar de 7 indicadores (IAN, IDA, IEG, IAA, IPS, IPV, INDE) + recomendações acionáveis
- **Comparação de Perfis:** até 3 alunos lado a lado com IPP e Pedra editáveis
- **Como Funciona:** documentação do modelo com threshold e zonas de risco

**Médias de referência:** carregadas do `ref_means` no pkl (calculadas do treino real). Se o pkl for antigo e não contiver `ref_means`, usa fallback hardcoded.

**Zonas de risco:**
- Baixo: `prob < threshold`
- Médio: `threshold ≤ prob < threshold + 0.15`
- Alto: `prob ≥ threshold + 0.15`

---

## Bot de Chat

Hospedado via **Vercel** (Serverless Functions). Requer variável de ambiente `OPENAI_API_KEY` configurada no painel da Vercel.

**3 personas / modos:**
- `guia` — linguagem acolhedora para alunos, temperature 0.7
- `gestor` — analítico para gestores, temperature 0.7
- `radar` — alertas de risco, temperature 0.3 (mais determinístico)

**Fallback offline:** implementado em JS no `index.html` — o bot responde com heurísticas estáticas quando a API não está disponível (útil para demos sem backend).

**LGPD:** dados de indicadores de alunos enviados para a API da OpenAI. Em uso real, exige DPA com a OpenAI ou processamento local. O bot **não** coleta nomes — apenas indicadores numéricos.

---

## Decisões Técnicas Relevantes

- **Por que Fbeta (β=2) e não max-F1?** Em triagem educacional, deixar de identificar um aluno em risco (falso negativo) é mais custoso do que acionar a equipe desnecessariamente (falso positivo). β=2 reflete isso.
- **Por que split temporal?** O modelo é treinado no passado e usado para prever o futuro. Split aleatório vazaria informação temporal.
- **Por que `ref_means` no pkl?** O app precisa de médias reais do treino para comparação. Hardcodar no app desacoplaria o app do modelo — qualquer retrain mudaria as médias sem atualizar o app.
- **XGBoost pode descartar features** com zero variância após imputação (e.g. `genero_cod` se ausente no treino). O código de importância de features usa `get_booster().get_score()` com mapeamento `f{i}` → nome real para lidar com isso.

---

## Como Regenerar o Modelo

```
1. Execute eda/EDA_PassosMagicos.ipynb  (análise, não obrigatório para o modelo)
2. Execute model/modelo_preditivo.ipynb  (gera model/modelo_risco_defasagem.pkl)
3. streamlit run streamlit_app/app.py   (carrega o pkl automaticamente)
```

---

## Dependências Principais

| Pacote | Versão mínima | Uso |
|--------|---------------|-----|
| streamlit | 1.45.0 | App web |
| scikit-learn | 1.5.0 | Pipeline, imputer, RF |
| xgboost | 2.0.0 | Modelo principal |
| pandas | 2.2.3 | Manipulação de dados |
| numpy | 2.2.5 | Cálculos numéricos |
| joblib | 1.3.0 | Serialização do pkl |
| matplotlib | 3.7.0 | Radar, gráficos do app |
