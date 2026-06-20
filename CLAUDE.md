# Datathon FIAP × Passos Mágicos — CLAUDE.md

## Visão Geral

Projeto de datathon acadêmico desenvolvido para a ONG **Passos Mágicos** (Embu-Guaçu, SP).
Objetivo: identificar precocemente alunos em risco de **defasagem escolar** usando os
indicadores coletados pela ONG nos anos 2022–2024.

Quatro entregáveis:
1. `eda/` — Análise Exploratória de Dados (12 perguntas)
2. `model/` — Modelo preditivo binário exportado como `.pkl`
3. `streamlit_app/` — App de apoio à decisão para pedagogos ("🌟Passos Mágicos - Tech Hub")
4. `bot/` — Chat com 3 personas (Guia do Aluno / Painel do Gestor / Radar de Risco)

---

## Estrutura de Diretórios

```
.
├── data/
│   ├── DATATHON - 2022.csv          # encoding=latin1, ~860 alunos
│   ├── DATATHON - 2023.csv          # encoding=latin1, ~1.014 alunos
│   └── DATATHON - 2024.csv          # encoding=latin1, ~1.156 alunos
├── eda/
│   └── EDA_PassosMagicos.ipynb
├── model/
│   ├── modelo_preditivo.ipynb
│   └── modelo_risco_defasagem.pkl
├── streamlit_app/
│   ├── app.py                       # entry point — st.navigation() com seções
│   ├── utils.py                     # load_model, build_features, predict, risk_level, GLOBAL_CSS
│   ├── requirements.txt
│   ├── .streamlit/
│   │   └── config.toml              # tema PM (light, PM_BLUE sidebar via CSS)
│   └── _pages/                      # prefixo _ desativa auto-detecção do Streamlit
│       ├── home.py
│       ├── radar.py
│       ├── eda.py
│       ├── apresentacao.py          # placeholder
│       ├── arquitetura.py           # placeholder
│       └── staff.py                 # placeholder (CRUD futuro)
├── relatorio_atividades_2025_bia.md   # contexto 2025 curado para RAG da Bia
├── codigo_etica_conduta.md            # código de ética limpo para RAG da Bia
└── bot/
    ├── index.html                     # frontend da Bia (sem secrets — proxy via /api/chat)
    ├── api/chat.js                    # Vercel serverless: proxy seguro para n8n
    ├── vercel.json                    # outputDirectory: "." (zero-config)
    ├── package.json                   # node 24.x, sem dependências
    └── workflow_bia.json              # workflow n8n exportado (importar no n8n)
```

---

## Relatório de Atividades 2025 — Contexto do Cliente

Arquivo: `relatorio_de_atividades_2025.pdf` (74 páginas, na raiz do projeto).

**Números-chave 2025:**
- 1.200 aprendizes atendidos · 4 unidades em Embu-Guaçu · 63 colaboradores
- 120 crianças alfabetizadas fora da idade esperada
- 119 universitários cursando ou formados (65 cursando + 54 formados)
- 87 no mercado de trabalho · salário médio R$ 2.772
- 14.000+ horas de oficinas no PAC · 7.570 livros lidos
- Receita ~R$ 8,8M (doações PF 30,3%, FUMCAD 26,7%, Rouanet 10,3%)
- 40% dos formados proficientes em inglês (vs 5% da população brasileira no nível B1)

**Programas de Psicologia por fase (crítico para o app e o bot):**
| Fase | Programa |
|------|----------|
| Alfa | Heróis da Educação |
| 1    | Guardiões do Saber |
| 2    | Sabedoria em Ação |
| 3    | Exploradores do Saber |
| 4    | Jornada das Emoções |
| 5    | Quebrando Barreiras |
| 6    | SuperAção |
| 7    | Eu no Comando |
| 8    | Ponto de Virada |
| 9    | Conectando Passos |
| 10   | Passos em Carreiras |
| Pais | Passos em Família (56 encontros/ano) |

