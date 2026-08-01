"""Página Vídeo Apresentação, embed do vídeo executivo do projeto."""
import os
import sys
import streamlit as st
from streamlit.components.v1 import html

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

YOUTUBE_EMBED_URL = "https://www.youtube.com/embed/lGd5BIrcSZ4"
YOUTUBE_WATCH_URL = "https://www.youtube.com/watch?v=lGd5BIrcSZ4"

st.markdown("""
<div class="pm-hero">
    <h1>🎬 Vídeo Apresentação</h1>
    <p>Apresentação do projeto Passos Mágicos, Datathon FIAP 2026</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "💡 Optamos por uma apresentação executiva, com foco no impacto e na experiência do "
    "usuário final, em vez de um detalhamento técnico dos modelos e da arquitetura. Esse "
    "aprofundamento técnico está documentado no "
    "[repositório do projeto](https://github.com/gnunes-io/passos_magicos_html)."
)

html(
    f'''
    <iframe
        src="{YOUTUBE_EMBED_URL}"
        title="Vídeo Apresentação — Passos Mágicos"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen="true"
        width="100%"
        height="500"
        style="display:block;"
    ></iframe>
    ''',
    height=500,
)

st.markdown("<br>", unsafe_allow_html=True)
st.caption(f"Assista também direto no [YouTube]({YOUTUBE_WATCH_URL}).")
