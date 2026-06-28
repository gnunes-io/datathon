# Datathon FIAP × Passos Mágicos — CLAUDE.md

## Visão Geral

Projeto de datathon acadêmico desenvolvido para a ONG **Passos Mágicos** (Embu-Guaçu, SP).
Objetivo: identificar precocemente alunos em risco de **defasagem escolar** usando os
indicadores coletados pela ONG nos anos 2022–2024.

Quatro entregáveis:
1. `eda/` — Análise Exploratória de Dados (12 perguntas)
2. `model/` — Modelo preditivo binário exportado como `.pkl`
3. `streamlit_app/` — App de apoio à decisão para pedagogos ("🌟Passos Mágicos - Tech Hub")
4. `bot/` — Bia, assistente psicopedagógica virtual (chat HTML/JS + n8n + OpenAI + RAG)

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
│   ├── assets/                      # imagens estáticas usadas pelas pages
│   │   ├── bia_intro.png            # personagem Bia (retrato bust, usado em bot.py)
│   │   ├── Arquitetura_Bia.png      # diagrama de arquitetura do sistema
│   │   ├── Passos-magicos-icon-cor.png
│   │   ├── bia.png                  # logo stack: HTML+JS
│   │   ├── openapi.png              # logo stack: OpenAI API
│   │   ├── n8n.png                  # logo stack: n8n
│   │   ├── pinecone.png             # logo stack: Pinecone
│   │   ├── supabase.png             # logo stack: Supabase
│   │   └── vercel.png               # logo stack: Vercel
│   └── _pages/                      # prefixo _ desativa auto-detecção do Streamlit
│       ├── home.py
│       ├── radar.py
│       ├── eda.py
│       ├── bot.py                   # página Bia — tema lavanda, logos stack, CTA
│       ├── apresentacao.py          # placeholder
│       ├── arquitetura.py           # placeholder
│       └── staff.py                 # placeholder (CRUD futuro)
└── bot/
    ├── index.html                   # frontend Bia (HTML/JS, mobile-friendly, sem secrets)
    ├── api/chat.js                  # Vercel serverless: proxy seguro para n8n
    ├── vercel.json                  # outputDirectory: "." (zero-config)
    ├── package.json                 # node 24.x, sem dependências
    ├── bia_avatar.png               # avatar da Bia usado no chat
    └── RAG/
        ├── relatorio_atividades_2025_bia.md  # contexto 2025 curado para ingestão
        └── codigo_etica_conduta.md           # código de ética para ingestão
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

**Bia page** (`_pages/bot.py`): tema lavanda completo (override do PM blue via CSS injection).
Seções: hero com círculos decorativos, "Por que criamos a Bia?" (imagem + texto + 8 tags),
"Como a Bia funciona" (6 cards com efeitos decorativos), arquitetura, stack tecnológico,
galeria, CTA final.

**CSS scoping de imagens — gotcha Streamlit:**
`st.image()` não aceita classes. Para aplicar estilos só em imagens específicas (ex.: logos
do stack) sem afetar outras da página, usar marcador + seletor `:has()`:
```python
st.markdown('<div class="logo-marker"></div>', unsafe_allow_html=True)
st.image(img_path, use_container_width=True)
```
```css
[data-testid="stMarkdown"]:has(.logo-marker) + [data-testid="stImage"] img {
    height: 68px !important; object-fit: contain;
}
```

**HTML inline em `st.markdown()` — gotcha indentação:**
Streamlit interpreta linhas com 4+ espaços iniciais como bloco de código Markdown.
Sempre usar string concatenada (`'<div>' + f'<span>{x}</span>' + '</div>'`) em vez de
f-strings multi-linha com indentação.

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