**Outros programas relevantes para recomendações:**
- IAN baixo → **Construindo Sonhos** (reforço Português + Matemática + simulados)
- IEG baixo → **Passos na Sua Casa** (visita domiciliar) + **Café em Família**
- IPS/contexto social → **Serviço Social**: entrevistas, cestas básicas, Mães no Mercado
- Inglês → **Speed Up** (voluntários internacionais, +40% proficiência) + **Canada Experience** (7/ano)
- Tecnologia → **Sala Cibernética** (F3-F4) + **Jovens Inventores** (robótica LEGO — premiado Poliedro 2025)
- Vestibular → **Vem Ser** (Me Salva!) — 30 aprovados em 2025
- Moradia em SP → **Casa Mágica** (31 aprendizes, 5 apartamentos, custeio integral)

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

**Fases do PAC:** Alfa (alfabetização, mapeada para 0 numericamente) + Fases 1–9 nos dados 2022–2024.
O relatório 2025 introduz Fase 10 (15 aprendizes), ainda fora do treino do modelo.
O formulário do app expõe todas as opções: Alfa (0), 1, 2, … 9.

**Pedras classificatórias** (derivadas automaticamente do INDE — não são input do usuário):
- Quartzo: INDE < 5,5
- Ágata: 5,5 ≤ INDE < 7,0
- Ametista: 7,0 ≤ INDE < 8,5
- Topázio: INDE ≥ 8,5

**Quirks dos CSVs:**
- Encoding `latin1` — sempre `pd.read_csv(..., encoding='latin1')`
- Decimais com vírgula — `str.replace(',', '.')` antes de `float()`
- 2022 usa sufixo curto: `'INDE 22'`, `'Pedra 22'` (não `'INDE 2022'`) — usar `find_col()` helper
- Fase em 2023 é texto `'FASE 2'`, `'ALFA'`; em 2024 é `'7E'`, `'4M'` — usar `parse_fase()` regex
- IPP ausente em 2022 — imputado pela mediana histórica do treino
- Gênero tem grafias mistas: `'F'`/`'M'` em 2022, `'Feminino'`/`'Masculino'` em 2023–2024

---

## Modelo Preditivo

**Target composto (decisão definitiva):**
```python
target = (Defasagem >= 1) | (INDE < 5.5)
```
Captura tanto defasagem formal (aluno cursando fase abaixo da esperada para a idade)
quanto Quartzo (pior faixa de desenvolvimento — INDE < 5,5).

**Treinamento — todos os 3 anos com validação cruzada OOF:**
- Dados: 2022 + 2023 + 2024 (~3.030 registros após limpeza)
- Validação: 5-fold Stratified K-Fold (OOF — sem leakage)
- Threshold calibrado nas predições OOF por Fbeta (β=2)

**Algoritmo final:** Random Forest (XGBoost descartado — probabilidades OOF divergem do modelo
final treinado em todos os dados quando `scale_pos_weight` é usado)

**Métricas (pkl atual):**
- AUC-ROC OOF: **0.9695**
- Threshold Fbeta β=2: **0.61**
- Positivos no treino: ~30% (target composto)

**Features (18 declaradas, 17 efetivas):**
- 9 diretas: IAN, IDA, IEG, IAA, IPS, IPP, IPV, INDE, Fase
- 9 derivadas: `ind_academico_medio`, `ind_psico_medio`, `gap_ian_fase`, `inde_x_ian`,
  `baixo_ida`, `baixo_ieg`, `fase_sq`, `genero_cod`, `pedra_ord`
- **`genero_cod` é sempre NaN** (gênero inconsistente nos CSVs) → sklearn 1.6+ SimpleImputer
  dropa a coluna → pipeline efetivamente opera com 17 features

**Importância das features (RF, ordem decrescente):**
INDE (15,2%) · inde_x_ian (13,9%) · gap_ian_fase (12,8%) · Fase (12,2%) · fase_sq (9,7%)
· ind_academico_medio (8,8%) · IAN (7,8%) · pedra_ord (4,9%) · IEG (4,3%) · IPV (2,2%)
· IDA (2,0%) · ind_psico_medio (1,6%) · IPP (1,2%) · IAA (0,8%) · IPS (0,6%)

