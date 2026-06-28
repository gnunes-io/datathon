"""Página inicial, apresentação do projeto e onboarding do pedagogo."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import LOGO_PATH, INDICATORS, PEDRAS_INFO, PM_BLUE, PM_GOLD, load_model, GLOBAL_CSS

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
payload = load_model()

# ── Hero ───────────────────────────────────────────────────────────────────────
_, logo_col, _ = st.columns([2, 1, 2])
with logo_col:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)

st.markdown("""
<div class="pm-hero">
    <h1>Radar de Risco, Passos Mágicos</h1>
    <p>Sistema de apoio à decisão para identificação precoce de alunos em risco de defasagem escolar</p>
</div>
""", unsafe_allow_html=True)

# ── Impacto 2025 ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Passos Mágicos em números (2025)</p>', unsafe_allow_html=True)

imp1, imp2, imp3, imp4, imp5, imp6 = st.columns(6)
for col, val, label in [
    (imp1, "1.200",  "aprendizes atendidos"),
    (imp2, "4",      "unidades em Embu-Guaçu"),
    (imp3, "119",    "universitários ativos"),
    (imp4, "87",     "no mercado de trabalho"),
    (imp5, "120",    "alfabetizados fora da idade"),
    (imp6, "+14.000h","de oficinas no PAC"),
]:
    with col:
        st.markdown(f"""
        <div style="background:white; border-radius:10px; padding:0.85rem 0.5rem;
                    text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.07);
                    border-top:3px solid {PM_GOLD};">
            <div style="font-size:1.5rem; font-weight:800; color:{PM_BLUE}; line-height:1.1;">{val}</div>
            <div style="font-size:0.72rem; color:#64748B; margin-top:0.2rem;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Jornada do aprendiz ────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Jornada do aprendiz</p>', unsafe_allow_html=True)
st.caption("O PAC é organizado em Fase Alfa (alfabetização) + Fases 1 a 9, com suporte psicossocial em cada etapa.")

jor_cols = st.columns(6, gap="small")
for col, etapa, desc in [
    (jor_cols[0], "🔤 Fase Alfa", "Alfabetização"),
    (jor_cols[1], "📚 Fases 1–9", "PAC, aceleração do conhecimento"),
    (jor_cols[2], "🏫 Bolsas Médio", "Arco-Íris, Einstein, FIAP School"),
    (jor_cols[3], "🎓 Vem Ser", "Prep. vestibular (Me Salva!)"),
    (jor_cols[4], "🏛️ Universidade", "119 universitários cursando/formados"),
    (jor_cols[5], "💼 Trabalho", "87 no mercado · R$ 2.772 médio"),
]:
    with col:
        st.markdown(f"""
        <div style="background:white; border-radius:8px; padding:0.75rem 0.6rem;
                    text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.06);
                    border-left:3px solid {PM_BLUE}; height:100%;">
            <div style="font-size:1.1rem;">{etapa.split()[0]}</div>
            <div style="font-size:0.72rem; font-weight:700; color:{PM_BLUE}; margin:0.2rem 0;">
                {' '.join(etapa.split()[1:])}
            </div>
            <div style="font-size:0.68rem; color:#64748B;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Como funciona ──────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Como funciona este sistema</p>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")
for col, num, titulo, desc in [
    (c1, "1", "Preencha os indicadores",
     "Insira os dados do aluno obtidos nas avaliações pedagógicas e psicossociais da ONG."),
    (c2, "2", "O sistema calcula o risco",
     "Um modelo de machine learning analisa o perfil e estima a probabilidade de defasagem escolar."),
    (c3, "3", "Tome uma decisão informada",
     "Receba os fatores de atenção com programas reais da ONG e recomendações priorizadas."),
]:
    with col:
        st.markdown(f"""
        <div class="step-card">
            <div class="num">{num}</div>
            <h4>{titulo}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Métricas do modelo ─────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Confiabilidade do sistema</p>', unsafe_allow_html=True)

if payload:
    auc  = payload.get('auc_roc', 0)
    thr  = payload.get('threshold', 0)
    has_shap = payload.get('shap_explainer') is not None
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Alunos no treino",
              f"~{3_030:,}".replace(",", "."), "2022–2023–2024")
    m2.metric("Capacidade discriminativa", f"{auc:.0%}",
              "AUC-ROC (validação cruzada OOF)")
    m3.metric("Threshold de risco", f"{thr:.0%}",
              "calibrado por Fbeta β=2 (sem leakage)")
    m4.metric("Explicabilidade SHAP", "✅ Ativa" if has_shap else "⚠️ Gere o pkl",
              "fatores por aluno")
else:
    st.warning("Modelo não carregado. Execute `model/modelo_preditivo.ipynb` para gerar o `.pkl`.")

st.info(
    "**Como interpretar o risco:** O modelo identifica dois perfis: "
    "(1) aluno **formalmente atrasado de série** (Defasagem ≥ 1 ano) e "
    "(2) aluno em **Quartzo** (INDE < 5,5, pior faixa de desenvolvimento). "
    "O threshold (61%) foi calibrado por Fbeta β=2: o sistema **prefere alertar** a deixar passar.",
    icon="ℹ️"
)

# ── Glossário de indicadores ───────────────────────────────────────────────────
st.markdown('<p class="section-hdr">O que cada indicador significa</p>', unsafe_allow_html=True)
st.caption("Clique para expandir cada indicador e ver a descrição completa.")

for sigla, nome, descricao in INDICATORS:
    with st.expander(f"**{sigla}**, {nome}"):
        st.markdown(f"""
        <div class="ind-card">
            <strong>{sigla}, {nome}</strong><br>
            <small>{descricao}</small>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Escala: 0 a 10 · Quanto maior, melhor o desempenho neste indicador.")

# ── Pedras ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Pedras classificatórias</p>', unsafe_allow_html=True)
st.caption("As pedras são atribuídas com base no INDE e representam o estágio de desenvolvimento do aluno.")

p1, p2, p3, p4 = st.columns(4)
for col, (pedra, (faixa, emoji, cor)) in zip([p1, p2, p3, p4], PEDRAS_INFO.items()):
    with col:
        st.markdown(f"""
        <div style="background:white; border-radius:10px; padding:1rem; text-align:center;
                    box-shadow:0 1px 3px rgba(0,0,0,0.08); border-top:3px solid {cor};">
            <div style="font-size:2rem;">{emoji}</div>
            <strong style="color:{PM_BLUE};">{pedra}</strong><br>
            <small style="color:#64748B;">{faixa}</small>
        </div>
        """, unsafe_allow_html=True)

# ── Aviso ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.warning(
    "**Aviso importante:** Este sistema é uma ferramenta de **apoio à decisão**, "
    "não um substituto ao julgamento da equipe pedagógica e psicossocial. "
    "Situações excepcionais (mudanças familiares, eventos de vida) podem não ser "
    "capturadas pelos indicadores numéricos. A decisão final é sempre do profissional. "
    "Os dados inseridos **não são armazenados** pelo sistema.",
    icon="⚠️"
)

st.markdown(
    "<div style='text-align:center; color:#94A3B8; font-size:0.8rem; margin-top:2rem;'>"
    "Datathon FIAP × Passos Mágicos · Sistema desenvolvido com fins acadêmicos"
    "</div>",
    unsafe_allow_html=True
)
