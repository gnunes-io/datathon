"""Página Vídeo Apresentação, em construção."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="pm-hero">
    <h1>🎬 Vídeo Apresentação</h1>
    <p>Apresentação do projeto Passos Mágicos, Datathon FIAP 2024</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center; padding:4rem 2rem; color:#94A3B8; font-size:1rem;'>"
    "🎬 Vídeo em breve<br><small>Adicione o link do vídeo nesta página</small>"
    "</div>",
    unsafe_allow_html=True,
)
