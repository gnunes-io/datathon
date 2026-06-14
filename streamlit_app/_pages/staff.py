"""Página Staff PsicoNeuroPedagogia — equipe real da ONG."""
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import GLOBAL_CSS, PM_BLUE, PM_GOLD

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="pm-hero">
    <h1>👥 Staff PsicoNeuroPedagogia</h1>
    <p>Equipe multidisciplinar da Associação Passos Mágicos — Embu-Guaçu, SP</p>
</div>
""", unsafe_allow_html=True)

# ── Liderança ──────────────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Fundadores</p>', unsafe_allow_html=True)

f1, f2 = st.columns(2, gap="medium")
with f1:
    st.markdown(f"""
    <div style="background:white; border-radius:12px; padding:1.25rem 1.25rem;
                box-shadow:0 1px 4px rgba(0,0,0,0.08); border-top:4px solid {PM_BLUE};">
        <div style="font-size:2rem; text-align:center; margin-bottom:0.5rem;">👨‍💼</div>
        <div style="font-weight:700; color:{PM_BLUE}; font-size:1rem; text-align:center;">
            Dimetri Ivanoff Júnior
        </div>
        <div style="text-align:center; font-size:0.78rem; color:#64748B; margin-top:0.15rem;">
            Fundador e Presidente
        </div>
        <hr style="border-color:#E2E8F0; margin:0.75rem 0;">
        <div style="font-size:0.8rem; color:#475569; line-height:1.5;">
            Formado em Administração pela FGV (1985). Dirige, ao lado de Michelle,
            a Oscar Flues Ind. & Com. há mais de 35 anos.
            Desde 1992 coordena o Projeto Passos Mágicos, formalizando-o em 2016.
        </div>
    </div>
    """, unsafe_allow_html=True)
with f2:
    st.markdown(f"""
    <div style="background:white; border-radius:12px; padding:1.25rem 1.25rem;
                box-shadow:0 1px 4px rgba(0,0,0,0.08); border-top:4px solid {PM_GOLD};">
        <div style="font-size:2rem; text-align:center; margin-bottom:0.5rem;">👩‍💼</div>
        <div style="font-weight:700; color:{PM_BLUE}; font-size:1rem; text-align:center;">
            Michelle Dolores Flues Ivanoff
        </div>
        <div style="text-align:center; font-size:0.78rem; color:#64748B; margin-top:0.15rem;">
            Diretora de Desenvolvimento Social
        </div>
        <hr style="border-color:#E2E8F0; margin:0.75rem 0;">
        <div style="font-size:0.8rem; color:#475569; line-height:1.5;">
            Formada em Psicologia (UNISA). Desde os 14 anos atua em causas humanitárias voluntárias.
            Em 1992 idealiza o Projeto Passos Mágicos e em 2016 funda a Associação.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Coordenação Pedagógica ─────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Coordenação Pedagógica</p>', unsafe_allow_html=True)
