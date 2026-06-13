"""Página Radar de Risco — avaliação individual com SHAP."""
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
    GLOBAL_CSS,
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

payload = load_model()
if payload is None:
    st.error("⚠️ Modelo não encontrado. Execute `model/modelo_preditivo.ipynb`.")
    st.stop()

threshold  = payload['threshold']
ref_means  = payload.get('ref_means', {
    'IAN': 7.5, 'IDA': 6.5, 'IEG': 6.8,
    'IAA': 7.2, 'IPS': 7.0, 'IPV': 6.3, 'INDE': 6.8,
})
has_shap = payload.get('shap_explainer') is not None

RADAR_LABELS = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPV', 'INDE']

_PEDRA_MAP = {
    'Quartzo':  ('🪨', '#6B7280', 'INDE < 5,5'),
    'Ágata':    ('💎', '#3B82F6', '5,5 ≤ INDE < 7,0'),
    'Ametista': ('💜', '#8B5CF6', '7,0 ≤ INDE < 8,5'),
    'Topázio':  ('⭐', '#F59E0B', 'INDE ≥ 8,5'),
}

def inde_to_pedra(inde: float) -> str:
    if inde >= 8.5: return 'Topázio'
    if inde >= 7.0: return 'Ametista'
    if inde >= 5.5: return 'Ágata'
    return 'Quartzo'

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
# FORMULÁRIO + RESULTADO
# ══════════════════════════════════════════════════════════════════════════════
form_col, result_col = st.columns([1.1, 0.9], gap="large")

with form_col:
    # Identificação — só Fase
    st.markdown('<p class="section-hdr">Identificação</p>', unsafe_allow_html=True)
    fase = st.selectbox("Fase escolar", list(range(1, 9)), index=2, key="fase")

    # Indicadores Acadêmicos
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

    # Pedra auto-calculada a partir do INDE
    pedra = inde_to_pedra(inde)
    emoji_p, cor_p, faixa_p = _PEDRA_MAP[pedra]
    st.markdown(
        f'<div style="background:rgba(0,0,0,0.04); border-left:3px solid {cor_p}; '
        f'border-radius:6px; padding:0.45rem 0.75rem; margin-bottom:0.75rem; font-size:0.85rem;">'
        f'Pedra: <strong>{emoji_p} {pedra}</strong> '
        f'<span style="opacity:0.55; font-size:0.78rem;">({faixa_p})</span></div>',
        unsafe_allow_html=True
    )

    # Indicadores Psicossociais
    st.markdown('<p class="section-hdr">Indicadores Psicossociais</p>', unsafe_allow_html=True)

    ps1, ps2 = st.columns(2)
    with ps1:
        iaa = num_input("IAA — Autoavaliação", "iaa", "IAA",
                        "Como o aluno avalia seu próprio progresso")
        ips = num_input("IPS — Psicossocial", "ips", "IPS",
                        "Aspectos emocionais e relacionamentos sociais")
    with ps2:
        ipv = num_input("IPV — Ponto de Virada", "ipv", "IPV",
                        "Indica transformação na trajetória do aluno")
        ipp = num_input("IPP — Psicopedagógico", "ipp_val", "IPS",
                        "Avaliação psicopedagógica — disponível a partir de 2023 (deixe na média se não houver)")

