"""Página Arquitetura — diagrama da solução."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="pm-hero">
    <h1>🏗️ Arquitetura da Solução</h1>
    <p>Diagrama técnico e fluxo de dados do projeto</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center; padding:4rem 2rem; color:#94A3B8; font-size:1rem;'>"
    "🏗️ Diagrama em breve<br><small>Adicione a imagem ou diagrama de arquitetura aqui</small>"
    "</div>",
    unsafe_allow_html=True,
)
