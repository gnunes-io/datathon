"""Página Assistente Psicopedagógico, Bia."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

BOT_URL = "https://passos-magicos-html.vercel.app/"

_ASSETS    = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
_INTRO_IMG = os.path.join(_ASSETS, 'bia_intro.png')
_ARCH_IMG  = os.path.join(_ASSETS, 'Arquitetura_Bia.png')

# ── CSS: tema lavanda da Bia ──────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main { background: #F7F4FF !important; }

.bia-hero {
    background: linear-gradient(140deg, #7C3AED 0%, #5B21B6 55%, #4C1D95 100%);
    border-radius: 16px; padding: 2.5rem 2rem 2.25rem;
    text-align: center; margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
}
.bia-hero h1  { color: #fff; font-size: 2.1rem; margin: 0 0 0.35rem; font-weight: 800;
                position: relative; z-index: 1; }
.bia-hero .sub { color: #E9D5FF; font-size: 0.9rem; margin: 0;
                 position: relative; z-index: 1; }
.bia-hero .hero-content { position: relative; z-index: 1; }

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
}

/* feature cards: inline styles por card, não usa .step-card global */
.bia-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem 1.2rem 1.35rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    margin-bottom: 1.1rem;
    height: 100%;
}
.bia-card .icon { font-size: 2rem; margin-bottom: 0.6rem; }
.bia-card h4    { font-size: 0.95rem; font-weight: 700; margin: 0 0 0.5rem; }
.bia-card p     { color: #64748B; font-size: 0.82rem; margin: 0; line-height: 1.55; }

/* carousel placeholder */
.bia-carousel { display:flex; gap:1rem; overflow-x:auto; padding:0.4rem 0.1rem 1rem;
                scrollbar-width: thin; scrollbar-color: #C4B5FD transparent; }
.bia-carousel::-webkit-scrollbar { height: 4px; }
.bia-carousel::-webkit-scrollbar-thumb { background: #C4B5FD; border-radius: 2px; }
.bia-ph-card {
    flex-shrink: 0; width: 260px; height: 165px;
    background: linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%);
    border-radius: 12px; border: 1px solid #C4B5FD;
    display: flex; align-items: center; justify-content: center;
    flex-direction: column; gap: 0.4rem;
}
.bia-ph-card span.ph-icon { font-size: 2rem; }
.bia-ph-card span.ph-lbl  { font-size: 0.75rem; color: #7C3AED; font-weight: 600; }

/* section headers */
[data-testid="stMarkdown"] h3 { color: #6D28D9; }
hr { border-color: #E9D5FF !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero com botão integrado ──────────────────────────────────────────────────
st.markdown(f"""
<div class="bia-hero">
    <!-- decorações de fundo -->
    <div style="position:absolute;top:-40px;right:-40px;width:180px;height:180px;
                border-radius:50%;background:rgba(255,255,255,0.07);pointer-events:none;"></div>
    <div style="position:absolute;bottom:-30px;left:-30px;width:130px;height:130px;
                border-radius:50%;background:rgba(255,255,255,0.05);pointer-events:none;"></div>
    <div style="position:absolute;top:20px;left:60px;width:60px;height:60px;
                border-radius:50%;background:rgba(255,255,255,0.04);pointer-events:none;"></div>
    <div style="position:absolute;bottom:15px;right:100px;width:40px;height:40px;
                border-radius:50%;background:rgba(255,255,255,0.06);pointer-events:none;"></div>
    <!-- conteúdo -->
    <div class="hero-content">
        <div style="display:inline-flex;align-items:center;gap:0.4rem;
                    background:rgba(255,255,255,0.12);border-radius:20px;
                    padding:0.2rem 0.85rem;margin-bottom:0.9rem;">
            <span style="width:7px;height:7px;background:#4ade80;border-radius:50%;flex-shrink:0;"></span>
            <span style="color:#E9D5FF;font-size:0.78rem;">Assistente Psicopedagógica Virtual · Online</span>
        </div>
        <h1>Conheça a Bia</h1>
        <p style="color:#EDE9FE;font-size:0.85rem;margin:0.3rem 0 0;opacity:0.8;letter-spacing:0.01em;">
            Passos Mágicos · Apoio educacional disponível 24h
        </p>
        <a class="bia-cta-btn" href="{BOT_URL}" target="_blank">Fale com a Bia →</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Por que criamos a Bia — imagem à esquerda ─────────────────────────────────
_pad, img_col, txt_col = st.columns([0.05, 0.30, 0.65], gap="medium")

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
    _C = "display:inline-flex;align-items:center;gap:0.35rem;background:#EDE9FE;color:#6D28D9;font-size:0.78rem;font-weight:600;padding:0.38rem 0.85rem;border-radius:20px;white-space:nowrap;"
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.25rem;">'
        f'<span style="{_C}">🤍 Humanizada</span>'
        f'<span style="{_C}">🧠 Especialista</span>'
        f'<span style="{_C}">💜 Acolhedora</span>'
        f'<span style="{_C}">🔒 Ética</span>'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Como a Bia funciona — cards com cores distintas ───────────────────────────
st.markdown("### Como a Bia funciona")