coord_cols = st.columns(3, gap="medium")
for col, nome, cargo in [
    (coord_cols[0], "Marcio Melito",     "Coordenador Pedagógico"),
    (coord_cols[1], "Sandra Cézero",     "Coordenadora Multiprofissional"),
    (coord_cols[2], "Rebecca Mitsunaga", "Coordenadora de Parcerias"),
]:
    with col:
        st.markdown(f"""
        <div style="background:white; border-radius:10px; padding:1rem; text-align:center;
                    box-shadow:0 1px 3px rgba(0,0,0,0.07); border-left:4px solid {PM_BLUE};">
            <div style="font-size:1.5rem;">🎓</div>
            <div style="font-weight:700; color:{PM_BLUE}; font-size:0.88rem; margin-top:0.3rem;">{nome}</div>
            <div style="font-size:0.75rem; color:#64748B;">{cargo}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Equipe Multidisciplinar ───────────────────────────────────────────────────
def _render_team_section(title, emoji, color, members, cargo_label=""):
    st.markdown(f'<p class="section-hdr">{title}</p>', unsafe_allow_html=True)
    cols = st.columns(min(len(members), 5), gap="small")
    for col, nome in zip(cols, members):
        with col:
            cargo_html = f'<div style="font-size:0.68rem; color:#64748B;">{cargo_label}</div>' if cargo_label else ''
            st.markdown(f"""
            <div style="background:white; border-radius:8px; padding:0.75rem 0.5rem;
                        text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.06);
                        border-top:3px solid {color};">
                <div style="font-size:1.2rem;">{emoji}</div>
                <div style="font-size:0.78rem; font-weight:600; color:{PM_BLUE};
                            margin-top:0.25rem; line-height:1.3;">{nome}</div>
                {cargo_html}
            </div>
            """, unsafe_allow_html=True)

_render_team_section("Psicologia", "🧠", "#8B5CF6", [
    "Camila Aparecida", "Carolina Costa", "Fernanda Freitas",
    "Leandro Rodrigues", "Thamyris Barbosa"
])
st.markdown("<br>", unsafe_allow_html=True)

_render_team_section("Psicopedagogia", "📖", "#3B82F6", [
    "Diane Alves", "Vanessa Muniz"
])
st.markdown("<br>", unsafe_allow_html=True)

_render_team_section("Neuropsicopedagogia", "🔬", "#06B6D4", [
    "Ana Queiroz", "Amanda Souza", "Josiane Lacerda"
])
st.markdown("<br>", unsafe_allow_html=True)

_render_team_section("Assistência Social", "🤝", "#10B981", [
    "Claudia Aguilar", "Sheila Faria"
])
st.markdown("<br>", unsafe_allow_html=True)

# ── Equipe Pedagógica ─────────────────────────────────────────────────────────
st.markdown('<p class="section-hdr">Equipe Pedagógica</p>', unsafe_allow_html=True)

tab_port, tab_mat, tab_ing, tab_alfa, tab_rob, tab_music = st.tabs([
    "Língua Portuguesa", "Matemática", "Inglês", "Alfabetização", "Robótica", "Musicalização"
])
with tab_port:
    for n in ["Fernanda Santos", "Juscelino Rodrigues", "Maria Tereza", "Michelle Bispo"]:
        st.markdown(f"- {n}")
with tab_mat:
    for n in ["Anderson Lima", "Carla Alves", "Daniel Cavalheiro", "Darlene Carvalho",
              "Jeferson Nogueira", "Samuel Santos"]:
        st.markdown(f"- {n}")
with tab_ing:
    for n in ["Marcio Melito", "Milene Santos", "Thainá Santana"]:
        st.markdown(f"- {n}")
with tab_alfa:
    for n in ["Adriana Pistori", "Edlene Ferreira"]:
        st.markdown(f"- {n}")
with tab_rob:
    for n in ["Anderson Lima", "Bruno Costa", "Cristoffer Viana", "Estefani Almeida"]:
        st.markdown(f"- {n}")
with tab_music:
    for n in ["Isabely Vilar", "Juliana Bordini"]:
        st.markdown(f"- {n}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Sobre o INDE e esse sistema ───────────────────────────────────────────────
st.info(
    "O **Índice de Desenvolvimento Educacional (INDE)** e suas pedras classificatórias foram criados "
    "pela equipe da Passos Mágicos e reconhecidos no **Prêmio Excelência Poliedro** — "
    "3º lugar em Gestão Escolar (2024) e vencedor em Tecnologia (2025, Programa Jovens Inventores). "
    "Este sistema de Radar de Risco foi construído sobre esse mesmo INDE como feature central do modelo preditivo.",
    icon="🏆"
)

st.markdown(
    "<div style='text-align:center; color:#94A3B8; font-size:0.75rem; margin-top:1.5rem;'>"
    "Dados da equipe extraídos do Relatório de Atividades 2025 · Passos Mágicos"
    "</div>",
    unsafe_allow_html=True
)
