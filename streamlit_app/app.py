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

# Logo no topo da sidebar, acima dos links de navegação
if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH, size="large")

# Pré-carrega o modelo para que o cache fique disponível em todas as páginas
load_model()

pg = st.navigation([
    st.Page("pages/home.py",  title="Início",           icon="🏠"),
    st.Page("pages/radar.py", title="Radar de Risco",   icon="🎯"),
    st.Page("pages/eda.py",   title="Dados Históricos", icon="📊"),
])

pg.run()
