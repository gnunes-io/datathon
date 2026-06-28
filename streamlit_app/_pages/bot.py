"""Página Assistente Psicopedagógico, Bia."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

BOT_URL = "https://passos-magicos-html.vercel.app/"

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
_INTRO_IMG  = os.path.join(_ASSETS, 'bia_intro.png')
_ARCH_IMG   = os.path.join(_ASSETS, 'Arquitetura_Bia.png')

# ── CSS: tema lavanda da Bia ──────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main { background: #F7F4FF !important; }

.bia-hero {
    background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
    border-radius: 16px; padding: 2rem 2rem 1.75rem;
    text-align: center; margin-bottom: 1.5rem;
}
.bia-hero h1  { color: #fff; font-size: 2rem; margin: 0 0 0.35rem; font-weight: 800; }
.bia-hero .sub { color: #E9D5FF; font-size: 0.9rem; margin: 0; }
.bia-cta-btn {
    display: inline-block;
    background: rgba(255,255,255,0.95);
    color: #6D28D9 !important;
    padding: 0.65rem 2.5rem;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.95rem;
    text-decoration: none !important;
    margin-top: 1.35rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.18);
    letter-spacing: 0.01em;
    transition: opacity 0.15s;
}
.bia-cta-btn:hover { opacity: 0.9; }

.section-hdr  { color: #7C3AED !important; border-bottom-color: #C4B5FD !important; }
.step-card    { border-top-color: #7C3AED !important; }
.step-card h4 { color: #7C3AED !important; }

[data-testid="stMarkdown"] h3 { color: #6D28D9; }
hr { border-color: #E9D5FF !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero com botão integrado ──────────────────────────────────────────────────
st.markdown(f"""
<div class="bia-hero">
    <h1>Conheça a Bia</h1>
    <div style="display:flex;align-items:center;justify-content:center;gap:0.4rem;margin-bottom:0.3rem;">
        <span style="width:9px;height:9px;background:#4ade80;border-radius:50%;flex-shrink:0;"></span>
        <span class="sub">Assistente Psicopedagógica Virtual · Online</span>
    </div>
    <p style="color:#EDE9FE;font-size:0.82rem;margin:0;opacity:0.75;">
        Passos Mágicos · Apoio educacional disponível 24h
    </p>
    <a class="bia-cta-btn" href="{BOT_URL}" target="_blank">Fale com a Bia →</a>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Por que criamos a Bia — imagem à esquerda ─────────────────────────────────
img_col, txt_col = st.columns([0.42, 0.58], gap="large")

with img_col:
    if os.path.exists(_INTRO_IMG):
        st.image(_INTRO_IMG, use_container_width=True)

with txt_col:
    st.markdown("### Por que criamos a Bia?")
    st.markdown("""
A equipe de Psicopedagogia da Passos Mágicos acompanha mais de **1.200 aprendizes**
distribuídos entre Fase Alfa e Fase 10. Identificar quem precisa de atenção imediata,
antes que a defasagem se consolide, é um desafio constante de tempo e escala.

A **Bia** nasceu para ampliar esse alcance: um canal de escuta disponível 24h, capaz de
acolher o aluno no momento em que ele sente a necessidade, coletar sinais de alerta e
encaminhá-lo para o programa certo, sem substituir o olhar humano das psicopedagogas,
mas chegando antes delas.
    """)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Como a Bia funciona ───────────────────────────────────────────────────────
st.markdown("### Como a Bia funciona")

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown("""
    <div class="step-card">
        <div style="font-size:2rem;">🙅</div>
        <h4>Anti-despejo de indicadores</h4>
        <p>A Bia nunca lista os números do aluno em bloco.
           Ela usa os indicadores (IAN, INDE, IEG…) como bússola interna,
           traduzindo-os em conversa acolhedora, sem transformar a interação
           em um relatório frio de dados.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="step-card">
        <div style="font-size:2rem;">🆔</div>
        <h4>Personalização por RA</h4>
        <p>Ao informar o número de matrícula (ex.: RA-42), a Bia consulta
           a base Supabase e acessa os indicadores reais do aprendiz:
           fase, INDE, pedra, IAN, IDA, IEG e mais, sem precisar que o aluno
           informe nenhum dado acadêmico manualmente.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="step-card">
        <div style="font-size:2rem;">📚</div>
        <h4>Respostas baseadas em RAG</h4>
        <p>Toda descrição de programa institucional (Construindo Sonhos,
           Speed Up, Vem Ser…) vem exclusivamente da base de conhecimento Pinecone,
           alimentada pelo Relatório de Atividades 2025 e pelo Código de Ética da ONG.
           A Bia nunca improvisa detalhes institucionais.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="step-card">
        <div style="font-size:2rem;">🆘</div>
        <h4>Protocolo de crise emocional</h4>
        <p>Ao detectar sinais de sofrimento intenso ou risco, a Bia entra no
           Estado de Crise: interrompe qualquer pauta acadêmica, valida o sentimento
           do aluno e oferece o contato do CVV (188), priorizando o acolhimento
           humano acima de qualquer encaminhamento educacional.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="step-card">
        <div style="font-size:2rem;">🧠</div>
        <h4>Memória de sessão contextual</h4>
        <p>Cada conversa mantém contexto de até 20 mensagens via Redis,
           permitindo que a Bia retome o fio da conversa sem perguntar as
           mesmas coisas repetidamente, a continuidade é parte do cuidado.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="step-card">
        <div style="font-size:2rem;">🔀</div>
        <h4>Redirecionamento gentil fora do escopo</h4>
        <p>Perguntas não relacionadas à jornada educacional (Copa do Mundo,
           receitas, política…) são redirecionadas com leveza para o foco
           psicopedagógico, sem rejeitar o aluno, mas mantendo o propósito
           do canal.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Arquitetura ───────────────────────────────────────────────────────────────
st.markdown("### Arquitetura do sistema")
st.markdown("""
A Bia opera em três camadas: um **frontend seguro** (HTML/JS no Vercel) que nunca
expõe credenciais; um **proxy serverless** que autentica e encaminha as mensagens;
e um **workflow n8n** que orquestra o agente GPT-4o-mini com ferramentas especializadas.
""")
if os.path.exists(_ARCH_IMG):
    st.image(_ARCH_IMG, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── CTA final ─────────────────────────────────────────────────────────────────
st.markdown("### Experimente agora")
st.markdown(
    "Informe seu **RA** (ex.: `RA-42`) para que a Bia possa personalizar o atendimento, "
    "ou faça uma pergunta livre sobre os programas da Passos Mágicos."
)
st.markdown(f"""
<a class="bia-cta-btn" href="{BOT_URL}" target="_blank"
   style="display:block; text-align:center; margin-top:0.75rem;">
    Abrir a Bia →
</a>
<br>
""", unsafe_allow_html=True)
