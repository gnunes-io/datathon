"""Página EDA Visual — panorama histórico dos dados da Passos Mágicos."""
import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import DATA_PATH, PM_BLUE, PM_GOLD, RISK_HIGH, RISK_LOW, GLOBAL_CSS

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Carregamento e cache dos dados ─────────────────────────────────────────────
INDICATOR_COLS = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']
PEDRA_ORDER    = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']
PEDRA_COLORS   = {'Quartzo': '#6B7280', 'Ágata': '#3B82F6',
                  'Ametista': '#8B5CF6', 'Topázio': '#F59E0B'}

def _parse_float(s):
    if pd.isna(s): return np.nan
    try: return float(str(s).replace(',', '.'))
    except: return np.nan

def _load_year(path, ano):
    df = pd.read_csv(path, encoding='latin1')
    df['ano'] = ano

    inde_col  = next((c for c in df.columns if 'INDE' in c and str(ano) in c), None)
    df['INDE'] = df[inde_col].apply(_parse_float) if inde_col else np.nan

    pedra_col  = next((c for c in df.columns if 'Pedra' in c and str(ano) in c), None)
    df['Pedra'] = df[pedra_col] if pedra_col else np.nan

    for col in INDICATOR_COLS[:-1]:   # todos exceto INDE (já processado)
        df[col] = df[col].apply(_parse_float) if col in df.columns else np.nan

    df['Fase']       = pd.to_numeric(df.get('Fase', np.nan), errors='coerce')
    df['Defasagem']  = pd.to_numeric(
        df.get('Defasagem', df.get('Defas', np.nan)), errors='coerce'
    )
    df['target']     = (df['Defasagem'] >= 1).astype(float)
    genero_col       = next((c for c in df.columns if 'n' in c.lower() and 'nero' in c.lower()), None)
    df['Genero']     = df[genero_col].map(
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
    df = pd.concat(frames, ignore_index=True)
    df['Pedra'] = pd.Categorical(df['Pedra'], categories=PEDRA_ORDER, ordered=True)
    return df

df = load_data()
if df.empty:
    st.error("Dados não encontrados em `data/`. Verifique os arquivos CSV.")
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pm-hero">
    <h1>📊 Dados Históricos</h1>
    <p>Panorama dos alunos da Passos Mágicos — 2022 a 2024</p>
</div>
""", unsafe_allow_html=True)

# ── Filtros sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filtros")
    anos_sel   = st.multiselect("Ano", [2022, 2023, 2024], default=[2022, 2023, 2024])
    pedras_sel = st.multiselect("Pedra", PEDRA_ORDER, default=PEDRA_ORDER)
    fase_range = st.slider("Faixa de fase", 1, 8, (1, 8))

mask = (
    df['ano'].isin(anos_sel) &
    df['Pedra'].isin(pedras_sel) &
    df['Fase'].between(fase_range[0], fase_range[1])
)
dff = df[mask].copy()
n_total = len(dff)
if n_total == 0:
    st.warning("Nenhum registro com os filtros selecionados.")
    st.stop()

# ── Cards de resumo ────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Resumo do período selecionado</p>',
            unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
inde_medio = dff['INDE'].mean()
taxa_risco = dff['target'].mean()
pedra_mais = (dff['Pedra'].value_counts().idxmax()
              if dff['Pedra'].notna().any() else '—')

# delta vs 2022 (se houver 2022 nos dados)
inde_2022 = df[df['ano'] == 2022]['INDE'].mean()
delta_inde = f"{inde_medio - inde_2022:+.2f} vs 2022" if 2022 in anos_sel and len(anos_sel) > 1 else None

m1.metric("Alunos no período", f"{n_total:,}".replace(",", "."))
m2.metric("INDE médio", f"{inde_medio:.2f}", delta_inde)
m3.metric("Taxa de risco de defasagem", f"{taxa_risco:.1%}")
m4.metric("Pedra mais frequente", str(pedra_mais))

st.markdown("---")

# ── Evolução temporal dos indicadores ─────────────────────────────────────────
st.markdown('<p class="section-hdr">Evolução dos indicadores por ano</p>',
            unsafe_allow_html=True)

ind_sel = st.multiselect(
    "Indicadores a exibir", INDICATOR_COLS,
    default=['INDE', 'IDA', 'IAN', 'IEG'],
    key="ind_evol"
)

if ind_sel:
    evol = (dff.groupby('ano')[ind_sel]
               .mean()
               .reset_index()
               .melt(id_vars='ano', var_name='Indicador', value_name='Média'))

    fig_evol = px.line(
        evol, x='ano', y='Média', color='Indicador',
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={'ano': 'Ano', 'Média': 'Valor médio (0–10)'},
    )
    fig_evol.update_traces(line_width=2.5, marker_size=8)
    fig_evol.update_layout(
        xaxis=dict(tickvals=[2022, 2023, 2024]),
        yaxis=dict(range=[0, 10]),
        legend=dict(orientation='h', yanchor='bottom', y=-0.3),
        height=380, paper_bgcolor='#F8FAFC', plot_bgcolor='white',
        margin=dict(t=20, b=60),
    )
    st.plotly_chart(fig_evol, use_container_width=True)

st.markdown("---")

# ── Distribuição das Pedras + Taxa de risco por pedra ─────────────────────────
left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.markdown('<p class="section-hdr">Distribuição das Pedras por ano</p>',
                unsafe_allow_html=True)

    pedra_dist = (dff[dff['Pedra'].notna()]
                  .groupby(['ano', 'Pedra'], observed=True)
                  .size()
                  .reset_index(name='n'))

    fig_pedra = px.bar(
        pedra_dist, x='ano', y='n', color='Pedra',
        barmode='group',
        color_discrete_map=PEDRA_COLORS,
        category_orders={'Pedra': PEDRA_ORDER},
        labels={'ano': 'Ano', 'n': 'Número de alunos', 'Pedra': 'Pedra'},
    )
    fig_pedra.update_layout(
        height=320, paper_bgcolor='#F8FAFC', plot_bgcolor='white',
        legend=dict(orientation='h', yanchor='bottom', y=-0.35),
        margin=dict(t=10, b=60),
        xaxis=dict(tickvals=[2022, 2023, 2024]),
    )
    st.plotly_chart(fig_pedra, use_container_width=True)

with right_col:
    st.markdown('<p class="section-hdr">Taxa de risco por Pedra Classificatória</p>',
                unsafe_allow_html=True)

    risco_pedra = (dff[dff['Pedra'].notna() & dff['target'].notna()]
                   .groupby('Pedra', observed=True)['target']
                   .agg(['mean', 'count'])
                   .reset_index()
                   .rename(columns={'mean': 'Taxa', 'count': 'n'}))
    risco_pedra['Taxa %'] = risco_pedra['Taxa'] * 100

    fig_rp = go.Figure(go.Bar(
        x=risco_pedra['Pedra'],
        y=risco_pedra['Taxa %'],
        marker_color=[PEDRA_COLORS.get(p, PM_BLUE) for p in risco_pedra['Pedra']],
        text=[f"{v:.1f}%" for v in risco_pedra['Taxa %']],
        textposition='outside',
        hovertemplate='%{x}<br>%{y:.1f}% em risco<extra></extra>',
    ))
    fig_rp.update_layout(
        yaxis=dict(range=[0, risco_pedra['Taxa %'].max() * 1.3 + 5],
                   title='Taxa de risco de defasagem (%)'),
        height=320, paper_bgcolor='#F8FAFC', plot_bgcolor='white',
        margin=dict(t=10, b=30),
    )
    st.plotly_chart(fig_rp, use_container_width=True)

st.markdown("---")

# ── Correlação entre indicadores ───────────────────────────────────────────────
st.markdown('<p class="section-hdr">Correlação entre indicadores</p>',
            unsafe_allow_html=True)
st.caption(
    "Quanto mais próximo de 1 (azul escuro), mais os dois indicadores variam juntos. "
    "Valores próximos de 0 indicam pouca relação linear."
)

corr_cols = [c for c in INDICATOR_COLS if dff[c].notna().sum() > 50]
if len(corr_cols) >= 2:
    corr_matrix = dff[corr_cols].corr().round(2)
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        aspect='auto',
    )
    fig_corr.update_layout(
        height=420, paper_bgcolor='#F8FAFC',
        margin=dict(t=10, b=10),
        coloraxis_colorbar=dict(title='r'),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("---")

# ── Box plots: risco vs sem risco ─────────────────────────────────────────────
st.markdown('<p class="section-hdr">Perfil de risco vs sem risco</p>',
            unsafe_allow_html=True)
st.caption("Comparação da distribuição dos indicadores entre alunos com e sem risco de defasagem.")

box_cols = [c for c in ['IAN', 'IDA', 'IEG', 'IAA', 'INDE', 'IPV']
            if dff[c].notna().sum() > 10]

dff_box = dff[dff['target'].notna()].copy()
dff_box['Grupo'] = dff_box['target'].map({0.0: 'Sem risco', 1.0: 'Em risco'})

if not dff_box.empty and box_cols:
    fig_box = make_subplots(rows=1, cols=len(box_cols),
                            subplot_titles=box_cols, shared_yaxes=True)
    for i, col in enumerate(box_cols, start=1):
        for grupo, cor in [('Sem risco', RISK_LOW), ('Em risco', RISK_HIGH)]:
            vals = dff_box[dff_box['Grupo'] == grupo][col].dropna()
            fig_box.add_trace(
                go.Box(y=vals.values, name=grupo, marker_color=cor,
                       showlegend=(i == 1), legendgroup=grupo,
                       boxmean=True,
                       hovertemplate=f"{col}<br>%{{y:.1f}}<extra>{grupo}</extra>"),
                row=1, col=i,
            )
    fig_box.update_layout(
        height=380, paper_bgcolor='#F8FAFC', plot_bgcolor='white',
        boxmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=-0.25),
        margin=dict(t=30, b=60),
        yaxis=dict(range=[0, 10]),
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ── Distribuição do INDE por fase ──────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-hdr">INDE médio por fase escolar</p>',
            unsafe_allow_html=True)

inde_fase = (dff[dff['INDE'].notna() & dff['Fase'].notna()]
             .groupby(['Fase', 'ano'])['INDE']
             .mean()
             .reset_index())
inde_fase['Fase'] = inde_fase['Fase'].astype(int)
inde_fase['Ano']  = inde_fase['ano'].astype(str)

fig_fase = px.line(
    inde_fase, x='Fase', y='INDE', color='Ano',
    markers=True,
    color_discrete_map={'2022': '#64748B', '2023': PM_BLUE, '2024': PM_GOLD},
    labels={'INDE': 'INDE médio', 'Fase': 'Fase escolar'},
)
fig_fase.add_hline(y=5.5, line_dash='dot', line_color='#DC2626',
                   annotation_text='Limiar Quartzo (5,5)')
fig_fase.add_hline(y=7.0, line_dash='dot', line_color='#3B82F6',
                   annotation_text='Limiar Ágata (7,0)')
fig_fase.update_layout(
    height=360, paper_bgcolor='#F8FAFC', plot_bgcolor='white',
    xaxis=dict(tickvals=list(range(1, 9))),
    yaxis=dict(range=[0, 10]),
    legend=dict(orientation='h', yanchor='bottom', y=-0.3),
    margin=dict(t=10, b=60),
)
st.plotly_chart(fig_fase, use_container_width=True)

st.markdown(
    "<div style='text-align:center; color:#94A3B8; font-size:0.8rem; margin-top:2rem;'>"
    "Datathon FIAP × Passos Mágicos · Dados reais da ONG (2022–2024)"
    "</div>",
    unsafe_allow_html=True
)
