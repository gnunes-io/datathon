"""Página Radar de Risco — avaliação individual com SHAP e comparação de perfis."""
import os
import sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    load_model, build_features, predict, risk_level,
    FEATURE_NAMES_PT, PM_BLUE, PM_GOLD, RISK_HIGH, RISK_MED, RISK_LOW,
)

payload = load_model()
if payload is None:
    st.error("⚠️ Modelo não encontrado. Execute `model/modelo_preditivo.ipynb`.")
    st.stop()

pipeline     = payload['pipeline']
feature_cols = payload['feature_cols']
threshold    = payload['threshold']
model_name   = payload.get('model_name', 'Modelo')
ref_means    = payload.get('ref_means', {
    'IAN': 7.5, 'IDA': 6.5, 'IEG': 6.8,
    'IAA': 7.2, 'IPS': 7.0, 'IPV': 6.3, 'INDE': 6.8,
})
has_shap = payload.get('shap_explainer') is not None

RADAR_LABELS = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPV', 'INDE']

# ── Estado da sessão ───────────────────────────────────────────────────────────
if 'historico' not in st.session_state:
    st.session_state.historico = []

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pm-hero">
    <h1>🎯 Radar de Risco</h1>
    <p>Preencha os indicadores do aluno — o resultado é calculado automaticamente</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FORMULÁRIO + RESULTADO — layout 2 colunas
# ══════════════════════════════════════════════════════════════════════════════
form_col, result_col = st.columns([1.1, 0.9], gap="large")

# ── Coluna ESQUERDA — formulário ───────────────────────────────────────────────
with form_col:
    st.markdown('<p class="section-hdr">Identificação</p>', unsafe_allow_html=True)
    id_col1, id_col2, id_col3 = st.columns(3)
    nome_aluno = id_col1.text_input("Nome / ID", placeholder="ex: Ana S.", key="nome")
    fase = id_col2.selectbox("Fase escolar", list(range(1, 9)), index=2, key="fase")
    genero = id_col3.radio("Gênero", ["Feminino", "Masculino", "Não informado"],
                           index=0, horizontal=True, key="genero")

    pedra_col1, pedra_col2 = st.columns([1, 2])
    pedra = pedra_col1.selectbox(
        "Pedra classificatória", ["Quartzo", "Ágata", "Ametista", "Topázio"],
        index=1, key="pedra"
    )
    pedra_col2.caption(
        "🪨 Quartzo < 5,5 · 💎 Ágata 5,5–7,0 · 💜 Ametista 7,0–8,5 · ⭐ Topázio ≥ 8,5"
    )

    # ── Indicadores Acadêmicos ─────────────────────────────────────────────────
    st.markdown('<p class="section-hdr">Indicadores Acadêmicos</p>', unsafe_allow_html=True)

    def num_input(label, key, ref_key, help_text):
        ref = ref_means.get(ref_key, 6.5)
        val = st.number_input(label, 0.0, 10.0, ref, 0.5, key=key, help=help_text)
        st.markdown(
            f'<div class="ref-caption">Média histórica: {ref:.1f}</div>',
            unsafe_allow_html=True
        )
        return val

    ac1, ac2 = st.columns(2)
    with ac1:
        ian  = num_input("IAN — Adequação de Nível", "ian", "IAN",
                         "Mede se o aluno está no nível adequado para a fase")
        ieg  = num_input("IEG — Engajamento", "ieg", "IEG",
                         "Frequência, participação e comportamento")
    with ac2:
        ida  = num_input("IDA — Desempenho Acadêmico", "ida", "IDA",
                         "Média em Matemática, Português e Inglês")
        inde = num_input("INDE — Índice Geral", "inde", "INDE",
                         "Índice global de desenvolvimento educacional")

    # ── Indicadores Psicossociais ──────────────────────────────────────────────
    st.markdown('<p class="section-hdr">Indicadores Psicossociais</p>', unsafe_allow_html=True)

    ps1, ps2 = st.columns(2)
    with ps1:
        iaa = num_input("IAA — Autoavaliação", "iaa", "IAA",
                        "Como o aluno avalia seu próprio progresso")
        ipv = num_input("IPV — Ponto de Virada", "ipv", "IPV",
                        "Indica transformação na trajetória do aluno")
    with ps2:
        ips = num_input("IPS — Psicossocial", "ips", "IPS",
                        "Aspectos emocionais e relacionamentos sociais")

        # IPP — com checkbox de disponibilidade
        ipp_ok = st.checkbox("IPP disponível para este aluno?", value=True, key="ipp_ok",
                             help="IPP só existe a partir de 2023. Desmarque se não houver avaliação.")
        if ipp_ok:
            ipp = st.number_input("IPP — Psicopedagógico", 0.0, 10.0,
                                  ref_means.get('IPP', ref_means.get('IPS', 6.5)),
                                  0.5, key="ipp_val",
                                  help="Avaliação psicopedagógica — disponível a partir de 2023")
        else:
            ipp = np.nan
            st.caption("IPP será imputado pela mediana histórica do treino.")