# ── Coluna DIREITA — resultado ─────────────────────────────────────────────────
with result_col:
    feats = build_features(ian, ida, ieg, iaa, ips, ipp, ipv, inde, fase,
                           'Não informado', pedra)
    prob, shap_vals = predict(payload, feats)
    nivel, emoji, cor = risk_level(prob, threshold)

    nivel_labels = {
        'alto':  'RISCO ALTO',
        'medio': 'RISCO MÉDIO',
        'baixo': 'BAIXO RISCO',
    }

    st.markdown(f"""
    <div class="risk-card" style="background:{cor};">
        <div class="pct">{prob:.0%}</div>
        <div class="label">{emoji} {nivel_labels[nivel]}</div>
        <div class="sub">probabilidade de defasagem · limiar: {threshold:.0%}</div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(min(prob, 1.0))
    if nivel == 'baixo':
        st.success(f"Probabilidade abaixo da zona de atenção (40%).", icon="✅")
    elif nivel == 'medio':
        st.warning("Zona de atenção (40–61%). Acompanhamento reforçado recomendado.", icon="⚠️")
    else:
        st.error("Acima do limiar de risco. Intervenção prioritária recomendada.", icon="🚨")

    # Tabela Indicadores vs média histórica
    st.markdown('<p class="section-hdr">Indicadores vs média histórica</p>',
                unsafe_allow_html=True)

    indicadores_exibir = [(s, feats[s], ref_means.get(s, 6.5)) for s in RADAR_LABELS]
    indicadores_exibir.append(('IPP', ipp, ref_means.get('IPP', ref_means.get('IPS', 6.5))))

    rows_html = ""
    for sigla, val, ref in indicadores_exibir:
        delta  = val - ref
        sinal  = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
        arrow  = "▲" if delta >= 0 else "▼"
        d_cor  = "#059669" if delta >= 0 else "#DC2626"
        pct_val = int(val * 10)
        pct_ref = int(ref * 10)
        rows_html += f"""
        <tr style="border-bottom:1px solid rgba(128,128,128,0.12);">
          <td style="padding:0.28rem 0.5rem; font-weight:600; white-space:nowrap;
                     border-left:3px solid {d_cor}; padding-left:0.6rem;">{sigla}</td>
          <td style="padding:0.28rem 0.5rem; text-align:center; font-variant-numeric:tabular-nums;">
            {val:.1f}
          </td>
          <td style="padding:0.28rem 0.5rem; width:55%;">
            <div style="background:rgba(128,128,128,0.12); border-radius:4px; height:6px; position:relative;">
              <div style="position:absolute; background:{d_cor}; border-radius:4px; height:6px;
                          width:{pct_val}%; max-width:100%;"></div>
              <div style="position:absolute; left:{pct_ref}%; top:-2px; width:2px; height:10px;
                          background:rgba(128,128,128,0.5);"></div>
            </div>
          </td>
          <td style="padding:0.28rem 0.5rem; text-align:right; font-size:0.78rem;
                     color:{d_cor}; white-space:nowrap; font-variant-numeric:tabular-nums;">
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
          <th style="text-align:right; padding:0.2rem 0.5rem;">Δ ref</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salvar nesta sessão", use_container_width=True):
        label = f"Aluno {len(st.session_state.historico)+1}"
        st.session_state.historico.append({
            'ID': label, 'Risco (%)': f"{prob:.1%}",
            'Nível': nivel_labels[nivel], 'IAN': ian, 'IDA': ida,
            'IEG': ieg, 'INDE': inde, 'Fase': fase, 'Pedra': pedra,
        })
        st.success(f"'{label}' salvo no histórico.")

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICOS — radar + SHAP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
viz_radar, viz_shap = st.columns([1, 1], gap="large")

_DARK = '#0F172A'
_GRID = 'rgba(255,255,255,0.08)'

with viz_radar:
    st.markdown('<p class="section-hdr">Perfil do aluno</p>', unsafe_allow_html=True)

    v_aluno = [feats[k] for k in RADAR_LABELS]
    v_ref   = [ref_means.get(k, 6.5) for k in RADAR_LABELS]
    theta   = RADAR_LABELS + [RADAR_LABELS[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=v_aluno + [v_aluno[0]], theta=theta, fill='toself',
        fillcolor='rgba(99,179,237,0.20)',
        line=dict(color='#63B3ED', width=2.5),
        name='Aluno', hovertemplate='%{theta}: %{r:.1f}<extra></extra>'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=v_ref + [v_ref[0]], theta=theta, fill='toself',
        fillcolor='rgba(255,255,255,0.03)',
        line=dict(color='rgba(255,255,255,0.30)', width=1.5, dash='dot'),
        name='Média histórica', hovertemplate='%{theta}: %{r:.1f}<extra></extra>'
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor=_DARK,
            radialaxis=dict(
                visible=True, range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                tickfont=dict(size=8, color='rgba(255,255,255,0.35)'),
                gridcolor=_GRID,
                linecolor=_GRID,
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color='white'),
                gridcolor=_GRID,
                linecolor=_GRID,
            ),
        ),
        showlegend=True,
        legend=dict(
            orientation='h', yanchor='bottom', y=-0.20,
            font=dict(size=11, color='white'),
            bgcolor='rgba(0,0,0,0)',
        ),
        margin=dict(l=55, r=55, t=30, b=65),
        height=400,
        paper_bgcolor=_DARK,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with viz_shap:
    st.markdown('<p class="section-hdr">Fatores que influenciaram esta predição</p>',
                unsafe_allow_html=True)

    if shap_vals is not None and not shap_vals.empty:
        top = (shap_vals
               .rename(FEATURE_NAMES_PT)
               .abs()
               .nlargest(10)
               .index)
        sv_top     = shap_vals.rename(FEATURE_NAMES_PT)[top].sort_values()
        bar_colors = [RISK_HIGH if v > 0 else RISK_LOW for v in sv_top.values]

        fig_shap = go.Figure(go.Bar(
            x=sv_top.values,
            y=sv_top.index,
            orientation='h',
            marker_color=bar_colors,
            hovertemplate='%{y}: %{x:+.3f}<extra></extra>',
        ))
        fig_shap.add_vline(x=0, line_color='rgba(255,255,255,0.25)', line_width=1)
        fig_shap.update_layout(
            xaxis_title='Impacto na probabilidade de risco (SHAP)',
            xaxis=dict(
                tickfont=dict(color='rgba(255,255,255,0.5)', size=9),
                title_font=dict(color='rgba(255,255,255,0.5)', size=10),
                gridcolor=_GRID,
                zerolinecolor='rgba(255,255,255,0.25)',
            ),
            yaxis=dict(tickfont=dict(size=10, color='white'), gridcolor=_GRID),
            margin=dict(l=10, r=15, t=10, b=50),
            height=400,
            paper_bgcolor=_DARK,
            plot_bgcolor=_DARK,
        )
        st.plotly_chart(fig_shap, use_container_width=True)
        st.caption("🔴 aumenta o risco · 🟢 reduz o risco · tamanho = magnitude para este aluno")
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