_CARDS = [
    ("🙅", "Anti-despejo de indicadores",
     "A Bia nunca lista os números do aluno em bloco. Ela usa os indicadores (IAN, INDE, IEG…) "
     "como bússola interna, traduzindo-os em conversa acolhedora, sem transformar a interação "
     "em um relatório frio de dados."),

    ("🆘", "Protocolo de crise emocional",
     "Ao detectar sinais de sofrimento intenso ou risco, a Bia entra no Estado de Crise: "
     "interrompe qualquer pauta acadêmica, valida o sentimento do aluno e oferece o contato "
     "do CVV (188), priorizando o acolhimento humano acima de qualquer encaminhamento educacional."),

    ("🆔", "Personalização por RA",
     "Ao informar o número de matrícula (ex.: RA-42), a Bia consulta a base Supabase e acessa "
     "os indicadores reais do aprendiz: fase, INDE, pedra, IAN, IDA, IEG e mais, sem precisar "
     "que o aluno informe nenhum dado acadêmico manualmente."),

    ("🧠", "Memória de sessão contextual",
     "Cada conversa mantém contexto de até 20 mensagens via Redis, permitindo que a Bia retome "
     "o fio da conversa sem perguntar as mesmas coisas repetidamente, "
     "a continuidade é parte do cuidado."),

    ("📚", "Respostas baseadas em RAG",
     "Toda descrição de programa institucional (Construindo Sonhos, Speed Up, Vem Ser…) "
     "vem exclusivamente da base de conhecimento Pinecone, alimentada pelo Relatório de "
     "Atividades 2025 e pelo Código de Ética da ONG. A Bia nunca improvisa detalhes institucionais."),

    ("🔀", "Redirecionamento gentil fora do escopo",
     "Perguntas não relacionadas à jornada educacional (Copa do Mundo, receitas, política…) "
     "são redirecionadas com leveza para o foco psicopedagógico, sem rejeitar o aluno, "
     "mas mantendo o propósito do canal."),
]

c1, c2 = st.columns(2, gap="large")
for i, (icon, title, text) in enumerate(_CARDS):
    col = c1 if i % 2 == 0 else c2
    with col:
        st.markdown(f"""
        <div class="bia-card" style="border-top:4px solid #7C3AED;">
            <div class="icon" style="text-align:center;">{icon}</div>
            <h4 style="color:#374151;text-align:center;">{title}</h4>
            <p>{text}</p>
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

# ── Galeria — carrossel placeholder ───────────────────────────────────────────
st.markdown("### 📸 Galeria")
st.caption("Em breve: registros do desenvolvimento, apresentações e bastidores do projeto.")

_PH_ITEMS = [
    ("📷", "Desenvolvimento"),
    ("👥", "Nossa Equipe"),
    ("🎤", "Apresentação"),
    ("🏫", "Passos Mágicos"),
    ("💻", "Tech Hub"),
]
ph_html = "".join(f"""
    <div class="bia-ph-card">
        <span class="ph-icon">{icon}</span>
        <span class="ph-lbl">{label}</span>
    </div>""" for icon, label in _PH_ITEMS)

st.markdown(f'<div class="bia-carousel">{ph_html}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── CTA final destacado ───────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#7C3AED 0%,#4C1D95 100%);
            border-radius:16px; padding:2.5rem 2rem; text-align:center; margin:0.5rem 0 1.5rem;">
    <h3 style="color:white; font-size:1.6rem; margin:0 0 0.6rem; font-weight:800;">
        Experimente agora
    </h3>
    <p style="color:#E9D5FF; font-size:0.9rem; margin:0 auto 1.5rem; max-width:480px; line-height:1.6;">
        Informe seu <strong style="color:white;">RA</strong> (ex.: RA-42) para que a Bia possa
        personalizar o atendimento, ou faça uma pergunta livre sobre os programas da Passos Mágicos.
    </p>
    <a href="{BOT_URL}" target="_blank"
       style="display:inline-block; background:rgba(255,255,255,0.95); color:#6D28D9;
              padding:0.75rem 3rem; border-radius:10px; font-weight:700; font-size:1rem;
              text-decoration:none; box-shadow:0 4px 16px rgba(0,0,0,0.22);">
        Fale com a Bia →
    </a>
</div>
""", unsafe_allow_html=True)

# ── Tags: Bia + Sistema ───────────────────────────────────────────────────────
_CHIP = "display:inline-flex;align-items:center;gap:0.35rem;background:#EDE9FE;color:#6D28D9;font-size:0.78rem;font-weight:600;padding:0.38rem 0.85rem;border-radius:20px;white-space:nowrap;"
_LBL  = "font-size:0.7rem;font-weight:700;letter-spacing:0.08em;color:#A78BFA;text-transform:uppercase;display:block;margin-bottom:0.6rem;"

st.markdown(
    '<div style="text-align:center;margin:0.5rem 0 2rem;padding:1.5rem 1.5rem;background:white;border-radius:16px;box-shadow:0 2px 12px rgba(124,58,237,0.07);">'
    f'<span style="{_LBL}">O Sistema</span>'
    '<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:0.5rem;">'
    f'<span style="{_CHIP}">📱 Mobile Friendly</span>'
    f'<span style="{_CHIP}">⏰ Disponível 24h</span>'
    f'<span style="{_CHIP}">💬 Lembra a Conversa</span>'
    f'<span style="{_CHIP}">🎯 Respostas Precisas</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)
