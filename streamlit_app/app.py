"""Entry point do app multipage — Passos Mágicos Radar de Risco."""
import os
import sys
import streamlit as st

# Garante que utils.py é importável a partir de qualquer página
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import GLOBAL_CSS, LOGO_PATH, load_model

st.set_page_config(
    page_title="Passos Mágicos — Radar de Risco",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Pré-carrega o modelo para que o cache fique disponível em todas as páginas
payload = load_model()

pg = st.navigation([
    st.Page("pages/home.py",  title="Início",           icon="🏠"),
    st.Page("pages/radar.py", title="Radar de Risco",   icon="🎯"),
    st.Page("pages/eda.py",   title="Dados Históricos", icon="📊"),
])

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown(f"### 🌟 Passos Mágicos")

    st.markdown("---")

    if payload:
        st.markdown("### Modelo")
        st.markdown(f"""
        **{payload.get('model_name', 'Modelo')}**
        - Treino: {payload.get('train_years', [2022])}
        - Validação: {payload.get('val_year', 2023)}
        - Teste: {payload.get('test_year', 2024)}
        - AUC-ROC: **{payload.get('auc_roc', 0):.3f}**
        - Threshold: **{payload.get('threshold', 0):.2f}**
        - SHAP: {"✅" if payload.get('shap_explainer') else "⚠️ ausente"}
        """)
        st.caption("Threshold calibrado em 2023 (validação)")
    else:
        st.warning("⚠️ Modelo não encontrado.\nExecute `model/modelo_preditivo.ipynb`.")

    st.markdown("---")
    st.markdown("### Pedras Classificatórias")
    st.markdown("""
    | Pedra | INDE |
    |-------|------|
    | 🪨 Quartzo | < 5,5 |
    | 💎 Ágata | 5,5 – 7,0 |
    | 💜 Ametista | 7,0 – 8,5 |
    | ⭐ Topázio | ≥ 8,5 |
    """)

pg.run()