# ── Coluna DIREITA — resultado em tempo real ───────────────────────────────────
with result_col:
    feats = build_features(ian, ida, ieg, iaa, ips, ipp, ipv, inde, fase, genero, pedra)
    prob, shap_vals = predict(payload, feats)
    nivel, emoji, cor = risk_level(prob, threshold)

    nivel_labels = {
        'alto':  'RISCO ALTO',
        'medio': 'RISCO MÉDIO',
        'baixo': 'BAIXO RISCO',
    }

    # Card de risco
    st.markdown(f"""
    <div class="risk-card" style="background:{cor};">
        <div class="pct">{prob:.0%}</div>
        <div class="label">{emoji} {nivel_labels[nivel]}</div>
        <div class="sub">probabilidade de defasagem · limiar: {threshold:.0%}</div>
    </div>
    """, unsafe_allow_html=True)

    # Barra de progresso + contexto de prevalência
    prev_2024 = 0.119
    st.progress(min(prob, 1.0))
    if nivel == 'baixo':
        st.success(f"Probabilidade abaixo do limiar de risco ({threshold:.0%}).", icon="✅")
    elif nivel == 'medio':
        st.warning("Zona de atenção. Acompanhamento reforçado recomendado.", icon="⚠️")
    else:
        st.error("Intervenção prioritária recomendada.", icon="🚨")

    st.caption(
        f"Contexto: em 2024, {prev_2024:.0%} dos alunos foram classificados em risco de defasagem."
    )

    # Deltas vs média histórica — tabela compacta, dark-mode compatível
    st.markdown('<p class="section-hdr">Indicadores vs média histórica</p>',
                unsafe_allow_html=True)

    indicadores_exibir = [(s, feats[s], ref_means.get(s, 6.5)) for s in RADAR_LABELS]
    if not np.isnan(ipp):
        indicadores_exibir.append(('IPP', ipp, ref_means.get('IPP', ref_means.get('IPS', 6.5))))

    rows_html = ""
    for sigla, val, ref in indicadores_exibir:
        delta  = val - ref
        sinal  = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
        arrow  = "▲" if delta >= 0 else "▼"
        cor    = "#059669" if delta >= 0 else "#DC2626"
        border = "#059669" if delta >= 0 else "#DC2626"
        # barra visual 0–10
        pct_val = int(val * 10)
        pct_ref = int(ref * 10)
        rows_html += f"""
        <tr style="border-bottom:1px solid rgba(128,128,128,0.12);">
          <td style="padding:0.28rem 0.5rem; font-weight:600; white-space:nowrap;
                     border-left:3px solid {border}; padding-left:0.6rem;">{sigla}</td>
          <td style="padding:0.28rem 0.5rem; text-align:center; font-variant-numeric:tabular-nums;">
            {val:.1f}
          </td>
          <td style="padding:0.28rem 0.5rem; width:55%;">
            <div style="background:rgba(128,128,128,0.12); border-radius:4px; height:6px; position:relative;">
              <div style="position:absolute; background:{cor}; border-radius:4px; height:6px;
                          width:{pct_val}%; max-width:100%;"></div>
              <div style="position:absolute; left:{pct_ref}%; top:-2px; width:2px; height:10px;
                          background:rgba(128,128,128,0.5);"></div>
            </div>
          </td>
          <td style="padding:0.28rem 0.5rem; text-align:right; font-size:0.78rem;
                     color:{cor}; white-space:nowrap; font-variant-numeric:tabular-nums;">
            {arrow} {sinal}
          </td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; font-size:0.84rem;">
      <thead>
        <tr style="opacity:0.5; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em;">
          <th style="text-align:left; padding:0.2rem 0.5rem 0.2rem 0.6rem;">Ind.</th>
          <th style="text-align:center; padding:0.2rem 0.5rem;">Valor</th>
          <th style="padding:0.2rem 0.5rem;"></th>
          <th style="text-align:right; padding:0.2rem 0.5rem;">Δ</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    <p style="font-size:0.72rem; opacity:0.45; margin-top:0.35rem;">
      Barra cinza: escala 0–10 · traço = média histórica · cor = diferença vs ref
    </p>
    """, unsafe_allow_html=True)

    # Botão para salvar no histórico da sessão
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salvar nesta sessão", use_container_width=True):
        nome_display = nome_aluno.strip() if nome_aluno.strip() else f"Aluno {len(st.session_state.historico)+1}"
        st.session_state.historico.append({
            'Nome': nome_display, 'Risco (%)': f"{prob:.1%}",
            'Nível': nivel_labels[nivel], 'IAN': ian, 'IDA': ida,
            'IEG': ieg, 'INDE': inde, 'Fase': fase,
        })
        st.success(f"'{nome_display}' salvo no histórico.")

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICOS — radar + SHAP (largura total)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
viz_radar, viz_shap = st.columns([1, 1], gap="large")

