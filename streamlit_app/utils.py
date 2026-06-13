"""Utilitários compartilhados — Passos Mágicos Radar de Risco."""
import os
import numpy as np
import pandas as pd
import joblib
import streamlit as st

# ── Caminhos ──────────────────────────────────────────────────────────────────
_HERE      = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH  = os.path.join(_HERE, '..', 'Passos-magicos-icon-cor.png')
MODEL_PATH = os.path.join(_HERE, '..', 'model', 'modelo_risco_defasagem.pkl')
DATA_PATH  = os.path.join(_HERE, '..', 'data')

# ── Cores Passos Mágicos ──────────────────────────────────────────────────────
PM_BLUE   = "#003087"
PM_GOLD   = "#F59E0B"
RISK_HIGH = "#DC2626"
RISK_MED  = "#D97706"
RISK_LOW  = "#059669"

# ── Nomes amigáveis das features (para SHAP e UI) ─────────────────────────────
FEATURE_NAMES_PT = {
    'IAN':               'Adequação de Nível',
    'IDA':               'Desempenho Acadêmico',
    'IEG':               'Engajamento',
    'IAA':               'Autoavaliação',
    'IPS':               'Psicossocial',
    'IPP':               'Psicopedagógico',
    'IPV':               'Ponto de Virada',
    'INDE':              'Índice Geral',
    'Fase':              'Fase Escolar',
    'ind_academico_medio': 'Média Acadêmica',
    'ind_psico_medio':   'Média Psicossocial',
    'gap_ian_fase':      'Gap Nível × Fase',
    'inde_x_ian':        'INDE × IAN',
    'baixo_ida':         'IDA Crítico (< 5)',
    'baixo_ieg':         'IEG Crítico (< 5)',
    'fase_sq':           'Fase²',
    'genero_cod':        'Gênero',
    'pedra_ord':         'Pedra Classificatória',
}

# ── Metadados dos indicadores principais ──────────────────────────────────────
INDICATORS = [
    ('IAN',  'Adequação de Nível',
     'Mede se o aluno está cursando conteúdo adequado para sua fase. '
     'Valor baixo indica que o aluno está em nível abaixo do esperado para a idade.'),
    ('IDA',  'Desempenho Acadêmico',
     'Média ponderada das avaliações em Matemática, Português e Inglês. '
     'É o indicador mais direto de aprendizado formal.'),
    ('IEG',  'Engajamento',
     'Mede frequência, participação e comportamento nas atividades da ONG. '
     'Baixo engajamento frequentemente precede queda acadêmica.'),
    ('IAA',  'Autoavaliação',
     'Como o próprio aluno avalia seu desempenho e evolução. '
     'Autoavaliação baixa pode indicar desmotivação ou baixa autoestima.'),
    ('IPS',  'Indicador Psicossocial',
     'Aspectos emocionais, relacionamentos e contexto familiar avaliados pela equipe de psicologia.'),
    ('IPP',  'Indicador Psicopedagógico',
     'Avaliação psicopedagógica realizada desde 2023. '
     'Identifica dificuldades específicas de aprendizado (atenção, memória, leitura).'),
    ('IPV',  'Ponto de Virada',
     'Indica se o aluno atingiu uma transformação significativa em sua trajetória educacional.'),
    ('INDE', 'Índice de Desenvolvimento Educacional',
     'Índice síntese que combina todos os indicadores. '
     'Base para as pedras classificatórias: Quartzo < Ágata < Ametista < Topázio.'),
]

PEDRAS_INFO = {
    'Quartzo':  ('INDE < 5,5',  '🪨', '#6B7280'),
    'Ágata':    ('5,5 ≤ INDE < 7,0', '💎', '#3B82F6'),
    'Ametista': ('7,0 ≤ INDE < 8,5', '💜', '#8B5CF6'),
    'Topázio':  ('INDE ≥ 8,5',  '⭐', '#F59E0B'),
}


# ── Carregamento do modelo ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Carregando modelo...")
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    payload = joblib.load(MODEL_PATH)
    for _, step in payload['pipeline'].steps:
        if hasattr(step, 'statistics_') and not hasattr(step, '_fill_dtype'):
            step._fill_dtype = step.statistics_.dtype
    return payload


# ── Feature engineering (idêntico ao notebook) ────────────────────────────────
def build_features(ian, ida, ieg, iaa, ips, ipp, ipv, inde, fase, genero, pedra):
    pedra_map  = {'Quartzo': 0, 'Ágata': 1, 'Ametista': 2, 'Topázio': 3}
    genero_map = {'Feminino': 0, 'Masculino': 1, 'Não informado': np.nan}
    return {
        'IAN': ian, 'IDA': ida, 'IEG': ieg, 'IAA': iaa,
        'IPS': ips, 'IPP': ipp, 'IPV': ipv, 'INDE': inde,
        'Fase': fase,
        'ind_academico_medio': (ida + ieg) / 2,
        'ind_psico_medio':     (iaa + ips) / 2,
        'gap_ian_fase':        ian - fase * 0.5,
        'inde_x_ian':          inde * ian,
        'baixo_ida':           float(ida < 5),
        'baixo_ieg':           float(ieg < 5),
        'fase_sq':             float(fase ** 2),
        'genero_cod':          genero_map.get(genero, np.nan),
        'pedra_ord':           float(pedra_map.get(pedra, np.nan))
        if pedra in pedra_map else np.nan,
    }


