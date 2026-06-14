"""Página GitHub — redirect para o repositório."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

GITHUB_URL = "https://google.com"  # placeholder — substituir pela URL do repo em produção

st.markdown("""
<div class="pm-hero">
    <h1>🐙 GitHub</h1>
    <p>Repositório do projeto — código-fonte, notebooks e documentação</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.link_button(
    "Abrir Repositório no GitHub →",
    url=GITHUB_URL,
    use_container_width=True,
    type="primary",
)
st.caption("O repositório será aberto em uma nova aba.")
