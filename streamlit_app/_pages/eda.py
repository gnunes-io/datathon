"""Página Quick Insights — panorama analítico dos dados da Passos Mágicos."""
import os
import sys
import re as _re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import DATA_PATH, PM_BLUE, PM_GOLD, RISK_HIGH, RISK_LOW, GLOBAL_CSS

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
INDICATOR_COLS = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']
PEDRA_ORDER    = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']
PEDRA_COLORS   = {
    'Quartzo': '#6B7280', 'Ágata': '#3B82F6',
    'Ametista': '#8B5CF6', 'Topázio': '#F59E0B',
}
YEAR_COLORS = {'2022': '#94A3B8', '2023': PM_BLUE, '2024': PM_GOLD}
_GRID       = '#E2E8F0'

# ── Data loading ───────────────────────────────────────────────────────────────
def _parse_float(s):
    if pd.isna(s): return np.nan
    try: return float(str(s).replace(',', '.'))
    except: return np.nan

def _parse_fase(x):
    if pd.isna(x): return np.nan
    s = str(x).strip()
    if s.upper() == 'ALFA': return 0.0
    try: return float(s)
    except: pass
    m = _re.match(r'FASE\s*(\d+)', s, _re.IGNORECASE)
    if m: return float(m.group(1))
    m = _re.match(r'^(\d+)', s)
    if m: return float(m.group(1))
    return np.nan

def _find_col(df, keyword, ano):
    full, short = str(ano), str(ano)[-2:]
    cols = [c for c in df.columns if keyword in c and full in c]
    if cols: return cols[0]
    cols = [c for c in df.columns if keyword in c
            and c.strip().endswith(short) and len(c) <= len(keyword) + 5]
    return cols[0] if cols else None

def _inde_to_pedra(v):
    if pd.isna(v): return np.nan
    if v < 5.5: return 'Quartzo'
    if v < 7.0: return 'Ágata'
    if v < 8.5: return 'Ametista'
    return 'Topázio'

def _load_year(path, ano):
    df = pd.read_csv(path, encoding='latin1')
    df['ano'] = ano
    # RA
    df['RA'] = df['RA'].astype(str) if 'RA' in df.columns else df.index.astype(str)
    # INDE
    inde_col  = _find_col(df, 'INDE', ano)
    df['INDE'] = df[inde_col].apply(_parse_float) if inde_col else np.nan
    # Pedra derivada do INDE (evita problemas de encoding nos CSVs)
    df['Pedra'] = df['INDE'].apply(_inde_to_pedra)
    # Indicators
    for col in INDICATOR_COLS[:-1]:
        df[col] = df[col].apply(_parse_float) if col in df.columns else np.nan
    df['Fase']    = df.get('Fase', pd.Series([np.nan] * len(df))).apply(_parse_fase)
    df['Defasagem'] = pd.to_numeric(
        df.get('Defasagem', df.get('Defas', np.nan)), errors='coerce'
    )
    # composite target — alinhado ao modelo preditivo
    df['target']           = ((df['Defasagem'] >= 1) | (df['INDE'] < 5.5)).astype(float)
    df['defasagem_formal'] = (df['Defasagem'] >= 1).astype(float)
    genero_col = next((c for c in df.columns if 'n' in c.lower() and 'nero' in c.lower()), None)
    df['Genero'] = df[genero_col].map(
        {'F': 'Feminino', 'M': 'Masculino', 'Feminino': 'Feminino', 'Masculino': 'Masculino'}
    ) if genero_col else np.nan
    return df

@st.cache_data(show_spinner="Carregando dados históricos...")
def load_data():
    frames = []
    for ano in [2022, 2023, 2024]:
        path = os.path.join(DATA_PATH, f'DATATHON - {ano}.csv')
        if os.path.exists(path):
            frames.append(_load_year(path, ano))
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out['Pedra'] = pd.Categorical(out['Pedra'], categories=PEDRA_ORDER, ordered=True)
    return out

df = load_data()
if df.empty:
    st.error("Dados não encontrados em `data/`. Verifique os arquivos CSV.")
    st.stop()

# ── Helpers ────────────────────────────────────────────────────────────────────
def _layout(**kw):
    base = dict(paper_bgcolor='#F8FAFC', plot_bgcolor='white', margin=dict(t=20, b=60))
    base.update(kw)
    return base

