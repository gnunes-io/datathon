"""Entry point do app multipage, Passos Mágicos Tech Hub."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import GLOBAL_CSS, LOGO_PATH, load_model

st.set_page_config(
    page_title="Passos Mágicos - Tech Hub",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH, size="large")

load_model()

pg = st.navigation({
    "": [
        st.Page("_pages/home.py", title="Início", icon="🏠"),
    ],
    "Ferramentas": [
        st.Page("_pages/radar.py", title="Radar de Risco",              icon="🎯"),
        st.Page("_pages/bot.py",   title="Assistente Psicopedagógico",  icon="💬"),
        st.Page("_pages/eda.py",   title="Quick Insights",              icon="📊"),
    ],
    "Apresentação": [
        st.Page("_pages/apresentacao.py", title="Vídeo",          icon="🎬"),
        st.Page("_pages/arquitetura.py",  title="Arquitetura",    icon="🏗️"),
        st.Page("_pages/pdf_exec.py",     title="PDF Executivo",  icon="📄"),
        st.Page("_pages/github_page.py",  title="GitHub",         icon="🐙"),
        st.Page("_pages/notebooks.py",    title="Notebooks",      icon="📓"),
    ],
})

pg.run()