def predict(payload, feats_dict):
    """Retorna (prob: float, shap_series: pd.Series | None)."""
    pipeline     = payload['pipeline']
    feature_cols = payload['feature_cols']
    df_in        = pd.DataFrame([feats_dict]).reindex(columns=feature_cols)
    prob         = float(pipeline.predict_proba(df_in)[:, 1][0])

    shap_vals = None
    explainer = payload.get('shap_explainer')
    if explainer is not None:
        try:
            X_imp = pipeline.named_steps['imputer'].transform(df_in)
            sv    = explainer.shap_values(X_imp, check_additivity=False)
            # Normalise to 1-D array of shape (n_features,) for class 1
            sv = np.array(sv[1] if isinstance(sv, list) else sv)
            if sv.ndim == 3:        # (samples, features, classes)
                sv = sv[0, :, 1]
            elif sv.ndim == 2:
                if sv.shape[0] == 1:    # (1, features)
                    sv = sv[0]
                elif sv.shape[1] == 2:  # (features, classes) — single sample
                    sv = sv[:, 1]
                else:
                    sv = sv[0]
            if len(sv) == len(feature_cols):
                shap_vals = pd.Series(sv, index=feature_cols)
        except Exception:
            pass

    return prob, shap_vals


def risk_level(prob, threshold):
    """Retorna (nível_str, emoji, cor_hex).

    Zonas: alto ≥ threshold · médio ≥ 0.40 · baixo < 0.40
    """
    if prob >= threshold:
        return 'alto',  '🔴', RISK_HIGH
    elif prob >= 0.40:
        return 'medio', '🟠', RISK_MED
    else:
        return 'baixo', '🟢', RISK_LOW


# ── CSS global ─────────────────────────────────────────────────────────────────
GLOBAL_CSS = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{ background: #F8FAFC; }}
[data-testid="stSidebar"] {{ background: {PM_BLUE} !important; }}
[data-testid="stSidebar"] * {{ color: #E2E8F0 !important; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.2); }}
[data-testid="stSidebar"] .stMarkdown h3 {{ color: {PM_GOLD} !important; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; }}

.pm-hero {{
    background: linear-gradient(135deg, #003087 0%, #0052CC 100%);
    border-radius: 16px; padding: 2rem 2rem 1.75rem;
    text-align: center; margin-bottom: 1.5rem;
}}
.pm-hero h1 {{ color: #fff; font-size: 1.9rem; margin: 0.5rem 0 0.25rem; }}
.pm-hero p  {{ color: #93C5FD; font-size: 0.95rem; margin: 0; }}

.risk-card {{
    border-radius: 12px; padding: 1.25rem 1.5rem;
    text-align: center; color: white; margin-bottom: 0.75rem;
}}
.risk-card .pct  {{ font-size: 2.8rem; font-weight: 800; margin: 0; line-height: 1.1; }}
.risk-card .label {{ font-size: 0.85rem; font-weight: 600; letter-spacing: 0.08em; margin: 0.2rem 0 0; opacity: 0.9; }}
.risk-card .sub  {{ font-size: 0.78rem; margin: 0.35rem 0 0; opacity: 0.8; }}

.metric-row {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.35rem 0.5rem 0.35rem 0.65rem;
    border-radius: 6px; margin-bottom: 0.25rem; font-size: 0.84rem;
    border-left: 3px solid transparent;
}}
.metric-row.above {{ border-left-color: {RISK_LOW}; }}
.metric-row.below {{ border-left-color: {RISK_HIGH}; }}
.metric-row .delta {{ font-size: 0.75rem; opacity: 0.6; }}

.step-card {{
    background: white; border-radius: 12px; padding: 1.25rem 1rem;
    text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    border-top: 3px solid {PM_GOLD}; height: 100%;
}}
.step-card .num {{ font-size: 1.6rem; font-weight: 800; color: {PM_GOLD}; }}
.step-card h4   {{ color: {PM_BLUE}; margin: 0.4rem 0 0.25rem; font-size: 0.95rem; }}
.step-card p    {{ color: #64748B; font-size: 0.82rem; margin: 0; }}

.ind-card {{
    background: white; border-radius: 10px; padding: 0.9rem 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 0.5rem;
    border-left: 4px solid {PM_BLUE};
}}
.ind-card strong {{ color: {PM_BLUE}; }}
.ind-card small  {{ color: #64748B; font-size: 0.8rem; }}

.section-hdr {{
    color: {PM_BLUE}; font-size: 0.8rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    border-bottom: 2px solid {PM_GOLD}; padding-bottom: 0.2rem;
    margin: 1rem 0 0.6rem;
}}

.ref-caption {{
    font-size: 0.72rem; color: #94A3B8; margin-top: -0.5rem;
    margin-bottom: 0.5rem; padding-left: 0.1rem;
}}
</style>
"""
