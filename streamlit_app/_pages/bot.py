"""Página Assistente Psicopedagógico — Bia."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

BOT_URL = "https://passos-magicos-html.vercel.app/"

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pm-hero">
    <h1>💬 Bia — Assistente Psicopedagógica Virtual</h1>
    <p>Uma IA de apoio à jornada educacional dos aprendizes Passos Mágicos,
       disponível a qualquer hora, com escuta ativa e encaminhamentos personalizados.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CTA principal ─────────────────────────────────────────────────────────────
st.link_button(
    "Conversar com a Bia →",
    url=BOT_URL,
    use_container_width=True,
    type="primary",
)
st.caption("O chat será aberto em uma nova aba.")

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Por que criamos a Bia ─────────────────────────────────────────────────────
st.markdown("### Por que criamos a Bia?")
st.markdown("""
A equipe de Psicopedagogia da Passos Mágicos acompanha mais de **1.200 aprendizes**
distribuídos entre Fase Alfa e Fase 10. Identificar quem precisa de atenção imediata —
antes que a defasagem se consolide — é um desafio constante de tempo e escala.

A **Bia** nasceu para ampliar esse alcance: um canal de escuta disponível 24h, capaz de
acolher o aluno no momento em que ele sente a necessidade, coletar sinais de alerta e
encaminhá-lo para o programa certo — sem substituir o olhar humano das psicopedagogas,
mas chegando antes delas.
""")

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Funcionalidades ───────────────────────────────────────────────────────────
st.markdown("### Como a Bia funciona")

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown(f"""
    <div class="step-card">
        <div style="font-size:2rem;">🙅</div>
        <h4>Anti-despejo de indicadores</h4>
        <p>A Bia nunca lista os números do aluno em bloco.
           Ela usa os indicadores (IAN, INDE, IEG…) como bússola interna,
           traduzindo-os em conversa acolhedora — sem transformar a interação
           em um relatório frio de dados.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step-card">
        <div style="font-size:2rem;">🆔</div>
        <h4>Personalização por RA</h4>
        <p>Ao informar o número de matrícula (ex.: RA-42), a Bia consulta
           a base Supabase e acessa os indicadores reais do aprendiz:
           fase, INDE, pedra, IAN, IDA, IEG e mais — sem precisar que o aluno
           informe nenhum dado acadêmico manualmente.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
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
    st.markdown(f"""
    <div class="step-card">
        <div style="font-size:2rem;">🆘</div>
        <h4>Protocolo de crise emocional</h4>
        <p>Ao detectar sinais de sofrimento intenso ou risco, a Bia entra no
           Estado de Crise: interrompe qualquer pauta acadêmica, valida o sentimento
           do aluno e oferece o contato do CVV (188) — priorizando o acolhimento
           humano acima de qualquer encaminhamento educacional.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step-card">
        <div style="font-size:2rem;">🧠</div>
        <h4>Memória de sessão contextual</h4>
        <p>Cada conversa mantém contexto de até 20 mensagens via Redis,
           permitindo que a Bia retome o fio da conversa sem perguntar as
           mesmas coisas repetidamente — a continuidade é parte do cuidado.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step-card">
        <div style="font-size:2rem;">🔀</div>
        <h4>Redirecionamento gentil fora do escopo</h4>
        <p>Perguntas não relacionadas à jornada educacional (Copa do Mundo,
           receitas, política…) são redirecionadas com leveza para o foco
           psicopedagógico — sem rejeitar o aluno, mas mantendo o propósito
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

_ARCH_IMG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Arquitetura_Bia.png")
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
st.link_button(
    "Abrir a Bia →",
    url=BOT_URL,
    use_container_width=True,
    type="primary",
)