# ── Radar chart Plotly ─────────────────────────────────────────────────────────
with viz_radar:
    st.markdown('<p class="section-hdr">Perfil do aluno (radar)</p>', unsafe_allow_html=True)

    v_aluno = [feats[k] for k in RADAR_LABELS]
    v_ref   = [ref_means.get(k, 6.5) for k in RADAR_LABELS]
    theta   = RADAR_LABELS + [RADAR_LABELS[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=v_aluno + [v_aluno[0]], theta=theta, fill='toself',
        fillcolor='rgba(0,51,153,0.15)',
        line=dict(color=PM_BLUE, width=2.5),
        name='Aluno', hovertemplate='%{theta}: %{r:.1f}<extra></extra>'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=v_ref + [v_ref[0]], theta=theta, fill='toself',
        fillcolor='rgba(100,100,100,0.05)',
        line=dict(color='#94A3B8', width=1.5, dash='dot'),
        name='Média histórica', hovertemplate='%{theta}: %{r:.1f}<extra></extra>'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10],
                            tickfont=dict(size=9), gridcolor='#E2E8F0'),
            angularaxis=dict(tickfont=dict(size=11, color=PM_BLUE)),
            bgcolor='white',
        ),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.18,
                    font=dict(size=11)),
        margin=dict(l=50, r=50, t=30, b=50),
        height=380,
        paper_bgcolor='#F8FAFC',
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ── SHAP chart ─────────────────────────────────────────────────────────────────
with viz_shap:
    st.markdown('<p class="section-hdr">Fatores que influenciaram esta predição</p>',
                unsafe_allow_html=True)

    if shap_vals is not None and not shap_vals.empty:
        top = (shap_vals
               .rename(FEATURE_NAMES_PT)
               .abs()
               .nlargest(10)
               .index)
        sv_top  = shap_vals.rename(FEATURE_NAMES_PT)[top].sort_values()
        bar_colors = [RISK_HIGH if v > 0 else RISK_LOW for v in sv_top.values]

        fig_shap = go.Figure(go.Bar(
            x=sv_top.values,
            y=sv_top.index,
            orientation='h',
            marker_color=bar_colors,
            hovertemplate='%{y}: %{x:+.3f}<extra></extra>',
        ))
        fig_shap.add_vline(x=0, line_color='#64748B', line_width=1)
        fig_shap.update_layout(
            xaxis_title='Impacto na probabilidade de risco (SHAP)',
            yaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=10, r=10, t=10, b=40),
            height=380,
            paper_bgcolor='#F8FAFC',
            plot_bgcolor='white',
        )
        st.plotly_chart(fig_shap, use_container_width=True)
        st.caption(
            "🔴 vermelho = aumenta o risco · 🟢 verde = reduz o risco. "
            "Tamanho da barra = magnitude do impacto para este aluno específico."
        )
    else:
        if not has_shap:
            st.info(
                "Para ver a explicação por aluno, regenere o modelo com "
                "`pip install shap` e re-execute `model/modelo_preditivo.ipynb`.",
                icon="💡"
            )
        else:
            st.warning("Não foi possível calcular SHAP para este perfil.", icon="⚠️")

