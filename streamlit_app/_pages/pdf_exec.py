"""Página PDF Executivo, redirect para o documento."""
import os
import sys
import streamlit as st
from streamlit.components.v1 import html

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

SLIDES_EMBED_URL = "https://docs.google.com/presentation/d/e/2PACX-1vQP11wbMvkAMAbPuvX3Z9uySGhqcwAm1q1tfLX1iRGdoBKnUxGYSATJUVd19i2bMxG8NAzKnSejG63W/pubembed?start=true&loop=true&delayms=5000"
SLIDES_PUBLIC_URL = "https://docs.google.com/presentation/d/1dLJoSnzWTKhTQt9kUWo6DjNK42BRzDJ0I_Dy8RBmzYs/edit?slide=id.p1#slide=id.p1"

st.markdown("""
<div class="pm-hero">
    <h1>📄 PDF Executivo</h1>
    <p>Sumário executivo do projeto Passos Mágicos × Datathon FIAP</p>
</div>
""", unsafe_allow_html=True)

html(
    f'''
    <iframe
        src="{SLIDES_EMBED_URL}"
        frameborder="0"
        width="100%"
        height="720"
        allowfullscreen="true"
        mozallowfullscreen="true"
        webkitallowfullscreen="true"
    ></iframe>
    ''',
    height=740,
)

st.markdown("<br>", unsafe_allow_html=True)
st.link_button(
    "Abrir apresentação no Google Slides →",
    url=SLIDES_PUBLIC_URL,
    use_container_width=True,
    type="primary",
)
st.caption("A apresentação também pode ser aberta em nova aba.")