**Payload exportado no `.pkl`:**
```python
{
    'pipeline':       Pipeline([('imputer', SimpleImputer), ('model', RandomForestClassifier)]),
    'feature_cols':   [...],      # 18 nomes (inclui genero_cod)
    'threshold':      0.61,       # Fbeta β=2 OOF
    'model_name':     'Random Forest',
    'auc_roc':        0.9695,     # OOF
    'ref_means':      dict,       # médias do treino: IAN/IDA/IEG/IAA/IPS/IPV/INDE
    'shap_explainer': TreeExplainer,
    'train_years':    [2022, 2023, 2024],
    'val_year':       None,
    'test_year':      None,
}
```

**Compatibilidade sklearn:**
```python
# Patch para versões antigas sem _fill_dtype
for _, step in payload['pipeline'].steps:
    if hasattr(step, 'statistics_') and not hasattr(step, '_fill_dtype'):
        step._fill_dtype = step.statistics_.dtype

# SHAP: usar valid_mask para mapear 17 colunas efetivas
imp = pipeline.named_steps['imputer']
valid_mask = ~np.isnan(imp.statistics_)
valid_cols = [c for c, v in zip(feature_cols, valid_mask) if v]
# SHAP retorna (1, 17, 2) — normalizar para (17,) e indexar com valid_cols
```

---

## App Streamlit

**Rodar localmente:**
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

O app procura o modelo em `../model/modelo_risco_defasagem.pkl`.

**Navegação — 3 seções na sidebar + links externos:**
```
Ferramentas:     🏠 Início · 🎯 Radar de Risco · 📊 Análise Rápida
Apresentação:    🎬 Vídeo Apresentação · 🏗️ Arquitetura
Equipe:          👥 Staff PsicoNeuroPedagogia

Links externos (placeholder google.com):
🤖 Assistente Pedagógico · 📓 Notebooks · 🐙 GitHub · 📄 PDF Executivo
```

**Por que `_pages/` e não `pages/`:**
A pasta `pages/` ativa a detecção automática legada do Streamlit, que ignora o `st.navigation()`
e exibe nomes de arquivo crus na sidebar. O prefixo `_` desativa esse comportamento.

**Zonas de risco:**
- 🟢 Baixo: `prob < 0.40`
- 🟠 Médio: `0.40 ≤ prob < threshold (0.61)`
- 🔴 Alto: `prob ≥ threshold`

**Fatores de atenção — prioridade por importância do modelo:**
```
Prioridade: INDE → IAN → IEG → IDA → IPV → IPP → IAA → IPS
Crítico (🔴): val < 5.0  → ação (_IND_ACTIONS) + programa da fase (_action_for_fase)
Atenção (🟡): 5.0 ≤ val < ref_mean → programa da fase se aplicável
Positivo (✅): val ≥ ref_mean
```
`_action_for_fase(ind, fase)` retorna o programa PM específico da fase para IAA/IPS/IPV/IPP
(ex.: Fase 4 + IAA baixo → "Jornada das Emoções"). Para IDA fase ≥ 8 sugere Vem Ser.

**Formulário — o que NÃO é coletado do usuário:**
- Nome/ID (não é feature)
- Gênero (sempre NaN no treino, 0% importância)
- Pedra (derivada automaticamente do INDE — `inde_to_pedra()` em radar.py)

**Staff page** (`_pages/staff.py`): populada com equipe real do Relatório 2025.
Seções: Fundadores · Coordenação Pedagógica · Psicologia · Psicopedagogia ·
Neuropsicopedagogia · Assistência Social · Equipe Pedagógica (tabs por disciplina).

**Home page** (`_pages/home.py`): seção de impacto com 6 métricas reais (1.200 aprendizes,
4 unidades, 119 universitários, 87 no mercado, 120 alfabetizados, +14.000h PAC) +
jornada do aprendiz visualizada em 6 etapas.