def _insight(html: str):
    st.markdown(
        f'<div style="background:#EFF6FF; border-left:3px solid {PM_BLUE}; '
        f'border-radius:0 6px 6px 0; padding:0.55rem 0.9rem; '
        f'font-size:0.82rem; color:#1E40AF; margin-top:0.3rem; margin-bottom:0.5rem;">'
        f'💡 {html}</div>',
        unsafe_allow_html=True,
    )

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pm-hero">
    <h1>📊 Quick Insights</h1>
    <p>Panorama analítico dos aprendizes da Passos Mágicos — 2022 a 2024</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filtros")
    anos_sel   = st.multiselect("Ano", [2022, 2023, 2024], default=[2022, 2023, 2024])
    pedras_sel = st.multiselect("Pedra", PEDRA_ORDER, default=PEDRA_ORDER)
    fase_range = st.slider("Faixa de fase", 0, 9, (0, 9),
                           help="0 = Fase Alfa (alfabetização)")

# NaN values pass through when field is missing; filters apply only to known values
mask = (
    df['ano'].isin(anos_sel) &
    (df['Pedra'].isin(pedras_sel) | df['Pedra'].isna()) &
    (df['Fase'].between(fase_range[0], fase_range[1]) | df['Fase'].isna())
)
dff = df[mask].copy()
if len(dff) == 0:
    st.warning("Nenhum registro com os filtros selecionados.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# 1. RESUMO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">Resumo do período selecionado</p>', unsafe_allow_html=True)

inde_medio      = dff['INDE'].mean()
taxa_risco      = dff['target'].mean()
taxa_def_formal = dff['defasagem_formal'].mean()
pedra_mais      = dff['Pedra'].value_counts().idxmax() if dff['Pedra'].notna().any() else '—'

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Alunos no período",    f"{len(dff):,}".replace(",", "."))
m2.metric("INDE médio",           f"{inde_medio:.2f}")
m3.metric("Risco composto",       f"{taxa_risco:.1%}",
          help="Defasagem ≥ 1 ano OU INDE < 5,5 — alinhado ao target do modelo")
m4.metric("Defasagem formal",     f"{taxa_def_formal:.1%}",
          help="Alunos cursando fase abaixo da esperada para a idade")
m5.metric("Pedra mais frequente", str(pedra_mais))

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 2. CRESCIMENTO — alunos por ano
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">Crescimento do programa</p>', unsafe_allow_html=True)

contagem = df.groupby('ano').size().reset_index(name='Alunos')
base_2022 = contagem.loc[contagem['ano'] == 2022, 'Alunos'].values[0] if 2022 in contagem['ano'].values else None

_labels = []
for _, row in contagem.iterrows():
    if base_2022 is None or row['ano'] == 2022:
        _labels.append(str(int(row['Alunos'])))
    else:
        pct = (row['Alunos'] / base_2022 - 1) * 100
        sign = '+' if pct >= 0 else ''
        _labels.append(f"{int(row['Alunos'])}<br>({sign}{pct:.0f}% vs 2022)")

_n = len(contagem)
_textpos = ['top center'] * _n
if _n >= 1: _textpos[0]  = 'top right'
if _n >= 2: _textpos[-1] = 'top left'

fig_cr = go.Figure(go.Scatter(
    x=contagem['ano'], y=contagem['Alunos'],
    mode='lines+markers+text',
    line=dict(color=PM_BLUE, width=3),
    marker=dict(size=12, color=PM_BLUE),
    text=_labels,
    textposition=_textpos,
    textfont=dict(size=12, color=PM_BLUE),
    fill='tozeroy', fillcolor='rgba(0,48,135,0.07)',
    hovertemplate='%{x}: %{y} alunos<extra></extra>',
))
fig_cr.update_layout(
    **_layout(height=340, margin=dict(t=20, b=40, l=60, r=40)),
    xaxis=dict(tickvals=[2022, 2023, 2024], gridcolor=_GRID, title='Ano'),
    yaxis=dict(title='Nº de alunos', gridcolor=_GRID,
               range=[0, contagem['Alunos'].max() * 1.35]),
)
st.plotly_chart(fig_cr, use_container_width=True)

_pct_cr = (contagem['Alunos'].iloc[-1] / contagem['Alunos'].iloc[0] - 1) * 100
_insight(
    f"O programa cresceu <strong>{_pct_cr:.0f}%</strong> entre 2022 e 2024 "
    f"({contagem['Alunos'].iloc[0]:,} → {contagem['Alunos'].iloc[-1]:,} alunos). "
    "O relatório 2025 registra 1.200 aprendizes — a trajetória de crescimento é consistente."
)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 3. PEDRAS POR ANO — volume absoluto
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">Distribuição das Pedras por ano</p>', unsafe_allow_html=True)

pedra_dist = (dff[dff['Pedra'].notna()]
              .groupby(['ano', 'Pedra'], observed=True)
              .size().reset_index(name='n'))

fig_pa = px.bar(
    pedra_dist, x='ano', y='n', color='Pedra',
    barmode='group',
    color_discrete_map=PEDRA_COLORS,
    category_orders={'Pedra': PEDRA_ORDER},
    labels={'ano': 'Ano', 'n': 'Nº de alunos'},
    text='n',
)
fig_pa.update_traces(textposition='outside', textfont_size=11)
fig_pa.update_layout(
    **_layout(height=360, margin=dict(t=40, b=60)),
    xaxis=dict(tickvals=[2022, 2023, 2024]),
    legend=dict(orientation='h', yanchor='bottom', y=-0.3),
)
st.plotly_chart(fig_pa, use_container_width=True)

pedra_dist['total_ano'] = pedra_dist.groupby('ano')['n'].transform('sum')
pedra_dist['pct']       = pedra_dist['n'] / pedra_dist['total_ano'] * 100
quartz = pedra_dist[pedra_dist['Pedra'] == 'Quartzo'].sort_values('ano')
if len(quartz) >= 2:
    dq = quartz['pct'].iloc[-1] - quartz['pct'].iloc[0]
    _ano_ini = int(quartz['ano'].iloc[0])
    _ano_fim = int(quartz['ano'].iloc[-1])
    _insight(
        f"A proporção de Quartzo <strong>{'caiu' if dq < 0 else 'subiu'} "
        f"{abs(dq):.1f} p.p.</strong> entre {_ano_ini} e {_ano_fim} "
        f"({quartz['pct'].iloc[0]:.0f}% → {quartz['pct'].iloc[-1]:.0f}%). "
        "Reduzir Quartzo é o principal KPI de impacto da ONG."
    )

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 4. TAXA DE DEFASAGEM — por ano e por fase
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">Taxa de risco de defasagem</p>', unsafe_allow_html=True)
st.caption("Risco composto: defasagem formal (≥ 1 ano) **ou** INDE < 5,5 — alinhado ao target do modelo preditivo.")

tab_ano, tab_fase = st.tabs(["Por ano", "Por fase"])

with tab_ano:
    ra = (dff.groupby('ano')['target']
          .agg(['mean', 'sum', 'count'])
          .reset_index()
          .rename(columns={'mean': 'Taxa', 'sum': 'Risco', 'count': 'Total'}))
    ra['Taxa %'] = ra['Taxa'] * 100

    fig_ra = go.Figure(go.Bar(
        x=ra['ano'], y=ra['Taxa %'],
        marker_color=[YEAR_COLORS.get(str(a), PM_BLUE) for a in ra['ano']],
        text=[f"{v:.1f}%<br><span style='font-size:10px'>{int(r)}/{int(t)}</span>"
              for v, r, t in zip(ra['Taxa %'], ra['Risco'], ra['Total'])],
        textposition='outside',
        hovertemplate='%{x}: %{y:.1f}% em risco<extra></extra>',
    ))
    fig_ra.update_layout(
        **_layout(height=320),
        xaxis=dict(tickvals=[2022, 2023, 2024]),
        yaxis=dict(range=[0, ra['Taxa %'].max() * 1.4], title='Taxa de risco (%)'),
    )
    st.plotly_chart(fig_ra, use_container_width=True)

    dr = ra['Taxa %'].iloc[-1] - ra['Taxa %'].iloc[0]
    _insight(
        f"A taxa de risco composta <strong>{'reduziu' if dr < 0 else 'cresceu'} "
        f"{abs(dr):.1f} p.p.</strong> entre 2022 e 2024. "
        "Lembre que o risco composto inclui alunos com INDE < 5,5 mesmo sem defasagem formal — "
        "em média mais restritivo do que a defasagem isolada."
    )

with tab_fase:
    rf = (dff[dff['Fase'].notna() & dff['target'].notna()]
          .groupby('Fase')['target']
          .agg(['mean', 'sum', 'count'])
          .reset_index()
          .rename(columns={'mean': 'Taxa', 'sum': 'Risco', 'count': 'Total'}))
    rf['Fase']      = rf['Fase'].astype(int)
    rf['Taxa %']    = rf['Taxa'] * 100
    rf['FaseLabel'] = rf['Fase'].apply(lambda f: 'Alfa' if f == 0 else f'F{f}')
    rf = rf.sort_values('Taxa %', ascending=True)

    bar_colors_rf = [
        RISK_HIGH if v >= 40 else ('#F59E0B' if v >= 20 else RISK_LOW)
        for v in rf['Taxa %']
    ]
    fig_rf = go.Figure(go.Bar(
        x=rf['Taxa %'],
        y=rf['FaseLabel'],
        orientation='h',
        marker_color=bar_colors_rf,
        text=[f"{v:.0f}%  ({int(r)}/{int(t)})"
              for v, r, t in zip(rf['Taxa %'], rf['Risco'], rf['Total'])],
        textposition='outside',
        hovertemplate='%{y}: %{x:.1f}%<extra></extra>',
    ))
    fig_rf.update_layout(
        **_layout(height=420, margin=dict(t=20, b=40, l=65)),
        xaxis=dict(range=[0, rf['Taxa %'].max() * 1.35], title='Taxa de risco (%)'),
        yaxis=dict(title='Fase'),
    )
    st.plotly_chart(fig_rf, use_container_width=True)

    top_f    = rf.iloc[-1]
    bot_f    = rf.iloc[0]
    top_nome = 'Alfa' if int(top_f['Fase']) == 0 else f"Fase {int(top_f['Fase'])}"
    bot_nome = 'Alfa' if int(bot_f['Fase']) == 0 else f"Fase {int(bot_f['Fase'])}"
    _insight(
        f"<strong>{top_nome}</strong> concentra a maior taxa de risco "
        f"({top_f['Taxa %']:.0f}% — {int(top_f['Risco'])} de {int(top_f['Total'])} alunos). "
        f"<strong>{bot_nome}</strong> tem a menor ({bot_f['Taxa %']:.0f}%). "
        "Considere cruzar taxa com volume total por fase para priorizar intervenções — "
        "alta taxa numa fase pequena pode ser menos urgente que taxa moderada num grupo grande."
    )

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 5. INDE MÉDIO POR FASE — escala 4–8
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">INDE médio por fase escolar</p>', unsafe_allow_html=True)
st.caption("Fases 8 e 9 não possuem INDE registrado nos dados 2022–2024 — alunos existem mas o campo está em branco na fonte.")

inde_fase = (dff[dff['INDE'].notna() & dff['Fase'].notna()]
             .groupby(['Fase', 'ano'])['INDE']
             .mean().reset_index())
inde_fase['Fase'] = inde_fase['Fase'].astype(int)
inde_fase['Ano']  = inde_fase['ano'].astype(str)
_fases_com_dado = sorted(inde_fase['Fase'].unique().tolist())

fig_if = px.line(
    inde_fase, x='Fase', y='INDE', color='Ano',
    markers=True,
    color_discrete_map=YEAR_COLORS,
    labels={'INDE': 'INDE médio', 'Fase': 'Fase escolar'},
)
fig_if.add_hline(y=5.5, line_dash='dot', line_color='#DC2626', line_width=1.5,
                 annotation_text='Quartzo ↔ Ágata (5,5)', annotation_position='bottom right',
                 annotation_font_size=10)
fig_if.add_hline(y=7.0, line_dash='dot', line_color='#3B82F6', line_width=1.5,
                 annotation_text='Ágata ↔ Ametista (7,0)', annotation_position='top right',
                 annotation_font_size=10)
# Ametista | Topázio threshold (8.5) is above the zoom range (4–8) — omitted intentionally
fig_if.add_hrect(y0=4,   y1=5.5, fillcolor='rgba(220,38,38,0.05)',  line_width=0)
fig_if.add_hrect(y0=5.5, y1=7.0, fillcolor='rgba(59,130,246,0.04)', line_width=0)
fig_if.add_hrect(y0=7.0, y1=8.0, fillcolor='rgba(139,92,246,0.04)', line_width=0)
fig_if.update_traces(line_width=2.5, marker_size=9)
fig_if.update_layout(
    **_layout(height=380),
    xaxis=dict(tickvals=_fases_com_dado, gridcolor=_GRID),
    yaxis=dict(range=[4, 8], title='INDE médio (zoom 4–8)', gridcolor=_GRID),
    legend=dict(orientation='h', yanchor='bottom', y=-0.3),
)
st.plotly_chart(fig_if, use_container_width=True)

_insight(
    "O zoom em 4–8 revela variações que a escala 0–10 mascara. "
    "Fases com INDE médio próximo de 5,5 são as mais vulneráveis a uma queda para Quartzo — "
    "uma variação de 0,3 pontos pode definir a pedra do aluno. "
    "A linha vermelha pontilhada é o limiar crítico do modelo preditivo."
)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 6. SCATTER — Engajamento × Desempenho (2024 apenas)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">Engajamento × Desempenho acadêmico — 2024</p>',
            unsafe_allow_html=True)
