"""
Passos Mágicos — Radar de Risco de Defasagem
App Streamlit: carrega o modelo treinado e retorna probabilidade de risco
com explicação dos indicadores mais relevantes.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Passos Mágicos — Radar de Risco",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { color: #e94560; font-size: 2.2rem; margin: 0; }
    .main-header p  { color: #a8dadc; font-size: 1.05rem; margin: 0.5rem 0 0; }

    .risk-card-alto {
        background: linear-gradient(135deg, #c0392b, #e74c3c);
        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;
    }
    .risk-card-medio {
        background: linear-gradient(135deg, #e67e22, #f39c12);
        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;
    }
    .risk-card-baixo {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;
    }
    .risk-card-alto h2, .risk-card-medio h2, .risk-card-baixo h2 {
        font-size: 3rem; margin: 0;
    }
    .metric-card {
        background: #f8f9fa; border-radius: 8px; padding: 1rem;
        border-left: 4px solid #4C72B0; margin-bottom: 0.5rem;
    }
    .info-box {
        background: #e8f4f8; border-radius: 8px; padding: 1rem;
        border: 1px solid #bee3f8; margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌟 Passos Mágicos — Radar de Risco</h1>
    <p>Identifique precocemente alunos em risco de defasagem escolar</p>
</div>
""", unsafe_allow_html=True)

# ── Carregamento do modelo ────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'modelo_risco_defasagem.pkl')

@st.cache_resource
def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

model_payload = load_model()

if model_payload is None:
    st.error("""
    ⚠️ **Modelo não encontrado.**

    Execute primeiro o notebook `model/modelo_preditivo.ipynb` para gerar o arquivo
    `modelo_risco_defasagem.pkl`.
    """)
    st.stop()

pipeline     = model_payload['pipeline']
feature_cols = model_payload['feature_cols']
threshold    = model_payload['threshold']
model_name   = model_payload.get('model_name', 'Modelo')

# ── Sidebar — informações do modelo ──────────────────────────────────────────
with st.sidebar:
    st.image("https://www.passosmagicos.org.br/wp-content/uploads/2020/09/logo-passos-magicos.png",
             use_column_width=True)
    st.markdown("---")
    st.markdown("### Sobre o Modelo")
    st.markdown(f"""
    - **Algoritmo:** {model_name}
    - **Threshold:** {threshold:.2f}
    - **Treino:** 2022–2023
    - **Validação:** 2024
    """)
    st.markdown("---")
    st.markdown("### Guia de Indicadores")
    st.markdown("""
    | Sigla | Descrição | Escala |
    |-------|-----------|--------|
    | IAN | Adequação de Nível | 0–10 |
    | IDA | Desempenho Acadêmico | 0–10 |
    | IEG | Engajamento | 0–10 |
    | IAA | Autoavaliação | 0–10 |
    | IPS | Psicossocial | 0–10 |
    | IPP | Psicopedagógico | 0–10 |
    | IPV | Ponto de Virada | 0–10 |
    | INDE | Índice Geral | 0–10 |
    """)