**SHAP — gotcha sklearn 1.6+:**
`genero_cod` all-NaN → imputer dropa a coluna → `X_imp` shape `(1, 17)` →
SHAP retorna `(1, 17, 2)`. Usar `valid_cols` (17 features não-NaN) para indexar o Series,
não `feature_cols` (18). Chamar com `check_additivity=False`.

---

## Bot de Chat — Bia (Psicopedagoga Virtual)

O bot evoluiu de "3 personas" para a **Bia**, assistente psicopedagógica única focada em alunos.

### Arquitetura

```
[index.html] → POST /api/chat → [api/chat.js Vercel] → n8n webhook /bia
                                       ↑
                              N8N_WEBHOOK_URL + WEBHOOK_SECRET
                              (env vars Vercel — NUNCA no frontend)
```

**n8n workflow** (`workflow_bia.json`):
```
Receber Mensagem (webhook POST /bia, header auth)
  → Preparar Dados (extrair message + sessionId)
  → Bia Psicopedagoga (AI Agent GPT-4o-mini)
      ├── Memória Redis (sessionKey = sessionId, janela 20 msgs)
      ├── BuscarAluno (Supabase tool — tabela alunos, filtro ra = RA-XXXX)
      └── ConhecimentosPM (Vector Store tool → Pinecone passosmagicos)
            ├── GPT-4o-mini RAG (LLM do retriever)
            ├── Pinecone PM (index passosmagicos)
            └── Embeddings PM (text-embedding-3-small)
  → Resposta OK (respondToWebhook com JSON { reply })
```

**Workflow de ingestão RAG** (mesmo arquivo, seção separada):
```
Manual Trigger → Google Drive (download .md) → Insert Pinecone
  Sub-nodes: Embeddings OpenAI1 (text-embedding-3-small)
             Default Data Loader (binary)
             Recursive Character Text Splitter (chunk 1000, overlap 150)
```

### Credenciais n8n necessárias
| Credencial | Uso |
|---|---|
| OpenAI API Key | GPT-4o-mini (agente) + GPT-4o-mini RAG + Embeddings |
| Redis | Memória de conversa por sessionId |
| Supabase URL + Service Key | BuscarAluno (tabela `alunos`) |
| Pinecone API Key | ConhecimentosPM + ingestão RAG |
| Header Auth | Validação do x-webhook-secret no webhook |
| Google Drive OAuth2 | Download dos .md para ingestão |

### Variáveis de ambiente Vercel
| Variável | Valor |
|---|---|
| `N8N_WEBHOOK_URL` | URL de produção `/webhook/bia` (NÃO `/webhook-test/bia`) |
| `WEBHOOK_SECRET` | Mesmo valor configurado no Header Auth do n8n |

### Supabase — tabela `alunos`
- 3.030 linhas, dados anonimizados do Datathon
- RA no formato `RA-XXXX` (ex: RA-1, RA-42, RA-3030)
- `nome` anonimizado: Aluno-1 … Aluno-3030 — **nunca mostrar ao aluno**
- Colunas: id, ra, nome, fase, ano, inde, pedra, ian, ida, ieg, iaa, ips, ipp, ipv, defasagem

### Pinecone — índice RAG
- Index: `passosmagicos`
- **Dimensões: 1536** (text-embedding-3-small padrão — NÃO usar 512)
- Metric: cosine
- Documentos indexados: `relatorio_atividades_2025_bia.md` + `codigo_etica_conduta.md`
- Manter separados (domínios semânticos distintos: programas vs ética)
- Chunk size recomendado: 1000 chars, overlap 150

### Arquitetura do prompt (decisão desta sessão)
O prompt atual mistura identidade, regras, fluxos e lógica de recomendação. A evolução planejada:

**Fase atual (MVP):** tudo no system prompt + RAG
**Próxima fase:** adicionar nó `ProcessarPerfil` entre BuscarAluno e o agente:
```javascript
// Nó Code no n8n — gera JSON estruturado antes do LLM
const dados = $input.first().json[0];
const forca = calcularForca(dados);      // indicador mais alto
const atencao = calcularAtencao(dados);  // indicador mais baixo
const recomendacoes = gerarRecomendacoes(dados); // regras estruturadas
return { forca, atencao, recomendacoes, pedra: dados.pedra, fase: dados.fase };
```
Isso reduz alucinações: o LLM só transforma JSON em conversa, não decide regras.