st.caption("Cada ponto é um aluno de 2024. As linhas marcam as medianas, formando 4 quadrantes de intervenção.")

dff_sc = df[df['ano'] == 2024].copy()
dff_sc = dff_sc[dff_sc['IEG'].notna() & dff_sc['IDA'].notna() & dff_sc['Pedra'].notna()]

if not dff_sc.empty:
    fig_sc = px.scatter(
        dff_sc, x='IEG', y='IDA', color='Pedra',
        opacity=0.55,
        color_discrete_map=PEDRA_COLORS,
        category_orders={'Pedra': PEDRA_ORDER},
        labels={'IEG': 'IEG — Engajamento', 'IDA': 'IDA — Desempenho Acadêmico'},
        hover_data={'RA': True, 'Fase': True, 'INDE': ':.2f'},
        custom_data=['RA', 'Fase', 'INDE', 'Pedra'],
    )
    fig_sc.update_traces(
        hovertemplate=(
            "<b>RA %{customdata[0]}</b><br>"
            "IEG: %{x:.1f} · IDA: %{y:.1f}<br>"
            "INDE: %{customdata[2]:.2f} · Fase: %{customdata[1]}<br>"
            "Pedra: %{customdata[3]}<extra></extra>"
        )
    )

    med_ieg, med_ida = dff_sc['IEG'].median(), dff_sc['IDA'].median()
    fig_sc.add_vline(x=med_ieg, line_dash='dot', line_color='#CBD5E1', line_width=1.5)
    fig_sc.add_hline(y=med_ida, line_dash='dot', line_color='#CBD5E1', line_width=1.5)

    _nq1 = int(((dff_sc['IEG'] <  med_ieg) & (dff_sc['IDA'] <  med_ida)).sum())
    _nq2 = int(((dff_sc['IEG'] <  med_ieg) & (dff_sc['IDA'] >= med_ida)).sum())
    _nq3 = int(((dff_sc['IEG'] >= med_ieg) & (dff_sc['IDA'] >= med_ida)).sum())
    _nq4 = int(((dff_sc['IEG'] >= med_ieg) & (dff_sc['IDA'] <  med_ida)).sum())

    _Q_LABELS = [
        (f"⚠️ Baixo engajamento<br>Baixo desempenho<br><b>n = {_nq1}</b>", 0.3, 0.5, 'left', 'bottom'),
        (f"📖 Engajado mas<br>com dificuldades<br><b>n = {_nq2}</b>",       0.3, 9.7, 'left', 'top'),
        (f"🌟 Alta performance<br><b>n = {_nq3}</b>",                       9.7, 9.7, 'right', 'top'),
        (f"🎯 Bom desempenho<br>pouco engajamento<br><b>n = {_nq4}</b>",    9.7, 0.5, 'right', 'bottom'),
    ]
    for txt, x, y, xanch, yanch in _Q_LABELS:
        fig_sc.add_annotation(
            x=x, y=y, text=txt, showarrow=False,
            font=dict(size=10, color='#374151', family='sans-serif'),
            bgcolor='rgba(255,255,255,0.82)',
            bordercolor='#CBD5E1',
            borderwidth=1,
            borderpad=5,
            xanchor=xanch, yanchor=yanch,
        )
    fig_sc.update_layout(
        **_layout(height=450),
        xaxis=dict(range=[-0.2, 10.5], gridcolor=_GRID),
        yaxis=dict(range=[-0.2, 10.5], gridcolor=_GRID),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    pct_baixo = _nq1 / len(dff_sc) * 100
    _insight(
        f"<strong>{pct_baixo:.0f}% dos alunos de 2024</strong> ({_nq1} alunos) estão abaixo da mediana "
        "nos dois eixos — prioridade máxima de intervenção multidimensional. "
        f"Outros <strong>{_nq4}</strong> alunos têm bom engajamento mas desempenho abaixo da mediana: "
        "participam das atividades mas podem ter dificuldades específicas de aprendizado — "
        "indicado para avaliação psicopedagógica (IPP)."
    )

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 7. FUNIL DE RISCO POR FASE — taxa + volume
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">Funil de risco por fase — onde priorizar</p>',
            unsafe_allow_html=True)