# ── Layout principal ──────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔍 Avaliação Individual", "📊 Comparação de Perfis", "📖 Como Funciona"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Avaliação Individual
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Insira os indicadores do aluno")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Indicadores Acadêmicos**")
        ian = st.slider("IAN — Adequação de Nível", 0.0, 10.0, 7.0, 0.1,
                        help="Mede se o aluno está no nível adequado para sua fase")
        ida = st.slider("IDA — Desempenho Acadêmico", 0.0, 10.0, 6.5, 0.1,
                        help="Média ponderada das notas em Matemática, Português e Inglês")
        ieg = st.slider("IEG — Engajamento", 0.0, 10.0, 6.0, 0.1,
                        help="Participação nas atividades, faltas e comportamento")
        inde = st.slider("INDE — Índice Geral", 0.0, 10.0, 6.5, 0.1,
                         help="Índice de desenvolvimento educacional global")

    with col_b:
        st.markdown("**Indicadores Psicossociais**")
        iaa = st.slider("IAA — Autoavaliação", 0.0, 10.0, 7.0, 0.1,
                        help="Como o aluno avalia seu próprio desempenho")
        ips = st.slider("IPS — Indicador Psicossocial", 0.0, 10.0, 6.5, 0.1,
                        help="Aspectos emocionais e sociais avaliados pela psicologia")
        ipp = st.slider("IPP — Psicopedagógico", 0.0, 10.0, 6.5, 0.1,
                        help="Avaliação psicopedagógica (disponível a partir de 2023)")
        ipv = st.slider("IPV — Ponto de Virada", 0.0, 10.0, 6.0, 0.1,
                        help="Indica se o aluno atingiu o ponto de virada em sua trajetória")

    with col_c:
        st.markdown("**Dados do Aluno**")
        fase = st.selectbox("Fase Escolar", list(range(1, 9)), index=2,
                            help="Equivalente ao ano/série do aluno")
        genero = st.radio("Gênero", ["Feminino", "Masculino", "Não informado"], index=0)
        pedra = st.selectbox("Pedra Classificatória",
                             ["Quartzo", "Ágata", "Ametista", "Topázio"],
                             index=1)

    st.markdown("---")

    # ── Cálculo do risco ──────────────────────────────────────────────────────
    def build_features(ian, ida, ieg, iaa, ips, ipp, ipv, inde, fase, genero, pedra):
        pedra_map  = {'Quartzo': 0, 'Ágata': 1, 'Ametista': 2, 'Topázio': 3}
        genero_map = {'Feminino': 0, 'Masculino': 1, 'Não informado': np.nan}
        return {
            'IAN': ian, 'IDA': ida, 'IEG': ieg, 'IAA': iaa,
            'IPS': ips, 'IPP': ipp, 'IPV': ipv, 'INDE': inde,
            'Fase': fase,
            'ind_academico_medio': (ida + ieg) / 2,
            'ind_psico_medio': (iaa + ips) / 2,
            'gap_ian_fase': ian - fase * 0.5,
            'inde_x_ian': inde * ian,
            'baixo_ida': int(ida < 5),
            'baixo_ieg': int(ieg < 5),
            'fase_sq': fase ** 2,
            'genero_cod': genero_map[genero],
            'pedra_ord': pedra_map[pedra]
        }

    if st.button("🔍 Calcular Risco de Defasagem", type="primary", use_container_width=True):
        feats = build_features(ian, ida, ieg, iaa, ips, ipp, ipv, inde, fase, genero, pedra)
        df_input = pd.DataFrame([feats])

        # Garante que as colunas estão na ordem certa
        df_input = df_input.reindex(columns=feature_cols)
        prob = pipeline.predict_proba(df_input)[:, 1][0]

        st.markdown("---")
        st.markdown("### Resultado da Avaliação")

        res_col1, res_col2, res_col3 = st.columns([1, 1.5, 1.5])

        with res_col1:
            if prob >= threshold + 0.15:
                card_class = "risk-card-alto"
                nivel = "RISCO ALTO"
                emoji = "🔴"
            elif prob >= threshold:
                card_class = "risk-card-medio"
                nivel = "RISCO MÉDIO"
                emoji = "🟠"
            else:
                card_class = "risk-card-baixo"
                nivel = "BAIXO RISCO"
                emoji = "🟢"

            st.markdown(f"""
            <div class="{card_class}">
                <h2>{emoji}</h2>
                <h3>{nivel}</h3>
                <h2>{prob:.1%}</h2>
                <p>probabilidade de defasagem</p>
            </div>
            """, unsafe_allow_html=True)

        with res_col2:
            st.markdown("#### Indicadores do Aluno vs Média Esperada")
            indicadores_info = {
                'IAN': (ian, 7.5, 'Adequação de Nível'),
                'IDA': (ida, 6.5, 'Desempenho Acadêmico'),
                'IEG': (ieg, 6.8, 'Engajamento'),
                'IAA': (iaa, 7.2, 'Autoavaliação'),
                'IPS': (ips, 7.0, 'Psicossocial'),
                'IPV': (ipv, 6.3, 'Ponto de Virada'),
                'INDE': (inde, 6.8, 'Índice Geral'),
            }
            for sigla, (valor, media_ref, nome) in indicadores_info.items():
                delta = valor - media_ref
                delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
                cor = "🟢" if delta >= 0 else "🔴"
                st.markdown(
                    f"<div class='metric-card'>{cor} <b>{sigla}</b>: {valor:.1f} "
                    f"<span style='color:gray'>({delta_str} vs média)</span></div>",
                    unsafe_allow_html=True
                )

        with res_col3:
            st.markdown("#### Gráfico de Radar")
            labels = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPV']
            valores_aluno = [ian, ida, ieg, iaa, ips, ipv]
            valores_ref   = [7.5, 6.5, 6.8, 7.2, 7.0, 6.3]

            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            angles += angles[:1]
            v_aluno = valores_aluno + valores_aluno[:1]
            v_ref   = valores_ref + valores_ref[:1]

            fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
            ax.plot(angles, v_aluno, 'b-', linewidth=2, label='Aluno')
            ax.fill(angles, v_aluno, alpha=0.15, color='blue')
            ax.plot(angles, v_ref, 'g--', linewidth=1.5, label='Média')
            ax.fill(angles, v_ref, alpha=0.05, color='green')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=9)
            ax.set_ylim(0, 10)
            ax.set_yticklabels([])
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
            ax.set_facecolor('#f8f9fa')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        # ── Recomendações ─────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 💡 Recomendações")

        recom_col1, recom_col2 = st.columns(2)

        with recom_col1:
            fatores = []
            if ian < 6:
                fatores.append(("🔴 IAN baixo", "O aluno apresenta inadequação de nível. Recomendar reforço pedagógico focado na nivelação da fase atual."))
            if ida < 5:
                fatores.append(("🔴 IDA crítico", "Desempenho acadêmico abaixo do esperado. Considerar aulas de apoio em Matemática e Português."))
            if ieg < 5:
                fatores.append(("🟠 IEG baixo", "Baixo engajamento detectado. Investigar causas (faltas, desmotivação) e acionar equipe pedagógica."))
            if iaa < 5:
                fatores.append(("🟠 IAA reduzido", "Autoavaliação baixa pode indicar baixa autoestima ou desmotivação. Encaminhar para acompanhamento psicológico."))
            if ips < 5:
                fatores.append(("🟠 IPS baixo", "Indicador psicossocial abaixo do limiar. Agendar avaliação com equipe de psicologia."))

            if fatores:
                st.markdown("**Fatores de Atenção:**")
                for titulo, descricao in fatores:
                    st.markdown(f"**{titulo}**")
                    st.markdown(f"<div class='info-box'>{descricao}</div>", unsafe_allow_html=True)
            else:
                st.success("✅ Nenhum indicador individual em zona crítica. Manter acompanhamento regular.")

        with recom_col2:
            st.markdown("**Pontos Positivos:**")
            pontos = []
            if ian >= 8:
                pontos.append("✅ Excelente adequação de nível")
            if ida >= 7:
                pontos.append("✅ Bom desempenho acadêmico")
            if ieg >= 7:
                pontos.append("✅ Alto engajamento com as atividades")
            if iaa >= 7:
                pontos.append("✅ Boa autoavaliação — aluno confiante")
            if ips >= 7:
                pontos.append("✅ Bom indicador psicossocial")
            if ipv >= 7:
                pontos.append("✅ Aproximando-se do ponto de virada")
            if not pontos:
                pontos.append("📌 Acompanhar evolução nos próximos meses")
            for p in pontos:
                st.markdown(p)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Comparação de Perfis
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Compare até 3 alunos lado a lado")
    st.info("Insira os indicadores de múltiplos alunos para comparar seus perfis de risco.")

    n_alunos = st.radio("Número de alunos", [2, 3], horizontal=True)

    alunos_data = []
    cols = st.columns(n_alunos)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**Aluno {i+1}**")
            nome_a = st.text_input("Nome/ID", value=f"Aluno {i+1}", key=f"nome_{i}")
            ian_a  = st.slider("IAN", 0.0, 10.0, 6.0 + i, 0.1, key=f"ian_{i}")
            ida_a  = st.slider("IDA", 0.0, 10.0, 6.0 - i * 0.5, 0.1, key=f"ida_{i}")
            ieg_a  = st.slider("IEG", 0.0, 10.0, 6.0 + i * 0.3, 0.1, key=f"ieg_{i}")
            iaa_a  = st.slider("IAA", 0.0, 10.0, 7.0 - i * 0.4, 0.1, key=f"iaa_{i}")
            ips_a  = st.slider("IPS", 0.0, 10.0, 6.5, 0.1, key=f"ips_{i}")
            ipv_a  = st.slider("IPV", 0.0, 10.0, 6.0 + i * 0.2, 0.1, key=f"ipv_{i}")
            inde_a = st.slider("INDE", 0.0, 10.0, 6.2 + i * 0.3, 0.1, key=f"inde_{i}")
            fase_a = st.selectbox("Fase", list(range(1, 9)), index=2, key=f"fase_{i}")
            alunos_data.append({'nome': nome_a, 'ian': ian_a, 'ida': ida_a, 'ieg': ieg_a,
                                 'iaa': iaa_a, 'ips': ips_a, 'ipv': ipv_a,
                                 'inde': inde_a, 'fase': fase_a})

    if st.button("Comparar Alunos", type="primary", use_container_width=True):
        resultados = []
        for a in alunos_data:
            feats = build_features(a['ian'], a['ida'], a['ieg'], a['iaa'], a['ips'],
                                   np.nan, a['ipv'], a['inde'], a['fase'],
                                   'Não informado', 'Ágata')
            df_inp = pd.DataFrame([feats]).reindex(columns=feature_cols)
            prob   = pipeline.predict_proba(df_inp)[:, 1][0]
            resultados.append({'nome': a['nome'], 'prob': prob,
                                'ian': a['ian'], 'ida': a['ida'],
                                'ieg': a['ieg'], 'inde': a['inde']})

        # Tabela
        df_res = pd.DataFrame(resultados).set_index('nome')
        df_res['Risco (%)'] = df_res['prob'].mul(100).round(1)
        df_res['Nível'] = df_res['prob'].apply(
            lambda p: '🔴 Alto' if p >= threshold + 0.15
                      else ('🟠 Médio' if p >= threshold else '🟢 Baixo')
        )
        st.dataframe(df_res[['Risco (%)', 'Nível', 'ian', 'ida', 'ieg', 'inde']]
                     .rename(columns={'ian':'IAN','ida':'IDA','ieg':'IEG','inde':'INDE'}),
                     use_container_width=True)

        # Gráfico de barras comparativo
        fig, ax = plt.subplots(figsize=(8, 4))
        names  = [r['nome'] for r in resultados]
        probs  = [r['prob'] * 100 for r in resultados]
        colors = ['#c0392b' if p >= (threshold + 0.15) * 100
                  else ('#e67e22' if p >= threshold * 100 else '#27ae60') for p in probs]
        bars = ax.bar(names, probs, color=colors, edgecolor='white', linewidth=1.5)
        ax.axhline(threshold * 100, color='red', linestyle='--', linewidth=1.5,
                   label=f'Threshold ({threshold*100:.0f}%)')
        for bar, val in zip(bars, probs):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.1f}%', ha='center', fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_ylabel('Probabilidade de Risco (%)')
        ax.set_title('Comparação de Risco de Defasagem', fontweight='bold')
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Como Funciona
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    ### Como o Modelo Funciona

    #### Dados de Treinamento
    O modelo foi treinado com dados reais de alunos da Passos Mágicos dos anos **2022 e 2023**,
    e validado nos dados de **2024**. O dataset contém mais de **1.800 registros** com indicadores
    coletados pela equipe pedagógica e psicossocial da ONG.

    #### Algoritmo
    Utilizamos **{model_name}** — um modelo de ensemble baseado em múltiplas árvores de decisão
    que combina as predições de centenas de árvores para produzir uma estimativa robusta
    de probabilidade de risco.

    #### Features Utilizadas
    O modelo utiliza **{n_feat} features**, incluindo:
    - Os 8 indicadores diretos da ONG (IAN, IDA, IEG, IAA, IPS, IPP, IPV, INDE)
    - Features derivadas: médias dos grupos de indicadores, flags de zona crítica,
      interações entre indicadores e fase escolar

    #### Definição de Risco
    Um aluno é classificado como **em risco de defasagem** quando está cursando uma fase
    escolar **1 ou mais anos abaixo** do esperado para sua idade.

    #### Interpretação da Probabilidade
    | Probabilidade | Nível | Ação Recomendada |
    |---------------|-------|-----------------|
    | < {thr_low:.0%} | 🟢 Baixo | Acompanhamento regular |
    | {thr_low:.0%} – {thr_high:.0%} | 🟠 Médio | Atenção redobrada, revisão pedagógica |
    | > {thr_high:.0%} | 🔴 Alto | Intervenção imediata, plano de suporte individualizado |

    #### Limitações
    - O modelo é uma ferramenta de **apoio à decisão**, não um substituto ao julgamento
      da equipe pedagógica e psicossocial
    - Performance pode degradar ao longo do tempo — recomenda-se re-treinar anualmente
    - Casos excepcionais (mudanças de vida, situações familiares) podem não ser capturados
      pelos indicadores numéricos
    """.format(
        model_name=model_name,
        n_feat=len(feature_cols),
        thr_low=threshold,
        thr_high=threshold + 0.15
    ))

    st.markdown("---")
    st.markdown("""
    #### Sobre a Passos Mágicos
    A **Associação Passos Mágicos** é uma ONG fundada em 1992 que transforma a vida de
    crianças e jovens em situação de vulnerabilidade social por meio da educação de qualidade.
    Atua em Embu-Guaçu (SP) com programa educacional complementar, suporte psicossocial
    e bolsas de estudo.

    🌐 [www.passosmagicos.org.br](https://www.passosmagicos.org.br)
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:0.85rem'>"
    "Datathon FIAP × Passos Mágicos · Desenvolvido com ❤️ para transformar educação"
    "</div>",
    unsafe_allow_html=True
)
