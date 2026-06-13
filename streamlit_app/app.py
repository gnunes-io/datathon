"""Entry point do app multipage — Passos Mágicos Tech Hub."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import GLOBAL_CSS, LOGO_PATH, load_model

st.set_page_config(
    page_title="🌟Passos Mágicos - Tech Hub",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if os.path.exists(LOGO_PATH):
    st.logo(LOGO_PATH, size="large")

load_model()

pg = st.navigation({
    "Ferramentas": [
        st.Page("_pages/home.py",  title="Início",           icon="🏠"),
        st.Page("_pages/radar.py", title="Radar de Risco",   icon="🎯"),
        st.Page("_pages/eda.py",   title="Análise Rápida",   icon="📊"),
    ],
    "Apresentação": [
        st.Page("_pages/apresentacao.py", title="Vídeo Apresentação", icon="🎬"),
        st.Page("_pages/arquitetura.py",  title="Arquitetura",        icon="🏗️"),
    ],
    "Equipe": [
        st.Page("_pages/staff.py", title="Staff PsicoNeuroPedagogia", icon="👥"),
    ],
})

# Links externos — aparecem abaixo da navegação na sidebar
with st.sidebar:
    st.markdown(
        "<hr style='border-color:rgba(255,255,255,0.15); margin:0.5rem 0;'>",
        unsafe_allow_html=True,
    )
    st.page_link("https://google.com", label="Assistente Pedagógico", icon="🤖")
    st.page_link("https://google.com", label="Notebooks",             icon="📓")
    st.page_link("https://google.com", label="GitHub",                icon="🐙")
    st.page_link("https://google.com", label="PDF Executivo",         icon="📄")

pg.run()