rf2 = (dff[dff['Fase'].notna() & dff['target'].notna()]
       .groupby('Fase')['target']
       .agg(['mean', 'count'])
       .reset_index()
       .rename(columns={'mean': 'Taxa', 'count': 'n'}))
rf2['Fase']      = rf2['Fase'].astype(int)
rf2['Taxa %']    = rf2['Taxa'] * 100
rf2['FaseLabel'] = rf2['Fase'].apply(lambda f: 'Alfa' if f == 0 else f'F{f}')
rf2 = rf2.sort_values('Fase')

fig_fun = go.Figure()
fig_fun.add_trace(go.Bar(
    x=rf2['FaseLabel'], y=rf2['n'],
    name='Total de alunos',
    marker_color='rgba(0,48,135,0.12)',
    yaxis='y2',
    hovertemplate='%{x}: %{y} alunos<extra></extra>',
))
fig_fun.add_trace(go.Scatter(
    x=rf2['FaseLabel'], y=rf2['Taxa %'],
    name='Taxa de risco (%)',
    mode='lines+markers+text',
    line=dict(color=RISK_HIGH, width=3),
    marker=dict(
        size=11,
        color=[RISK_HIGH if v >= 40 else ('#F59E0B' if v >= 20 else RISK_LOW) for v in rf2['Taxa %']],
    ),
    text=[f"{v:.0f}%" for v in rf2['Taxa %']],
    textposition='top center',
    textfont=dict(size=10),
    hovertemplate='%{x}: %{y:.1f}% em risco<extra></extra>',
))
fig_fun.update_layout(
    **_layout(height=380),
    xaxis=dict(title='Fase escolar'),
    yaxis=dict(title='Taxa de risco (%)', range=[0, 110], gridcolor=_GRID),
    yaxis2=dict(title='Nº de alunos', overlaying='y', side='right',
                showgrid=False, range=[0, rf2['n'].max() * 4]),
    legend=dict(orientation='h', yanchor='bottom', y=-0.3),
    hovermode='x unified',
)
st.plotly_chart(fig_fun, use_container_width=True)

