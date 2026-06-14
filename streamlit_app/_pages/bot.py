"""Página Assistente Psicopedagógico — redirect para o chatbot."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

BOT_URL = "https://google.com"  # placeholder — substituir pela URL Vercel em produção

st.markdown("""
<div class="pm-hero">
    <h1>🤖 Assistente Psicopedagógico</h1>
    <p>Chat inteligente com 3 personas: Guia do Aluno · Painel do Gestor · Radar de Risco</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")
for col, emoji, titulo, desc in [
    (c1, "🧒", "Guia do Aluno",     "Linguagem acolhedora para apoiar os aprendizes em sua jornada educacional."),
    (c2, "📊", "Painel do Gestor",  "Análises e dados para gestores e coordenadores pedagógicos."),
    (c3, "🚨", "Radar de Risco",    "Alertas preditivos e recomendações de intervenção por indicador e fase."),
]:
    with col:
        st.markdown(f"""
        <div class="step-card">
            <div style="font-size:2rem;">{emoji}</div>
            <h4>{titulo}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.link_button(
    "Abrir Assistente Psicopedagógico →",
    url=BOT_URL,
    use_container_width=True,
    type="primary",
)
st.caption("O assistente será aberto em uma nova aba.")
