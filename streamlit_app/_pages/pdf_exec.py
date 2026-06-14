"""Página PDF Executivo — redirect para o documento."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

PDF_URL = "https://google.com"  # placeholder — substituir pela URL do PDF em produção

st.markdown("""
<div class="pm-hero">
    <h1>📄 PDF Executivo</h1>
    <p>Sumário executivo do projeto Passos Mágicos × Datathon FIAP</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.link_button(
    "Abrir PDF Executivo →",
    url=PDF_URL,
    use_container_width=True,
    type="primary",
)
st.caption("O documento será aberto em uma nova aba.")