fase_max     = rf2.loc[rf2['Taxa %'].idxmax()]
fase_max_vol = rf2.loc[(rf2['Taxa %'] * rf2['n']).idxmax()]
_fn = lambda f: 'Alfa' if int(f) == 0 else f"Fase {int(f)}"
_insight(
    f"<strong>{_fn(fase_max['Fase'])}</strong> tem a maior taxa de risco ({fase_max['Taxa %']:.0f}%). "
    f"Mas <strong>{_fn(fase_max_vol['Fase'])}</strong> tem o maior volume absoluto de alunos em risco "
    f"({int(fase_max_vol['Taxa %'] * fase_max_vol['n'] / 100):.0f} alunos) — "
    "alta taxa numa fase pequena pode ser menos urgente que taxa moderada num grupo grande."
)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 8. DISTRIBUIÇÃO DO INDE — histograma com limiares
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">Distribuição do INDE — onde os alunos se concentram</p>',
            unsafe_allow_html=True)

anos_hist = st.multiselect(
    "Comparar anos (sobreposição):", [2022, 2023, 2024], default=[2022, 2024],
    key="hist_anos",
    help="Sobreponha anos para visualizar a migração de alunos entre pedras ao longo do tempo.",
)
fig_hist = go.Figure()
for ano in anos_hist:
    vals = dff[dff['ano'] == ano]['INDE'].dropna()
    fig_hist.add_trace(go.Histogram(
        x=vals, nbinsx=28, name=str(ano),
        marker_color=YEAR_COLORS.get(str(ano), PM_BLUE),
        opacity=0.65, histnorm='percent',
        hovertemplate=f"{ano}: %{{x:.1f}} | %{{y:.1f}}%<extra></extra>",
    ))