# ══════════════════════════════════════════════════════════════════════════════
# RECOMENDAÇÕES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-hdr">Recomendações e próximos passos</p>',
            unsafe_allow_html=True)

rec_col, pos_col, action_col = st.columns(3, gap="medium")

with rec_col:
    st.markdown("**⚠️ Fatores de atenção**")
    alertas = []
    if ian  < 6:   alertas.append(("IAN baixo",   "Reforço pedagógico para nivelação de fase"))
    if ida  < 5:   alertas.append(("IDA crítico",  "Apoio em Matemática e Português"))
    if ieg  < 5:   alertas.append(("IEG baixo",    "Investigar causas de baixa participação"))
    if iaa  < 5:   alertas.append(("IAA reduzido", "Encaminhar para acompanhamento psicológico"))
    if ips  < 5:   alertas.append(("IPS baixo",    "Agendar avaliação com equipe de psicologia"))
    if not np.isnan(ipp) and ipp < 5:
        alertas.append(("IPP baixo", "Investigar dificuldades específicas de aprendizado"))
    if not alertas:
        st.success("Nenhum indicador individual em zona crítica.")
    else:
        for titulo, desc in alertas:
            with st.container():
                st.markdown(f"**🔸 {titulo}**")
                st.caption(desc)

with pos_col:
    st.markdown("**✅ Pontos positivos**")
    pontos = []
    if ian  >= 8:  pontos.append("Excelente adequação de nível")
    if ida  >= 7:  pontos.append("Bom desempenho acadêmico")
    if ieg  >= 7:  pontos.append("Alto engajamento com atividades")
    if iaa  >= 7:  pontos.append("Boa autoavaliação — aluno confiante")
    if ips  >= 7:  pontos.append("Bom indicador psicossocial")
    if ipv  >= 7:  pontos.append("Próximo do ponto de virada")
    if not pontos: pontos.append("Acompanhar evolução nos próximos ciclos")
    for p in pontos:
        st.markdown(f"✅ {p}")

with action_col:
    st.markdown("**📋 Próximos passos**")
    if nivel == 'alto':
        steps = [
            "Acionar equipe pedagógica esta semana",
            "Elaborar plano de suporte individualizado",
            "Agendar reunião com família",
            "Registrar ocorrência no sistema da ONG",
        ]
    elif nivel == 'medio':
        steps = [
            "Revisão pedagógica no próximo mês",
            "Aumentar frequência de acompanhamento",
            "Verificar engajamento nas próximas semanas",
        ]
    else:
        steps = [
            "Manter acompanhamento regular",
            "Reavaliar na próxima coleta de indicadores",
        ]
    for s in steps:
        st.markdown(f"☐ {s}")