**Exemplos few-shot** substituem regras longas — modelos aprendem melhor por exemplo do que por instrução.

### Testes realizados e resultados
| Cenário | Status | Observação |
|---|---|---|
| Abertura sem RA | ✅ | Pede RA antes de ajudar (fix desta sessão) |
| Off-topic (Ferrari) | ✅ | Redireciona com leveza |
| RA válido + dados | ✅ | BuscarAluno dispara, celebra positivo primeiro |
| Pedir nome | ⚠️ | Às vezes pula, mas pega quando aluno diz natural |
| Recomendação correta | ✅ | Construindo Sonhos para IDA baixo |
| RAG (Vem Ser) | ❌ | Pinecone vazio — bloqueador pré-produção |
| Crise / CVV 188 | ✅ | Acolhe + orienta CVV sem diagnóstico |
| RA inválido | ✅ | Resposta acolhedora, orienta coordenação |

### Segurança
- Secrets **NUNCA** no frontend JS (`index.html`)
- `api/chat.js` é o único lugar com acesso a `N8N_WEBHOOK_URL` e `WEBHOOK_SECRET`
- n8n valida `x-webhook-secret` em todo request
- LGPD: indicadores numéricos enviados à OpenAI — em produção exige DPA ou processamento local

---

## Decisões Técnicas Relevantes

- **Target composto** `(Defasagem ≥ 1) | (INDE < 5,5)`: o target original (`Defasagem ≥ 1`)
  captura apenas defasagem formal de série, que é dominada por alunos com IAN=10 em Fase 9.
  O modelo não respondia a variações de indicadores acadêmicos. O INDE < 5,5 (Quartzo) foi
  adicionado para capturar risco real de aprendizado.

- **Random Forest sobre XGBoost:** o `scale_pos_weight` do XGBoost causa divergência entre
  as probabilidades OOF e as probabilidades do modelo final treinado em todos os dados.
  O threshold calibrado no OOF não se transfere. RF tem probabilidades naturalmente calibradas.

- **Todos os 3 anos no treino + OOF:** sem conjunto de teste separado — o modelo usa todos os
  dados disponíveis. A validade é estimada pelas predições OOF (cada sample foi predita por
  um fold no qual não participou do treino).

- **Fbeta (β=2):** falso negativo (deixar de identificar aluno em risco) custa 2× mais que
  falso positivo (acionamento desnecessário) — adequado para triagem educacional.

- **`ref_means` no pkl:** médias reais do treino para comparação no app. Hardcodar no app
  desacoplaria as médias do modelo — qualquer retrain mudaria as referências sem atualizar o app.

- **Pedra derivada do INDE no app:** usuário não seleciona pedra — ela é calculada em tempo real
  a partir do INDE inserido. Evita inconsistência (usuário informar Topázio com INDE=4,0).

---

## Como Regenerar o Modelo

```
1. Execute model/modelo_preditivo.ipynb  (gera model/modelo_risco_defasagem.pkl)
2. Reinicie o Streamlit: Ctrl+C → streamlit run app.py
   (@st.cache_resource mantém o pkl antigo até reiniciar o servidor)
```

---

## Dependências Principais

| Pacote | Versão mínima | Uso |
|--------|---------------|-----|
| streamlit | 1.45.0 | App web + st.navigation() |
| scikit-learn | 1.5.0 | Pipeline, SimpleImputer, RandomForest |
| xgboost | 2.0.0 | Comparação no notebook |
| shap | 0.44.0 | TreeExplainer para explicabilidade por aluno |
| pandas | 2.2.3 | Manipulação de dados |
| numpy | 2.2.5 | Cálculos numéricos |
| joblib | 1.3.0 | Serialização do pkl |
| plotly | 5.18.0 | Radar chart + SHAP bar chart |
