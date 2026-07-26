# [Passos Mágicos — Radar de Risco de Defasagem Escolar](https://datathon-dtsw05.streamlit.app/)

![Status do Projeto](https://img.shields.io/badge/Status-Finalizado-success)
![AUC-ROC](https://img.shields.io/badge/AUC--ROC_OOF-96%2C95%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/Uso-Acadêmico-lightgrey)

## Sobre o Projeto

Este é o **Tech Hub Passos Mágicos**, um sistema de apoio à decisão pedagógica desenvolvido para o Datathon FIAP × Passos Mágicos (ONG de Embu-Guaçu, SP). O objetivo é identificar **precocemente** alunos em risco de **defasagem escolar** a partir dos indicadores socioemocionais e acadêmicos coletados pela ONG entre 2022 e 2024.

Em vez de esperar a defasagem formal se manifestar (aluno cursando uma fase abaixo da esperada para a idade), o modelo combina esse sinal com o **INDE** (Índice de Desenvolvimento Educacional) para capturar também o risco de aprendizado real — alunos na pior faixa de desenvolvimento (Quartzo, INDE < 5,5) mesmo sem defasagem formal registrada. Isso dá ao pedagogo uma janela de intervenção antes que o problema apareça no boletim.

O projeto tem quatro entregáveis integrados: uma **EDA** com 12 perguntas analíticas, um **modelo preditivo binário** exportado como `.pkl`, um **app Streamlit** de apoio à decisão para pedagogos, e a **Bia**, assistente psicopedagógica virtual com RAG.

---

## 🚀 Principais Destaques

* **Target Composto Além da Defasagem Formal:** `(Defasagem ≥ 1) | (INDE < 5,5)`. O target isolado de defasagem formal é dominado por alunos com IAN=10 na Fase 9 e não reage a variações de indicadores acadêmicos — o INDE < 5,5 (Quartzo) foi adicionado para capturar risco real de aprendizado.
* **Validação Sem Leakage, Três Anos Combinados:** 5-fold Stratified K-Fold Out-Of-Fold (OOF) sobre 2022+2023+2024 combinados, sem conjunto de teste separado — cada amostra é avaliada por um fold no qual não participou do treino.
* **Threshold Calibrado para Triagem Educacional:** Fbeta (β=2) sobre as probabilidades OOF, penalizando falso negativo (deixar de identificar um aluno em risco) duas vezes mais que falso positivo.
* **Explicabilidade por Aluno:** SHAP TreeExplainer integrado ao app, mostrando quais indicadores mais pesaram na predição individual, com recomendação do programa PM específico da fase do aluno.
* **Bia — Psicopedagoga Virtual com RAG:** chat que combina memória de conversa (Redis), busca semântica em documentos institucionais (Pinecone) e dados reais do aluno (Supabase) via agente GPT-4o-mini orquestrado em n8n.

Com um **Random Forest** calibrado sobre validação cruzada OOF, o modelo atinge resultados sólidos para triagem em escala:

| Métrica | Resultado | Descrição |
| :--- | :--- | :--- |
| **AUC-ROC (OOF)** | **0,9695** | Separabilidade entre alunos em risco e fora de risco, sem vazamento de dados. |
| **Threshold (Fbeta β=2)** | **0,61** | Ponto de corte calibrado para minimizar falsos negativos na triagem. |
| **Validação** | **5-fold Stratified K-Fold OOF** | Sem conjunto de teste isolado — todo o histórico 2022–2024 é usado no treino final. |
| **Algoritmo final** | **Random Forest** | Preferido ao XGBoost, cujo `scale_pos_weight` desalinha as probabilidades OOF do modelo final. |
| **Positivos no treino** | **~30%** | Proporção de alunos classificados em risco pelo target composto. |

---

## Engenharia de Dados e Modelagem

O projeto segue um pipeline linear e auditável, documentado em [`model/modelo_preditivo.ipynb`](model/modelo_preditivo.ipynb):

### 1. Coleta de Dados (`Data Ingestion`)
* **Fonte:** três CSVs anuais da Passos Mágicos (`DATATHON - 2022/2023/2024.csv`), ~3.030 registros combinados, encoding `latin1`.
* **Quirks tratados:** decimais com vírgula, nomenclatura de colunas inconsistente entre anos (`'INDE 22'` vs `'INDE 2023'`), formato de fase em texto livre (`'FASE 2'`, `'7E'`, `'ALFA'`), grafias mistas de gênero.
* **IPP ausente em 2022** — imputado pela mediana histórica do treino.

### 2. Engenharia de Features
9 indicadores diretos (IAN, IDA, IEG, IAA, IPS, IPP, IPV, INDE, Fase) mais 9 features derivadas para capturar interações não lineares:

* `ind_academico_medio`, `ind_psico_medio` — médias compostas por domínio.
* `gap_ian_fase`, `inde_x_ian`, `fase_sq` — interação entre nível de adequação e progressão de fase.
* `baixo_ida`, `baixo_ieg` — flags de indicadores críticos.
* `pedra_ord` — ordinal da classificação Quartzo/Ágata/Ametista/Topázio, derivada do INDE.
* `genero_cod` — sempre `NaN` (gênero inconsistente nas três bases) e descartado automaticamente pelo `SimpleImputer`, deixando 17 features efetivas.

### 3. Validação Cruzada Sem Vazamento
* `StratifiedKFold(5)` sobre os três anos combinados, garantindo representatividade da classe minoritária em cada fold.
* Sem hold-out separado — a validade é estimada inteiramente pelas predições **Out-Of-Fold**, e o modelo final é retreinado em 100% dos dados.
* Threshold de decisão calibrado nas predições OOF (Fbeta β=2), não no modelo final, evitando otimismo.

### 4. Modelagem e Avaliação
* **Pipeline sklearn:** `SimpleImputer` + `RandomForestClassifier`, serializado com `joblib` junto de `feature_cols`, `threshold`, `ref_means` (médias do treino para comparação no app) e o `shap_explainer`.
* **Métricas avaliadas:** AUC-ROC OOF, Fbeta (β=2), importância de features via Random Forest.

### 5. Modelos Avaliados

* **Random Forest (modelo final — AUC-ROC 0,9695 OOF)**
  Probabilidades naturalmente calibradas; robusto às 17 features com correlação entre si (INDE, inde_x_ian, gap_ian_fase dominam a importância).
* **XGBoost (descartado)**
  O `scale_pos_weight` necessário para lidar com o desbalanceamento faz as probabilidades OOF divergirem das probabilidades do modelo final treinado em todos os dados — o threshold calibrado no OOF deixa de ser válido.

---

## 📊 Resultados Alcançados

O modelo classifica o risco de defasagem de cada aluno a partir de indicadores já coletados pela ONG, sem necessidade de dados adicionais:

* **AUC-ROC (OOF):** 0,9695 — excelente separabilidade entre alunos em risco e fora de risco.
* **Feature mais importante:** INDE (15,2%), seguida de `inde_x_ian` (13,9%) e `gap_ian_fase` (12,8%).
* **Threshold operacional:** 0,61, calibrado para o custo assimétrico da triagem educacional (Fbeta β=2).
* **Zonas de risco no app:** 🟢 Baixo (`prob < 0,40`) · 🟠 Médio (`0,40 ≤ prob < 0,61`) · 🔴 Alto (`prob ≥ 0,61`).

---

## Arquitetura do Sistema

```
data/           CSVs anuais da Passos Mágicos (2022-2024, git-ignored fonte bruta)
eda/            Notebook de Análise Exploratória (12 perguntas)
model/          Notebook de treino + modelo_risco_defasagem.pkl
streamlit_app/  App multipage (Radar de Risco, Quick Insights, Bia, Staff, Notebooks...)
bot/            Frontend da Bia (HTML/JS) + proxy serverless Vercel
```

**Fluxo de dados:**
- **Treino (offline):** `data/*.csv` → `eda/EDA_PassosMagicos.ipynb` → `model/modelo_preditivo.ipynb` → `model/modelo_risco_defasagem.pkl`
- **Inferência (runtime):** Formulário `streamlit_app/_pages/radar.py` → `utils.predict()` (pipeline + threshold) → probabilidade de risco + explicação SHAP + recomendação de programa PM
- **Suporte pedagógico (chat):** `streamlit_app/_pages/bot.py` → `bot/index.html` → proxy Vercel → workflow n8n (agente GPT-4o-mini + memória Redis + RAG Pinecone + dados Supabase)

---

## Executando o Projeto

### Pré-requisitos
* Python 3.10+
* Modelo treinado em `model/modelo_risco_defasagem.pkl` (gerado por `model/modelo_preditivo.ipynb`)

### Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/DeleteTableSemWhere/Passos-Magicos.git
    cd Passos-Magicos
    ```

2. Instale as dependências do app:
    ```bash
    cd streamlit_app
    pip install -r requirements.txt
    ```

### Execução

```bash
# (Re)treinar o modelo, opcional — o .pkl já vem versionado no repositório
jupyter notebook model/modelo_preditivo.ipynb

# Rodar a aplicação
cd streamlit_app
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`.

---

## Páginas da Aplicação

| Página | Descrição |
| :--- | :--- |
| **Início** | Contexto do projeto e jornada do aprendiz na Passos Mágicos |
| **Radar de Risco** | Formulário de predição individual com zona de risco, SHAP e recomendação de programa |
| **Quick Insights** | Dashboard EDA interativo: distribuições, evolução por ano, funil de risco por fase |
| **Assistente Psicopedagógico** | Apresentação da Bia — assistente virtual com RAG e acesso aos dados do aluno |
| **Vídeo / Arquitetura / PDF Executivo** | Material de apresentação do projeto |
| **Notebooks** | Preview embutido dos notebooks de EDA e modelagem via nbviewer |
| **GitHub** | Link para o repositório do projeto |
| **Staff PsicoNeuroPedagogia** | Equipe real de Psicologia, Psicopedagogia e Assistência Social da ONG |

---

## Autores

Desenvolvido como parte do Datathon FIAP × Passos Mágicos.

<div align="center">
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/BrunoAssis12">
        <img src="https://github.com/BrunoAssis12.png" width="100px;" alt=""/>
        <br /><sub><b>Bruno Assis</b></sub>
      </a><br />
      🚀 Data Scientist
    </td>
    <td align="center">
      <a href="https://github.com/gnunes-io">
        <img src="https://github.com/gnunes-io.png" width="100px;" alt=""/>
        <br /><sub><b>Gabriel Nunes</b></sub>
      </a><br />
      ⚙️ Data Architect
    </td>
    <td align="center">
      <a href="https://github.com/Jonathan-Paixao">
        <img src="https://github.com/Jonathan-Paixao.png" width="100px;" alt=""/>
        <br /><sub><b>Jonathan Paixão</b></sub>
      </a><br />
      🐍 Python Dev
    </td>
    <td align="center">
      <a href="https://github.com/rafaelvieiravidal-glitch">
        <img src="https://github.com/rafaelvieiravidal-glitch.png" width="100px;" alt=""/>
        <br /><sub><b>Rafael Vieira</b></sub>
      </a><br />
      📉 Quant
    </td>
    <td align="center">
      <a href="#">
        <img src="https://github.com/ghost.png" width="100px;" alt=""/>
        <br /><sub><b>Wagner da Silva</b></sub>
      </a><br />
      🧠 AI Engineer
    </td>
  </tr>
</table>
</div>

<br>

---

## 🛡️ Aviso Legal

Este projeto tem fins estritamente educacionais e acadêmicos, desenvolvido no âmbito de um Datathon FIAP em parceria com a ONG Passos Mágicos. As predições geradas pelo modelo de Machine Learning possuem margem de erro e **não substituem a avaliação de um pedagogo, psicólogo ou psicopedagogo qualificado**. Qualquer indicação de risco deve ser interpretada por um profissional com acesso ao histórico completo do aluno.