**n8n workflow** (`PsicopedaBia.json`):
```
Receber Mensagem (webhook POST /bia, header auth)
  → Preparar Dados (extrair message + sessionId)
  → Bia Psicopedagoga (AI Agent GPT-4o-mini)
      ├── Memória Redis (sessionKey = sessionId, janela 20 msgs)
      ├── BuscarAluno (Supabase tool — tabela passos_magicos, filtro ra = RA-XXXX)
      └── ConhecimentosPM (Vector Store tool → Pinecone magis-steps)
            ├── GPT-4o-mini RAG (LLM do retriever)
            ├── Pinecone PM (index magis-steps)
            └── Embeddings PM (text-embedding-3-small, 1536 dims)
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
| Supabase URL + Service Key | BuscarAluno (tabela `passos_magicos`) |
| Pinecone API Key | ConhecimentosPM + ingestão RAG |
| Header Auth | Validação do x-webhook-secret no webhook |
| Google Drive OAuth2 | Download dos .md para ingestão |

### Variáveis de ambiente Vercel
| Variável | Valor |
|---|---|
| `N8N_WEBHOOK_URL` | URL de produção `/webhook/bia` (NÃO `/webhook-test/bia`) |
| `WEBHOOK_SECRET` | Mesmo valor configurado no Header Auth do n8n |

### Supabase — tabela `passos_magicos`
- 3.030 linhas, dados anonimizados do Datathon
- RA no formato `RA-XXXX` (ex: RA-1, RA-42, RA-3030)
- `nome` anonimizado: Aluno-1 … Aluno-3030 — **nunca mostrar ao aluno**
- Colunas: id, ra, nome, fase, ano, inde, pedra, ian, ida, ieg, iaa, ips, ipp, ipv, defasagem

### Pinecone — índice RAG
- Index: `magis-steps`
- **Dimensões: 1536** (text-embedding-3-small — NÃO usar 512)
- Metric: cosine
- Documentos indexados: `relatorio_atividades_2025_bia.md` + `codigo_etica_conduta.md` (ingeridos manualmente, um de cada vez)
- Chunk size: 1000 chars, overlap 150

### ConhecimentosPM — configuração da UI (não serializada no JSON)
Campos visíveis no n8n que não aparecem no `PsicopedaBia.json` exportado:
- **Data Name**: usar `PassosMagicos` (sem espaços) — gera a frase "Useful for when you need to answer questions about PassosMagicos..." que o LLM lê para decidir quando chamar o tool. Evitar nomes técnicos como `magissteps`.
- **Limit**: 8 chunks retornados por consulta
- **Embeddings PM**: `text-embedding-3-small` + 1536 dims (deve bater com o modelo de ingestão)

### Arquitetura do prompt (versão atual)

O prompt é estruturado em camadas determinísticas para maximizar confiabilidade com GPT-4o-mini:

1. **ORDEM DE DECISÃO** — sequência executada a cada mensagem: crise → institucional → RA → BuscarAluno → nome → resposta
2. **REGRA DE FERRAMENTAS** — sempre chamar ferramenta antes de responder, nunca o contrário
3. **ESTADOS 1–7** — fluxo explícito: AGUARDANDO_RA → BUSCANDO_DADOS → AGUARDANDO_NOME → ACOLHIMENTO_INICIAL → EXPLORANDO_DESAFIO → RECOMENDANDO_APOIO → CRISE
4. **REGRA CRÍTICA ConhecimentosPM** — obrigatório para qualquer tema institucional; nunca usar memória do modelo
5. **Exemplos few-shot** — calibram comportamento por exemplo, não só por regra

**Sem RA:** permitido responder sobre ONG, programas e valores via ConhecimentosPM — RA só exigido para personalização.
**Com RA:** após ESTADO 3 (nome confirmado) — nunca descrever programa sem consultar ConhecimentosPM.
**Recomendações:** seção de routing interno (indicador → programa) sem descrições — descrições sempre vêm do RAG.

### Testes realizados e resultados (prompt v3 — com ESTADOS)
| Cenário | Status | Observação |
|---|---|---|
| Programa sem RA (Construindo Sonhos) | ✅ | Respondeu sem pedir RA — regra institucional funciona |
| RA formato `0042` informal | ✅ | Extraiu `RA-42` corretamente, BuscarAluno disparou |
| Anti-despejo de indicadores | ✅ | Recusou listagem mesmo quando pedido explicitamente |
| Crise emocional / CVV 188 | ✅ | ESTADO 7 perfeito — zero menção a indicadores ou programas |
| Off-topic (Copa do Mundo) | ✅ | Redirecionou com leveza |
| ESTADO 3 (pedir nome após BuscarAluno) | ⚠️ | Às vezes pula — fix aplicado: "vá para ESTADO 3 antes de qualquer comentário" |
| ConhecimentosPM chamado para perguntas institucionais | ⏳ | Speed Up confirmou RAG ativo; Construindo Sonhos pendente confirmação no n8n |

### Mobile-friendly — `bot/index.html`
Layout refatorado para ser keyboard-safe em iOS/Android:
- `textarea` com `font-size: 16px` — abaixo disso iOS Safari faz zoom automático no foco
- `body`: `display:flex; flex-direction:column; height:100dvh` — sem `calc()` fixo
- `<main>`: `flex:1; min-height:0; overflow-y:auto` — scroll nativo, sem altura calculada
- `<footer>` (barra de input): substitui `position:fixed` — reflui corretamente com o teclado
- `viewport-fit=cover` + meta apple PWA para notch/home indicator
- `overscroll-behavior:none` no body, `touch-action:manipulation` nos botões

### Segurança
- Secrets **NUNCA** no frontend JS (`index.html`)
- `api/chat.js` é o único lugar com acesso a `N8N_WEBHOOK_URL` e `WEBHOOK_SECRET`
- n8n valida `x-webhook-secret` em todo request
- LGPD: indicadores numéricos enviados à OpenAI — em produção exige DPA ou processamento local

---

## Regras de Deploy / Push

- **`bot/`** → pushar sempre para **dois** repositórios:
  1. `gnunes-io/datathon` (este repo, pasta `bot/`)
  2. `gnunes-io/passos_magicos_html` (repo separado em `C:\Users\gabri\passos_magicos_html_tmp\`)
     — copiar o `bot/index.html` atualizado para lá e commitar/pushar.
- **Demais pastas** (`streamlit_app/`, `eda/`, `model/`, etc.) → somente `gnunes-io/datathon`.

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