for val, lbl, cor in [
    (5.5, 'Quartzo | Ágata', '#DC2626'),
    (7.0, 'Ágata | Ametista', '#3B82F6'),
    (8.5, 'Ametista | Topázio', '#F59E0B'),
]:
    fig_hist.add_vline(x=val, line_dash='dash', line_color=cor, line_width=2,
                       annotation_text=lbl, annotation_position='top',
                       annotation_font_size=10)
fig_hist.update_layout(
    **_layout(height=360),
    barmode='overlay',
    xaxis=dict(title='INDE', range=[0, 10], gridcolor=_GRID),
    yaxis=dict(title='% de alunos', gridcolor=_GRID),
    legend=dict(orientation='h', yanchor='bottom', y=-0.3),
)
st.plotly_chart(fig_hist, use_container_width=True)

_insight(
    "Observe os picos próximos às linhas verticais — esses são os 'near misses'. "
    "Alunos levemente abaixo de 5,5 são os que mais se beneficiam de uma intervenção focada. "
    "Se a curva do ano mais recente se deslocou para a direita, o programa está elevando o INDE do grupo como um todo."
)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 9. CORRELAÇÃO ENTRE INDICADORES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-hdr">Correlação entre indicadores</p>', unsafe_allow_html=True)
st.caption(
    "**1,0 (vermelho escuro)** = movem-se perfeitamente juntos. "
    "**0** = sem relação linear. "
    "Negativo = relação inversa."
)

