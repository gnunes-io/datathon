"""Página Notebooks — redirect para os notebooks do projeto."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

NOTEBOOKS_URL = "https://google.com"  # placeholder — substituir pela URL (Colab/GitHub) em produção

st.markdown("""
<div class="pm-hero">
    <h1>📓 Notebooks</h1>
    <p>Análise Exploratória de Dados e modelo preditivo — notebooks interativos</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="medium")
with c1:
    st.markdown(f"""
    <div class="ind-card">
        <strong>📊 EDA — Análise Exploratória</strong><br>
        <small>12 perguntas analíticas sobre os dados 2022–2024 da Passos Mágicos</small>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="ind-card">
        <strong>🤖 Modelo Preditivo</strong><br>
        <small>Random Forest com validação cruzada OOF · AUC-ROC 0,9695 · Threshold 61%</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.link_button(
    "Abrir Notebooks →",
    url=NOTEBOOKS_URL,
    use_container_width=True,
    type="primary",
)
st.caption("Os notebooks serão abertos em uma nova aba.")
