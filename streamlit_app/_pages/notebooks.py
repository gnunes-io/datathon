"""Página Notebooks, preview embutido via nbviewer para os notebooks do projeto."""
import os
import sys
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

GITHUB_REPO = "gnunes-io/datathon"
GITHUB_BRANCH = "main"

NOTEBOOKS = {
    "eda": {
        "label": "📊 EDA",
        "path": "eda/EDA_PassosMagicos.ipynb",
        "title": "EDA, Análise Exploratória",
        "desc": "12 perguntas analíticas sobre os dados 2022–2024 da Passos Mágicos",
    },
    "modelo": {
        "label": "🤖 Modelo ML",
        "path": "model/modelo_preditivo.ipynb",
        "title": "Modelo Preditivo",
        "desc": "Random Forest com validação cruzada OOF · AUC-ROC 0,9695 · Threshold 61%",
    },
}

st.markdown("""
<div class="pm-hero">
    <h1>📓 Notebooks</h1>
    <p>Análise Exploratória de Dados e modelo preditivo, notebooks interativos</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if "notebook_ativo" not in st.session_state:
    st.session_state.notebook_ativo = "eda"

c1, c2 = st.columns(2, gap="medium")
with c1:
    if st.button(
        NOTEBOOKS["eda"]["label"],
        use_container_width=True,
        type="primary" if st.session_state.notebook_ativo == "eda" else "secondary",
    ):
        st.session_state.notebook_ativo = "eda"
        st.rerun()
with c2:
    if st.button(
        NOTEBOOKS["modelo"]["label"],
        use_container_width=True,
        type="primary" if st.session_state.notebook_ativo == "modelo" else "secondary",
    ):
        st.session_state.notebook_ativo = "modelo"
        st.rerun()

ativo = NOTEBOOKS[st.session_state.notebook_ativo]

st.markdown(f"""
<div class="ind-card">
    <strong>{ativo['title']}</strong><br>
    <small>{ativo['desc']}</small>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

nbviewer_url = f"https://nbviewer.org/github/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{ativo['path']}"
github_url = f"https://github.com/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{ativo['path']}"

components.iframe(nbviewer_url, height=900, scrolling=True)

st.caption(f"Preview via [nbviewer]({nbviewer_url}) · [ver no GitHub]({github_url})")