# ══════════════════════════════════════════════════════════════════════════════
# HISTÓRICO DA SESSÃO
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.historico:
    with st.expander(f"📋 Histórico desta sessão ({len(st.session_state.historico)} avaliações)"):
        df_hist = pd.DataFrame(st.session_state.historico)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        if st.button("🗑️ Limpar histórico"):
            st.session_state.historico = []
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# COMPARAÇÃO DE PERFIS
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("📊 Comparar múltiplos alunos"):
    st.caption("Compare até 3 alunos lado a lado. Gênero não é coletado aqui — use 'Não informado'.")
    n_alunos = st.radio("Número de alunos", [2, 3], horizontal=True, key="n_comp")

    comp_data = []
    comp_cols = st.columns(n_alunos, gap="medium")
    for i, col in enumerate(comp_cols):
        with col:
            st.markdown(f"**Aluno {i+1}**")
            d = {
                'nome':  st.text_input("Nome/ID", value=f"Aluno {i+1}", key=f"cn_{i}"),
                'ian':   st.number_input("IAN",  0.0, 10.0, 6.0, 0.5, key=f"cian_{i}"),
                'ida':   st.number_input("IDA",  0.0, 10.0, 6.0, 0.5, key=f"cida_{i}"),
                'ieg':   st.number_input("IEG",  0.0, 10.0, 6.0, 0.5, key=f"cieg_{i}"),
                'iaa':   st.number_input("IAA",  0.0, 10.0, 7.0, 0.5, key=f"ciaa_{i}"),
                'ips':   st.number_input("IPS",  0.0, 10.0, 6.5, 0.5, key=f"cips_{i}"),
                'ipv':   st.number_input("IPV",  0.0, 10.0, 6.0, 0.5, key=f"cipv_{i}"),
                'inde':  st.number_input("INDE", 0.0, 10.0, 6.5, 0.5, key=f"cinde_{i}"),
                'ipp_ok': st.checkbox("IPP disp.", value=False, key=f"cipp_ok_{i}"),
                'fase':  st.selectbox("Fase", list(range(1, 9)), index=2, key=f"cfase_{i}"),
                'pedra': st.selectbox("Pedra", ["Quartzo", "Ágata", "Ametista", "Topázio"],
                                      index=1, key=f"cpedra_{i}"),
            }
            d['ipp'] = st.number_input("IPP", 0.0, 10.0, 6.5, 0.5,
                                       key=f"cipp_{i}") if d['ipp_ok'] else np.nan
            comp_data.append(d)

    if st.button("Comparar", type="primary", key="btn_comp"):
        resultados = []
        for a in comp_data:
            f = build_features(a['ian'], a['ida'], a['ieg'], a['iaa'], a['ips'],
                               a['ipp'], a['ipv'], a['inde'], a['fase'],
                               'Não informado', a['pedra'])
            p, _ = predict(payload, f)
            n, e, c = risk_level(p, threshold)
            resultados.append({'Nome': a['nome'], 'Risco (%)': p * 100,
                                'Nível': f"{e} {n.title()}",
                                'IAN': a['ian'], 'IDA': a['ida'],
                                'IEG': a['ieg'], 'INDE': a['inde']})

        df_comp = pd.DataFrame(resultados)
        st.dataframe(df_comp.set_index('Nome').style.format({'Risco (%)': '{:.1f}%'}),
                     use_container_width=True)

        cores = [
            RISK_HIGH if r >= (threshold + 0.15) * 100
            else (RISK_MED if r >= threshold * 100 else RISK_LOW)
            for r in df_comp['Risco (%)']
        ]
        fig_comp = go.Figure(go.Bar(
            x=df_comp['Nome'], y=df_comp['Risco (%)'],
            marker_color=cores,
            text=[f"{v:.1f}%" for v in df_comp['Risco (%)']],
            textposition='outside',
        ))
        fig_comp.add_hline(y=threshold * 100, line_dash='dash', line_color='#64748B',
                           annotation_text=f"Limiar {threshold:.0%}")
        fig_comp.update_layout(
            yaxis=dict(range=[0, 100], title='Probabilidade de risco (%)'),
            xaxis_title='Aluno',
            height=350, paper_bgcolor='#F8FAFC', plot_bgcolor='white',
            margin=dict(t=30, b=30),
        )
        st.plotly_chart(fig_comp, use_container_width=True)