corr_cols = [c for c in INDICATOR_COLS if dff[c].notna().sum() > 50]
if len(corr_cols) >= 2:
    corr_m = dff[corr_cols].corr().round(2)
    fig_corr = px.imshow(
        corr_m, text_auto=True,
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1, aspect='auto',
    )
    fig_corr.update_traces(textfont_size=12)
    fig_corr.update_layout(
        height=430, paper_bgcolor='#F8FAFC',
        margin=dict(t=10, b=10),
        coloraxis_colorbar=dict(title='r'),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # fill diagonal with 0 to find strongest off-diagonal pair
    _arr = corr_m.to_numpy().copy()
    np.fill_diagonal(_arr, 0)
    corr_no_diag = pd.DataFrame(_arr, index=corr_m.index, columns=corr_m.columns)
    pair  = corr_no_diag.abs().unstack().idxmax()
    r_val = corr_m.loc[pair[0], pair[1]]
    if 'INDE' in corr_m.columns:
        inde_row = corr_m['INDE'].drop('INDE').abs().idxmax()
        inde_insight = (
            f" O indicador mais ligado ao INDE é o <strong>{inde_row}</strong> "
            f"(r = {corr_m.loc['INDE', inde_row]:.2f})."
        )
    else:
        inde_insight = ""
    _insight(
        f"Par mais correlacionado: <strong>{pair[0]} × {pair[1]}</strong> (r = {r_val:.2f}).{inde_insight} "
        "Indicadores com correlação baixa entre si precisam ser monitorados de forma independente — "
        "um aluno pode ter bom desempenho acadêmico e saúde psicossocial comprometida (e vice-versa)."
    )

st.markdown(
    "<div style='text-align:center; color:#94A3B8; font-size:0.8rem; margin-top:2rem;'>"
    "Datathon FIAP × Passos Mágicos · Dados reais da ONG (2022–2024)"
    "</div>",
    unsafe_allow_html=True
)
